"""
Scene Director
--------------
Converts output/generated_episode_01.json into Google Flow-ready
scene files.

Input:
    output/generated_episode_01.json

Output:
    output/scenes/scene_01.json
    output/scenes/scene_02.json
    ...

The script does NOT generate video and does NOT call Google Flow.
It prepares deterministic prompts and character-reference data for
the next video-generation stage.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(__file__).resolve().parent.parent
EPISODE_FILE = BASE_DIR / "output" / "generated_episode_01.json"
SCENES_DIR = BASE_DIR / "output" / "scenes"


# ---------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------

def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("Episode JSON root must be an object.")

    return data


def clean_name(name: str) -> str:
    """Create a safe filename component."""
    value = re.sub(r"[^A-Za-z0-9_-]+", "_", str(name).strip())
    return value.strip("_") or "scene"


def flow_character_tag(name: str) -> str:
    """
    Google Flow character prompt syntax.

    Example:
        Meera -> @Meera
    """
    return "@" + str(name).strip().replace(" ", "")


def get_episode(data: Dict[str, Any]) -> Dict[str, Any]:
    episode = data.get("episode")
    if not isinstance(episode, dict):
        raise ValueError("Missing 'episode' object in generated episode JSON.")
    return episode


def get_scenes(episode: Dict[str, Any]) -> List[Dict[str, Any]]:
    scenes = episode.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        raise ValueError("Episode does not contain a non-empty 'scenes' list.")
    return scenes


def build_registry(episode: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Build one canonical character registry from the episode-level
    canonical_character_identities section.
    """
    registry: Dict[str, Dict[str, Any]] = {}

    identities = episode.get("canonical_character_identities", [])

    if isinstance(identities, list):
        for item in identities:
            if not isinstance(item, dict):
                continue

            name = str(item.get("name", "")).strip()
            canonical_id = str(item.get("canonical_id", "")).strip()

            if not name or not canonical_id:
                continue

            registry[name.lower()] = {
                "name": name,
                "canonical_id": canonical_id,
                "identity_locked": bool(item.get("identity_locked", True)),
                "design_version": item.get("design_version", 1),
                "appearance": str(item.get("appearance", "")).strip(),
                "voice_style": str(item.get("voice_style", "")).strip(),
            }

    # Also collect references from scenes in case a character is not
    # present in the episode-level registry.
    for scene in get_scenes(episode):
        refs = scene.get("character_references", [])
        if not isinstance(refs, list):
            continue

        for item in refs:
            if not isinstance(item, dict):
                continue

            name = str(item.get("name", "")).strip()
            canonical_id = str(item.get("canonical_id", "")).strip()

            if not name or not canonical_id:
                continue

            key = name.lower()

            if key not in registry:
                registry[key] = {
                    "name": name,
                    "canonical_id": canonical_id,
                    "identity_locked": bool(item.get("identity_locked", True)),
                    "design_version": item.get("design_version", 1),
                    "appearance": str(item.get("appearance", "")).strip(),
                    "voice_style": str(item.get("voice_style", "")).strip(),
                }

    return registry


