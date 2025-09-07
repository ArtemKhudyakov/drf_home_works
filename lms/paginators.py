from rest_framework.pagination import PageNumberPagination

class LessonPaginator(PageNumberPagination):
    """
    Пагинатор для уроков
    """
    page_size = 5  # Количество уроков на странице по умолчанию
    page_size_query_param = 'page_size'  # Параметр для изменения количества элементов на странице
    max_page_size = 50  # Максимальное количество элементов на странице


class CoursePaginator(PageNumberPagination):
    """
    Пагинатор для курсов
    """
    page_size = 2  # Количество курсов на странице по умолчанию
    page_size_query_param = 'page_size'  # Параметр для изменения количества элементов на странице
    max_page_size = 20  # Максимальное количество элементов на странице