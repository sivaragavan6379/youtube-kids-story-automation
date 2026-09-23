import os
import json
import time
from pathlib import Path

from google import genai
from google.genai import types


# ============================================================
# CONFIGURATION
# ============================================================

PRIMARY_MODEL = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-2.5-flash-lite"

MAX_RETRIES = 4

BASE_DIR = Path(__file__).resolve().parent.parent

MEMORY_FILE = BASE_DIR / "universe" / "universe_memory.json"
ARC_FILE = BASE_DIR / "output" / "generated_arc.json"

OUTPUT_DIR = BASE_DIR / "output"
EPISODE_OUTPUT_FILE = OUTPUT_DIR / "generated_episode_01.json"


# ============================================================
# EPISODE DIRECTOR
# ============================================================

class EpisodeDirector:

    def __init__(self):

        self.api_key = os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY environment variable is missing."
            )

        self.client = genai.Client(
            api_key=self.api_key
        )

        OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True
        )


    # ========================================================
    # LOAD JSON
    # ========================================================

    def load_json(self, file_path):

        if not file_path.exists():

            raise FileNotFoundError(
                f"Required file not found: {file_path}"
            )

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(file)

        except json.JSONDecodeError as error:

            raise RuntimeError(
                f"Invalid JSON file: {file_path}\n"
                f"Error: {error}"
            )


    # ========================================================
    # LOAD UNIVERSE
    # ========================================================

    def load_universe(self):

        memory = self.load_json(
            MEMORY_FILE
        )

        print("✅ Universe memory loaded.")

        return memory


    # ========================================================
    # LOAD ARC
    # ========================================================

    def load_arc(self):

        arc_data = self.load_json(
            ARC_FILE
        )

        if "arc" not in arc_data:

            raise RuntimeError(
                "generated_arc.json does not contain "
                "the required 'arc' object."
            )

        arc = arc_data["arc"]

        if "episodes" not in arc:

            raise RuntimeError(
                "Generated arc does not contain episodes."
            )

        if not arc["episodes"]:

            raise RuntimeError(
                "Generated arc contains no episodes."
            )

        print(
            f"✅ Story arc loaded: {arc.get('title', 'Unknown')}"
        )

        return arc


    # ========================================================
    # FIND EPISODE
    # ========================================================

    def get_episode(self, arc, episode_number=1):

        for episode in arc["episodes"]:

            if episode.get("episode_number") == episode_number:

                print(
                    f"✅ Episode {episode_number} selected: "
                    f"{episode.get('title', 'Untitled')}"
                )

                return episode

        raise RuntimeError(
            f"Episode {episode_number} was not found "
            f"in generated_arc.json."
        )


    # ========================================================
    # GET CHARACTER INFORMATION
    # ========================================================

    def find_characters_in_memory(
        self,
        universe,
        character_names
    ):

        found = []

        wanted = {
            name.strip().lower()
            for name in character_names
        }

        def recursive_search(value):

            if isinstance(value, dict):

                name = value.get("name")

                if (
                    isinstance(name, str)
                    and name.strip().lower() in wanted
                ):

                    found.append(value)

                for child in value.values():

                    recursive_search(child)

            elif isinstance(value, list):

                for child in value:

                    recursive_search(child)

        recursive_search(universe)

        # Remove duplicates
        unique = {}

        for character in found:

            name = character.get("name")

            if name:

                unique[name.lower()] = character

        return list(unique.values())


    # ========================================================
    # BUILD PROMPT
    # ========================================================

    def build_prompt(
        self,
        universe,
        arc,
        episode
    ):

        important_characters = (
            episode.get(
                "important_characters",
                []
            )
        )

        character_data = self.find_characters_in_memory(
            universe,
            important_characters
        )

        character_text = json.dumps(
            character_data,
            ensure_ascii=False,
            indent=2
        )

        # ----------------------------------------------------
        # Only send the information needed for this episode.
        # This reduces unnecessary output and token usage.
        # ----------------------------------------------------

        arc_context = {
            "title": arc.get("title"),
            "summary": arc.get("summary"),
            "theme": arc.get("theme"),
            "central_conflict": arc.get(
                "central_conflict"
            ),
            "arc_goal": arc.get(
                "arc_goal"
            ),
            "main_characters": arc.get(
                "main_characters",
                []
            ),
            "supporting_characters": arc.get(
                "supporting_characters",
                []
            ),
            "returning_characters": arc.get(
                "returning_characters",
                []
            ),
            "locations": arc.get(
                "locations",
                []
            ),
            "artifacts": arc.get(
                "artifacts",
                []
            ),
            "mysteries": arc.get(
                "mysteries",
                []
            ),
            "central_mysteries": arc.get(
                "central_mysteries",
                []
            ),
            "foreshadowing": arc.get(
                "foreshadowing",
                []
            )
        }

        episode_context = {
            "episode_number": episode.get(
                "episode_number"
            ),
            "title": episode.get(
                "title"
            ),
            "main_objective": episode.get(
                "main_objective"
            ),
            "important_characters": important_characters,
            "key_event": episode.get(
                "key_event"
            ),
            "character_development": episode.get(
                "character_development"
            ),
            "mystery_progression": episode.get(
                "mystery_progression"
            ),
            "ending_hook": episode.get(
                "ending_hook"
            )
        }

        prompt = f"""
You are the EPISODE DIRECTOR for a long-running
Tamil animated children's shared universe.

This is NOT a standalone story.

Every episode must preserve continuity with previous
episodes and arcs.

============================================================
CORE UNIVERSE RULE
============================================================

The universe behaves like a long-running animated series.

Previous events are REAL and MUST remain canon.

Do not rewrite:

- previous characters
- previous relationships
- previous artifacts
- previous mysteries
- previous locations
- previous events
- previous villains
- established character personalities

If a returning character appears, their previous history
must influence their behavior.

If a new character appears, make the character visually
and narratively distinct.

============================================================
LANGUAGE
============================================================

The episode story and spoken dialogue MUST be in natural
Tamil.

Use simple, expressive Tamil suitable for children.

Do NOT write English dialogue.

Character names may remain in their established form.

Example:

"மீரா, அந்த கல்லிலிருந்து மீண்டும் சத்தம் வருகிறது!"

Dialogue should sound like real spoken Tamil,
not like a textbook.

============================================================
TARGET
============================================================

Create ONE complete episode:

Episode number:
{episode.get("episode_number")}

Episode title:
{episode.get("title")}

The episode should be suitable for animation using
Google Flow or a similar AI video system.

The episode should contain:

- story progression
- character acting
- facial expressions
- body movement
- environmental movement
- spoken dialogue
- sound effects
- background music suggestions
- camera directions
- visual continuity
- ending hook

============================================================
ARC CONTEXT
============================================================

{json.dumps(
    arc_context,
    ensure_ascii=False,
    indent=2
)}

============================================================
CURRENT EPISODE PLAN
============================================================

{json.dumps(
    episode_context,
    ensure_ascii=False,
    indent=2
)}

============================================================
CHARACTER INFORMATION FROM UNIVERSE MEMORY
============================================================

{character_text}

============================================================
IMPORTANT CHARACTER RULE
============================================================

Use the established character appearance and personality
from universe memory.

Do NOT redesign an existing character.

Do NOT change:

- age
- face
- hair
- skin tone
- clothing identity
- important accessories
- personality
- established role

The visual description must remain consistent across
future episodes.

============================================================
STORY STRUCTURE
============================================================

Create exactly 8 scenes.

Each scene should move the story forward.

Recommended structure:

Scene 1:
Strong opening / hook

Scene 2:
Characters understand the problem

Scene 3:
Journey or investigation begins

Scene 4:
Discovery

Scene 5:
Problem becomes more dangerous

Scene 6:
Characters work together

Scene 7:
Major emotional/action moment

Scene 8:
Resolution of this episode + strong future hook

The episode should NOT completely solve the larger arc.

============================================================
DIALOGUE
============================================================

Every important scene should contain dialogue.

Dialogue must reveal:

- personality
- emotion
- relationships
- story information
- mystery progression

Avoid unnecessary dialogue.

Do not make every character speak in every scene.

Use natural pauses and reactions.

============================================================
ANIMATION
============================================================

This is a real animated series.

Do NOT describe scenes as static pictures.

Characters must perform actions.

Examples:

- walking
- running
- turning
- looking around
- pointing
- picking up objects
- touching artifacts
- reacting with surprise
- smiling
- becoming worried
- nodding
- looking at each other
- climbing
- environmental interaction

Include natural environmental movement:

- leaves moving
- wind
- birds flying
- clouds moving
- water movement
- dust
- light changes
- glowing objects
- mist
- shadows

============================================================
CAMERA
============================================================

Give useful camera instructions.

Examples:

- wide establishing shot
- medium shot
- close-up
- over-the-shoulder
- tracking shot
- slow camera push-in
- camera pan
- low angle
- high angle

Do not overuse cinematic movements.

============================================================
FLOW VIDEO PROMPT
============================================================

For every scene create a concise animation prompt.

The prompt should describe:

character appearance
+
character action
+
facial expression
+
environment
+
camera movement
+
lighting
+
animation style

The prompt must be suitable for generating
an actual moving video.

Do not describe a slideshow.

============================================================
VOICE
============================================================

For each spoken line provide:

character
dialogue
emotion
delivery style

Keep individual dialogue lines short enough for
natural speech animation.

============================================================
SOUND
============================================================

For each scene provide:

BGM:
background music mood

SFX:
important sound effects

============================================================
CONTINUITY
============================================================

At the end of the episode provide:

1. continuity_used
2. new_information
3. unresolved_mysteries
4. introduced_clues
5. future_hook
6. character_state_changes

These fields will later be written back into
universe_memory.json.

============================================================
IMPORTANT
============================================================

Do not invent unrelated characters.

Do not introduce a major villain unless the episode plan
requires it.

Do not resolve the main arc mystery early.

Do not randomly change established lore.

Do not make the episode feel disconnected from the
previous arc.

The ending must naturally connect to the next episode.

============================================================
OUTPUT
============================================================

Return ONLY valid JSON.

No markdown.

No ```json.

No explanation outside JSON.

Keep descriptions detailed enough for production,
but compact enough to fit the output limit.

Exactly 8 scenes.

Each scene should have:

scene_number
title
duration_seconds
location
characters
story_action
dialogue
visual_prompt
camera
animation
facial_expression
bgm
sfx

Dialogue must be an array.

Each dialogue object must contain:

character
text
emotion
delivery

At the end include:

continuity_used
new_information
unresolved_mysteries
introduced_clues
future_hook
character_state_changes
"""


        return prompt


    # ========================================================
    # GEMINI SCHEMA
    # ========================================================

    def get_schema(self):

        return {

            "type": "OBJECT",

            "properties": {

                "episode": {

                    "type": "OBJECT",

                    "properties": {

                        "episode_number": {
                            "type": "INTEGER"
                        },

                        "title": {
                            "type": "STRING"
                        },

                        "language": {
                            "type": "STRING"
                        },

                        "summary": {
                            "type": "STRING"
                        },

                        "scenes": {

                            "type": "ARRAY",

                            "items": {

                                "type": "OBJECT",

                                "properties": {

                                    "scene_number": {
                                        "type": "INTEGER"
                                    },

                                    "title": {
                                        "type": "STRING"
                                    },

                                    "duration_seconds": {
                                        "type": "INTEGER"
                                    },

                                    "location": {
                                        "type": "STRING"
                                    },

                                    "characters": {

                                        "type": "ARRAY",

                                        "items": {
                                            "type": "STRING"
                                        }
                                    },

                                    "story_action": {
                                        "type": "STRING"
                                    },

                                    "dialogue": {

                                        "type": "ARRAY",

                                        "items": {

                                            "type": "OBJECT",

                                            "properties": {

                                                "character": {
                                                    "type": "STRING"
                                                },

                                                "text": {
                                                    "type": "STRING"
                                                },

                                                "emotion": {
                                                    "type": "STRING"
                                                },

                                                "delivery": {
                                                    "type": "STRING"
                                                }

                                            },

                                            "required": [
                                                "character",
                                                "text",
                                                "emotion",
                                                "delivery"
                                            ]
                                        }
                                    },

                                    "visual_prompt": {
                                        "type": "STRING"
                                    },

                                    "camera": {
                                        "type": "STRING"
                                    },

                                    "animation": {
                                        "type": "STRING"
                                    },

                                    "facial_expression": {
                                        "type": "STRING"
                                    },

                                    "bgm": {
                                        "type": "STRING"
                                    },

                                    "sfx": {
                                        "type": "STRING"
                                    }

                                },

                                "required": [
                                    "scene_number",
                                    "title",
                                    "duration_seconds",
                                    "location",
                                    "characters",
                                    "story_action",
                                    "dialogue",
                                    "visual_prompt",
                                    "camera",
                                    "animation",
                                    "facial_expression",
                                    "bgm",
                                    "sfx"
                                ]
                            }
                        },

                        "continuity_used": {

                            "type": "ARRAY",

                            "items": {
                                "type": "STRING"
                            }
                        },

                        "new_information": {

                            "type": "ARRAY",

                            "items": {
                                "type": "STRING"
                            }
                        },

                        "unresolved_mysteries": {

                            "type": "ARRAY",

                            "items": {
                                "type": "STRING"
                            }
                        },

                        "introduced_clues": {

                            "type": "ARRAY",

                            "items": {
                                "type": "STRING"
                            }
                        },

                        "future_hook": {
                            "type": "STRING"
                        },

                        "character_state_changes": {

                            "type": "ARRAY",

                            "items": {

                                "type": "OBJECT",

                                "properties": {

                                    "character": {
                                        "type": "STRING"
                                    },

                                    "change": {
                                        "type": "STRING"
                                    }

                                },

                                "required": [
                                    "character",
                                    "change"
                                ]
                            }
                        }

                    },

                    "required": [
                        "episode_number",
                        "title",
                        "language",
                        "summary",
                        "scenes",
                        "continuity_used",
                        "new_information",
                        "unresolved_mysteries",
                        "introduced_clues",
                        "future_hook",
                        "character_state_changes"
                    ]
                }

            },

            "required": [
                "episode"
            ]
        }


    # ========================================================
    # VALIDATE EPISODE
    # ========================================================

    def validate_episode(self, result):

        if not isinstance(result, dict):

            raise RuntimeError(
                "Gemini result is not a JSON object."
            )

        if "episode" not in result:

            raise RuntimeError(
                "Generated result does not contain "
                "'episode'."
            )

        episode = result["episode"]

        required_fields = [
            "episode_number",
            "title",
            "language",
            "summary",
            "scenes",
            "continuity_used",
            "new_information",
            "unresolved_mysteries",
            "introduced_clues",
            "future_hook",
            "character_state_changes"
        ]

        for field in required_fields:

            if field not in episode:

                raise RuntimeError(
                    f"Generated episode is missing "
                    f"required field: {field}"
                )

        scenes = episode["scenes"]

        if len(scenes) != 8:

            raise RuntimeError(
                f"Expected exactly 8 scenes, "
                f"but received {len(scenes)}."
            )

        for index, scene in enumerate(
            scenes,
            start=1
        ):

            if scene.get("scene_number") != index:

                raise RuntimeError(
                    f"Scene numbering error. "
                    f"Expected scene {index}."
                )

            if not scene.get("dialogue"):

                raise RuntimeError(
                    f"Scene {index} contains no dialogue."
                )

        return True


    # ========================================================
    # REQUEST GEMINI
    # ========================================================

    def request_gemini(
        self,
        prompt,
        schema
    ):

        models_to_try = [
            PRIMARY_MODEL,
            FALLBACK_MODEL
        ]

        last_error = None

        for model_name in models_to_try:

            print()
            print(
                "============================================"
            )

            print(
                f"🤖 Trying model: {model_name}"
            )

            print(
                "============================================"
            )

            for attempt in range(
                1,
                MAX_RETRIES + 1
            ):

                try:

                    print(
                        f"🔄 Attempt "
                        f"{attempt}/{MAX_RETRIES}"
                    )

                    response = (
                        self.client.models.generate_content(

                            model=model_name,

                            contents=prompt,

                            config=(
                                types.GenerateContentConfig(

                                    response_mime_type=(
                                        "application/json"
                                    ),

                                    response_schema=schema,

                                    temperature=0.9,

                                    max_output_tokens=18000
                                )
                            )
                        )
                    )

                    if (
                        response
                        and response.text
                    ):

                        print(
                            f"✅ Response received "
                            f"from {model_name}"
                        )

                        return response.text

                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                except Exception as error:

                    last_error = error

                    error_text = str(error)

                    print()
                    print(
                        f"⚠️ Gemini error:"
                    )
                    print(
                        error_text
                    )

                    temporary_error = (

                        "503" in error_text

                        or
                        "UNAVAILABLE" in error_text

                        or
                        "429" in error_text

                        or
                        "RESOURCE_EXHAUSTED"
                        in error_text

                        or
                        "500" in error_text
                    )

                    if (
                        temporary_error
                        and
                        attempt < MAX_RETRIES
                    ):

                        wait_seconds = (
                            5 *
                            (
                                2 ** (
                                    attempt - 1
                                )
                            )
                        )

                        print(
                            f"⏳ Waiting "
                            f"{wait_seconds} seconds..."
                        )

                        time.sleep(
                            wait_seconds
                        )

                        continue

                    break

            print()
            print(
                f"⚠️ Model {model_name} failed."
            )

            print(
                "➡️ Trying fallback model..."
            )

        raise RuntimeError(
            "Gemini episode generation failed "
            "after all retries and fallback models.\n"
            f"Last error: {last_error}"
        )


    # ========================================================
    # GENERATE EPISODE
    # ========================================================

    def generate_episode(
        self,
        episode_number=1
    ):

        print()
        print(
            "============================================"
        )

        print(
            "🎬 EPISODE DIRECTOR"
        )

        print(
            "============================================"
        )

        print(
            f"🎯 Generating Episode {episode_number}"
        )

        universe = self.load_universe()

        arc = self.load_arc()

        episode = self.get_episode(
            arc,
            episode_number
        )

        prompt = self.build_prompt(
            universe,
            arc,
            episode
        )

        schema = self.get_schema()

        response_text = self.request_gemini(
            prompt,
            schema
        )

        print()
        print(
            "🧩 Parsing generated episode..."
        )

        try:

            result = json.loads(
                response_text
            )

        except json.JSONDecodeError as error:

            print()
            print(
                "❌ Invalid JSON received."
            )

            print(
                response_text[
                    :5000
                ]
            )

            raise RuntimeError(
                "Gemini returned invalid JSON.\n"
                f"JSON error: {error}"
            )

        self.validate_episode(
            result
        )

        # ----------------------------------------------------
        # Force correct episode number
        # ----------------------------------------------------

        result["episode"][
            "episode_number"
        ] = episode_number

        # ----------------------------------------------------
        # Save result
        # ----------------------------------------------------

        with open(
            EPISODE_OUTPUT_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                result,
                file,
                ensure_ascii=False,
                indent=2
            )

        print()
        print(
            "============================================"
        )

        print(
            "✅ EPISODE GENERATED SUCCESSFULLY"
        )

        print(
            "============================================"
        )

        print(
            f"📄 Output:"
        )

        print(
            EPISODE_OUTPUT_FILE
        )

        print(
            f"🎬 Episode:"
            f" {result['episode']['title']}"
        )

        print(
            f"🎞️ Scenes:"
            f" {len(result['episode']['scenes'])}"
        )

        return result


# ============================================================
# MAIN
# ============================================================

def main():

    director = EpisodeDirector()

    director.generate_episode(
        episode_number=1
    )


if __name__ == "__main__":

    main()
