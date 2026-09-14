import os
import subprocess


def create_final_short(video_files, audio_files, output_path="final_short.mp4"):
    """
    Combine animated scene videos and Tamil audio into one vertical YouTube Short.
    """

    if not video_files:
        raise RuntimeError("No video files were provided.")

    if len(video_files) != len(audio_files):
        raise RuntimeError(
            "The number of videos and audio files must be equal."
        )

    print("\n🎬 Preparing final YouTube Short...")

    scene_files = []

    for index, (video_path, audio_path) in enumerate(
        zip(video_files, audio_files),
        start=1
    ):
        if not os.path.exists(video_path):
            raise RuntimeError(f"Missing video: {video_path}")

        if not os.path.exists(audio_path):
            raise RuntimeError(f"Missing audio: {audio_path}")

        scene_output = f"scene_{index:02d}_with_audio.mp4"

        print(f"🔊 Combining audio with Scene {index}...")

        command = [
            "ffmpeg",
            "-y",
            "-i",
            video_path,
            "-i",
            audio_path,
            "-filter_complex",
            (
                "[0:v]scale=720:1280:force_original_aspect_ratio=increase,"
                "crop=720:1280,setsar=1[v]"
            ),
            "-map",
            "[v]",
            "-map",
            "1:a",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-shortest",
            scene_output,
        ]

        subprocess.run(command, check=True)

        if not os.path.exists(scene_output):
            raise RuntimeError(
                f"Failed to create scene video: {scene_output}"
            )

        scene_files.append(scene_output)

    concat_file = "concat_list.txt"

    with open(concat_file, "w", encoding="utf-8") as file:
        for scene_file in scene_files:
            absolute_path = os.path.abspath(scene_file)
            safe_path = absolute_path.replace("'", "'\\''")
            file.write(f"file '{safe_path}'\n")

    print("🔗 Joining all scenes...")

    join_command = [
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
        output_path,
    ]

    subprocess.run(join_command, check=True)

    if not os.path.exists(output_path):
        raise RuntimeError(
            f"Final Short was not created: {output_path}"
        )

    final_size = os.path.getsize(output_path)

    print("✅ FINAL SHORT CREATED")
    print(f"🎬 Output: {output_path}")
    print(f"📦 File size: {final_size} bytes")

    return output_path
