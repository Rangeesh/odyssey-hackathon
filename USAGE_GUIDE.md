# LYRA Usage Guide

## How to Use the Application

### 1. Access the Application

Open your browser and go to: **<http://localhost:8000>**

### 2. Generate a Music Video

1. Start typing a song name in the input field
   - Example: `Bohemian`
   - Example: `Shape of`

2. **Select from Suggestions** or click **🔍 Find Lyrics**

3. **Review Lyrics**
   - Read through the lyrics to ensure they are correct
   - This prevents wasting credits on the wrong song

4. Click the **"🎬 Generate Video"** button

5. **Watch the Magic**
   - The job card will show a grid of 6 scenes
   - As AI generates images, they will appear in the grid
   - You can see exactly which lyrics correspond to each image
   - Once complete, the final video will be available to play and download

### 3. Monitor Progress

The "Recent Video Jobs" section shows all your video generation jobs with:

- **Song Title & Artist**
- **Status Badge** (Pending, Processing, Completed, Failed)
- **Progress Bar** (0-100%)
- **Status Message** (what's currently happening)
- **Auto-refresh** every 3 seconds

### 4. Cancel a Job (Optional)

If you need to stop a video generation:

- Find the job in the "Recent Video Jobs" section
- Jobs with **"Pending"** or **"Processing"** status can be cancelled
- Click the **"❌ Cancel"** button next to the status badge
- Confirm the cancellation
- The job will stop and be marked as "Cancelled"

**Note:** Cancelled jobs will stop at the next checkpoint. Jobs in the middle of video generation may take a moment to cancel.

### 5. Watch Your Video

Once a job is completed:

- A video player will appear in the job card
- Click play to watch your AI-generated music video
- Click the download button to save it locally

## Common Issues

### "Could not find lyrics"

This means the song isn't in the LRCLIB database. Try:

- ✅ Check spelling of song name and artist
- ✅ Try a more popular song
- ✅ Use the exact song title (not shortened versions)
- ✅ Include the artist name

**Songs that typically work well:**

- Popular hits from major artists
- Songs with official lyrics
- English language songs (better coverage)

### Video Generation Takes Too Long

Video generation is resource-intensive:

- Expect 5-10 minutes for a 1-minute video
- The process involves:
  - Fetching lyrics (5 seconds)
  - Generating 6 AI images (1-2 minutes)
  - Generating 6 AI video clips (3-5 minutes)
  - Stitching videos together (30 seconds)

### Job Shows "Failed"

Common reasons:

1. **Lyrics not found** - Song doesn't exist in database
2. **API key missing** - Check your `.env` file has `GOOGLE_API_KEY` and `ODYSSEY_API_KEY`
3. **API quota exceeded** - You've hit your daily API limits
4. **Network error** - Check your internet connection

## Tips for Best Results

### Song Selection

- ✅ Choose songs with clear, synced lyrics
- ✅ Popular songs have better lyrics coverage
- ✅ Include artist name for better matching

### Multiple Videos

- You can generate multiple videos simultaneously
- Each job runs independently
- Monitor all jobs in the "Recent Jobs" section

### Video Quality

- Videos are generated at 24 FPS
- Each segment is 10 seconds long
- Total video length: ~1 minute (6 segments)

## Example Songs to Try

Here are some songs that typically work well:

1. **Bohemian Rhapsody Queen**
2. **Imagine John Lennon**
3. **Hotel California Eagles**
4. **Billie Jean Michael Jackson**
5. **Shape of You Ed Sheeran**
6. **Blinding Lights The Weeknd**
7. **Someone Like You Adele**
8. **Wonderwall Oasis**

## API Endpoints (Advanced)

If you want to use the REST API directly:

```bash
# Search for lyrics
curl "http://localhost:8000/api/jobs/search/?q=bohemian+rhapsody+queen"

# Create a video job
curl -X POST http://localhost:8000/api/jobs/ \
  -H "Content-Type: application/json" \
  -d '{"song_title": "Bohemian Rhapsody", "artist": "Queen"}'

# List all jobs
curl http://localhost:8000/api/jobs/
```

## Need Help?

1. Check the terminal where the server is running for error messages
2. Verify your `.env` file has the required API keys
3. Make sure you're using the conda environment: `conda activate odyssey-hackathon`
4. Try restarting the server: `cd backend && ./start_server.sh`
