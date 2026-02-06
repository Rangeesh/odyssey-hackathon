import asyncio
import os
import requests
from dotenv import load_dotenv
from odyssey import (
    Odyssey,
    OdysseyAuthError,
    OdysseyConnectionError,
    OdysseyStreamError,
)

load_dotenv()


async def generate_single_video(
    image_path, output_filename="single_segment_video.mp4", duration=10
):
    print(f"🎬 Starting video generation from: {image_path}")

    api_key = os.environ.get("ODYSSEY_API_KEY")
    if not api_key:
        print("Error: ODYSSEY_API_KEY not found.")
        return

    client = Odyssey(api_key=api_key)

    try:
        print("Connecting to Odyssey...")
        await client.connect(on_video_frame=lambda f: None)
        print("Connected.")

        # Prompt based on the image context (dark cartoon style)
        prompt = "Cinematic shot, atmospheric lighting, subtle motion, hand-drawn cartoon style on dark background"

        print(f"   Starting stream with image...")
        stream_id = await client.start_stream(prompt, image_path=image_path)
        print(f"   Stream started: {stream_id}")

        print(f"   Recording for {duration} seconds...")
        await asyncio.sleep(duration)

        await client.end_stream()
        print("   Stream ended.")

        print("   Retrieving recording...")
        recording = await client.get_recording(stream_id)
        video_url = recording.video_url

        if not video_url:
            print("❌ No video URL found.")
            return

        print(f"   Downloading video from: {video_url}")
        v_response = requests.get(video_url)
        with open(output_filename, "wb") as f:
            f.write(v_response.content)
        print(f"✅ Saved video to: {output_filename}")

    except OdysseyAuthError:
        print("❌ Authentication failed. Check your API key.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    # Use the specific image provided
    img_path = "segment_5_image.png"

    if not os.path.exists(img_path):
        print(f"Error: Image file '{img_path}' not found.")
    else:
        asyncio.run(generate_single_video(img_path))
