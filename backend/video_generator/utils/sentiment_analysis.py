import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()


def analyze_sentiment(lyrics: str) -> str:
    """
    Analyzes the sentiment of the provided lyrics using Google's Gemini model.
    Returns a string describing the sentiment/mood.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found.")
        return "Neutral"

    client = genai.Client(api_key=api_key)

    prompt = (
        f"Analyze the sentiment and mood of the following song lyrics. "
        f"Provide a concise description of the emotional tone (e.g., 'Upbeat and Joyful', 'Dark and Melancholic', 'Energetic', 'Romantic', 'Angry'). "
        f"Return ONLY the sentiment description, nothing else.\n\n"
        f"Lyrics:\n{lyrics[:2000]}"  # Truncate if too long to save tokens/avoid errors
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt],
        )
        if response.text:
            return response.text.strip()
        return "Neutral"
    except Exception as e:
        print(f"Error analyzing sentiment: {e}")
        return "Neutral"
