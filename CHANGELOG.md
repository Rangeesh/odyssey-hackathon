# LYRA Changelog

## [Latest] - 2026-02-06

### Added - Visual Progress Tracking

#### New Features
- ✅ **Segment Grid** - Job cards now display a grid of 6 segments
- ✅ **Real-time Images** - Images appear in the grid as soon as they are generated
- ✅ **Lyrics Display** - Each image is paired with its corresponding lyrics line
- ✅ **Video Previews** - Video clips replace images once animation is complete
- ✅ **Two-step Workflow** - Search & Preview Lyrics -> Generate Video
- ✅ **Data Persistence** - Segment data stored in database for reliable updates

#### Technical Implementation
- Added `segments` JSONField to `VideoJob` model
- Updated `tasks.py` to populate segment data incrementally
- Modified `index.html` to support the search-then-generate flow
- Updated `job_list_partial.html` to render the segment grid
- Added CSS for responsive grid layout

### Added - Search Suggestions

#### New Features
- ✅ **Real-time Suggestions** - Dropdown appears as you type song names
- ✅ **Rich Song Data** - Displays title, artist, album, and duration
- ✅ **Synced Badges** - Clearly indicates which songs have synced lyrics
- ✅ **Smart Debouncing** - Optimized API calls for smooth typing experience
- ✅ **Proxy Endpoint** - Secure backend proxy to avoid CORS issues
- ✅ **Theme Support** - Fully styled for both Light and Dark modes

#### Technical Implementation
- Added `/search-suggestions/` endpoint in Django views
- Implemented JavaScript debouncing (300ms)
- Created CSS styles for dropdown and suggestion items
- Updated `generate_video` view to handle formatted input

### Added - Dark Mode

#### New Features
- ✅ **Theme Toggle Button** - Easy-to-use button in header to switch themes
- ✅ **Light & Dark Themes** - Beautiful color schemes for both modes
- ✅ **Smooth Transitions** - All colors animate smoothly when switching
- ✅ **Persistent Preference** - Theme choice saved in localStorage
- ✅ **Animated Toggle** - Button rotates 360° with icon change (🌙 ↔ ☀️)
- ✅ **Comprehensive Theming** - Every element styled for both modes

#### Technical Implementation
- CSS custom properties (variables) for easy theme management
- JavaScript localStorage for persistence
- `data-theme` attribute on document root
- 0.3s transitions for smooth color changes
- Responsive design maintained in both themes

