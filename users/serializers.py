from rest_framework import serializers

from .models import User, Payment

class PaymentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    paid_course = serializers.StringRelatedField(read_only=True)
    paid_lesson = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'payment_date', 'paid_course',
            'paid_lesson', 'amount', 'payment_method'
        ]

class UserProfileSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True, source='payment_set')

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "country",
            "city",
            "phone",
            "avatar",
            "role",
            "is_blocked",
            "payments"
        ]
        read_only_fields = ["id", "email", "role", "is_blocked"]


    def validate_username(self, value):
        """Проверка уникальности username"""
        if User.objects.filter(username=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Пользователь с таким именем уже существует.")
        return value



