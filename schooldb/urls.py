from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ----------------- ADMIN -----------------
    path("admin/", admin.site.urls),

    # ----------------- STUDENTS APP -----------------
    path("", include("students.urls")),  # includes all URLs from the students app
]

# ----------------- MEDIA FILES (for student photos, etc.) -----------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ----------------- STATIC FILES (optional, only for development) -----------------
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