#### Color Schemes
**Light Mode:**
- Purple gradient background (#667eea to #764ba2)
- White cards with dark text
- High contrast for readability

**Dark Mode:**
- Dark blue gradient background (#1a1a2e to #16213e)
- Deep blue cards with light text
- Reduced eye strain for nighttime use

### Added - Job Cancellation Feature

#### New Features
- ✅ **Cancel Button** - Added "❌ Cancel" button for pending and processing jobs
- ✅ **Cancellation Confirmation** - Popup dialog to prevent accidental cancellations
- ✅ **Graceful Shutdown** - Jobs stop at safe checkpoints without corrupting data
- ✅ **Status Updates** - New "Cancelled" status with visual indicators
- ✅ **Real-time Feedback** - Job list refreshes immediately after cancellation

#### Technical Changes
- Added `cancelled` boolean field to `VideoJob` model
- Added "cancelled" to status choices
- Created `/cancel/<job_id>/` endpoint for cancellation
- Added cancellation checks at 5 key points in generation process
- Updated templates to show cancel button conditionally
- Added JavaScript `cancelJob()` function with CSRF token handling
- Added CSS styling for cancelled jobs (grey, reduced opacity)

#### Database Migration
- Created migration `0002_videojob_cancelled_alter_videojob_status.py`
- Applied migration successfully

### Improved - User Experience

#### Better Error Handling
- ✅ **Pre-validation** - Lyrics are checked BEFORE creating jobs
- ✅ **No Failed Jobs** - Jobs only start if lyrics exist
- ✅ **Clear Messages** - Specific error messages for different failure cases
- ✅ **Success Feedback** - Confirmation when video generation starts

#### Simplified Workflow
- ✅ **Single Form** - One input field, one button
- ✅ **Automatic Validation** - No need to search separately
- ✅ **Helpful Instructions** - Info box explains the process
- ✅ **Better Layout** - Cleaner, more intuitive interface

### Removed - Node.js Frontend

#### Migration to Django Templates
- ❌ Removed entire `frontend/` directory (React + Vite)
- ❌ Removed Node.js dependency
- ❌ Removed npm/package.json
- ❌ Removed separate frontend server

#### New Pure Django Interface
- ✅ Django templates in `backend/video_generator/templates/`
- ✅ Static files (CSS/JS) in `backend/video_generator/static/`
- ✅ Single server on port 8000
- ✅ No build process required

### Fixed

#### Pillow/libtiff Issues
- Fixed `Library not loaded: @rpath/libtiff.5.dylib` error
- Created symlink for libtiff compatibility
- Updated `start_server.sh` with correct environment variables
- Documented macOS-specific fixes

#### Port Configuration
- Fixed port mismatch between frontend and backend
- Standardized on port 8000 for all services
- Updated CORS settings

## Documentation Updates

### New Files
- `RUNNING.md` - Quick start guide
- `USAGE_GUIDE.md` - Detailed usage instructions
- `CANCEL_FEATURE.md` - Cancellation feature documentation
- `MIGRATION_COMPLETE.md` - React to Django migration notes
- `CHANGELOG.md` - This file

### Updated Files
- `README.md` - Updated with new features and simplified setup
- `.gitignore` - Added appropriate Python/Django ignores

## Breaking Changes

### For Users
- **URL Changed**: Frontend now at `http://localhost:8000` (was `http://localhost:5173`)
- **No Node.js**: No need to run `npm install` or `npm run dev`
- **Single Command**: Just `./start_server.sh` to start everything

### For Developers
- **No React**: Frontend is now Django templates
- **No API Separation**: Web interface uses Django views, not REST API
- **Different Structure**: Templates in `video_generator/templates/`

## Migration Guide

### From Old Version (React Frontend)

1. **Stop all servers**:
   ```bash
   # Kill any running processes
   lsof -ti:8000,5173,5176 | xargs kill -9
   ```

2. **Pull latest changes**:
   ```bash
   git pull origin main
   ```

3. **Run migrations**:
   ```bash
   cd backend
   python manage.py migrate
   ```

4. **Start new server**:
   ```bash
   ./start_server.sh
   ```

5. **Access at new URL**:
   ```
   http://localhost:8000
   ```

## Known Issues

### Limitations
- Cannot cancel jobs that are in the middle of an API call
- Partial files from cancelled jobs remain in media folder
- Video generation cancellation may take 10-30 seconds to complete
- Cannot pause/resume jobs (only cancel)

### Workarounds
- For faster cancellation, cancel jobs early (before video generation starts)
- Manually clean up media files from cancelled jobs if needed
- Wait for current segment to finish before cancellation takes effect

## Upcoming Features

### Planned
- Bulk cancel multiple jobs
- Auto-cleanup of cancelled job files
- Pause/resume functionality
- Job priority management
- Email notifications
- Progress estimation (time remaining)

### Under Consideration
- Multiple video quality options
- Custom video length selection
- Batch video generation from playlist
- Social media export formats
- Video editing capabilities

## Performance Improvements

### Current
- Auto-refresh every 3 seconds (configurable)
- Async video generation (6 segments in parallel)
- Efficient database queries with `order_by` and `[:10]` limiting

### Future
- WebSocket for real-time updates (no polling)
- Caching for frequently accessed data
- Background task queue (Celery)
- CDN for static files
- Video compression optimization

## Security Updates

### Current
- CSRF protection on all POST requests
- UUID-based job IDs (not sequential)
- CORS restricted to localhost
- No authentication required (local development)

### Future
- User authentication system
- API key management
- Rate limiting
- Job ownership validation
- Secure file uploads

---

For more information, see:
- [README.md](README.md) - Main documentation
- [RUNNING.md](RUNNING.md) - How to run the application
- [USAGE_GUIDE.md](USAGE_GUIDE.md) - Detailed usage instructions
- [CANCEL_FEATURE.md](CANCEL_FEATURE.md) - Cancellation feature details
