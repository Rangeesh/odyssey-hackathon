# LYRA - LYRics Animated

LYRA is an AI-powered music video generator that creates animated visuals synchronized with song lyrics.

## Features

- **Lyrics Fetching:** Automatically fetches synced lyrics (LRC) from LRCLIB.
- **AI Image Generation:** Generates artistic, hand-drawn style illustrations for each segment using Google Gemini.
- **AI Video Animation:** Animates these illustrations into video clips using Odyssey.
- **Video Stitching:** Combines all segments into a final music video.
- **Web Interface:** Pure Django-based web interface - no Node.js required!
- **Job Management:** Cancel pending or in-progress video generations with one click.
- **Real-time Updates:** Auto-refreshing job status every 3 seconds.
- **Dark Mode:** Beautiful dark theme with smooth transitions and persistent preference.
- **Smart Search:** Real-time search suggestions with synced lyrics indicators.
- **Visual Progress:** See images and lyrics segments appear in real-time as they are generated.

## Quick Setup (Conda)

1. Ensure you have Conda installed.
2. Create the environment:

   ```bash
   conda env create -f environment.yml
   ```

   Or run:

   ```bash
   bash scripts/create_conda_env.sh
   ```

3. Activate the environment:

   ```bash
   conda activate odyssey-hackathon
   ```

4. **Important for macOS users:** If you encounter Pillow/libtiff errors, run:

   ```bash
   brew install libtiff
   ln -sf /opt/homebrew/Cellar/libtiff/4.7.1/lib/libtiff.6.dylib /opt/homebrew/lib/libtiff.5.dylib
   ```

## Running the Application

### Start the Django Server

Navigate to the backend directory and run:

```bash
cd backend
./start_server.sh
```

Or manually with:

```bash
cd backend
export DYLD_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_LIBRARY_PATH
python manage.py runserver 8000
```

### Access the Application

Open your browser and go to: **<http://localhost:8000>**

That's it! The application now uses Django templates - no Node.js required.

## Features

- **Search for Songs** - Enter song name and artist to find lyrics
- **Generate Videos** - Click "Generate Video" to create AI-powered music videos
- **Monitor Progress** - Watch real-time progress updates (auto-refreshes every 3 seconds)
- **View Videos** - Play and download completed videos directly in the browser

## API Endpoints (Optional)

The REST API is still available for programmatic access:

- `GET /api/jobs/` - List all video generation jobs
- `POST /api/jobs/` - Create a new video generation job
- `GET /api/jobs/search/?q=<query>` - Search for song lyrics
- `GET /admin/` - Django admin interface

## Quick Setup (venv)

1. Install Python 3.12+
2. Create and activate a virtual environment:

 ```bash
 python3.14 -m venv .venv
 source .venv/bin/activate
 ```

1. Install dependencies:

 ```bash
 pip install -e .
 ```

1. Or run:

 ```bash
 bash scripts/create_venv.sh
 ```

Project dependencies and Python version are managed in `pyproject.toml`.

The Odyssey Python SDK will be installed automatically from GitHub:

- <https://github.com/odysseyml/odyssey-python>
If you want to install it manually:

 ```bash

The Google Generative AI SDK (`google-genai`) will also be installed automatically.
To install it manually:
 ```bash
 pip install -q -U google-genai

The Pillow library (`PIL`) will also be installed automatically.
To install it manually:
 ```bash
 pip install Pillow
 ```

 ```
 pip install git+https://github.com/odysseyml/odyssey-python.git
 ```

Note: Make sure to update the GOOGLE_API_KEY `export GOOGLE_API_KEY=<API_KEY>`

`test_nano_banana.py` -> Works with Google API Key.
