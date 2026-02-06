import subprocess
import asyncio
import os
import re
import time
import requests
import sys
from pathlib import Path
from dotenv import load_dotenv
from .fetch_lyrics import get_song_lyrics
from .lyrics_to_image import generate_image_from_lyrics
from .sentiment_analysis import analyze_sentiment
from odyssey import Odyssey

# Handle both relative and absolute imports
try:
    from .fetch_lyrics import get_song_lyrics
    from .lyrics_to_image import generate_image_from_lyrics
except ImportError:
    # When run directly, use absolute imports
    sys.path.insert(0, os.path.dirname(__file__))
    from fetch_lyrics import get_song_lyrics
    from lyrics_to_image import generate_image_from_lyrics

# Load environment variables
load_dotenv()

# Maximum video duration in seconds
MAX_VIDEO_DURATION = 40  # 1 minute max


def get_video_duration(video_path):
    """
    Gets the actual duration of a video file in seconds using ffprobe.
    Returns None if the duration cannot be determined.
    """
    try:
        command = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1:nokey=1",
            video_path
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode == 0 and result.stdout.strip():
            return float(result.stdout.strip())
    except Exception as e:
        print(f"⚠️ Error getting video duration for {video_path}: {e}")
    return None


def trim_video_to_duration(input_video, output_video, max_duration):
    """
    Trims a video to a maximum duration using FFmpeg.
    Returns True if successful, False otherwise.
    """
    try:
        command = [
            "ffmpeg",
            "-i", input_video,
            "-t", str(max_duration),
            "-c:v", "copy",
            "-c:a", "copy",
            "-y",
            output_video
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print(f"   ✅ Trimmed {os.path.basename(input_video)} to {max_duration}s")
            return True
        else:
            print(f"   ⚠️ Failed to trim video: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ⚠️ Error trimming video: {e}")
        return False

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


def get_intelligent_segments(parsed_lyrics, max_duration=5):
    """
    Creates video segments based on LRC timestamps (max_duration per segment).
    If a gap between lyrics is > max_duration, subdivides it equally.
    Returns list of (segment_index, start_time, end_time, lyrics_text).
    Respects MAX_VIDEO_DURATION limit.
    """
    if not parsed_lyrics:
        # No lyrics - create a single segment
        return [(0, 0, min(10, MAX_VIDEO_DURATION), "(Instrumental / Music)")]
    
    segments = []
    segment_index = 0
    
    # Get total duration from last timestamp + 5 seconds buffer, but cap at MAX_VIDEO_DURATION
    total_duration = min(parsed_lyrics[-1][0] + 5, MAX_VIDEO_DURATION)
    
    current_time = 0
    
    for idx, (timestamp, text) in enumerate(parsed_lyrics):
        # If there's a large gap before this timestamp, fill it
        if timestamp - current_time > max_duration:
            gap_duration = timestamp - current_time
            num_sub_segments = int(gap_duration / max_duration) + (1 if gap_duration % max_duration else 0)
            sub_duration = gap_duration / num_sub_segments
            
            for j in range(num_sub_segments):
                seg_start = current_time + (j * sub_duration)
                seg_end = current_time + ((j + 1) * sub_duration)
                segments.append((segment_index, seg_start, seg_end, "(Instrumental / Music)"))
                segment_index += 1
            
            current_time = timestamp
        
        # Now add segment for the current lyric
        # Look ahead to next timestamp (or use max_duration)
        if idx + 1 < len(parsed_lyrics):
            next_timestamp = parsed_lyrics[idx + 1][0]
            end_time = min(current_time + max_duration, next_timestamp)
        else:
            end_time = current_time + max_duration
        
        # Collect all lyrics until end_time
        segment_lyrics = text
        for future_idx in range(idx + 1, len(parsed_lyrics)):
            if parsed_lyrics[future_idx][0] < end_time:
                segment_lyrics += " " + parsed_lyrics[future_idx][1]
            else:
                break
        
        segments.append((segment_index, current_time, end_time, segment_lyrics.strip()))
        segment_index += 1
        current_time = end_time
        
        # Stop if we've gone past total duration
        if current_time >= total_duration:
            break
    
    return segments


def get_lyrics_for_interval(parsed_lyrics, start_time, end_time):
    """
    Returns text of lyrics that fall within the interval.
    """
    texts = []
    for t, text in parsed_lyrics:
        if start_time <= t < end_time:
            texts.append(text)
    return " ".join(texts).strip()


def create_captions_file(lyrics, captions_path):
    """
    Creates a captions text file for FFmpeg drawtext filter.
    Keeps text simple and raw (no escaping needed).
    """
    # Write raw lyrics as-is
    with open(captions_path, "w", encoding="utf-8") as f:
        f.write(lyrics)
    
    return captions_path


def add_lyrics_to_video(input_video, captions_path, output_video):
    """
    Adds lyrics overlay to a video using FFmpeg drawtext filter.
    Checks if output already exists to avoid re-processing.
    """
    if os.path.exists(output_video):
        print(f"   Captions video {output_video} already exists. Skipping.")
        return output_video
    
    if not os.path.exists(captions_path):
        print(f"   ❌ Captions file not found: {captions_path}")
        return input_video
    
    try:
        print(f"   🎨 Adding lyrics overlay to {os.path.basename(input_video)}...")
        
        # Convert to absolute path for FFmpeg
        abs_captions_path = os.path.abspath(captions_path)
        
        # FFmpeg command with drawtext filter - NO QUOTES around file path for subprocess
        filter_str = f"drawtext=textfile={abs_captions_path}:fontcolor=white:fontsize=36:x=(w-text_w)/2:y=h-100:line_spacing=4:box=1:boxcolor=black@0.5:boxborderw=5"
        
        command = [
            "ffmpeg",
            "-i", input_video,
            "-vf", filter_str,
            "-c:a", "copy",
            "-y",
            output_video
        ]
        
        # Debug: print the command being run
        print(f"   DEBUG: Captions file: {abs_captions_path} (exists: {os.path.exists(abs_captions_path)})")
        print(f"   DEBUG: FFmpeg filter: {filter_str}")
        
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        
        if result.returncode != 0:
            print(f"   ⚠️ FFmpeg error (full stderr):")
            print(result.stderr)
            print(f"   ⚠️ FFmpeg may need a font file. Trying with font fallback...")
            # Return the input video if FFmpeg fails
            return input_video
        
        print(f"   ✅ Added lyrics to {os.path.basename(output_video)}")
        return output_video
        
    except FileNotFoundError:
        print(f"   ⚠️ FFmpeg not found. Returning video without captions.")
        return input_video
    except Exception as e:
        print(f"   ⚠️ Error adding lyrics: {e}. Returning video without captions.")
        return input_video


async def generate_video_segment_independent(
    image_path, prompt, output_filename, duration=5, captions_path=None, semaphore=None
):
    """
    Generates a video segment using a dedicated Odyssey client instance.
    Applies lyrics overlay if captions_path is provided.
    This allows parallel execution if the API supports concurrent connections.
    Uses a semaphore to limit concurrent connections to 3.
    """
    if semaphore is None:
        semaphore = asyncio.Semaphore(3)
    
    # Check if video already exists (final or raw)
    raw_video_path = output_filename.replace(".mp4", "_raw.mp4")
    if os.path.exists(output_filename):
        print(f"🎬 Video {output_filename} already exists. Skipping generation.")
        return output_filename
    if os.path.exists(raw_video_path):
        print(f"🎬 Raw video {raw_video_path} already exists. Skipping Odyssey generation.")
        # If we have the raw video, try to apply captions if not done yet
        if captions_path and os.path.exists(captions_path):
            final_video = add_lyrics_to_video(raw_video_path, captions_path, output_filename)
            if final_video == output_filename and os.path.exists(raw_video_path):
                os.remove(raw_video_path)
            return final_video
        else:
            os.rename(raw_video_path, output_filename)
            return output_filename
    
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
            stream_id = await client.start_stream(prompt, portrait=False, image=image_path)
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
            
            # Save raw video to temporary file
            raw_video_path = output_filename.replace(".mp4", "_raw.mp4")
            with open(raw_video_path, "wb") as f:
                f.write(v_response.content)
            print(f"✅ Saved raw video segment: {raw_video_path}")
            
            # Apply lyrics overlay if captions file provided
            if captions_path and os.path.exists(captions_path):
                final_video = add_lyrics_to_video(raw_video_path, captions_path, output_filename)
                # Clean up raw video after captions applied
                if final_video == output_filename and os.path.exists(raw_video_path):
                    os.remove(raw_video_path)
                return final_video
            else:
                # No captions, return raw video
                os.rename(raw_video_path, output_filename)
                return output_filename

        except Exception as e:
            print(f"❌ Error generating video segment {output_filename}: {e}")
            return None
        finally:
            await client.disconnect()


def validate_and_trim_videos(video_files, max_duration=MAX_VIDEO_DURATION):
    """
    Validates video durations and trims files if necessary to stay within max_duration.
    Returns a list of validated/trimmed video paths.
    """
    print(f"\n📏 Checking video durations (max: {max_duration}s)...")
    
    validated_videos = []
    total_duration = 0
    
    for i, video_path in enumerate(video_files):
        if not os.path.exists(video_path):
            print(f"   ⚠️ Video not found: {video_path}")
            continue
        
        actual_duration = get_video_duration(video_path)
        if actual_duration is None:
            print(f"   ⚠️ Could not determine duration of {os.path.basename(video_path)}")
            validated_videos.append(video_path)
            continue
        
        remaining_budget = max_duration - total_duration
        
        if actual_duration > remaining_budget:
            # Need to trim this video
            trimmed_path = video_path.replace(".mp4", "_trimmed.mp4")
            print(f"   ⚠️ {os.path.basename(video_path)}: {actual_duration:.1f}s exceeds budget of {remaining_budget:.1f}s")
            
            if trim_video_to_duration(video_path, trimmed_path, remaining_budget):
                validated_videos.append(trimmed_path)
                total_duration += remaining_budget
                print(f"   ✅ Total duration so far: {total_duration:.1f}s / {max_duration}s")
                # Stop if we've hit the max
                if total_duration >= max_duration:
                    print(f"   ⚠️ Reached maximum duration limit. Stopping video inclusion.")
                    break
            else:
                # Trimming failed, skip this video
                print(f"   ⚠️ Failed to trim {os.path.basename(video_path)}, skipping.")
        else:
            # Video fits within budget
            validated_videos.append(video_path)
            total_duration += actual_duration
            print(f"   ✅ {os.path.basename(video_path)}: {actual_duration:.1f}s (total: {total_duration:.1f}s / {max_duration}s)")
            
            # Stop if we've hit the max
            if total_duration >= max_duration:
                print(f"   ⚠️ Reached maximum duration limit. Stopping video inclusion.")
                break
    
    print(f"\n📊 Final video duration: {total_duration:.1f}s / {max_duration}s")
    return validated_videos


def stitch_videos_ffmpeg(video_files, output_filename="final_music_video.mp4", list_filename="list.txt"):
    """
    Stitches a list of video files together using FFmpeg.
    Validates durations before stitching to ensure compliance with MAX_VIDEO_DURATION.
    """
    if not video_files:
        print("No video files to stitch.")
        return None

    # Validate and trim videos to stay within max duration
    video_files = validate_and_trim_videos(video_files, MAX_VIDEO_DURATION)
    
    if not video_files:
        print("No valid videos to stitch after validation.")
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

    # Analyze sentiment
    sentiment = analyze_sentiment(raw_lyrics)
    print(f"🧠 Detected Sentiment: {sentiment}")

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

    # Get intelligent segments based on LRC timestamps
    if is_lrc:
        segments = get_intelligent_segments(parsed_lyrics, max_duration=5)
    else:
        # Fallback: create segments that fit within MAX_VIDEO_DURATION
        # Use 10-second segments up to the max duration
        segments = []
        for i in range(MAX_VIDEO_DURATION // 10):
            start = i * 10
            end = (i + 1) * 10
            if start >= MAX_VIDEO_DURATION:
                break
            end = min(end, MAX_VIDEO_DURATION)
            segments.append((i, start, end, "(Instrumental / Music)"))
    
    total_segments = len(segments)
    
    for segment_index, start_time, end_time, segment_lyrics in segments:
        print(f"\n--- Preparing Segment {segment_index + 1}/{total_segments} ({start_time:.1f}s - {end_time:.1f}s) ---")

        if not segment_lyrics or segment_lyrics == "(Instrumental / Music)":
            segment_lyrics = "(Instrumental / Music)"

        print(f"🎵 Lyrics: {segment_lyrics}")

        # Generate Image
        # Prompt combines full context (mood) and specific segment
        lyrics_context = (
            f"Song: {query}. "
            f"Context: {full_lyrics_text[:200]}... "
            f"Current Lyrics: {segment_lyrics}"
        )

        img_filename = os.path.join(images_dir, f"segment_{segment_index}.png")
        vid_filename = os.path.join(song_dir, f"segment_{segment_index}.mp4")
        duration = end_time - start_time

        # Check if image already exists
        if os.path.exists(img_filename):
            print(f"   Image {img_filename} already exists. Using existing image.")
            generated_img_path = img_filename
        else:
            generated_img_path = generate_image_from_lyrics(
                lyrics_context, 
                output_file=img_filename, 
                sentiment=sentiment,
                segment_lyrics=segment_lyrics
            )

        if generated_img_path:
            video_prompt = f"Subtle animation of {segment_lyrics}, {sentiment.lower()} cartoon style, minimal motion, atmospheric, landscape orientation"
            
            # Create captions file for this segment
            captions_dir = os.path.join(song_dir, "captions")
            os.makedirs(captions_dir, exist_ok=True)
            captions_filename = os.path.join(captions_dir, f"segment_{segment_index}_captions.txt")
            captions_path = create_captions_file(segment_lyrics, captions_filename)
            
            segment_tasks_data.append(
                {
                    "image": generated_img_path,
                    "prompt": video_prompt,
                    "output": vid_filename,
                    "captions": captions_path,
                    "lyrics": segment_lyrics,
                    "duration": duration,
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
                s["image"], 
                s["prompt"], 
                s["output"],
                duration=s.get("duration", 5),  # Use actual segment duration
                captions_path=s.get("captions"),
                semaphore=semaphore
            )
            for s in segment_tasks_data
        ]
        results = await asyncio.gather(*tasks)
        # Filter out None results
        video_files = [r for r in results if r]
        # Sort by segment index to ensure correct order
        video_files.sort(key=lambda x: int(re.search(r"segment_(\d+)(?:_raw)?\.mp4", x).group(1)))

    # 5. Stitch Videos
    if video_files:
        output_filename = os.path.join(song_dir, f"{song_name}_final.mp4")
        list_filename = os.path.join(song_dir, "list.txt")
        stitch_videos_ffmpeg(video_files, output_filename, list_filename)
    else:
        print("\n⚠️ No videos were generated, so stitching was skipped.")


if __name__ == "__main__":
    asyncio.run(main())
