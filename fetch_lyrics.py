import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def get_song_lyrics(query):
    """
    Fetches lyrics from LRCLIB.net based on a search query (Song Title + Artist).
    Returns the plain lyrics if found, or None.
    """
    base_url = "https://lrclib.net/api/search"
    params = {"q": query}

    print(f"🔍 Searching LRCLIB for: '{query}'...")

    try:
        # Configure retries
        session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))

        # LRCLIB encourages a user agent
        headers = {
            "User-Agent": "OdysseyHackathonBot/1.0 (https://github.com/odysseyml/odyssey-hackathon)"
        }

        # Increased timeout and verify=True (default)
        response = session.get(base_url, params=params, headers=headers, timeout=15)
        response.raise_for_status()

        results = response.json()

        if not results:
            print("❌ No results found.")
            return None

        # Get the best match (usually the first one)
        track = results[0]
        artist = track.get("artistName", "Unknown Artist")
        title = track.get("trackName", "Unknown Track")
        album = track.get("albumName", "Unknown Album")

        print(f"✅ Found: '{title}' by '{artist}' (Album: {album})")

        # Prefer syncedLyrics, fall back to plainLyrics
        lyrics = track.get("syncedLyrics")
        if not lyrics:
            print("⚠️ No synced lyrics found, checking for plain lyrics...")
            lyrics = track.get("plainLyrics")

        return lyrics

    except Exception as e:
        print(f"❌ Error fetching lyrics: {e}")
        return None


if __name__ == "__main__":
    search_query = input("Enter song name and artist: ")
    if search_query:
        lyrics = get_song_lyrics(search_query)
        if lyrics:
            print("\n--- LYRICS PREVIEW ---\n")
            print(lyrics[:500])  # Print first 500 chars
            if len(lyrics) > 500:
                print("\n... (truncated)")
