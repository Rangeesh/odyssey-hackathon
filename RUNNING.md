# LYRA - Running Instructions

## Quick Start

1. **Activate your conda environment:**

   ```bash
   conda activate odyssey-hackathon
   ```

2. **Start the Django server:**

   ```bash
   cd backend
   ./start_server.sh
   ```

3. **Open your browser:**
   Go to **<http://localhost:8000>**

That's it! No Node.js required.

## How It Works

1. **Search for a song** - Enter song name and artist in the search box
2. **View lyrics** - The app will fetch synced lyrics from LRCLIB
3. **Generate video** - Click "Generate Video" to start the AI video generation process
4. **Monitor progress** - Watch the job status in the "Recent Jobs" section (auto-refreshes every 3 seconds)
5. **View video** - Once complete, the video will be playable directly in the browser

## Stopping the Server

Press `CTRL+C` in the terminal window where the server is running.

## Restarting the Application

```bash
cd backend
./start_server.sh
```

## Troubleshooting

### Port Already in Use

If you get a "port already in use" error:

```bash
lsof -ti:8000 | xargs kill -9
```

### Pillow/libtiff Error

If you see `Library not loaded: @rpath/libtiff.5.dylib`:

```bash
brew install libtiff
ln -sf /opt/homebrew/Cellar/libtiff/4.7.1/lib/libtiff.6.dylib /opt/homebrew/lib/libtiff.5.dylib
```

Then make sure to use the `start_server.sh` script which sets the correct environment variables.

### Static Files Not Loading

If CSS/JS files are not loading, run:

```bash
cd backend
python manage.py collectstatic --noinput
```

## Environment Variables

Make sure you have a `.env` file in the root directory with:

```
GOOGLE_API_KEY=your_google_api_key_here
ODYSSEY_API_KEY=your_odyssey_api_key_here
```

## Database

The application uses SQLite by default. The database file is located at:
`backend/db.sqlite3`

To reset the database:

```bash
cd backend
rm db.sqlite3
python manage.py migrate
```

## Technology Stack

- **Backend:** Django 6.0 (Python)
- **Frontend:** Django Templates (HTML/CSS/JavaScript)
- **Database:** SQLite
- **AI:** Google Gemini (image generation), Odyssey (video animation)
- **Lyrics:** LRCLIB API

No Node.js, React, or npm required!
