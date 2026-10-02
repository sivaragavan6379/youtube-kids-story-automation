from __future__ import annotations

import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
MEMORY_FILE = BASE_DIR / "universe" / "universe_memory.json"
SCENES_DIR = BASE_DIR / "output" / "scenes"
SHOTS_DIR = BASE_DIR / "output" / "shots"
OUTPUT_FILE = BASE_DIR / "output" / "kathaikalam_pipeline.json"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    memory = load_json(MEMORY_FILE)

    character_registry = memory.get("characters", {})
    characters = {}
    scenes = []

    for scene_path in sorted(SCENES_DIR.glob("scene_*.json")):
        scene = load_json(scene_path)
        scene_number = scene.get("scene", {}).get("scene_number")

        # Scene Director already carries the canonical character references
        # needed by Kathaikalam Director.
        for ref in scene.get("character_references", []):
            cid = str(ref.get("canonical_id", "")).strip()
            name = str(ref.get("name", "")).strip()
            if not cid or not name:
                continue

            mem = character_registry.get(cid, {})
            characters[cid] = {
                "name": name,
                "canonical_id": cid,
                "appearance": ref.get("appearance") or mem.get("appearance", ""),
                "voice_style": ref.get("voice_style") or mem.get("voice_style", ""),
                "design_version": ref.get("design_version", mem.get("design_version", 1)),
                "identity_locked": True,
                "status": mem.get("status", "active"),
                "appearance_type": mem.get("appearance_type", "returning"),
                "first_arc": mem.get("first_arc", mem.get("last_arc", "")),
                "last_arc": mem.get("last_arc", ""),
                "reference_image": mem.get("reference_image", ""),
                "reference_asset_id": mem.get("reference_asset_id", ""),
            }

        shot_path = SHOTS_DIR / f"scene_{int(scene_number):02d}_shots.json"
        shots = load_json(shot_path) if shot_path.exists() else {"shots": []}

        scenes.append({
            "scene_number": scene_number,
            "scene_title": scene.get("scene", {}).get("title", ""),
            "target_duration_seconds": scene.get("scene", {}).get("duration_seconds", 0),
            "generated_duration_seconds": shots.get("generated_duration_seconds", 0),
            "location": scene.get("scene", {}).get("location", ""),
            "story_action": scene.get("scene", {}).get("story_action", ""),
            "character_ids": [
                str(c.get("canonical_id"))
                for c in scene.get("character_references", [])
                if c.get("canonical_id")
            ],
            "shots": shots.get("shots", []),
        })

    episode = {}
    for path in [
        BASE_DIR / "output" / "generated_episode_01.json",
    ]:
        if path.exists():
            episode = load_json(path)
            break

    payload = {
        "schema_version": "1.0",
        "pipeline": "Kathaikalam Director",
        "source": "youtube-kids-story-automation",
        "universe": memory.get("universe", {}),
        "episode": {
            "episode_number": episode.get("episode_number", 1),
            "title": episode.get("title", ""),
            "language": episode.get("language", "Tamil"),
            "arc": memory.get("universe", {}).get("current_arc", ""),
        },
        "character_registry": list(characters.values()),
        "scenes": scenes,
        "continuity": {
            "canonical_identity_lock": True,
            "auto_attach_characters": True,
            "allow_new_characters": True,
            "reuse_existing_character_ids": True,
        },
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Created: {OUTPUT_FILE}")
    print(f"Characters: {len(characters)}")
    print(f"Scenes: {len(scenes)}")
    print(
        "Shots:",
        sum(len(scene.get("shots", [])) for scene in scenes),
    )


if __name__ == "__main__":
    main()
