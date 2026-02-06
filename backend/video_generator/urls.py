from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VideoJobViewSet,
    index,
    generate_video,
    job_list_partial,
    cancel_job,
    search_suggestions,
    search_lyrics,
)

router = DefaultRouter()
router.register(r"jobs", VideoJobViewSet)

urlpatterns = [
    # Web interface URLs
    path("search/", search_lyrics, name="search_lyrics"),
    path("generate/", generate_video, name="generate_video"),
    path("search-suggestions/", search_suggestions, name="search_suggestions"),
    path("jobs-partial/", job_list_partial, name="job_list_partial"),
    path("cancel/<uuid:job_id>/", cancel_job, name="cancel_job"),
    # API URLs (keep for compatibility)
    path("api/", include(router.urls)),
]
