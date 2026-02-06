from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from video_generator.views import index

urlpatterns = [
    path("", index, name="index"),  # Main web interface
    path("admin/", admin.site.urls),
    path("", include("video_generator.urls")),  # Includes both web and API routes
]

# Always serve media files (needed for production on Cloud Run)
urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
