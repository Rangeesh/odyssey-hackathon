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
        f"Create a single cohesive digital illustration in a dark, stylized cartoon aesthetic with clean outlines and controlled detail.\n\n"
        f"The illustration represents the emotional core and imagery of the following song lyrics:\n"
        f"“{lyrics}”\n\n"
        f"Depict one primary scene that symbolically captures the overall mood of the lyrics rather than illustrating each line literally. The theme should remain consistent across the entire image, with a unified visual metaphor that feels calm, slightly melancholic, and introspective.\n\n"
        f"Subject:\n"
        f"One central character or focal element that embodies the emotional tone of the song. The character is clearly readable, simply posed, and not performing exaggerated actions. Facial expression and body language convey emotion subtly.\n\n"
        f"Environment:\n"
        f"A minimal, atmospheric setting that supports the theme of the lyrics. Background elements are sparse and intentional, with no unnecessary objects. The environment feels like a single moment frozen in time.\n\n"
        f"Style:\n"
        f"Dark cartoon illustration style.\n"
        f"Soft shading, limited color palette.\n"
        f"Muted tones with one or two accent colors.\n"
        f"No photorealism.\n"
        f"No excessive textures.\n"
        f"No complex patterns.\n\n"
        f"Composition:\n"
        f"Centered or slightly off-center composition.\n"
        f"Clear foreground subject.\n"
        f"Background remains simple and uncluttered.\n"
        f"Strong silhouette readability.\n\n"
        f"Lighting:\n"
        f"Low-key, moody lighting.\n"
        f"Soft directional light.\n"
        f"Gentle contrast, no harsh highlights.\n\n"
        f"Motion readiness (important):\n"
        f"The scene should feel stable and grounded, as if it could subtly come alive.\n"
        f"No extreme poses, no chaotic motion.\n"
        f"Designed to support gentle animation and continuity.\n\n"
        f"Constraints:\n"
        f"No text.\n"
        f"No lyric words shown visually.\n"
        f"No multiple scenes.\n"
        f"No crowded elements.\n"
        f"No dramatic action.\n"
        f"No surreal distortions.\n"
        f"Aspect Ratio: 16:9 landscape.\n\n"
        f"Overall tone:\n"
        f"Cohesive, restrained, emotionally focused.\n"
        f"Designed as a strong starting frame for an interactive or evolving Odyssey simulation."
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
                        return output_file

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
