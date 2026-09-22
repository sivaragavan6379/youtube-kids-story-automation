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

ARC_OUTPUT_FILE = (
    OUTPUT_DIR / "generated_arc.json"
)


# ============================================================
# ARC DIRECTOR
# ============================================================

class ArcDirector:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY environment variable "
                "was not found."
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
                f"Universe memory not found:\n"
                f"{MEMORY_FILE}"
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
                f"Invalid universe memory JSON:\n{error}"
            )

    # ========================================================
    # BUILD ARC PROMPT
    # ========================================================

    def build_prompt(self, universe):

        universe_json = json.dumps(
            universe,
            ensure_ascii=False,
            indent=2
        )

        return f"""
You are the ARC DIRECTOR of a long-running Tamil
animated shared universe.

You are responsible for designing a complete story arc
before individual episodes are produced.

This universe should feel like a continuously evolving
animated world.

The audience should be able to enjoy each episode,
while long-term viewers discover connections between
episodes, characters, mysteries and previous events.

============================================================
UNIVERSE MEMORY
============================================================

{universe_json}

============================================================
YOUR RESPONSIBILITIES
============================================================

Design the NEXT STORY ARC.

The arc should contain:

- a central story problem
- main characters
- supporting characters
- possible new characters
- locations
- mysteries
- important objects/artifacts
- relationships
- character development
- major events
- clues
- foreshadowing
- episode progression
- an arc climax
- consequences
- a future story hook

============================================================
CHARACTER CREATION
============================================================

Do NOT create characters unnecessarily.

First inspect the existing universe characters.

If an existing character can naturally fill a role,
reuse that character.

Create a new character only when the story genuinely
needs one.

Every important new character must have:

- name
- type
- appearance
- personality
- goal
- motivation
- strengths
- weaknesses
- abilities
- relationships
- voice style
- story role

============================================================
CHARACTER DEVELOPMENT
============================================================

Important characters should change during the arc.

Possible development:

Beginning
    ↓
Problem
    ↓
Challenge
    ↓
Failure
    ↓
Learning
    ↓
Decision
    ↓
Growth
    ↓
Climax

Do not force every character to follow the same pattern.

============================================================
LONG-TERM CONTINUITY
============================================================

Previous universe events must remain valid.

If an existing mystery is relevant, continue it.

If an existing character returns, explain why.

If an old location returns, preserve its established identity.

If an artifact returns, preserve its established history.

Do not randomly rewrite established facts.

============================================================
MYSTERY DESIGN
============================================================

The arc may contain:

- one central mystery
- several smaller mysteries
- hidden clues
- misleading clues
- partial revelations
- unanswered questions

Not every mystery must be solved within this arc.

Some mysteries can continue into future arcs.

============================================================
FORESHADOWING
============================================================

Plant clues that can become important later.

A clue introduced early may be explained much later.

Examples:

- strange symbol
- mysterious artifact
- unknown person
- ancient story
- unexplained ability
- hidden location
- secret relationship
- unusual event

Foreshadowing must have a potential purpose.

============================================================
ARC STRUCTURE
============================================================

Create between 6 and 10 episodes.

Each episode should have:

- episode number
- title
- main objective
- important characters
- key event
- character development
- mystery progression
- ending hook

The episodes must build toward the arc climax.

Do NOT make every episode feel like an unrelated adventure.

============================================================
ARC PACING
============================================================

A possible structure is:

Early episodes:
Introduction + mystery

Middle episodes:
Investigation + complications

Later episodes:
Revelations + increasing danger

Final episodes:
Climax + consequences

But you may use a different structure if it produces
a stronger story.

============================================================
CHILD-FRIENDLY STORY
============================================================

Keep the universe appropriate for children.

Use:

- adventure
- friendship
- humor
- curiosity
- emotion
- discovery
- mystery
- courage

Danger can exist, but avoid graphic violence.

============================================================
TAMIL CULTURAL SETTING
============================================================

Stories should naturally use Tamil language and cultural
elements when appropriate.

Do not insert cultural elements randomly.

They should belong naturally to the world.

============================================================
IMPORTANT
============================================================

Do NOT write complete episode scripts yet.

We only want the ARC PLAN.

The Episode Director will later use this arc plan to
write individual episodes.

Return ONLY the requested JSON.
"""

    # ========================================================
    # RESPONSE SCHEMA
    # ========================================================

    def get_schema(self):

        return {
            "type": "OBJECT",

            "properties": {

                "arc": {

                    "type": "OBJECT",

                    "properties": {

                        "title": {
                            "type": "STRING"
                        },

                        "summary": {
                            "type": "STRING"
                        },

                        "theme": {
                            "type": "STRING"
                        },

                        "central_conflict": {
                            "type": "STRING"
                        },

                        "arc_goal": {
                            "type": "STRING"
                        },

                        "planned_episode_count": {
                            "type": "INTEGER"
                        },

                        "main_characters": {
                            "type": "ARRAY",

                            "items": {
                                "type": "STRING"
                            }
                        },

                        "supporting_characters": {
                            "type": "ARRAY",

                            "items": {
                                "type": "STRING"
                            }
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
                                        "type": "STRING"
                                    },

                                    "personality": {
                                        "type": "ARRAY",

                                        "items": {
                                            "type": "STRING"
                                        }
                                    },

                                    "goal": {
                                        "type": "STRING"
                                    },

                                    "motivation": {
                                        "type": "STRING"
                                    },

                                    "strengths": {
                                        "type": "ARRAY",

                                        "items": {
                                            "type": "STRING"
                                        }
                                    },

                                    "weaknesses": {
                                        "type": "ARRAY",

                                        "items": {
                                            "type": "STRING"
                                        }
                                    },

                                    "abilities": {
                                        "type": "ARRAY",

                                        "items": {
                                            "type": "STRING"
                                        }
                                    },

                                    "voice_style": {
                                        "type": "STRING"
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
                                    "goal",
                                    "motivation",
                                    "strengths",
                                    "weaknesses",
                                    "abilities",
                                    "voice_style",
                                    "story_role"
                                ]
                            }
                        },

                        "locations": {

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

                        "artifacts": {

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

                                    "origin": {
                                        "type": "STRING"
                                    }

                                },

                                "required": [
                                    "name",
                                    "description",
                                    "importance",
                                    "origin"
                                ]
                            }
                        },

                        "mysteries": {

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

                        "episodes": {

                            "type": "ARRAY",

                            "items": {

                                "type": "OBJECT",

                                "properties": {

                                    "episode_number": {
                                        "type": "INTEGER"
                                    },

                                    "title": {
                                        "type": "STRING"
                                    },

                                    "main_objective": {
                                        "type": "STRING"
                                    },

                                    "important_characters": {
                                        "type": "ARRAY",

                                        "items": {
                                            "type": "STRING"
                                        }
                                    },

                                    "key_event": {
                                        "type": "STRING"
                                    },

                                    "character_development": {
                                        "type": "STRING"
                                    },

                                    "mystery_progression": {
                                        "type": "STRING"
                                    },

                                    "ending_hook": {
                                        "type": "STRING"
                                    }

                                },

                                "required": [
                                    "episode_number",
                                    "title",
                                    "main_objective",
                                    "important_characters",
                                    "key_event",
                                    "character_development",
                                    "mystery_progression",
                                    "ending_hook"
                                ]
                            }
                        },

                        "central_mysteries": {

                            "type": "ARRAY",

                            "items": {
                                "type": "STRING"
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

                                    "introduced_episode": {
                                        "type": "INTEGER"
                                    },

                                    "possible_future_connection": {
                                        "type": "STRING"
                                    }

                                },

                                "required": [
                                    "clue",
                                    "introduced_episode",
                                    "possible_future_connection"
                                ]
                            }
                        },

                        "major_events": {

                            "type": "ARRAY",

                            "items": {

                                "type": "STRING"
                            }
                        },

                        "arc_climax": {
                            "type": "STRING"
                        },

                        "arc_consequences": {

                            "type": "ARRAY",

                            "items": {
                                "type": "STRING"
                            }
                        },

                        "future_arc_hook": {
                            "type": "STRING"
                        }

                    },

                    "required": [
                        "title",
                        "summary",
                        "theme",
                        "central_conflict",
                        "arc_goal",
                        "planned_episode_count",
                        "main_characters",
                        "supporting_characters",
                        "new_characters",
                        "locations",
                        "artifacts",
                        "episodes",
                        "central_mysteries",
                        "foreshadowing",
                        "major_events",
                        "arc_climax",
                        "arc_consequences",
                        "future_arc_hook"
                    ]
                }

            },

            "required": [
                "arc"
            ]
        }

    # ========================================================
    # GENERATE ARC
    # ========================================================

    def generate_arc(self):

        universe = self.load_universe()

        prompt = self.build_prompt(
            universe
        )

        schema = self.get_schema()

        print()
        print("============================================")
        print("🌌 ARC DIRECTOR")
        print("============================================")
        print()

        print("🧠 Designing the next story arc...")
        print()

        try:

            response = self.client.models.generate_content(

                model=MODEL_NAME,

                contents=prompt,

                config=types.GenerateContentConfig(

                    response_mime_type="application/json",

                    response_schema=schema,

                    temperature=1.0,

                    max_output_tokens=16000
                )
            )

        except Exception as error:

            raise RuntimeError(
                f"Gemini ARC generation failed:\n{error}"
            )

        if not response.text:

            raise RuntimeError(
                "Gemini returned an empty ARC response."
            )

        try:

            result = json.loads(
                response.text
            )

        except json.JSONDecodeError as error:

            raise RuntimeError(
                f"Invalid ARC JSON:\n{error}"
            )

        self.validate_arc(result)

        return result

    # ========================================================
    # VALIDATE ARC
    # ========================================================

    def validate_arc(self, result):

        if "arc" not in result:

            raise RuntimeError(
                "ARC response is missing 'arc'."
            )

        arc = result["arc"]

        required_fields = [
            "title",
            "summary",
            "theme",
            "central_conflict",
            "arc_goal",
            "planned_episode_count",
            "main_characters",
            "supporting_characters",
            "new_characters",
            "locations",
            "artifacts",
            "episodes",
            "central_mysteries",
            "foreshadowing",
            "major_events",
            "arc_climax",
            "arc_consequences",
            "future_arc_hook"
        ]

        for field in required_fields:

            if field not in arc:

                raise RuntimeError(
                    f"ARC missing field: {field}"
                )

        episode_count = len(
            arc["episodes"]
        )

        if episode_count < 6:

            raise RuntimeError(
                "ARC must contain at least 6 episodes."
            )

        if episode_count > 10:

            raise RuntimeError(
                "ARC cannot contain more than 10 episodes."
            )

        print("✅ ARC validation passed.")

    # ========================================================
    # SAVE ARC
    # ========================================================

    def save_arc(self, result):

        OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            ARC_OUTPUT_FILE,
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
            f"💾 ARC saved to:\n"
            f"{ARC_OUTPUT_FILE}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    director = ArcDirector()

    result = director.generate_arc()

    director.save_arc(
        result
    )

    arc = result["arc"]

    print()
    print("============================================")
    print("🎬 ARC CREATED")
    print("============================================")
    print()

    print(
        f"Title: {arc['title']}"
    )

    print(
        f"Theme: {arc['theme']}"
    )

    print(
        f"Episodes: {len(arc['episodes'])}"
    )

    print(
        f"New characters: "
        f"{len(arc['new_characters'])}"
    )

    print(
        f"Mysteries: "
        f"{len(arc['central_mysteries'])}"
    )

    print()

    print("Episode roadmap:")

    for episode in arc["episodes"]:

        print(
            f"  EP {episode['episode_number']}: "
            f"{episode['title']}"
        )

    print()

    print("============================================")
    print("✅ ARC DIRECTOR TEST COMPLETE")
    print("============================================")


if __name__ == "__main__":
    main()
