from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view 
from django.conf import settings
from .serializers import RegisterSerializer, LoginSerializer
from .models import User
import bcrypt, jwt, mercadopago
from datetime import datetime, timedelta, timezone

def make_jwt(user: User):
    payload = {
        "sub": user.id,
        "email": user.email,
        "role": (user.role or "user"),
        "is_admin": (user.role == "admin"),
        "exp": datetime.now(timezone.utc) + timedelta(hours=12),
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token

class RegisterView(APIView):
    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        user = ser.save()
        return Response({
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "dni": user.dni,
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    def post(self, request):
        ser = LoginSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        email = ser.validated_data["email"]
        password = ser.validated_data["password"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Credenciales inválidas."},
                            status=status.HTTP_401_UNAUTHORIZED)

        # Verifica bcrypt (compatible con crypt('...', gen_salt('bf')))
        if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return Response({"detail": "Credenciales inválidas."},
                            status=status.HTTP_401_UNAUTHORIZED)

        token = make_jwt(user)
        return Response({
            "access":token,
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "dni": user.dni,
                "role": user.role,
                "is_admin": user.role == "admin"
            }
        })

@api_view(['POST'])
def create_preference(request):
    import mercadopago
    from rest_framework.response import Response
    from rest_framework import status

    # 🔹 Token de prueba del vendedor (BACKEND)
    sdk = mercadopago.SDK("APP_USR-3373909775013222-110923-0a06eadd95e02c5e7dd31893c77abd15-2977405472")

    title = request.data.get("title", "Entrada de evento")
    price = request.data.get("price", 1)
    quantity = int(request.data.get("quantity", 1))

    preference_data = {
        "items": [
            {
                "title": title,
                "quantity": quantity,
                "unit_price": float(price),
                "currency_id": "PEN",
            }
        ],
        "statement_descriptor": "TESTEVENTOS",
    }

    # ⚠️ Evita usar auto_return en localhost
    host = request.get_host()
    is_local = "localhost" in host or "127.0.0.1" in host
    if not is_local:
        preference_data["back_urls"] = {
            "success": "https://apis-capstone.up.railway.app/pago-exitoso",
            "failure": "https://apis-capstone.up.railway.app/pago-fallido",
            "pending": "https://apis-capstone.up.railway.app/pago-pendiente",
        }
        preference_data["auto_return"] = "approved"

    preference = sdk.preference().create(preference_data)

    print("💬 MercadoPago preference:", preference)  # 👈 importante para ver qué devuelve

    # ✅ Manejo seguro de errores
    if not preference or "response" not in preference:
        return Response(
            {"error": "MercadoPago no devolvió respuesta válida"},
            status=status.HTTP_502_BAD_GATEWAY
        )

    # Si hay error del lado de Mercado Pago
    if preference.get("status") != 201:
        return Response(
            {"error": preference.get("response", {}), "status": preference.get("status")},
            status=status.HTTP_400_BAD_REQUEST
        )

    pref_id = preference["response"].get("id")
    if not pref_id:
        return Response(
            {"error": "MercadoPago no devolvió un ID válido", "response": preference.get("response", {})},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response({"id": pref_id}, status=status.HTTP_201_CREATED)
