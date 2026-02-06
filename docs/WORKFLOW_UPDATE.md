# Workflow Update: Search -> Preview -> Generate

## Overview

The application workflow has been updated to provide more control and visibility over the video generation process.

## New Workflow

1.  **Search Phase**:
    -   User enters a song name/artist in the search bar.
    -   Suggestions appear as they type.
    -   User clicks "🔍 Find Lyrics" (or selects a suggestion).

2.  **Preview Phase**:
    -   The system fetches and displays the lyrics found.
    -   User can review the lyrics to ensure they match the intended song.
    -   A "🎬 Generate Video" button appears below the lyrics.

3.  **Generation Phase**:
    -   User clicks "Generate Video".
    -   A new job is created.
    -   **Real-time Updates**:
        -   The job card now displays a grid of 6 segments.
        -   As images are generated for each segment, they appear in the grid.
        -   Corresponding lyrics for each segment are shown below the image.
        -   Once video clips are generated, they replace the static images in the grid (looping preview).
    -   **Final Result**:
        -   Once all segments are stitched, the final full-length video player appears.

## Technical Changes

-   **Database**: Added `segments` JSONField to `VideoJob` model to store structured data for each segment (lyrics, image path, video path, status).
-   **Backend Logic**: Updated `tasks.py` to populate and update the `segments` field in real-time during the generation process.
-   **Frontend**:
    -   Updated `index.html` to support the two-step search/generate flow.
    -   Updated `job_list_partial.html` to render the segment grid using the new data structure.
    -   Added CSS for the segment grid layout.

## Benefits

-   **Verification**: Users can verify lyrics before spending time/credits on generation.
-   **Engagement**: Users can see the creative process unfold (images appearing one by one) rather than just a progress bar.
-   **Transparency**: It's clear which lyrics correspond to which visual segment.

---

**Updated**: February 6, 2026
**Status**: Production Ready ✅
