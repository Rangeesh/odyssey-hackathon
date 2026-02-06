# Cancel Job Feature

## Overview

You can now cancel video generation jobs that are pending or in progress. This is useful if:
- You accidentally started the wrong song
- You want to stop a long-running job
- You need to free up resources for other jobs

## How to Cancel a Job

### From the Web Interface

1. Go to **http://localhost:8000**
2. Find the job you want to cancel in the "Recent Video Jobs" section
3. Look for jobs with status **"Pending"** or **"Processing"**
4. Click the **"❌ Cancel"** button next to the status badge
5. Confirm the cancellation in the popup dialog
6. The job will be marked as "Cancelled" and stop processing

### Job Statuses

- **Pending** - Job is waiting to start (can be cancelled)
- **Processing** - Job is currently running (can be cancelled)
- **Completed** - Job finished successfully (cannot be cancelled)
- **Failed** - Job encountered an error (cannot be cancelled)
- **Cancelled** - Job was stopped by user

## What Happens When You Cancel

1. **Immediate Effect**: The `cancelled` flag is set to `true` in the database
2. **Background Check**: The generation thread checks this flag at multiple points:
   - Before starting processing
   - After fetching lyrics
   - Before each image segment generation
   - After video generation completes
3. **Clean Stop**: When cancellation is detected, the job:
   - Stops processing immediately
   - Sets status to "cancelled"
   - Updates message to "Job cancelled by user"
   - Saves the current state

## Limitations

- **Cannot cancel completed or failed jobs** - These are already finished
- **Video generation may complete** - If cancellation happens during the final video stitching, the videos may still complete
- **Partial files remain** - Generated images/videos up to the cancellation point remain in the media folder
- **API calls already made** - Any API calls (Gemini, Odyssey) that were already sent cannot be cancelled

## Technical Details

### Database Changes

Added two new fields to `VideoJob` model:
- `cancelled` (BooleanField) - Flag to signal cancellation
- `status` - Added "cancelled" as a valid status choice

### API Endpoint

**POST** `/cancel/<job_id>/`

Request:
```bash
curl -X POST http://localhost:8000/cancel/<job-uuid>/ \
  -H "X-CSRFToken: <token>"
```

Response (Success):
```json
{
  "success": true,
  "message": "Job 'Song Title' has been cancelled."
}
```

Response (Error):
```json
{
  "success": false,
  "message": "Cannot cancel job with status: completed"
}
```

### Cancellation Check Points

The generation process checks for cancellation at these points:

1. **Before starting** (line 19 in tasks.py)
2. **After fetching lyrics** (line 37)
3. **Before each image segment** (line 57, in loop)
4. **After all images generated** (line 101)
5. **After video generation** (line 118)

This ensures the job can be cancelled at any stage without leaving it in an inconsistent state.

## Best Practices

1. **Cancel early** - If you realize you made a mistake, cancel immediately to save API credits
2. **Wait for confirmation** - The UI will show "Cancelled" status when the job stops
3. **Check progress** - Jobs at higher progress (>50%) may take a moment to cancel as they finish the current segment
4. **Clean up** - Cancelled jobs remain in the database for reference but don't consume resources

## Example Usage

### Cancel a pending job
```javascript
// From browser console
cancelJob('550e8400-e29b-41d4-a716-446655440000');
```

### Cancel via API
```bash
curl -X POST http://localhost:8000/cancel/550e8400-e29b-41d4-a716-446655440000/ \
  -H "X-CSRFToken: your-csrf-token"
```

## UI Features

- **Cancel button** appears only for pending/processing jobs
- **Confirmation dialog** prevents accidental cancellations
- **Immediate feedback** - Job list refreshes automatically after cancellation
- **Visual indicator** - Cancelled jobs appear with grey styling and reduced opacity
- **Status badge** - Shows "CANCELLED" in grey

## Future Enhancements

Potential improvements:
- Bulk cancel multiple jobs
- Auto-cleanup of partial files from cancelled jobs
- Pause/resume functionality
- Cancel with reason/notes
- Email notification when job is cancelled
