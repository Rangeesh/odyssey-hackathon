# Search Suggestions Feature

## Overview

LYRA now includes intelligent search suggestions powered by the LRCLIB API. As you type a song name, the application automatically suggests matching tracks with artist and album information.

## Features

### 1. Real-time Suggestions
- **Instant Feedback**: Suggestions appear as you type (debounced by 300ms)
- **Rich Data**: Shows Song Title, Artist, Album, and Duration
- **Synced Indicator**: Badges show which songs have synced lyrics available
- **Smart Filtering**: Only shows relevant results from the LRCLIB database

### 2. User Interface
- **Dropdown Menu**: Clean, styled dropdown appearing below the search box
- **Keyboard Navigation**: (Planned) Navigate suggestions with arrow keys
- **Click Selection**: Clicking a suggestion automatically fills the search box
- **Theme Support**: Fully styled for both Light and Dark modes

### 3. Technical Implementation
- **Proxy API**: Backend endpoint `/search-suggestions/` proxies requests to LRCLIB to avoid CORS issues
- **Debouncing**: JavaScript prevents excessive API calls while typing
- **Error Handling**: Graceful degradation if the API is unavailable

## How to Use

1. Start typing a song name in the search box (e.g., "Bohemian")
2. Wait a moment for suggestions to appear
3. Click on the correct song from the list
4. The search box is automatically filled with "Title Artist"
5. Click "Generate Video" to start

## API Endpoint

**GET** `/search-suggestions/?q=query`

Response:
```json
[
  {
    "id": 12345,
    "title": "Bohemian Rhapsody",
    "artist": "Queen",
    "album": "A Night at the Opera",
    "duration": 354,
    "synced": true
  },
  ...
]
```

## Benefits

- **Accuracy**: Ensures you find the exact version of the song you want
- **Efficiency**: Reduces typing and prevents spelling errors
- **Discovery**: Helps find songs even if you only know part of the name
- **Confidence**: "Synced" badge confirms high-quality lyrics are available

---

**Added**: February 6, 2026
**Status**: Production Ready ✅
