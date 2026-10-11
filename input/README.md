# Private video handoff

The publishing workflow downloads the MP4 from your private Google Drive and uploads it to YouTube.

1. Upload the MP4 to Google Drive.
2. Keep it private; the Google account used for OAuth must own it or have access to it.
3. Copy the file ID from its Drive URL. Example: in
   `https://drive.google.com/file/d/FILE_ID/view`, the file ID is `FILE_ID`.
4. Run **Actions → Publish Episode Video to YouTube** and paste that ID.

Do not upload private videos, OAuth tokens, or client-secret files to this public GitHub repository.
The workflow defaults to **unlisted**. An 8-second test clip is not a full episode.
