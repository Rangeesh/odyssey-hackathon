import os
import time
from dotenv import load_dotenv
from google import genai
from PIL import Image

# Load environment variables
load_dotenv()


def generate_image_from_lyrics(lyrics: str, output_file: str = "lyrics_image.png"):
    """
    Generates an image based on the provided song lyrics using Google's Gemini 2.5 Flash Image model.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment variables.")
        return

    client = genai.Client(api_key=api_key)

    # Construct a prompt that encourages artistic interpretation
    prompt = (
        f"Create a highly detailed, artistic, and mood-evoking digital painting "
        f"based on the following song lyrics. Capture the emotion and imagery: \n\n"
        f"'{lyrics}'"
    )

    print(f'🎨 Generating image for lyrics:\n"{lyrics}"\n')
    print("Waiting for API response (this might take a moment)...")

    max_retries = 3
    retry_delay = 20  # seconds

    for attempt in range(max_retries):
        try:
            # Using gemini-2.5-flash-image (Nano Banana)
            response = client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=[prompt],
            )

            image_saved = False
            if response.parts:
                for part in response.parts:
                    if part.inline_data is not None:
                        image = part.as_image()
                        image.save(output_file)
                        print(f"\n✅ Success! Image saved to: {output_file}")
                        image_saved = True
                        break

            if not image_saved:
                print("\n⚠️ The API returned a response, but no image data was found.")
                if response.text:
                    print(f"Response text: {response.text}")

            # If successful, break the loop
            break

        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                print(
                    f"\n⏳ Rate limit hit. Waiting {retry_delay} seconds before retry {attempt + 2}/{max_retries}..."
                )
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"\n❌ Error generating image: {e}")
                if "429" in str(e):
                    print(
                        "\n💡 Tip: You hit a rate limit (Quota Exceeded). Try again later."
                    )
                break


if __name__ == "__main__":
    import sys

    # You can change these lyrics to whatever you want!
    if len(sys.argv) > 1:
        lyrics_input = " ".join(sys.argv[1:])
    else:
        try:
            lyrics_input = input(
                "Enter song lyrics (or press Enter for a default): "
            ).strip()
        except EOFError:
            lyrics_input = ""

    if not lyrics_input:
        lyrics_input = "Lucy in the sky with diamonds, picture yourself in a boat on a river, with tangerine trees and marmalade skies"

    generate_image_from_lyrics(lyrics_input)
