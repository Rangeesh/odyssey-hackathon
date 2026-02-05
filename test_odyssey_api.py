import asyncio
from odyssey import Odyssey, OdysseyAuthError, OdysseyConnectionError, OdysseyStreamError

async def main():
    print("Creating client")
    client = Odyssey(api_key="API_KEY")
    print("Client created")
    stream_id = None

    try:
        print("Connecting")
        await client.connect(on_video_frame=lambda f: None)
        print("Connected")

        stream_id = await client.start_stream("A serene mountain landscape", portrait=False)
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
