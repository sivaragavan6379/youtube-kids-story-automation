import os
import json
from pathlib import Path

from google import genai
from google.genai import types


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "gemini-2.5-flash"

BASE_DIR = Path(__file__).resolve().parent.parent

MEMORY_FILE = (
    BASE_DIR
    / "universe"
    / "universe_memory.json"
)

OUTPUT_DIR = BASE_DIR / "output"

EPISODE_OUTPUT_FILE = (
    OUTPUT_DIR / "generated_episode.json"
)


# ============================================================
# STORY DIRECTOR
# ============================================================

class StoryDirector:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY environment variable was not found."
            )

        self.client = genai.Client(
            api_key=api_key
        )

    # ========================================================
    # LOAD UNIVERSE MEMORY
    # ========================================================

    def load_universe(self):

        if not MEMORY_FILE.exists():
            raise FileNotFoundError(
                f"Universe memory file not found:\n{MEMORY_FILE}"
            )

        try:

            with open(
                MEMORY_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(file)

        except json.JSONDecodeError as error:

            raise RuntimeError(
                f"Universe memory contains invalid JSON: {error}"
            )

    # ========================================================
    # BUILD STORY PROMPT
    # ========================================================

    def build_prompt(self, universe):

        universe_json = json.dumps(
            universe,
            ensure_ascii=False,
            indent=2
        )

        return f"""
You are the STORY DIRECTOR of a long-running Tamil
animated shared universe.

This is NOT a collection of unrelated stories.

Every episode belongs to the same evolving universe.

Your job is to create the NEXT EPISODE while maintaining
continuity with everything that already happened.

============================================================
CORE STORY PRINCIPLES
============================================================

1. Create an entertaining children's animated adventure.

2. The story must be understandable as an individual episode.

3. At the same time, the episode should contribute to a
   larger long-term universe.

4. Existing characters may return when there is a logical
   story reason.

5. Do NOT bring back a character merely for a cameo.

6. New characters may be created whenever the story genuinely
   needs them.

7. Do NOT create unnecessary characters.

8. Before creating a new character, inspect the existing
   character list.

9. If an existing character can naturally perform the role,
   reuse that character.

10. Never accidentally create a duplicate version of an
    existing character.

============================================================
CHARACTER CONTINUITY
============================================================

For every returning character, preserve:

- identity
- appearance
- age
- species
- personality
- important relationships
- abilities
- established history

A character may change over time, but meaningful changes
must happen because of story events.

Characters should have character development.

============================================================
LONG-TERM UNIVERSE
============================================================

The universe may contain:

- multiple series
- multiple story arcs
- many episodes
- heroes
- friends
- villains
- locations
- artifacts
- mysteries
- relationships
- legends
- secrets
- unresolved events

New story arcs may introduce completely new characters.

Old characters may return later.

Different series can share the same universe.

============================================================
CONTINUITY AND CONSEQUENCES
============================================================

Previous events should matter.

If an earlier episode introduced:

- a mystery
- an artifact
- a location
- a promise
- a friendship
- an enemy
- a secret
- an unexplained event

then future episodes may build upon it.

Do not randomly rewrite established history.

============================================================
MYSTERIES
============================================================

Not every mystery should be solved immediately.

Some mysteries can remain unresolved for many episodes.

A mystery can become important much later.

============================================================
FORESHADOWING
============================================================

You may plant small clues for future stories.

Examples:

- strange symbol
- unexplained object
- mysterious person
- unusual event
- forgotten legend
- secret location
- strange message

The clue should feel natural inside the current story.

============================================================
STORY QUALITY
============================================================

The story should contain appropriate combinations of:

- adventure
- curiosity
- humor
- friendship
- emotion
- mystery
- discovery
- danger appropriate for children
- meaningful character moments

Avoid making every episode follow exactly the same formula.

============================================================
LANGUAGE
============================================================

Dialogue:

Natural Tamil.

Visual directions:

English.

Character dialogue must belong to the character,
not to a narrator.

============================================================
ANIMATION PREPARATION
============================================================

Every scene must contain:

- characters
- location
- action
- Tamil dialogue
- visual prompt
- sound effects
- music mood

The visual prompt should describe:

- character actions
- facial expressions
- body movement
- camera movement
- environment movement
- lighting
- cinematic composition
- character consistency

Do NOT include subtitles or on-screen text unless the story
specifically requires it.

============================================================
CURRENT UNIVERSE MEMORY
============================================================

{universe_json}

============================================================
TASK
============================================================

Create the NEXT EPISODE for this universe.

Because this is the beginning of the universe, you may
establish the first important characters and locations.

However, create only characters that are actually needed.

The story should leave room for future connected stories.

Return ONLY the requested JSON structure.
"""


    # ========================================================
    # JSON SCHEMA
    # ========================================================

    def get_schema(self):

        return {
            "type": "OBJECT",

            "properties": {

                "episode": {
                    "type": "OBJECT",

                    "properties": {

                        "title": {
                            "type": "STRING"
                        },

                        "summary": {
                            "type": "STRING"
                        },

                        "series_name": {
                            "type": "STRING"
                        },

                        "arc_name": {
                            "type": "STRING"
                        },

                        "episode_number": {
                            "type": "INTEGER"
                        },

                        "characters_used": {
                            "type": "ARRAY",
                            "items": {
                                "type": "STRING"
                            }
                        },

                        "locations_used": {
                            "type": "ARRAY",
                            "items": {
                                "type": "STRING"
                            }
                        },

                        "scenes": {
                            "type": "ARRAY",

                            "items": {

                                "type": "OBJECT",

                                "properties": {

                                    "scene_number": {
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

                                    "action": {
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

                                                "text_tamil": {
                                                    "type": "STRING"
                                                }

                                            },

                                            "required": [
                                                "character",
                                                "text_tamil"
                                            ]
                                        }
                                    },

                                    "visual_prompt": {
                                        "type": "STRING"
                                    },

                                    "sound_effects": {
                                        "type": "ARRAY",
                                        "items": {
                                            "type": "STRING"
                                        }
                                    },

                                    "music_mood": {
                                        "type": "STRING"
                                    }

                                },

                                "required": [
                                    "scene_number",
                                    "location",
                                    "characters",
                                    "action",
                                    "dialogue",
                                    "visual_prompt",
                                    "sound_effects",
                                    "music_mood"
                                ]
                            }
                        }

                    },

                    "required": [
                        "title",
                        "summary",
                        "series_name",
                        "arc_name",
                        "episode_number",
                        "characters_used",
                        "locations_used",
                        "scenes"
                    ]
                },

                "new_characters": {
                    "type": "ARRAY",

                    "items": {

                        "type": "OBJECT",

                        "properties": {

                            "name": {
                                "type": "STRING"
                            },

                            "type": {
                                "type": "STRING"
                            },

                            "appearance": {
                                "type": "OBJECT",

                                "properties": {

                                    "age": {
                                        "type": "STRING"
                                    },

                                    "species": {
                                        "type": "STRING"
                                    },

                                    "physical_description": {
                                        "type": "STRING"
                                    },

                                    "clothing": {
                                        "type": "STRING"
                                    },

                                    "visual_identity": {
                                        "type": "STRING"
                                    }

                                },

                                "required": [
                                    "age",
                                    "species",
                                    "physical_description",
                                    "clothing",
                                    "visual_identity"
                                ]
                            },

                            "personality": {
                                "type": "ARRAY",

                                "items": {
                                    "type": "STRING"
                                }
                            },

                            "voice": {
                                "type": "OBJECT",

                                "properties": {

                                    "language": {
                                        "type": "STRING"
                                    },

                                    "style": {
                                        "type": "STRING"
                                    }

                                },

                                "required": [
                                    "language",
                                    "style"
                                ]
                            },

                            "abilities": {
                                "type": "ARRAY",

                                "items": {
                                    "type": "STRING"
                                }
                            },

                            "story_role": {
                                "type": "STRING"
                            }

                        },

                        "required": [
                            "name",
                            "type",
                            "appearance",
                            "personality",
                            "voice",
                            "abilities",
                            "story_role"
                        ]
                    }
                },

                "new_locations": {
                    "type": "ARRAY",

                    "items": {

                        "type": "OBJECT",

                        "properties": {

                            "name": {
                                "type": "STRING"
                            },

                            "description": {
                                "type": "STRING"
                            },

                            "visual_identity": {
                                "type": "STRING"
                            }

                        },

                        "required": [
                            "name",
                            "description",
                            "visual_identity"
                        ]
                    }
                },

                "new_mysteries": {
                    "type": "ARRAY",

                    "items": {

                        "type": "OBJECT",

                        "properties": {

                            "name": {
                                "type": "STRING"
                            },

                            "description": {
                                "type": "STRING"
                            },

                            "importance": {
                                "type": "STRING"
                            },

                            "status": {
                                "type": "STRING"
                            }

                        },

                        "required": [
                            "name",
                            "description",
                            "importance",
                            "status"
                        ]
                    }
                },

                "new_threads": {
                    "type": "ARRAY",

                    "items": {

                        "type": "OBJECT",

                        "properties": {

                            "description": {
                                "type": "STRING"
                            },

                            "future_potential": {
                                "type": "STRING"
                            }

                        },

                        "required": [
                            "description",
                            "future_potential"
                        ]
                    }
                },

                "foreshadowing": {
                    "type": "ARRAY",

                    "items": {

                        "type": "OBJECT",

                        "properties": {

                            "clue": {
                                "type": "STRING"
                            },

                            "possible_future_connection": {
                                "type": "STRING"
                            }

                        },

                        "required": [
                            "clue",
                            "possible_future_connection"
                        ]
                    }
                }

            },

            "required": [
                "episode",
                "new_characters",
                "new_locations",
                "new_mysteries",
                "new_threads",
                "foreshadowing"
            ]
        }


    # ========================================================
    # GENERATE EPISODE
    # ========================================================

    def generate_episode(self):

        universe = self.load_universe()

        prompt = self.build_prompt(
            universe
        )

        schema = self.get_schema()

        print()
        print("🧠 Gemini Story Director")
        print("----------------------------------------")
        print(f"Model: {MODEL_NAME}")
        print(f"Memory: {MEMORY_FILE}")
        print()
        print("Generating next episode...")
        print()

        try:

            response = self.client.models.generate_content(

                model=MODEL_NAME,

                contents=prompt,

                config=types.GenerateContentConfig(

                    response_mime_type="application/json",

                    response_schema=schema,

                    temperature=1.0,

                    max_output_tokens=12000
                )
            )

        except Exception as error:

            raise RuntimeError(
                f"Gemini API request failed:\n{error}"
            )

        if not response.text:

            raise RuntimeError(
                "Gemini returned an empty response."
            )

        try:

            result = json.loads(
                response.text
            )

        except json.JSONDecodeError as error:

            raise RuntimeError(
                f"Gemini returned invalid JSON:\n{error}"
            )

        self.validate_result(result)

        return result


    # ========================================================
    # BASIC APPLICATION VALIDATION
    # ========================================================

    def validate_result(self, result):

        required_top_level = [
            "episode",
            "new_characters",
            "new_locations",
            "new_mysteries",
            "new_threads",
            "foreshadowing"
        ]

        for field in required_top_level:

            if field not in result:

                raise RuntimeError(
                    f"Missing required field: {field}"
                )

        episode = result["episode"]

        required_episode_fields = [
            "title",
            "summary",
            "series_name",
            "arc_name",
            "episode_number",
            "characters_used",
            "locations_used",
            "scenes"
        ]

        for field in required_episode_fields:

            if field not in episode:

                raise RuntimeError(
                    f"Missing episode field: {field}"
                )

        if not episode["scenes"]:

            raise RuntimeError(
                "Gemini generated zero scenes."
            )

        for scene in episode["scenes"]:

            if not scene.get("dialogue"):

                raise RuntimeError(
                    f"Scene {scene.get('scene_number')} "
                    "has no dialogue."
                )

        print("✅ Application validation passed.")


    # ========================================================
    # SAVE GENERATED EPISODE
    # ========================================================

    def save_episode(self, result):

        OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

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

        print(
            f"💾 Episode saved to:\n"
            f"{EPISODE_OUTPUT_FILE}"
        )


# ============================================================
# MAIN TEST
# ============================================================

def main():

    print()
    print("============================================")
    print("🌌 TAMIL ANIMATED UNIVERSE")
    print("🧠 GEMINI STORY DIRECTOR")
    print("============================================")

    director = StoryDirector()

    result = director.generate_episode()

    director.save_episode(
        result
    )

    episode = result["episode"]

    print()
    print("============================================")
    print("✅ EPISODE GENERATED")
    print("============================================")
    print()

    print(
        f"Title: {episode['title']}"
    )

    print(
        f"Series: {episode['series_name']}"
    )

    print(
        f"Arc: {episode['arc_name']}"
    )

    print(
        f"Scenes: {len(episode['scenes'])}"
    )

    print(
        f"New characters: "
        f"{len(result['new_characters'])}"
    )

    print(
        f"New locations: "
        f"{len(result['new_locations'])}"
    )

    print(
        f"New mysteries: "
        f"{len(result['new_mysteries'])}"
    )

    print()
    print("============================================")
    print("🎉 GEMINI TEST COMPLETE")
    print("============================================")


if __name__ == "__main__":
    main()
