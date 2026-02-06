import subprocess
import asyncio
import os
import re
import time
import requests
from dotenv import load_dotenv
from .fetch_lyrics import get_song_lyrics
from .lyrics_to_image import generate_image_from_lyrics
from odyssey import Odyssey

# Load environment variables
load_dotenv()


def parse_lrc_lyrics(lrc_text):
    """
    Parses LRC lyrics into a list of (timestamp_seconds, text).
    """
    lines = []
    # Regex for [mm:ss.xx] or [mm:ss]
    pattern = re.compile(r"\[(\d+):(\d+(?:\.\d+)?)\](.*)")

    for line in lrc_text.split("\n"):
        match = pattern.match(line.strip())
        if match:
            minutes = int(match.group(1))
            seconds = float(match.group(2))
            text = match.group(3).strip()
            total_seconds = minutes * 60 + seconds
            lines.append((total_seconds, text))

    return sorted(lines, key=lambda x: x[0])


def get_lyrics_for_interval(parsed_lyrics, start_time, end_time):
    """
    Returns text of lyrics that fall within the interval.
    """
    texts = []
    for t, text in parsed_lyrics:
        if start_time <= t < end_time:
            texts.append(text)
    return " ".join(texts).strip()


async def generate_video_segment_independent(
    image_path, prompt, output_filename, duration=10, semaphore=None
):
    """
    Generates a video segment using a dedicated Odyssey client instance.
    This allows parallel execution if the API supports concurrent connections.
    Uses a semaphore to limit concurrent connections to 3.
    """
    if semaphore is None:
        semaphore = asyncio.Semaphore(3)

    async with semaphore:
        print(f"🎬 Starting video generation for: {output_filename}")

        odyssey_key = os.environ.get("ODYSSEY_API_KEY")
        if not odyssey_key:
            print("Error: ODYSSEY_API_KEY not found.")
            return None

        client = Odyssey(api_key=odyssey_key)

        try:
            await client.connect(on_video_frame=lambda f: None)

            # Start stream with image (using 'image' parameter, not deprecated 'image_path')
            stream_id = await client.start_stream(prompt, image=image_path)
            print(f"   Stream started ({output_filename}): {stream_id}")

            # Wait for the desired duration
            await asyncio.sleep(duration)

            # End stream
            await client.end_stream()
            print(f"   Stream ended ({output_filename}).")

            # Wait for recording to be ready and retry if not found
            recording = None
            max_retries = 10  # Increased retries
            for attempt in range(max_retries):
                try:
                    await asyncio.sleep(3)  # Wait 3 seconds before each attempt
                    recording = await client.get_recording(stream_id)
                    if recording and recording.video_url:
                        break
                except Exception as e:
                    if attempt == max_retries - 1:
                        print(
                            f"   Failed to get recording after {max_retries} attempts: {e}"
                        )
                        # Don't raise, just let it fail gracefully
                    print(
                        f"   Retry {attempt + 1}/{max_retries} for {output_filename}: {e}"
                    )

            if not recording:
                print(f"❌ Recording not found for {output_filename} after retries.")
                return None

            video_url = recording.video_url

            if not video_url:
                print(f"❌ No video URL found for {output_filename}.")
                return None

            print(f"   Downloading video from: {video_url}")
            v_response = requests.get(video_url)
            with open(output_filename, "wb") as f:
                f.write(v_response.content)
            print(f"✅ Saved video segment: {output_filename}")
            return output_filename

        except Exception as e:
            print(f"❌ Error generating video segment {output_filename}: {e}")
            return None
        finally:
            await client.disconnect()


