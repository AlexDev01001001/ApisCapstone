from rest_framework import serializers
from .models import User
import bcrypt


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    dni = serializers.CharField(required=True, allow_blank=False, max_length=20)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email ya registrado.")
        return value

    def create(self, validated_data):
        pwd = validated_data.pop('password')
        dni = validated_data.pop('dni')
        hashed = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        return User.objects.create(password_hash=hashed, dni=dni,role="user",**validated_data)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
