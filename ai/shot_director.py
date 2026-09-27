import os
import json
import time
import re
from pathlib import Path
from google import genai
from google.genai import types

PRIMARY_MODEL = "gemini-3.8-flash"
FALLBACK_MODEL = "gemini-3.5-flash-lite"
MODELS = [PRIMARY_MODEL, FALLBACK_MODEL]
MAX_RETRIES = 4
BASE_DIR = Path(__file__).resolve().parent.parent
SCENES_DIR = BASE_DIR / "output" / "scenes"
OUTPUT_DIR = BASE_DIR / "output" / "shots"
INDEX_FILE = SCENES_DIR / "index.json"
ALLOWED_DURATIONS = [4, 6, 8]


class ShotDirector:
    def __init__(self):
        self.keys = []
        for name in ("GEMINI_API_KEY", "GEMINI_API_KEY_2"):
            value = os.getenv(name, "").strip()
            if value and value not in self.keys:
                self.keys.append(value)
        if not self.keys:
            raise RuntimeError("No Gemini API key found. Set GEMINI_API_KEY.")
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        print(f"🔑 Gemini API keys available: {len(self.keys)}")

    def load(self, path):
        if not path.exists():
            raise FileNotFoundError(f"Required file not found: {path}")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON: {path}: {e}")

    def save(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def duration_plan(self, target):
        target = max(1, int(target or 8))
        plans = {
            1:[4],2:[4],3:[4],4:[4],5:[6],6:[6],7:[4,4],8:[8],
            9:[4,6],10:[4,6],11:[6,6],12:[6,6],13:[6,8],14:[6,8],
            15:[8,4,4],16:[8,8]
        }
        if target in plans:
            return plans[target]
        result = []
        while target > 8:
            result.append(8)
            target -= 8
        result.append(4 if target <= 4 else 6 if target <= 6 else 8)
        return result

    def registry(self, scene):
        result = {}
        for c in scene.get("character_references", []):
            name = str(c.get("name", "")).strip()
            cid = str(c.get("canonical_id", "")).strip()
            if not name or not cid:
                raise RuntimeError("Every character must have a canonical_id.")
            if c.get("identity_locked") is not True:
                raise RuntimeError(f"Character {name} is not identity locked.")
            result[name.lower()] = {
                "name": name,
                "canonical_id": cid,
                "flow_tag": c.get("flow_tag", f"@{name}"),
                "appearance": c.get("appearance", ""),
                "voice_style": c.get("voice_style", ""),
                "design_version": c.get("design_version", 1),
            }
        return result

    def character_text(self, scene):
        return "\n".join(
            f"- {c['name']} | id={c['canonical_id']} | tag={c['flow_tag']} | "
            f"appearance={c['appearance']} | voice={c['voice_style']}"
            for c in self.registry(scene).values()
        )

    def prompt(self, scene, durations):
        ep = scene.get("episode", {})
        s = scene.get("scene", {})
        v = scene.get("visual", {})
        a = scene.get("audio", {})
        cont = scene.get("continuity", {})
        dialogue = "\n".join(
            f"{d.get('character')}: {d.get('text')} [emotion: {d.get('emotion')}] "
            f"[delivery: {d.get('delivery')}]" for d in scene.get("dialogue", [])
        ) or "No dialogue."
        return f"""
You are the SHOT DIRECTOR for a continuous Tamil children's animated universe.
Convert ONE existing production scene into short cinematic video shots for a
programmatic Veo video API. This is NOT a story-writing task.

EPISODE: {ep.get('title','')} | LANGUAGE: {ep.get('language','Tamil')}
SCENE {s.get('scene_number')}: {s.get('title','')}
LOCATION: {s.get('location','')}
TARGET DURATION: {s.get('duration_seconds',8)} seconds
STORY ACTION: {s.get('story_action','')}
EXACT SHOT DURATIONS: {json.dumps(durations)}

CANONICAL CHARACTERS:
{self.character_text(scene)}

IDENTITY LOCK: Preserve every character's exact face, age, skin tone, hair,
clothing, body proportions, accessories and distinctive features. Never
redesign, merge, replace, de-age, recolor, or create alternate versions.
Only characters listed above may appear.

SOURCE VISUAL PROMPT:
{v.get('visual_prompt_source','')}
CAMERA: {v.get('camera','')}
ANIMATION: {v.get('animation','')}
FACIAL PERFORMANCE: {v.get('facial_expression','')}
DIALOGUE:
{dialogue}
BGM: {a.get('bgm','')}
SFX: {a.get('sfx','')}

CONTINUITY:
Previous: {json.dumps(cont.get('previous_episode_context',[]), ensure_ascii=False)}
New information: {json.dumps(cont.get('new_information',[]), ensure_ascii=False)}
Mysteries: {json.dumps(cont.get('unresolved_mysteries',[]), ensure_ascii=False)}
Clues: {json.dumps(cont.get('introduced_clues',[]), ensure_ascii=False)}
Future hook: {cont.get('future_hook','')}

RULES:
1. Create exactly {len(durations)} shots with exactly these durations.
2. Shots form one continuous scene with believable positions, objects, lighting,
   character actions and camera continuity.
3. Preserve Tamil dialogue exactly; assign each spoken line to one shot.
4. Use close/medium shots when facial performance or dialogue matters.
5. Show natural blinking, eye movement, breathing, gestures, hair/cloth motion,
   environmental motion and cinematic camera movement.
6. No extra characters, subtitles, captions, logos, watermarks or text.
7. Important artifacts must remain visually consistent.
8. Every visual_prompt must be directly usable by a video generator.
9. Do not resolve mysteries or change story facts.
10. If total generated duration exceeds target, make the final shot naturally
    trimmable by the episode assembler.

RETURN ONLY VALID JSON:
{{
  "scene_number": {s.get('scene_number')},
  "scene_title": "...",
  "target_duration_seconds": {s.get('duration_seconds',8)},
  "generated_duration_seconds": {sum(durations)},
  "shots": [
    {{
      "shot_number": 1,
      "duration_seconds": {durations[0]},
      "purpose": "...",
      "characters": [{{"name":"...","canonical_id":"...","flow_tag":"@...","action":"...","emotion":"..."}}],
      "action": "...",
      "dialogue": [{{"character":"...","text":"...","emotion":"...","delivery":"..."}}],
      "camera": "...",
      "facial_performance": "...",
      "environment_motion": "...",
      "visual_prompt": "...",
      "bgm": "...",
      "sfx": "...",
      "transition_to_next_shot": "..."
    }}
  ],
  "continuity_lock": {{
    "canonical_character_ids": [],
    "identity_locked": true,
    "important_objects": [],
    "location": "...",
    "lighting": "..."
  }}
}}
""".strip()

    def schema(self):
        char = {"type":"OBJECT","properties":{
            "name":{"type":"STRING"},"canonical_id":{"type":"STRING"},
            "flow_tag":{"type":"STRING"},"action":{"type":"STRING"},
            "emotion":{"type":"STRING"}},
            "required":["name","canonical_id","flow_tag","action","emotion"]}
        dlg = {"type":"OBJECT","properties":{
            "character":{"type":"STRING"},"text":{"type":"STRING"},
            "emotion":{"type":"STRING"},"delivery":{"type":"STRING"}},
            "required":["character","text","emotion","delivery"]}
        shot = {"type":"OBJECT","properties":{
            "shot_number":{"type":"INTEGER"},"duration_seconds":{"type":"INTEGER"},
            "purpose":{"type":"STRING"},"characters":{"type":"ARRAY","items":char},
            "action":{"type":"STRING"},"dialogue":{"type":"ARRAY","items":dlg},
            "camera":{"type":"STRING"},"facial_performance":{"type":"STRING"},
            "environment_motion":{"type":"STRING"},"visual_prompt":{"type":"STRING"},
            "bgm":{"type":"STRING"},"sfx":{"type":"STRING"},
            "transition_to_next_shot":{"type":"STRING"}},
            "required":["shot_number","duration_seconds","purpose","characters","action",
                         "dialogue","camera","facial_performance","environment_motion",
                         "visual_prompt","bgm","sfx","transition_to_next_shot"]}
        return {"type":"OBJECT","properties":{
            "scene_number":{"type":"INTEGER"},"scene_title":{"type":"STRING"},
            "target_duration_seconds":{"type":"INTEGER"},"generated_duration_seconds":{"type":"INTEGER"},
            "shots":{"type":"ARRAY","items":shot},
            "continuity_lock":{"type":"OBJECT","properties":{
                "canonical_character_ids":{"type":"ARRAY","items":{"type":"STRING"}},
                "identity_locked":{"type":"BOOLEAN"},
                "important_objects":{"type":"ARRAY","items":{"type":"STRING"}},
                "location":{"type":"STRING"},"lighting":{"type":"STRING"}},
                "required":["canonical_character_ids","identity_locked","important_objects","location","lighting"]}},
            "required":["scene_number","scene_title","target_duration_seconds",
                         "generated_duration_seconds","shots","continuity_lock"]}

    def parse(self, response):
        text = (getattr(response, "text", None) or "").strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\\s*", "", text)
            text = re.sub(r"\\s*```$", "", text)
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid Gemini JSON: {e}")

    def validate(self, result, scene, durations):
        expected = scene["scene"]["scene_number"]
        if result.get("scene_number") != expected:
            raise RuntimeError("Scene number mismatch.")
        shots = result.get("shots", [])
        if len(shots) != len(durations):
            raise RuntimeError(f"Expected {len(durations)} shots, got {len(shots)}.")
        reg = self.registry(scene)
        ids = {c["canonical_id"] for c in reg.values()}
        names = set(reg)
        for i, (shot, duration) in enumerate(zip(shots, durations), 1):
            if shot.get("shot_number") != i or shot.get("duration_seconds") != duration:
                raise RuntimeError(f"Shot {i} numbering/duration invalid.")
            if not shot.get("visual_prompt"):
                raise RuntimeError(f"Shot {i} has no visual_prompt.")
            for c in shot.get("characters", []):
                if c.get("name", "").lower() not in names:
                    raise RuntimeError(f"Unrequested character in shot {i}: {c.get('name')}")
                if c.get("canonical_id") not in ids:
                    raise RuntimeError(f"Invalid canonical ID in shot {i}.")
            for d in shot.get("dialogue", []):
                if d.get("character", "").lower() not in names:
                    raise RuntimeError(f"Unrequested dialogue character in shot {i}.")
        if result.get("continuity_lock", {}).get("identity_locked") is not True:
            raise RuntimeError("Identity lock disabled.")
        result["target_duration_seconds"] = scene["scene"].get("duration_seconds", sum(durations))
        result["generated_duration_seconds"] = sum(durations)
        return result

    def generate(self, scene):
        target = scene["scene"].get("duration_seconds", 8)
        durations = self.duration_plan(target)
        last_error = None
        for key_no, key in enumerate(self.keys, 1):
            for model in MODELS:
                for attempt in range(1, MAX_RETRIES + 1):
                    try:
                        print(f"🤖 Scene {scene['scene']['scene_number']} | key {key_no} | {model} | attempt {attempt}")
                        client = genai.Client(api_key=key)
                        response = client.models.generate_content(
                            model=model,
                            contents=self.prompt(scene, durations),
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json",
                                response_schema=self.schema(),
                            ),
                        )
                        return self.validate(self.parse(response), scene, durations)
                    except Exception as e:
                        last_error = e
                        print(f"⚠️ {e}")
                        if attempt < MAX_RETRIES:
                            delay = 8 * (2 ** (attempt - 1))
                            print(f"⏳ Retrying in {delay}s...")
                            time.sleep(delay)
        raise RuntimeError(f"Shot generation failed. Last error: {last_error}")

    def enrich(self, result, scene):
        reg = self.registry(scene)
        ep = scene.get("episode", {})
        info = scene.get("scene", {})
        audio = scene.get("audio", {})
        for shot in result["shots"]:
            chars = []
            for c in shot.get("characters", []):
                ref = reg[c["name"].lower()]
                chars.append({**ref, "identity_locked":True,
                              "action":c.get("action",""), "emotion":c.get("emotion","")})
            shot["canonical_characters"] = chars
            shot["video_generation"] = {
                "provider":"Google Gemini API","model":"veo-3.1-generate-preview",
                "duration_seconds":shot["duration_seconds"],"aspect_ratio":"9:16",
                "resolution":"720p","native_audio":True,"prompt_ready":True,
                "requires_character_consistency":True}
            identity = " | ".join(f"{c['name']} ({c['canonical_id']}): {c['appearance']}" for c in chars)
            dialogue = json.dumps(shot.get("dialogue",[]), ensure_ascii=False)
            shot["veo_prompt"] = (
                f"Cinematic 3D animated children's adventure, Tamil episode '{ep.get('title','')}', "
                f"location {info.get('location','')}. Use ONLY established characters: "
                f"{', '.join(c['flow_tag'] for c in chars)}. Exact canonical identity: {identity}. "
                f"Never redesign faces, age, skin, hair, clothing, proportions or accessories. "
                f"Action: {shot.get('action','')}. Camera: {shot.get('camera','')}. "
                f"Facial performance: {shot.get('facial_performance','')}. "
                f"Environment motion: {shot.get('environment_motion','')}. "
                f"Visual direction: {shot.get('visual_prompt','')}. "
                f"Speak Tamil dialogue naturally when present: {dialogue}. "
                f"BGM: {shot.get('bgm') or audio.get('bgm','')}. SFX: {shot.get('sfx') or audio.get('sfx','')}. "
                "Natural blinking, eye movement, breathing, gestures, hair/cloth motion, "
                "environment motion and cinematic camera movement. No subtitles, captions, "
                "logos, watermarks or on-screen text."
            )
        return result

    def process(self):
        index = self.load(INDEX_FILE)
        entries = index.get("scenes", [])
        if not entries:
            raise RuntimeError("No scenes found in output/scenes/index.json")
        summary = []
        total_shots = total_target = total_generated = 0
        for entry in entries:
            source = self.load(BASE_DIR / entry["file"])
            result = self.enrich(self.generate(source), source)
            n = source["scene"]["scene_number"]
            path = OUTPUT_DIR / f"scene_{n:02d}_shots.json"
            self.save(path, result)
            summary.append({
                "scene_number":n,"scene_title":result["scene_title"],
                "target_duration_seconds":result["target_duration_seconds"],
                "generated_duration_seconds":result["generated_duration_seconds"],
                "shot_count":len(result["shots"]),
                "file":str(path.relative_to(BASE_DIR)).replace("\\","/")})
            total_shots += len(result["shots"])
            total_target += result["target_duration_seconds"]
            total_generated += result["generated_duration_seconds"]
        out = {
            "episode_number":index.get("episode_number"),"episode_title":index.get("episode_title"),
            "language":index.get("language","Tamil"),"scene_count":len(summary),
            "total_shots":total_shots,"total_target_duration_seconds":total_target,
            "total_generated_duration_seconds":total_generated,
            "allowed_shot_durations_seconds":ALLOWED_DURATIONS,
            "video_generation":{"provider":"Google Gemini API","model":"veo-3.1-generate-preview",
                                 "aspect_ratio":"9:16","resolution":"720p","native_audio":True},
            "scenes":summary}
        self.save(OUTPUT_DIR / "index.json", out)
        print("============================================================")
        print("✅ SHOT DIRECTOR COMPLETED")
        print(f"🎬 Scenes: {len(summary)} | 🎞️ Shots: {total_shots}")
        print(f"⏱️ Target: {total_target}s | 🎥 Planned: {total_generated}s")
        print(f"📁 {OUTPUT_DIR}")
        print("============================================================")
        return out


def main():
    ShotDirector().process()


if __name__ == "__main__":
    main()