def resolve_character(
    name: str,
    scene: Dict[str, Any],
    registry: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Resolve a scene character against the canonical registry."""
    key = str(name).strip().lower()

    if key in registry:
        return dict(registry[key])

    # Fallback to scene-local character reference.
    refs = scene.get("character_references", [])
    if isinstance(refs, list):
        for item in refs:
            if not isinstance(item, dict):
                continue
            if str(item.get("name", "")).strip().lower() == key:
                return {
                    "name": str(item.get("name", name)).strip(),
                    "canonical_id": str(item.get("canonical_id", "")).strip(),
                    "identity_locked": bool(item.get("identity_locked", True)),
                    "design_version": item.get("design_version", 1),
                    "appearance": str(item.get("appearance", "")).strip(),
                    "voice_style": str(item.get("voice_style", "")).strip(),
                }

    raise ValueError(
        f"Character '{name}' appears in the scene but has no canonical identity."
    )


# ---------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------

def build_character_block(
    characters: List[Dict[str, Any]],
) -> str:
    lines = []

    for character in characters:
        name = character["name"]
        tag = flow_character_tag(name)
        appearance = character.get("appearance", "").strip()
        voice = character.get("voice_style", "").strip()

        lines.append(
            f"{tag} ({name}): {appearance}"
        )

        if voice:
            lines.append(f"Voice style: {voice}")

    return "\n".join(lines)


def build_dialogue_block(scene: Dict[str, Any]) -> str:
    dialogue = scene.get("dialogue", [])

    if not isinstance(dialogue, list) or not dialogue:
        return "No spoken dialogue in this scene."

    lines = []

    for item in dialogue:
        if not isinstance(item, dict):
            continue

        character = str(item.get("character", "")).strip()
        text = str(item.get("text", "")).strip()
        emotion = str(item.get("emotion", "")).strip()
        delivery = str(item.get("delivery", "")).strip()

        if not character or not text:
            continue

        line = f"{character}: {text}"

        if emotion:
            line += f" [emotion: {emotion}]"

        if delivery:
            line += f" [delivery: {delivery}]"

        lines.append(line)

    return "\n".join(lines) if lines else "No spoken dialogue in this scene."


def build_flow_prompt(
    episode: Dict[str, Any],
    scene: Dict[str, Any],
    characters: List[Dict[str, Any]],
) -> str:
    scene_number = scene.get("scene_number")
    title = str(scene.get("title", "")).strip()
    location = str(scene.get("location", "")).strip()
    story_action = str(scene.get("story_action", "")).strip()
    visual_prompt = str(scene.get("visual_prompt", "")).strip()
    camera = str(scene.get("camera", "")).strip()
    animation = str(scene.get("animation", "")).strip()
    facial_expression = str(scene.get("facial_expression", "")).strip()
    bgm = str(scene.get("bgm", "")).strip()
    sfx = str(scene.get("sfx", "")).strip()

    tags = ", ".join(flow_character_tag(c["name"]) for c in characters)

    dialogue_block = build_dialogue_block(scene)
    character_block = build_character_block(characters)

    return f"""
Create a cinematic animated children's adventure scene for the Tamil
shared universe episode "{episode.get("title", "")}".

SCENE
Scene {scene_number}: {title}
Location: {location}
Duration target: {scene.get("duration_seconds", 0)} seconds

CHARACTERS
Use these exact established Flow characters: {tags}

CANONICAL CHARACTER IDENTITY
{character_block}

CONTINUITY RULE
Preserve every referenced character's established face, age, skin tone,
hair style, hairstyle, clothing identity, body proportions, accessories,
and distinctive features exactly. Do not redesign, re-face, de-age,
recolor skin or hair, change clothing identity, or merge character
identities. Keep each character visually consistent with previous scenes.

STORY ACTION
{story_action}

VISUAL DIRECTION
{visual_prompt}

CAMERA
{camera}

CHARACTER AND ENVIRONMENT MOTION
{animation}

FACIAL PERFORMANCE
{facial_expression}

TAMIL DIALOGUE
{dialogue_block}

AUDIO
Background music: {bgm}
Sound effects: {sfx}

ANIMATION QUALITY
Natural body movement, believable walking and gestures, subtle eye
movement and blinking, expressive facial performance, synchronized
mouth movement while speaking Tamil, natural head movement, realistic
cloth and hair motion, environmental motion, cinematic camera movement,
consistent lighting, and smooth transitions.

STYLE
High-quality cinematic 3D animated children's adventure.
Rich South Indian coastal/village environment.
Detailed characters with expressive faces.
Natural lighting and physically believable movement.
Keep the scene visually coherent from beginning to end.

IMPORTANT
Do not introduce an unrequested character.
Do not change the established appearance of any referenced character.
Do not add subtitles, captions, logos, watermarks, or text on screen.
""".strip()


# ---------------------------------------------------------------------
# Scene JSON generation
# ---------------------------------------------------------------------

def build_scene_output(
    episode: Dict[str, Any],
    scene: Dict[str, Any],
    registry: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:

    scene_number = int(scene.get("scene_number", 0))
    if scene_number <= 0:
        raise ValueError("Every scene must have a positive scene_number.")

    scene_character_names = scene.get("characters", [])
    if not isinstance(scene_character_names, list):
        raise ValueError(f"Scene {scene_number}: 'characters' must be a list.")

    characters = []

    for name in scene_character_names:
        character = resolve_character(str(name), scene, registry)

        if not character.get("canonical_id"):
            raise ValueError(
                f"Scene {scene_number}: character '{name}' has no canonical_id."
            )

        characters.append(character)

    character_refs = []
    for character in characters:
        character_refs.append(
            {
                "name": character["name"],
                "flow_tag": flow_character_tag(character["name"]),
                "canonical_id": character["canonical_id"],
                "identity_locked": character["identity_locked"],
                "design_version": character["design_version"],
                "appearance": character["appearance"],
                "voice_style": character["voice_style"],
            }
        )

    return {
        "episode": {
            "episode_number": episode.get("episode_number"),
            "title": episode.get("title"),
            "language": episode.get("language"),
        },
        "scene": {
            "scene_number": scene_number,
            "title": scene.get("title"),
            "duration_seconds": scene.get("duration_seconds"),
            "location": scene.get("location"),
            "story_action": scene.get("story_action"),
            "characters": scene_character_names,
        },
        "character_references": character_refs,
        "dialogue": scene.get("dialogue", []),
        "visual": {
            "visual_prompt_source": scene.get("visual_prompt", ""),
            "camera": scene.get("camera", ""),
            "animation": scene.get("animation", ""),
            "facial_expression": scene.get("facial_expression", ""),
        },
        "audio": {
            "bgm": scene.get("bgm", ""),
            "sfx": scene.get("sfx", ""),
        },
        "flow": {
            "character_tags": [
                flow_character_tag(c["name"]) for c in characters
            ],
            "prompt": build_flow_prompt(episode, scene, characters),
            "requires_character_assets": True,
            "requires_consistent_character_identity": True,
            "target_aspect_ratio": "9:16",
            "target_resolution": "720x1280",
        },
        "continuity": {
            "identity_locked": all(
                c["identity_locked"] for c in characters
            ),
            "canonical_ids": [
                c["canonical_id"] for c in characters
            ],
            "previous_episode_context": episode.get("continuity_used", []),
            "new_information": episode.get("new_information", []),
            "unresolved_mysteries": episode.get("unresolved_mysteries", []),
            "introduced_clues": episode.get("introduced_clues", []),
            "future_hook": episode.get("future_hook", ""),
        },
    }


def main() -> None:
    print("=" * 70)
    print("SCENE DIRECTOR")
    print("=" * 70)

    data = load_json(EPISODE_FILE)
    episode = get_episode(data)
    scenes = get_scenes(episode)
    registry = build_registry(episode)

    if not registry:
        raise ValueError("No canonical character identities found.")

    SCENES_DIR.mkdir(parents=True, exist_ok=True)

    # Remove old generated scene JSON files so stale scenes cannot remain.
    for old_file in SCENES_DIR.glob("scene_*.json"):
        old_file.unlink()

    print(f"Episode: {episode.get('title')}")
    print(f"Scenes: {len(scenes)}")
    print(f"Canonical characters: {len(registry)}")
    print()

    generated_files = []

    for scene in scenes:
        scene_output = build_scene_output(
            episode=episode,
            scene=scene,
            registry=registry,
        )

        number = scene_output["scene"]["scene_number"]
        filename = f"scene_{number:02d}.json"
        output_path = SCENES_DIR / filename

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(
                scene_output,
                f,
                ensure_ascii=False,
                indent=2,
            )

        generated_files.append(output_path)

        names = ", ".join(
            scene_output["scene"]["characters"]
        )

        print(f"✅ Scene {number:02d}: {filename}")
        print(f"   Characters: {names}")
        print(
            f"   Flow refs: "
            + ", ".join(scene_output["flow"]["character_tags"])
        )

    # Create an index file for the next automation stage.
    index = {
        "episode_number": episode.get("episode_number"),
        "episode_title": episode.get("title"),
        "language": episode.get("language"),
        "scene_count": len(generated_files),
        "scene_directory": "output/scenes",
        "scenes": [
            {
                "scene_number": json.loads(
                    path.read_text(encoding="utf-8")
                )["scene"]["scene_number"],
                "file": str(path.relative_to(BASE_DIR)).replace("\\", "/"),
            }
            for path in generated_files
        ],
    }

    index_path = SCENES_DIR / "index.json"

    with index_path.open("w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print()
    print("=" * 70)
    print("SCENE DIRECTOR COMPLETE")
    print("=" * 70)
    print(f"Generated {len(generated_files)} scene files.")
    print(f"Output directory: {SCENES_DIR}")
    print(f"Index: {index_path}")


if __name__ == "__main__":
    main()
