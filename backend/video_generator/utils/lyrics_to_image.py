import os
import time
from dotenv import load_dotenv
from google import genai
from PIL import Image as PILImage  # Rename to avoid collision with genai.Image

# Load environment variables
load_dotenv()

# Target aspect ratio for videos: 16:9 landscape
TARGET_WIDTH = 1280
TARGET_HEIGHT = 720


def resize_to_landscape(image_path: str, width: int = TARGET_WIDTH, height: int = TARGET_HEIGHT):
    """
    Resizes an image to landscape format (16:9) with padding if needed.
    Preserves the original image content and adds padding to match target dimensions.
    """
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            print(f"⚠️ Image file not found: {image_path}")
            return image_path
        
        # Open image with PIL
        img = PILImage.open(image_path)
        
        # Verify it's a PIL Image
        if not hasattr(img, 'size'):
            print(f"⚠️ Warning: Image object doesn't have .size attribute. Attempting conversion...")
            # Try to convert to RGB if needed
            img = img.convert('RGB')
        
        original_width, original_height = img.size
        print(f"   Opening image: {original_width}x{original_height}")
        
        # Calculate aspect ratios
        target_aspect = width / height
        original_aspect = original_width / original_height
        
        # Resize to fit within target dimensions while preserving aspect ratio
        if original_aspect > target_aspect:
            # Image is wider than target - fit to width
            new_width = width
            new_height = int(width / original_aspect)
        else:
            # Image is taller than target - fit to height
            new_height = height
            new_width = int(height * original_aspect)
        
        print(f"   Resizing to: {new_width}x{new_height}")
        img_resized = img.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
        
        # Create a new image with target dimensions and dark background
        background = PILImage.new('RGB', (width, height), color=(20, 20, 30))
        
        # Paste resized image centered on background
        x_offset = (width - new_width) // 2
        y_offset = (height - new_height) // 2
        background.paste(img_resized, (x_offset, y_offset))
        
        # Save over the original
        background.save(image_path, 'PNG')
        print(f"✅ Resized to landscape {width}x{height}: {image_path}")
        return image_path
        
    except Exception as e:
        print(f"⚠️ Error resizing image: {e}")
        import traceback
        traceback.print_exc()
        return image_path


def generate_image_from_lyrics(lyrics: str, output_file: str = "lyrics_image.png", segment_lyrics: str = None):
    """
    Generates an image based on the provided song lyrics using Google's Gemini 2.5 Flash Image model.
    
    Args:
        lyrics: Full song lyrics for emotional context
        output_file: Output filename for the generated image
        segment_lyrics: Specific segment lyrics to display in the overlay (if different from full lyrics)
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment variables.")
        return

    client = genai.Client(api_key=api_key)

    # Use segment_lyrics for overlay if provided, otherwise use full lyrics
    overlay_lyrics = segment_lyrics if segment_lyrics else lyrics

    # Construct a prompt that encourages artistic interpretation
    prompt = (
        f"Create a single cohesive digital illustration in a dark, stylized cartoon aesthetic with clean outlines and controlled detail.\n\n"
        f"The illustration represents the emotional core and imagery of the following song lyrics:\n"
        f"“{lyrics}”\n\n"
        f"Depict one primary scene that symbolically captures the overall mood of the lyrics rather than illustrating each line literally. "
        f"The theme should remain consistent across the entire image, with a unified visual metaphor that feels calm, slightly melancholic, and introspective.\n\n"

        f"Subject:\n"
        f"One central character or focal element that embodies the emotional tone of the song. "
        f"The character is clearly readable, simply posed, and not performing exaggerated actions. "
        f"Facial expression and body language convey emotion subtly.\n\n"

        f"Environment:\n"
        f"A minimal, atmospheric setting that supports the theme of the lyrics. "
        f"Background elements are sparse and intentional, with no unnecessary objects. "
        f"The environment feels like a single moment frozen in time.\n\n"

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

        f"Lyrics overlay (STRICT – ONLY these exact lyrics, no modifications):\n"
        f"Display these exact lyrics ONLY in the lower center of the frame:\n"
        f"\"{overlay_lyrics}\"\n\n"
        f"CRITICAL REQUIREMENTS:\n"
        f"- Display ONLY the lyrics specified above, word-for-word, no changes.\n"
        f"- Place the text ONLY in the lower center of the frame.\n"
        f"- The text is horizontally centered and occupies the bottom third of the image.\n"
        f"- A slight, tasteful overlap with the main character is allowed, but the character remains clearly readable.\n"
        f"- Use a single block of text with clean line breaks.\n"
        f"- No scattered words.\n"
        f"- No diagonal placement.\n"
        f"- No wrapping around objects.\n"
        f"- No text near the top or sides of the frame.\n"
        f"- No paraphrasing or summarizing the lyrics.\n"
        f"- No adding or removing any words.\n"
        f"- No substitutions or alternatives.\n\n"
        f"Typography:\n"
        f"Typography is minimal and calm, similar to modern lyric videos.\n"
        f"Text color is subtle and readable, harmonizing with the image palette.\n"
        f"No outlines.\n"
        f"No shadows.\n"
        f"No text boxes.\n"
        f"No borders.\n"
        f"No UI elements.\n\n"

        f"Motion readiness (important):\n"
        f"The scene should feel stable and grounded, as if it could subtly come alive.\n"
        f"Text placement should support gentle fade-in, fade-out, or slight vertical drift animation.\n"
        f"No extreme poses.\n"
        f"No chaotic motion.\n\n"

        f"Constraints:\n"
        f"No captions or explanatory text beyond the exact lyrics provided.\n"
        f"No multiple scenes.\n"
        f"No crowded elements.\n"
        f"No dramatic action.\n"
        f"No surreal distortions.\n"
        f"Aspect Ratio: 16:9 landscape.\n\n"

        f"Overall tone:\n"
        f"Cohesive, restrained, emotionally focused.\n"
        f"Designed as a strong starting frame for an interactive or evolving Odyssey simulation.\n\n"
        f"VALIDATION:\n"
        f"✓ The exact lyrics \"{overlay_lyrics}\" appear in the lower center of the image.\n"
        f"✓ No other text appears in the image.\n"
        f"✓ No words are missing, added, or changed.\n"
        f"✗ If the lyrics appear anywhere outside the lower center of the image, the result is INCORRECT.\n"
        f"✗ If different text appears in the image, the result is INCORRECT."
    )

    print(f'🎨 Generating image for lyrics:\n"{lyrics}"\n')
    if segment_lyrics and segment_lyrics != lyrics:
        print(f'📍 Overlay text:\n"{segment_lyrics}"\n')
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
                        genai_image = part.as_image()  # This is genai.Image, not PIL.Image
                        genai_image.save(output_file)
                        print(f"\n✅ Image saved to: {output_file}")
                        
                        # Now resize to landscape format using PIL
                        resize_to_landscape(output_file)
                        print(f"   Final dimensions: {TARGET_WIDTH}x{TARGET_HEIGHT}")
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
