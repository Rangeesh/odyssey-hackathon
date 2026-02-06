from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from video_generator.views import index

urlpatterns = [
    path("", index, name="index"),  # Main web interface
    path("admin/", admin.site.urls),
    path("", include("video_generator.urls")),  # Includes both web and API routes
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