def stitch_videos_ffmpeg(
    video_files, output_filename="final_music_video.mp4", list_filename="list.txt"
):
    """
    Stitches a list of video files together using FFmpeg.
    """
    if not video_files:
        print("No video files to stitch.")
        return None

    print("\n🧵 Stitching videos together with FFmpeg...")

    try:
        # Get the song directory from the output filename
        song_dir = os.path.dirname(output_filename)

        # Create the list file for FFmpeg with relative paths
        with open(list_filename, "w") as f:
            for v in video_files:
                f.write(f"file '{os.path.basename(v)}'\n")

        # Run FFmpeg command from within the song directory
        command = [
            "ffmpeg",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            os.path.basename(list_filename),
            "-c",
            "copy",
            os.path.basename(output_filename),
            "-y",  # Overwrite output file if it exists
        ]

        result = subprocess.run(
            command, check=True, capture_output=True, text=True, cwd=song_dir
        )
        print(result.stdout)
        print(result.stderr)

        print(f"\n🎉 Final video saved: {output_filename}")
        return output_filename

    except FileNotFoundError:
        print("Error: ffmpeg is not installed or not in your PATH.")
        print("Please install ffmpeg to use this feature.")
    except subprocess.CalledProcessError as e:
        print(f"Error during ffmpeg execution: {e}")
        print(f"FFmpeg stdout: {e.stdout}")
        print(f"FFmpeg stderr: {e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Clean up the list file
        if os.path.exists(list_filename):
            os.remove(list_filename)
    return None


async def main():
    # 1. Get Song Info
    import sys

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        try:
            query = input("Enter song name and artist: ")
        except EOFError:
            query = ""

    if not query:
        query = "Bohemian Rhapsody Queen"

    # Create a directory for the song
    song_name = query.replace(" ", "_")
    song_dir = song_name
    images_dir = os.path.join(song_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    raw_lyrics = get_song_lyrics(query)
    if not raw_lyrics:
        print("Could not find lyrics. Exiting.")
        return

    # Save lyrics to a file
    lyrics_filename = os.path.join(song_dir, "lyrics.txt")
    with open(lyrics_filename, "w") as f:
        f.write(raw_lyrics)

    # Check if we got synced lyrics (LRC)
    is_lrc = "[" in raw_lyrics and "]" in raw_lyrics and ":" in raw_lyrics

    full_lyrics_text = raw_lyrics
    parsed_lyrics = []

    if is_lrc:
        parsed_lyrics = parse_lrc_lyrics(raw_lyrics)
        # Extract just text for full context
        full_lyrics_text = " ".join([text for _, text in parsed_lyrics])
        print(f"✅ Parsed {len(parsed_lyrics)} synced lyric lines.")
    else:
        print("⚠️ Warning: Lyrics are not time-synced. Will split text evenly.")

    # List to store task data for parallel execution
    segment_tasks_data = []

    # 3. Generate Images (Sequential to avoid Gemini rate limits)
    print("\n📸 Generating images for all segments first...")

    for i in range(6):
        start_time = i * 10
        end_time = (i + 1) * 10

        print(f"\n--- Preparing Segment {i + 1}/6 ({start_time}s - {end_time}s) ---")

        # Get lyrics for this segment
        segment_lyrics = ""
        if is_lrc:
            segment_lyrics = get_lyrics_for_interval(
                parsed_lyrics, start_time, end_time
            )

        if not segment_lyrics:
            segment_lyrics = "(Instrumental / Music)"

        print(f"🎵 Lyrics: {segment_lyrics}")

        # Generate Image
        # Prompt combines full context (mood) and specific segment
        lyrics_context = (
            f"Song: {query}. "
            f"Context: {full_lyrics_text[:200]}... "
            f"Current Lyrics: {segment_lyrics}"
        )

        img_filename = os.path.join(images_dir, f"segment_{i}.png")
        vid_filename = os.path.join(song_dir, f"segment_{i}.mp4")

        # Check if image already exists
        if os.path.exists(img_filename):
            print(f"   Image {img_filename} already exists. Using existing image.")
            generated_img_path = img_filename
        else:
            generated_img_path = generate_image_from_lyrics(
                lyrics_context, output_file=img_filename
            )

        if generated_img_path:
            video_prompt = f"Subtle animation of {segment_lyrics}, dark cartoon style, minimal motion, atmospheric"
            segment_tasks_data.append(
                {
                    "image": generated_img_path,
                    "prompt": video_prompt,
                    "output": vid_filename,
                }
            )
        else:
            print("Skipping video generation for this segment due to image failure.")

    # 4. Generate Videos (Parallel with concurrency limit)
    video_files = []
    if segment_tasks_data:
        print(
            f"\n🚀 Starting parallel video generation for {len(segment_tasks_data)} segments..."
        )
        # Create a semaphore to limit to 3 concurrent connections
        semaphore = asyncio.Semaphore(3)
        tasks = [
            generate_video_segment_independent(
                s["image"], s["prompt"], s["output"], semaphore=semaphore
            )
            for s in segment_tasks_data
        ]
        results = await asyncio.gather(*tasks)
        # Filter out None results
        video_files = [r for r in results if r]
        # Sort by segment index to ensure correct order
        video_files.sort(
            key=lambda x: int(re.search(r"segment_(\d+)\.mp4", x).group(1))
        )

    # 5. Stitch Videos
    if MOVIEPY_AVAILABLE and video_files:
        print("\n🧵 Stitching videos together...")
        try:
            clips = [VideoFileClip(v) for v in video_files]
            final_clip = concatenate_videoclips(clips)
            final_clip.write_videofile("final_music_video.mp4", fps=24)
            print("\n🎉 Final video saved: final_music_video.mp4")
        except Exception as e:
            print(f"Error stitching videos: {e}")
    elif video_files:
        print("\n⚠️ No videos were generated, so stitching was skipped.")
        for v in video_files:
            print(f" - {v}")


if __name__ == "__main__":
    asyncio.run(main())
