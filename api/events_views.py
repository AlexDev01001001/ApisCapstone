# api/events_views.py
from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Event
from .events_serializers import EventSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
class EventViewSet(viewsets.ModelViewSet):
    """
    CRUD para eventos (tabla public.events en Supabase, managed=False)
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]

    # filtros: /api/events/?status=active&organizer_id=1&venue_id=2
    filterset_fields = ["status", "organizer_id", "venue_id", "is_published"]
    # búsqueda simple en título/descr.
    search_fields = ["title", "description"]
    # orden: /api/events/?ordering=-start_datetime
    ordering_fields = ["start_datetime", "end_datetime", "created_at"]
    ordering = ["-start_datetime"]

    def perform_create(self, serializer):
        # si hay usuario autenticado, lo colocamos como organizer_user (FK a usuarios_customuser)
        organizer_user = self.request.user if (self.request.user and self.request.user.is_authenticated) else None
        serializer.save(organizer_user=organizer_user)

    def create(self, request, *args, **kwargs):
        """
        Respuesta 201 con el objeto creado o 400 con errores de validación.
        """
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        PUT/PATCH protegido por IsOrganizerOrReadOnly.
        """
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        DELETE protegido por IsOrganizerOrReadOnly.
        """
        return super().destroy(request, *args, **kwargs)


class ImageUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No se envió ningún archivo."}, status=status.HTTP_400_BAD_REQUEST)

        # Guarda la imagen en media/events/
        file_path = default_storage.save(f"events/{file_obj.name}", file_obj)
        file_url = request.build_absolute_uri(settings.MEDIA_URL + file_path)

        return Response({"url": file_url}, status=status.HTTP_201_CREATED)