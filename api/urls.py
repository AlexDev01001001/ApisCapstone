# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# tus vistas de auth ya existentes
from .views import RegisterView, LoginView

# CRUD de eventos
from .events_views import EventViewSet

router = DefaultRouter()
router.register(r"events", EventViewSet, basename="event")

urlpatterns = [
    # auth (las que ya usabas)
    path("auth/register", RegisterView.as_view()),
    path("auth/login", LoginView.as_view()),

    # router de eventos
    path("", include(router.urls)),
]