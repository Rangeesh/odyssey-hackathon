import asyncio
import os
from dotenv import load_dotenv
from odyssey import (
    Odyssey,
    OdysseyAuthError,
    OdysseyConnectionError,
    OdysseyStreamError,
)

load_dotenv()


async def main():
    print("Creating client")
    api_key = os.environ.get("ODYSSEY_API_KEY")
    if not api_key:
        print("Error: ODYSSEY_API_KEY not found in environment variables.")
        return

    client = Odyssey(api_key=api_key)
    print("Client created")
    stream_id = None

    try:
        print("Connecting")
        await client.connect(on_video_frame=lambda f: None)
        print("Connected")

        stream_id = await client.start_stream(
            "A serene mountain landscape", portrait=False
        )
        print("Stream ID:", stream_id)
        print("StreamStarted")
        await client.interact("Add a waterfall on the left")
        print("Client interaction")
        await asyncio.sleep(5)
        await client.end_stream()
        print("Stream ended")

    except OdysseyAuthError:
        print("Bad API key")
        return
    except OdysseyConnectionError as e:
        print(f"Connect failed: {e}")
        return
    except OdysseyStreamError as e:
        print(f"Stream op failed: {e}")
        return
    finally:
        await client.disconnect()

    # Recording lookup can happen after disconnect
    if stream_id:
        print("Getting recording")
        recording = await client.get_recording(stream_id)
        print("Video URL:", recording.video_url)
        print("Preview URL:", recording.preview_url)
        print("Thumbnail URL:", recording.thumbnail_url)
        print("Events URL:", recording.events_url)


if __name__ == "__main__":
    asyncio.run(main())
