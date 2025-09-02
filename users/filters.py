import django_filters
from .models import Payment
from lms.models import Course, Lesson

class PaymentFilter(django_filters.FilterSet):
    course = django_filters.ModelChoiceFilter(
        field_name='paid_course',
        queryset=Course.objects.all(),
        label='Курс'
    )
    lesson = django_filters.ModelChoiceFilter(
        field_name='paid_lesson',
        queryset=Lesson.objects.all(),
        label='Урок'
    )
    payment_method = django_filters.ChoiceFilter(
        choices=Payment.PAYMENT_METHODS,
        label='Способ оплаты'
    )
    ordering = django_filters.OrderingFilter(
        fields=(
            ('payment_date', 'date'),
            ('-payment_date', '-date'),
        ),
        field_labels={
            'payment_date': 'Дате оплаты (по возрастанию)',
            '-payment_date': 'Дате оплаты (по убыванию)',
        }
    )

    class Meta:
        model = Payment
        fields = ['course', 'lesson', 'payment_method']