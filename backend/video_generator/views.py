import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import VideoJob
from .serializers import VideoJobSerializer
from .tasks import start_generation_thread
from .utils.fetch_lyrics import get_song_lyrics


# Django Template Views
def index(request):
    """Main page with search and job list"""
    jobs = VideoJob.objects.all().order_by("-created_at")[:10]
    return render(request, "video_generator/index.html", {"jobs": jobs})


def search_suggestions(request):
    """Proxy request to LRCLIB search API for suggestions"""
    query = request.GET.get("q", "").strip()
    if not query or len(query) < 2:
        return JsonResponse([], safe=False)
    
    try:
        # Call LRCLIB API
        url = "https://lrclib.net/api/search"
        params = {"q": query}
        headers = {
            "User-Agent": "OdysseyHackathonBot/1.0 (https://github.com/odysseyml/odyssey-hackathon)"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Format suggestions
        suggestions = []
        for item in data[:10]:  # Limit to 10 suggestions
            suggestions.append({
                "id": item.get("id"),
                "title": item.get("trackName"),
                "artist": item.get("artistName"),
                "album": item.get("albumName"),
                "duration": item.get("duration"),
                "synced": bool(item.get("syncedLyrics"))
            })
            
        return JsonResponse(suggestions, safe=False)
    except Exception as e:
        print(f"Error fetching suggestions: {e}")
        return JsonResponse([], safe=False)


def search_lyrics(request):
    """Search for song lyrics and show preview"""
    query = request.GET.get("q", "").strip()
    jobs = VideoJob.objects.all().order_by("-created_at")[:10]
    
    context = {
        "jobs": jobs,
        "query": query,
    }
    
    if query:
        lyrics = get_song_lyrics(query)
        if lyrics:
            context["lyrics"] = lyrics
            # Try to parse artist/title from query for the form
            parts = query.split()
            if len(parts) > 2:
                context["song_title"] = " ".join(parts[:-1])
                context["artist"] = parts[-1]
            elif len(parts) == 2:
                context["song_title"] = parts[0]
                context["artist"] = parts[1]
            else:
                context["song_title"] = query
                context["artist"] = "Unknown"
        else:
            context["error_message"] = f"Could not find lyrics for '{query}'."
    
    return render(request, "video_generator/index.html", context)


@require_http_methods(["POST"])
def generate_video(request):
    """Create a new video generation job"""
    song_title = request.POST.get("song_title", "").strip()
    artist = request.POST.get("artist", "").strip()
    
    if not song_title:
        return redirect("index")
    
    job = VideoJob.objects.create(
        song_title=song_title,
        artist=artist,
        status="pending",
        message="Job created, waiting to start...",
    )
    start_generation_thread(job.id)
    
    return redirect("index")


def job_list_partial(request):
    """Partial view for AJAX job list updates"""
    jobs = VideoJob.objects.all().order_by("-created_at")[:10]
    return render(request, "video_generator/job_list_partial.html", {"jobs": jobs})


@require_http_methods(["POST"])
def cancel_job(request, job_id):
    """Cancel a video generation job"""
    try:
        job = VideoJob.objects.get(id=job_id)
        
        # Only allow cancelling pending or processing jobs
        if job.status in ["pending", "processing"]:
            job.cancelled = True
            job.status = "cancelled"
            job.message = "Job cancelled by user."
            job.save()
            
            return JsonResponse({
                "success": True,
                "message": f"Job '{job.song_title}' has been cancelled."
            })
        else:
            return JsonResponse({
                "success": False,
                "message": f"Cannot cancel job with status: {job.status}"
            }, status=400)
            
    except VideoJob.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Job not found."
        }, status=404)


# REST API ViewSet (keep for API compatibility)
class VideoJobViewSet(viewsets.ModelViewSet):
    queryset = VideoJob.objects.all().order_by("-created_at")
    serializer_class = VideoJobSerializer

    @action(detail=False, methods=["get"])
    def search(self, request):
        query = request.query_params.get("q")
        if not query:
            return Response({"error": "Missing query parameter 'q'"}, status=400)

        lyrics = get_song_lyrics(query)
        if lyrics:
            return Response(
                {
                    "lyrics": lyrics[:500] + "..." if len(lyrics) > 500 else lyrics,
                    "found": True,
                }
            )
        else:
            return Response({"found": False}, status=404)

    def perform_create(self, serializer):
        job = serializer.save()
        start_generation_thread(job.id)
