from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .serializers import RegisterSerializer, LoginSerializer
from .models import User
import bcrypt, jwt
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
