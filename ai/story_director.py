import os
import json
from pathlib import Path

from google import genai
from google.genai import types


# ============================================================
# GEMINI STORY DIRECTOR
# ============================================================

MODEL_NAME = "gemini-2.5-flash"

BASE_DIR = Path(__file__).resolve().parent.parent
MEMORY_FILE = BASE_DIR / "universe" / "universe_memory.json"


class StoryDirector:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not available."
            )

        self.client = genai.Client(
            api_key=api_key
        )

    # --------------------------------------------------------
    # LOAD UNIVERSE
    # --------------------------------------------------------

    def load_universe(self):

        if not MEMORY_FILE.exists():
            raise FileNotFoundError(
                f"Universe memory not found: {MEMORY_FILE}"
            )

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    # --------------------------------------------------------
    # BUILD STORY PROMPT
    # --------------------------------------------------------

    def build_prompt(self, universe):

        universe_json = json.dumps(
            universe,
            ensure_ascii=False,
            indent=2
        )

        prompt = f"""
You are the Story Director of a long-running
Tamil animated shared universe.

This is NOT a collection of unrelated stories.

Every episode belongs to a connected universe.

Your responsibilities:

1. Create entertaining Tamil children's stories.
2. Maintain continuity with previous episodes.
3. Reuse existing characters when appropriate.
4. Create new characters only when the story needs them.
5. Never randomly change an established character.
6. Connect new stories to previous events when appropriate.
7. Maintain character relationships.
8. Maintain the timeline.
9. Continue unresolved mysteries when appropriate.
10. Plant meaningful clues that may become important later.
11. Allow completely new story arcs and series.
12. Allow previous characters to return naturally.
13. Make returning characters relevant to the story.
14. Develop characters over time.
15. Create emotional, funny, adventurous and mysterious moments.
16. Keep the content appropriate for children.
17. Write dialogue in natural Tamil.
18. Write visual directions in English so the animation system
    can understand them.

IMPORTANT CONTINUITY RULE:

Before creating a new character, inspect the existing characters.

If an existing character can naturally fulfill the role,
reuse that character.

Only create a new character when necessary.

IMPORTANT CHARACTER RULE:

Once a character is established, preserve their core:

- appearance
- age
- species
- personality
- important relationships
- abilities
- identity

Changes are allowed only when the story explains them.

IMPORTANT SHARED UNIVERSE RULE:

A returning character must have a logical reason to return.

Do not insert old characters merely for a cameo.

IMPORTANT MYSTERY RULE:

Some mysteries may remain unresolved for many episodes.

Do not resolve every mystery immediately.

IMPORTANT FORESHADOWING RULE:

You may introduce small clues that become meaningful
many episodes later.

The audience should be able to understand the current episode
even when deeper universe mysteries are unresolved.

CURRENT UNIVERSE MEMORY:

{universe_json}

Create the next episode for this universe.

The episode should feel like part of a much larger animated
universe rather than a standalone story.
"""

        return prompt

    # --------------------------------------------------------
    # RESPONSE SCHEMA
    # --------------------------------------------------------

    def get_response_schema(self):

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

                        "series_id": {
                            "type": "STRING"
                        },

                        "arc_id": {
                            "type": "STRING"
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

                                                "language": {
                                                    "type": "STRING"
                                                },

                                                "text": {
                                                    "type": "STRING"
                                                }

                                            },

                                            "required": [
                                                "character",
                                                "language",
                                                "text"
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
                        "series_id",
                        "arc_id",
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
                "new_mysteries",
                "new_locations",
                "new_threads",
                "foreshadowing"
            ]
        }

    # --------------------------------------------------------
    # GENERATE EPISODE
    # --------------------------------------------------------

    def generate_episode(self):

        universe = self.load_universe()

        prompt = self.build_prompt(
            universe
        )

        schema = self.get_response_schema()

        print("🧠 Asking Gemini to create the next episode...")

        response = self.client.models.generate_content(

            model=MODEL_NAME,

            contents=prompt,

            config=types.GenerateContentConfig(

                response_mime_type="application/json",

                response_schema=schema
            )
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
                f"Gemini returned invalid JSON: {error}"
            )

        print("✅ Gemini generated the episode.")

        return result


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("========================================")
    print("🧠 GEMINI STORY DIRECTOR TEST")
    print("========================================")
    print()

    director = StoryDirector()

    result = director.generate_episode()

    print()
    print("========================================")
    print("📖 GENERATED EPISODE")
    print("========================================")
    print()

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        )
    )
