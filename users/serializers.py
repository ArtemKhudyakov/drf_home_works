from rest_framework import serializers
from .models import User

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'country', 'city', 'phone', 'avatar', 'role', 'is_blocked'
        ]
        read_only_fields = ['id', 'email', 'role', 'is_blocked']  # Эти поля нельзя менять

    def validate_username(self, value):
        """Проверка уникальности username"""
        if User.objects.filter(username=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Пользователь с таким именем уже существует.")
        return value