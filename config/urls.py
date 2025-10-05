from django.contrib import admin
from django.urls import path
from django.urls import path, include
from api.views import RegisterView, LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/register', RegisterView.as_view()),
    path('api/auth/login', LoginView.as_view()),
]
