import threading
import asyncio
import os
import re
import requests
from .models import VideoJob
from .utils.fetch_lyrics import get_song_lyrics
from .utils.lyrics_to_image import generate_image_from_lyrics
from .utils.sentiment_analysis import analyze_sentiment
from .utils.generate_music_video import (
    parse_lrc_lyrics,
    get_lyrics_for_interval,
    generate_video_segment_independent,
)
from odyssey import Odyssey
from moviepy import VideoFileClip, concatenate_videoclips


def run_video_generation(job_id):
    job = VideoJob.objects.get(id=job_id)

    # Check if cancelled before starting
    if job.cancelled:
        job.status = "cancelled"
        job.message = "Job was cancelled before processing started."
        job.save()
        return

    job.status = "processing"
    job.progress = 5
    job.message = "Fetching lyrics..."
    job.save()

    try:
        # 1. Get Lyrics
        query = f"{job.song_title} {job.artist}"
        raw_lyrics = get_song_lyrics(query)

        if not raw_lyrics:
            job.status = "failed"
            job.message = "Lyrics not found."
            job.save()
            return

        # Analyze Sentiment
        sentiment = analyze_sentiment(raw_lyrics)
        print(f"Detected sentiment: {sentiment}")

        # Check for cancellation
        job.refresh_from_db()
        if job.cancelled:
            job.status = "cancelled"
            job.message = "Job cancelled by user."
            job.save()
            return

        job.progress = 10
        job.message = "Parsing lyrics..."
        job.save()

        is_lrc = "[" in raw_lyrics and "]" in raw_lyrics
        full_lyrics_text = raw_lyrics
        parsed_lyrics = []

        if is_lrc:
            parsed_lyrics = parse_lrc_lyrics(raw_lyrics)
            full_lyrics_text = " ".join([text for _, text in parsed_lyrics])

        # 2. Generate Images
        job.progress = 20
        job.message = "Generating images..."
        job.save()

        segment_tasks_data = []

        # Initialize segments list in DB
        job.segments = []
        job.save()

        # We generate 6 segments (1 minute)
        for i in range(6):
            # Check for cancellation before each segment
            job.refresh_from_db()
            if job.cancelled:
                job.status = "cancelled"
                job.message = "Job cancelled by user."
                job.save()
                return

            start_time = i * 10
            end_time = (i + 1) * 10

            segment_lyrics = ""
            if is_lrc:
                segment_lyrics = get_lyrics_for_interval(
                    parsed_lyrics, start_time, end_time
                )

            if not segment_lyrics:
                segment_lyrics = "(Instrumental / Music)"

            # Add placeholder segment to DB
            current_segments = job.segments
            current_segments.append(
                {
                    "index": i,
                    "lyrics": segment_lyrics,
                    "image": None,
                    "video": None,
                    "status": "generating_image",
                }
            )
            job.segments = current_segments
            job.save()

            image_prompt = (
                f"Song: {query}. "
                f"Mood/Context: {full_lyrics_text[:200]}... "
                f"Current Scene: {segment_lyrics}. "
                f"Style: Hand-drawn cartoon, whimsical, expressive."
            )

            # Save images in a media folder
            output_dir = "media/generated_content"
            os.makedirs(output_dir, exist_ok=True)

            img_filename = os.path.join(output_dir, f"{job.id}_segment_{i}_image.png")
            vid_filename = os.path.join(output_dir, f"{job.id}_segment_{i}_video.mp4")

            generated_img_path = generate_image_from_lyrics(
                image_prompt, output_file=img_filename, sentiment=sentiment
            )

            if generated_img_path:
                # Update segment with image
                current_segments = job.segments
                # Find the segment by index and update it
                for seg in current_segments:
                    if seg["index"] == i:
                        seg["image"] = (
                            "/" + generated_img_path
                        )  # Ensure absolute path for frontend
                        seg["status"] = "image_ready"
                        break
                job.segments = current_segments
                job.save()

                video_prompt = f"Animated cartoon scene of {segment_lyrics}, hand-drawn style, moving camera"
                segment_tasks_data.append(
                    {
                        "image": generated_img_path,
                        "prompt": video_prompt,
                        "output": vid_filename,
                        "index": i,  # Store index to update DB later
                    }
                )

            # Update progress
            job.progress = 20 + int((i + 1) / 6 * 30)  # up to 50%
            job.save()

        # 3. Generate Videos
        job.refresh_from_db()
        if job.cancelled:
            job.status = "cancelled"
            job.message = "Job cancelled by user."
            job.save()
            return

        job.message = "Generating videos (this may take a while)..."

        # Update status of segments to generating_video
        current_segments = job.segments
        for seg in current_segments:
            if seg["status"] == "image_ready":
                seg["status"] = "generating_video"
        job.segments = current_segments
        job.save()

        async def run_async_generation():
            # We need to wrap the generate function to return the index too
            async def generate_with_index(image, prompt, output, index):
                result = await generate_video_segment_independent(image, prompt, output)
                return (result, index)

            tasks = [
                generate_with_index(s["image"], s["prompt"], s["output"], s["index"])
                for s in segment_tasks_data
            ]
            return await asyncio.gather(*tasks)

        results_with_index = asyncio.run(run_async_generation())

        # Process results and update DB
        video_files = []
        current_segments = job.segments

        for result, index in results_with_index:
            if result:
                video_files.append(result)
                # Update segment with video
                for seg in current_segments:
                    if seg["index"] == index:
                        seg["video"] = "/" + result
                        seg["status"] = "video_ready"
                        break

        job.segments = current_segments
        job.save()

        # Check for cancellation after video generation
        job.refresh_from_db()
        if job.cancelled:
            job.status = "cancelled"
            job.message = "Job cancelled by user."
            job.save()
            return

        # Sort files
        video_files.sort(key=lambda x: int(re.search(r"segment_(\d+)_", x).group(1)))

        job.progress = 80
        job.message = "Stitching videos..."
        job.save()

        # 4. Stitch
        if video_files:
            final_output = os.path.join(output_dir, f"{job.id}_final.mp4")
            clips = [VideoFileClip(v) for v in video_files]
            final_clip = concatenate_videoclips(clips)
            final_clip.write_videofile(final_output, fps=24)

            # Ensure the path is absolute or relative to MEDIA_ROOT for Django to serve it
            # The current path is relative to the backend directory, e.g. "media/generated_content/..."
            # When serving via Django static/media, we usually want the URL path component
            # If MEDIA_URL is "/media/", then we want "generated_content/..."

            # Assuming output_dir is "media/generated_content"
            # We want to store "/media/generated_content/..." in the DB if that's how it's served
            # Or just the relative path if using .url on a FileField (but we use CharField)

            # Let's make sure it starts with /media/ if it doesn't already
            if not final_output.startswith("/"):
                db_video_path = "/" + final_output
            else:
                db_video_path = final_output

            job.video_file = db_video_path
            job.status = "completed"
            job.progress = 100
            job.message = "Done!"
            job.save()
        else:
            job.status = "failed"
            job.message = "No video segments were generated."
            job.save()

    except Exception as e:
        job.status = "failed"
        job.message = str(e)
        job.save()
        print(f"Job failed: {e}")


def start_generation_thread(job_id):
    thread = threading.Thread(target=run_video_generation, args=(job_id,))
    thread.start()
