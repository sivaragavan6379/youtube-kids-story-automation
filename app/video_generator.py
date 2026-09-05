import os
import time
import subprocess
import requests


PIXAZO_API_KEY = os.getenv("PIXAZO_API_KEY")

GENERATE_URL = "https://gateway.pixazo.ai/ltx-video/v1/image-to-video"
STATUS_URL = "https://gateway.pixazo.ai/v2/requests/status"


def animate_image(image_url, motion_prompt, output_file):
    """
    Convert a still image into a real AI-generated animated video
    using Pixazo LTX Video.
    """

    if not PIXAZO_API_KEY:
        raise ValueError("PIXAZO_API_KEY is not set.")

    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": PIXAZO_API_KEY
    }

    data = {
        "prompt": motion_prompt,
        "image_url": image_url,
        "strength": 1.0,

        # Vertical YouTube Shorts format
        "width": 704,
        "height": 1280,

        # About 5 seconds at 24 FPS
        "num_frames": 121,
        "frame_rate": 24,

        "steps": 8,
        "cfg": 3.0
    }

    print("Starting AI animation...")
    print("Motion prompt:", motion_prompt)

    response = requests.post(
        GENERATE_URL,
        headers=headers,
        json=data,
        timeout=120
    )

    response.raise_for_status()

    result = response.json()

    print("Pixazo response:", result)

    request_id = result.get("request_id")

    if not request_id:
        raise RuntimeError(
            f"Pixazo did not return a request_id: {result}"
        )

    print("Animation request created:", request_id)

    # Wait for AI video generation
    while True:

        time.sleep(5)

        status_response = requests.get(
            f"{STATUS_URL}/{request_id}",
            headers={
                "Ocp-Apim-Subscription-Key": PIXAZO_API_KEY
            },
            timeout=60
        )

        status_response.raise_for_status()

        status_data = status_response.json()

        status = status_data.get("status")

        print("Animation status:", status)

        if status == "COMPLETED":

            output = status_data.get("output", {})
            media_urls = output.get("media_url", [])

            if not media_urls:
                raise RuntimeError(
                    f"Video completed but no media URL was returned: "
                    f"{status_data}"
                )

            video_url = media_urls[0]

            print("AI animation completed!")
            print("Downloading video...")

            video_response = requests.get(
                video_url,
                timeout=300
            )

            video_response.raise_for_status()

            with open(output_file, "wb") as video_file:
                video_file.write(video_response.content)

            print("Video saved:", output_file)

            return output_file

        elif status in ["FAILED", "ERROR"]:

            error = status_data.get(
                "error",
                "Unknown error"
            )

            raise RuntimeError(
                f"Pixazo AI video generation failed: {error}"
            )


def combine_videos(video_files, output_file):
    """
    Combine multiple AI-generated vertical videos
    into one YouTube Short.
    """

    if not video_files:
        raise ValueError("No video files provided.")

    print("\n" + "=" * 60)
    print("🎬 COMBINING AI ANIMATED SCENES")
    print("=" * 60)

    # Check every input video
    for video in video_files:

        if not os.path.exists(video):
            raise FileNotFoundError(
                f"Video not found: {video}"
            )

        print(f"🎞️ Adding: {video}")

    # Create FFmpeg concat file
    concat_file = "video_list.txt"

    with open(concat_file, "w", encoding="utf-8") as file:

        for video in video_files:
            absolute_path = os.path.abspath(video)

            # FFmpeg concat format
            file.write(
                f"file '{absolute_path}'\n"
            )

    print("\n🔗 Joining videos...")

    command = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        concat_file,
        "-c",
        "copy",
        output_file
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Remove temporary concat file
    if os.path.exists(concat_file):
        os.remove(concat_file)

    if result.returncode != 0:

        print("❌ FFmpeg error:")
        print(result.stderr)

        raise RuntimeError(
            "Failed to combine videos."
        )

    if not os.path.exists(output_file):
        raise RuntimeError(
            "Combined video was not created."
        )

    file_size = os.path.getsize(output_file)

    print("✅ VIDEOS COMBINED SUCCESSFULLY")
    print(f"🎬 Short video: {output_file}")
    print(f"📦 File size: {file_size} bytes")

    print("=" * 60)

    return output_file
