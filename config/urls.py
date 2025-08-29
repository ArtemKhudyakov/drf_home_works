from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls", namespace="users")),
    path("courses/", include("lms.urls", namespace="courses")),
    path("lessons/", include("lms.urls", namespace="lessons")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
