from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from google import genai
from google.genai import types


BASE_DIR = Path(__file__).resolve().parent.parent
SHOTS_DIR = BASE_DIR / "output" / "shots"
VIDEO_DIR = BASE_DIR / "output" / "videos"
INDEX_FILE = VIDEO_DIR / "generation_index.json"

MODEL = os.getenv("VEO_MODEL", "veo-3.1-generate-preview")
MAX_SHOTS = int(os.getenv("VEO_MAX_SHOTS", "1"))
START_SHOT = int(os.getenv("VEO_START_SHOT", "1"))
POLL_SECONDS = int(os.getenv("VEO_POLL_SECONDS", "10"))
MAX_WAIT_SECONDS = int(os.getenv("VEO_MAX_WAIT_SECONDS", "600"))

ALLOWED_DURATIONS = {4, 6, 8}
ALLOWED_ASPECT_RATIOS = {"9:16", "16:9"}
ALLOWED_RESOLUTIONS = {"720p", "1080p", "4k"}


def get_api_keys() -> list[str]:
    keys = [
        os.getenv("GEMINI_API_KEY", "").strip(),
        os.getenv("GEMINI_API_KEY_2", "").strip(),
    ]
    keys = [k for k in keys if k]
    if not keys:
        raise RuntimeError("No Gemini API key found.")
    return list(dict.fromkeys(keys))


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def discover_shots() -> list[tuple[int, int, dict[str, Any], Path]]:
    if not SHOTS_DIR.exists():
        raise FileNotFoundError(f"Shot directory not found: {SHOTS_DIR}")

    results = []

    for path in sorted(SHOTS_DIR.glob("scene_*_shots.json")):
        data = load_json(path)
        scene_number = int(data.get("scene_number", 0))
        shots = data.get("shots", [])

        if scene_number <= 0:
            raise ValueError(f"Invalid scene_number in {path}")
        if not isinstance(shots, list):
            raise ValueError(f"'shots' must be a list in {path}")

        for shot in shots:
            if not isinstance(shot, dict):
                raise ValueError(f"Invalid shot entry in {path}")

            shot_number = int(shot.get("shot_number", 0))
            if shot_number <= 0:
                raise ValueError(f"Invalid shot_number in {path}")

            results.append((scene_number, shot_number, shot, path))

    results.sort(key=lambda x: (x[0], x[1]))
    return results


def validate_shot(
    scene_number: int,
    shot_number: int,
    shot: dict[str, Any],
) -> tuple[str, int, str, str]:
    prompt = str(shot.get("veo_prompt", "")).strip()
    if not prompt:
        raise ValueError(
            f"Scene {scene_number} shot {shot_number}: missing veo_prompt"
        )

    generation = shot.get("video_generation", {})
    if not isinstance(generation, dict):
        generation = {}

    duration = int(
        generation.get(
            "duration_seconds",
            shot.get("duration_seconds", 8),
        )
    )
    aspect_ratio = str(generation.get("aspect_ratio", "9:16"))
    resolution = str(generation.get("resolution", "720p"))

    if duration not in ALLOWED_DURATIONS:
        raise ValueError(
            f"Scene {scene_number} shot {shot_number}: "
            f"unsupported duration {duration}"
        )

    if aspect_ratio not in ALLOWED_ASPECT_RATIOS:
        raise ValueError(
            f"Scene {scene_number} shot {shot_number}: "
            f"unsupported aspect ratio {aspect_ratio}"
        )

    if resolution not in ALLOWED_RESOLUTIONS:
        raise ValueError(
            f"Scene {scene_number} shot {shot_number}: "
            f"unsupported resolution {resolution}"
        )

    return prompt, duration, aspect_ratio, resolution


def output_path(scene_number: int, shot_number: int) -> Path:
    directory = VIDEO_DIR / f"scene_{scene_number:02d}"
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"shot_{shot_number:02d}.mp4"


