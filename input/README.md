# Input videos

Upload the MP4 you want to publish to this folder as `episode.mp4`.

Expected path:
`input/episode.mp4`

The GitHub Actions workflow uploads that file to YouTube. Keep the workflow's
privacy setting as `unlisted` for the first test.

Important:
- Do not commit OAuth tokens, API keys, or client-secret JSON files.
- A short test clip is not a full episode.
- This step publishes an existing MP4; video generation is a separate stage.
