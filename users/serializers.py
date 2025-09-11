from rest_framework import serializers

from lms.models import Course, Lesson

from .models import Payment, User
from .services import (
    convert_rub_to_usd,
    create_stripe_price,
    create_stripe_product,
    create_stripe_session,
    get_payment_status
)


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для платежей"""

    user = serializers.StringRelatedField(read_only=True)
    paid_course = serializers.StringRelatedField(read_only=True)
    paid_lesson = serializers.StringRelatedField(read_only=True)
    status = serializers.SerializerMethodField()
    payment_url = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            "id",
            "user",
            "payment_date",
            "paid_course",
            "paid_lesson",
            "amount",
            "payment_method",
            "session_id",
            "link_for_pay",
            "status",
            "payment_url",
        ]
        read_only_fields = ["session_id", "link_for_pay", "status"]

    def get_status(self, obj):
        """Получает статус платежа из Stripe"""
        if obj.session_id:
            return get_payment_status(obj.session_id)
        return "created"

    def get_payment_url(self, obj):
        """Возвращает URL для оплаты"""
        return obj.link_for_pay


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания платежа"""

    course_id = serializers.IntegerField(write_only=True, required=False)
    lesson_id = serializers.IntegerField(write_only=True, required=False)

    # Добавляем read-only поля для ответа
    id = serializers.IntegerField(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    payment_date = serializers.DateTimeField(read_only=True)
    amount = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    session_id = serializers.CharField(read_only=True)
    link_for_pay = serializers.URLField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "user",
            "payment_date",
            "course_id",
            "lesson_id",
            "amount",
            "payment_method",
            "session_id",
            "link_for_pay",
            "status",
        ]
        extra_kwargs = {"payment_method": {"required": True}}

    def get_status(self, obj):
        """Получает статус платежа из Stripe"""
        from .services import get_payment_status

        if obj.session_id:
            return get_payment_status(obj.session_id)
        return "created"

    def validate(self, attrs):
        """Проверяет, что указан только один объект для оплаты"""
        course_id = attrs.get("course_id")
        lesson_id = attrs.get("lesson_id")

        if not course_id and not lesson_id:
            raise serializers.ValidationError("Укажите course_id или lesson_id")

        if course_id and lesson_id:
            raise serializers.ValidationError("Укажите только course_id или только lesson_id")

        return attrs

    def create(self, validated_data):
        """Создает платеж и сессию в Stripe"""
        from lms.models import Course, Lesson

        from .services import convert_rub_to_usd, create_stripe_price, create_stripe_product, create_stripe_session

        request = self.context.get("request")
        user = request.user
        course_id = validated_data.pop("course_id", None)
        lesson_id = validated_data.pop("lesson_id", None)
        payment_method = validated_data.get("payment_method")

        # Получаем объект для оплаты
        if course_id:
            paid_object = Course.objects.get(id=course_id)
            amount = 10000  # Стоимость курса в рублях
            object_type = "course"
            name = f"Курс: {paid_object.name}"
        else:
            paid_object = Lesson.objects.get(id=lesson_id)
            amount = 1000  # Стоимость урока в рублях
            object_type = "lesson"
            name = f"Урок: {paid_object.name}"

        # Конвертируем в USD для Stripe (используем фиксированный курс)
        try:
            from .services import convert_rub_to_usd

            amount_usd = convert_rub_to_usd(amount)
        except:
            # Fallback на фиксированный курс
            amount_usd = amount / 80.0

        try:
            # Создаем продукт и цену в Stripe
            product = create_stripe_product(name, paid_object.description)
            price = create_stripe_price(amount_usd, product.id)
            session = create_stripe_session(price.id)

            # Создаем платеж в базе
            payment_data = {
                "user": user,
                "amount": amount,
                "payment_method": payment_method,
                "session_id": session.id,
                "link_for_pay": session.url,
            }

            if object_type == "course":
                payment_data["paid_course"] = paid_object
            else:
                payment_data["paid_lesson"] = paid_object

            payment = Payment.objects.create(**payment_data)

            return payment

        except Exception as e:
            raise serializers.ValidationError(f"Ошибка при создании платежа: {str(e)}")


class UserPublicProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для публичного просмотра (ограниченные данные)"""

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "country", "city", "phone", "avatar", "role"]
        read_only_fields = ["id", "email", "role"]


class UserPrivateProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для приватного просмотра (все данные)"""

    payments = PaymentSerializer(many=True, read_only=True)

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
            "payments",
            "is_verified",
            "date_joined",
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