def generate_one(
    api_key: str,
    scene_number: int,
    shot_number: int,
    shot: dict[str, Any],
) -> dict[str, Any]:
    prompt, duration, aspect_ratio, resolution = validate_shot(
        scene_number,
        shot_number,
        shot,
    )

    destination = output_path(scene_number, shot_number)

    if destination.exists() and destination.stat().st_size > 0:
        print(f"SKIP existing: {destination}")
        return {
            "scene_number": scene_number,
            "shot_number": shot_number,
            "status": "skipped_existing",
            "file": str(destination.relative_to(BASE_DIR)),
        }

    print(f"Generating scene {scene_number} shot {shot_number}")
    print(f"Model: {MODEL}")
    print(f"Duration: {duration}s")
    print(f"Aspect ratio: {aspect_ratio}")
    print(f"Resolution: {resolution}")

    client = genai.Client(api_key=api_key)

    config = types.GenerateVideosConfig(
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        duration_seconds=str(duration),
    )

    operation = client.models.generate_videos(
        model=MODEL,
        prompt=prompt,
        config=config,
    )

    started = time.time()

    while not operation.done:
        elapsed = int(time.time() - started)
        if elapsed >= MAX_WAIT_SECONDS:
            raise TimeoutError(
                f"Veo generation timed out after {MAX_WAIT_SECONDS}s"
            )

        print(f"Waiting for Veo... {elapsed}s")
        time.sleep(POLL_SECONDS)
        operation = client.operations.get(operation)

    if getattr(operation, "error", None):
        raise RuntimeError(f"Veo operation failed: {operation.error}")

    response = operation.response
    generated_videos = getattr(response, "generated_videos", None)

    if not generated_videos:
        raise RuntimeError("Veo returned no generated videos.")

    generated_video = generated_videos[0]

    client.files.download(
        file=generated_video.video,
        destination=str(destination),
    )

    if not destination.exists() or destination.stat().st_size == 0:
        raise RuntimeError("Downloaded MP4 is missing or empty.")

    elapsed = int(time.time() - started)

    print(f"✅ Video saved: {destination}")
    print(f"✅ Size: {destination.stat().st_size} bytes")
    print(f"✅ Generation time: {elapsed}s")

    return {
        "scene_number": scene_number,
        "shot_number": shot_number,
        "status": "generated",
        "file": str(destination.relative_to(BASE_DIR)),
        "model": MODEL,
        "duration_seconds": duration,
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
        "bytes": destination.stat().st_size,
        "elapsed_seconds": elapsed,
    }


def save_index(results: list[dict[str, Any]]) -> None:
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)

    payload = {
        "model": MODEL,
        "results": results,
    }

    with INDEX_FILE.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def main() -> None:
    keys = get_api_keys()
    shots = discover_shots()

    if not shots:
        raise RuntimeError("No shot files found.")

    selected = [
        item for index, item in enumerate(shots, start=1)
        if index >= START_SHOT
    ]

    if MAX_SHOTS > 0:
        selected = selected[:MAX_SHOTS]

    print(f"Total available shots: {len(shots)}")
    print(f"Shots selected: {len(selected)}")
    print(f"Gemini keys available: {len(keys)}")

    results = []

    for scene_number, shot_number, shot, source_file in selected:
        last_error = None

        for key_index, key in enumerate(keys, start=1):
            try:
                result = generate_one(
                    key,
                    scene_number,
                    shot_number,
                    shot,
                )
                result["source"] = str(source_file.relative_to(BASE_DIR))
                result["key_index"] = key_index
                results.append(result)
                last_error = None
                break
            except Exception as error:
                last_error = error
                print(
                    f"Key {key_index} failed: "
                    f"{type(error).__name__}: {error}"
                )
                if key_index < len(keys):
                    time.sleep(5)

        if last_error is not None:
            raise last_error

        save_index(results)

    save_index(results)

    generated = sum(
        1 for item in results if item["status"] == "generated"
    )
    skipped = sum(
        1 for item in results if item["status"] == "skipped_existing"
    )

    print("=" * 60)
    print("VEO TEST GENERATION COMPLETE")
    print(f"Generated: {generated}")
    print(f"Skipped: {skipped}")
    print(f"Index: {INDEX_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
