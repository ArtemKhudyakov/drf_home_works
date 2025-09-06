from rest_framework import serializers

from .models import Payment, User


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра платежей"""
    user = serializers.StringRelatedField(read_only=True)
    paid_course = serializers.StringRelatedField(read_only=True)
    paid_lesson = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Payment
        fields = ["id", "user", "payment_date", "paid_course", "paid_lesson", "amount", "payment_method"]


class UserPublicProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для публичного просмотра (ограниченные данные)"""

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name",
            "country", "city", "phone", "avatar", "role"
        ]
        read_only_fields = ["id", "email", "role"]


class UserPrivateProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для приватного просмотра (все данные)"""
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "country", "city", "phone", "avatar", "role",
            "is_blocked", "payments", "is_verified", "date_joined"
        ]
        read_only_fields = ["id", "email", "role", "is_blocked", "is_verified", "date_joined"]




class UserApiRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "country",
            "city",
            "phone",
            "avatar",
        ]

    def validate_username(self, value):
        """Проверка уникальности username"""
        if User.objects.filter(username=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Пользователь с таким именем уже существует.")
        return value