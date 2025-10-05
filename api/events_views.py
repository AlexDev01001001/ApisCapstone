# api/events_views.py
from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Event
from .events_serializers import EventSerializer
from rest_framework.permissions import AllowAny   # ← IMPORTAR ESTO     

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
