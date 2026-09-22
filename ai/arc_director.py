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

MEMORY_FILE = (
    BASE_DIR
    / "universe"
    / "universe_memory.json"
)

OUTPUT_DIR = BASE_DIR / "output"

ARC_OUTPUT_FILE = (
    OUTPUT_DIR
    / "generated_arc.json"
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

                universe = json.load(file)

        except json.JSONDecodeError as error:

            raise RuntimeError(
                "Invalid universe memory JSON:\n"
                f"{error}"
            )

        print(
            "✅ Universe memory loaded."
        )

        return universe


    # ========================================================
    # BUILD ARC PROMPT
    # ========================================================

    def build_prompt(self, universe):

        universe_json = json.dumps(
            universe,
            ensure_ascii=False,
            indent=2
        )

        prompt = f"""
You are the ARC DIRECTOR of a long-running
Tamil animated shared universe.

You are responsible for designing the NEXT COMPLETE
STORY ARC before individual episodes are written.

The universe should feel like a continuously evolving
animated world similar in structure to a long-running
adventure series.

Each episode should work independently for children,
but long-term viewers should discover connections
between:

- characters
- previous events
- locations
- artifacts
- mysteries
- relationships
- villains
- clues
- unresolved story threads
- future arcs

============================================================
AUTHORITATIVE UNIVERSE MEMORY
============================================================

The following JSON is the existing universe history.

Treat it as authoritative.

DO NOT randomly rewrite established facts.

{universe_json}

============================================================
MAIN OBJECTIVE
============================================================

Design the NEXT STORY ARC.

The arc must feel like a natural continuation
of the existing universe.

The arc should contain:

- central conflict
- arc goal
- main characters
- supporting characters
- new characters when genuinely necessary
- locations
- artifacts
- mysteries
- character development
- major events
- clues
- foreshadowing
- episode progression
- climax
- consequences
- future story hook

============================================================
CONTINUITY RULES
============================================================

These rules are extremely important.

1. Previous events remain true.

2. Existing characters must keep their established identity.

3. Existing characters may return naturally.

4. If an existing character returns, explain WHY
   they are involved in this arc.

5. Existing locations must preserve their identity,
   history and important characteristics.

6. Existing artifacts must preserve their identity,
   origin and established history.

7. Existing mysteries should continue when relevant.

8. Existing relationships should not randomly disappear.

9. Do not resurrect or remove characters without
   a story reason.

10. Do not randomly change established facts.

11. New characters may be introduced when the story
    genuinely requires them.

12. New characters should connect naturally to the
    existing world.

13. A new character can become important in later arcs.

14. Old characters may return as:

    - friends
    - helpers
    - mentors
    - rivals
    - witnesses
    - guides
    - temporary opponents
    - comic characters
    - important mystery connections

15. Returning characters should not be included
    just for fan service.

============================================================
SHARED UNIVERSE FEEL
============================================================

This is NOT a collection of unrelated stories.

The world must gradually grow.

A small event in one arc may become important
many arcs later.

A character introduced in this arc may return
in a future arc.

An artifact discovered in this arc may become
important much later.

A mystery introduced early may only be solved
after several arcs.

A location may have hidden history.

A minor character may later become important.

Create meaningful long-term connections.

============================================================
CHARACTER CREATION
============================================================

First inspect existing characters.

Reuse an existing character whenever that character
can naturally perform the required role.

Do NOT create unnecessary characters.

However, if the story genuinely needs a new character,
create one.

Every important new character MUST include:

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

The appearance must be visually specific enough
for future AI image/video generation.

Keep character identity stable.

For example, specify:

- approximate age
- skin tone
- face shape
- eyes
- hairstyle
- hair color
- clothing
- footwear
- accessories
- body proportions
- distinctive visual features

Do not unnecessarily change their appearance
between future stories.

============================================================
CHARACTER DEVELOPMENT
============================================================

Important characters should experience meaningful
development.

Development may include:

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

Not every character needs the same development.

Character development should naturally come from
the story.

============================================================
MYSTERY SYSTEM
============================================================

Use mysteries to create long-term curiosity.

Possible mystery types:

- unknown symbol
- mysterious artifact
- hidden location
- unknown character
- ancient story
- unexplained ability
- missing object
- strange event
- secret relationship
- forgotten history
- hidden organization
- unexplained phenomenon

Some mysteries should be solved during the arc.

Some mysteries may remain partially unanswered.

Some mysteries may continue into future arcs.

Do NOT create meaningless mysteries.

Every major mystery should have a potential
future purpose.

============================================================
FORESHADOWING
============================================================

Plant clues that may become important later.

Examples:

- strange symbol
- unusual object
- unexplained reaction
- mysterious visitor
- old photograph
- ancient inscription
- strange sound
- hidden room
- unknown name
- forgotten story
- unusual ability

Foreshadowing should have a possible future connection.

Do not explain every clue immediately.

============================================================
ARC STRUCTURE
============================================================

Create between 6 and 10 episodes.

Each episode MUST contain:

- episode_number
- title
- main_objective
- important_characters
- key_event
- character_development
- mystery_progression
- ending_hook

Episodes must connect to one another.

Do NOT create unrelated adventures.

The story should progressively build toward the climax.

============================================================
EPISODE PACING
============================================================

A possible structure:

Early episodes:

- introduce the new problem
- establish characters
- introduce mystery
- plant clues

Middle episodes:

- investigation
- discovery
- complications
- character challenges
- new clues
- partial revelations

Later episodes:

- major discoveries
- increasing danger
- important decisions
- mystery revelations
- emotional development

Final episodes:

- major confrontation
- climax
- consequences
- unresolved future mystery
- future arc hook

You may modify this structure if it creates
a better story.

============================================================
NEW CHARACTER CONNECTIONS
============================================================

When creating a new character, think about:

- Why do they exist in this world?
- How did they enter the story?
- Who do they know?
- What do they want?
- What do they know?
- What do they hide?
- Can they return later?
- What relationship could they develop?
- What future story could involve them?

============================================================
ARTIFACTS
============================================================

Important artifacts should have:

- name
- description
- importance
- origin

Artifacts can become recurring elements.

Do not randomly change their history.

============================================================
LOCATIONS
============================================================

Important locations should have:

- name
- description
- visual identity

The visual identity should help future AI video
generation maintain consistent locations.

============================================================
CHILD-FRIENDLY CONTENT
============================================================

The series is designed for children.

Use:

- adventure
- friendship
- curiosity
- humor
- emotion
- discovery
- mystery
- courage
- teamwork
- imagination

Danger can exist.

Avoid graphic violence.

Avoid disturbing horror.

Keep conflicts suitable for children.

============================================================
TAMIL CULTURAL SETTING
============================================================

Use Tamil language and Tamil cultural elements
naturally when appropriate.

Possible elements include:

- Tamil village environments
- festivals
- traditions
- food
- nature
- family relationships
- local occupations
- schools
- temples or culturally appropriate places
- rural landscapes
- Tamil names
- Tamil expressions

Do NOT insert cultural elements randomly.

They must belong naturally to the story.

============================================================
LONG-TERM STORY DESIGN
============================================================

Think beyond this arc.

This arc should leave behind useful story material.

Possible future material:

- unresolved mystery
- new villain
- new character
- hidden artifact
- unexplored location
- secret relationship
- unexplained event
- new ability
- future threat
- unknown organization
- historical clue

The future hook should create a natural reason
for another story arc.

============================================================
IMPORTANT
============================================================

Do NOT write complete episode scripts.

Do NOT write dialogue.

Do NOT write scene-by-scene production instructions.

We only need the ARC PLAN.

The Episode Director will later use this
arc plan to create individual episodes.

Return ONLY JSON matching the provided schema.
"""


        return prompt


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

                                    "relationships": {

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
                                    "relationships",
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
                        "mysteries",
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
    # GEMINI REQUEST
    # ========================================================

    def request_gemini(
        self,
        model_name,
        prompt,
        schema
    ):

        last_error = None

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

                                temperature=1.0,

                                max_output_tokens=16000
                            )
                        )
                    )
                )

                if response is None:

                    raise RuntimeError(
                        "Gemini returned no response."
                    )

                response_text = (
                    response.text
                )

                if not response_text:

                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                print(
                    f"✅ Response received "
                    f"from {model_name}"
                )

                return response_text

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

                retryable = (

                    "503" in error_text

                    or
                    "UNAVAILABLE"
                    in error_text

                    or
                    "429" in error_text

                    or
                    "RESOURCE_EXHAUSTED"
                    in error_text

                    or
                    "500" in error_text

                    or
                    "INTERNAL"
                    in error_text
                )

                if not retryable:

                    print(
                        "❌ Error is not retryable."
                    )

                    break

                if attempt < MAX_RETRIES:

                    wait_seconds = (
                        5 * (
                            2 ** (
                                attempt - 1
                            )
                        )
                    )

                    print(
                        f"⏳ Waiting "
                        f"{wait_seconds} seconds "
                        f"before retry..."
                    )

                    time.sleep(
                        wait_seconds
                    )

        raise RuntimeError(
            f"Model {model_name} failed "
            f"after {MAX_RETRIES} attempts.\n"
            f"Last error: {last_error}"
        )


    # ========================================================
    # GENERATE ARC
    # ========================================================

    def generate_arc(self):

        universe = (
            self.load_universe()
        )

        prompt = (
            self.build_prompt(
                universe
            )
        )

        schema = (
            self.get_schema()
        )

        print()
        print(
            "============================================"
        )
        print(
            "🌌 ARC DIRECTOR"
        )
        print(
            "============================================"
        )
        print()

        print(
            "🧠 Designing the next story arc..."
        )

        print()

        models_to_try = [

            PRIMARY_MODEL,

            FALLBACK_MODEL
        ]

        response_text = None

        last_error = None

        for model_name in models_to_try:

            print()
            print(
                "--------------------------------------------"
            )

            print(
                f"🤖 Trying model: "
                f"{model_name}"
            )

            print(
                "--------------------------------------------"
            )

            try:

                response_text = (
                    self.request_gemini(

                        model_name=model_name,

                        prompt=prompt,

                        schema=schema
                    )
                )

                break

            except Exception as error:

                last_error = error

                print()

                print(
                    f"⚠️ Model "
                    f"{model_name} failed."
                )

                print(
                    f"Reason: {error}"
                )

                print()

                if model_name != FALLBACK_MODEL:

                    print(
                        "➡️ Switching to fallback model..."
                    )

                else:

                    print(
                        "❌ All Gemini models failed."
                    )

        if not response_text:

            raise RuntimeError(
                "Gemini ARC generation failed "
                "after all retries and fallback "
                "models.\n"
                f"Last error: {last_error}"
            )

        # ----------------------------------------------------
        # PARSE JSON
        # ----------------------------------------------------

        try:

            result = json.loads(
                response_text
            )

        except json.JSONDecodeError as error:

            # Sometimes an API may unexpectedly
            # return markdown fences.

            cleaned = (
                response_text
                .strip()
            )

            if cleaned.startswith(
                "```json"
            ):

                cleaned = (
                    cleaned[
                        7:
                    ]
                    .strip()
                )

                if cleaned.endswith(
                    "```"
                ):

                    cleaned = (
                        cleaned[
                            :-3
                        ]
                        .strip()
                    )

            elif cleaned.startswith(
                "```"
            ):

                cleaned = (
                    cleaned[
                        3:
                    ]
                    .strip()
                )

                if cleaned.endswith(
                    "```"
                ):

                    cleaned = (
                        cleaned[
                            :-3
                        ]
                        .strip()
                    )

            try:

                result = json.loads(
                    cleaned
                )

            except json.JSONDecodeError:

                raise RuntimeError(
                    "Gemini returned invalid JSON.\n"
                    f"JSON error: {error}\n\n"
                    f"Response:\n"
                    f"{response_text[:3000]}"
                )

        # ----------------------------------------------------
        # VALIDATE
        # ----------------------------------------------------

        self.validate_arc(
            result
        )

        return result


    # ========================================================
    # VALIDATE ARC
    # ========================================================

    def validate_arc(
        self,
        result
    ):

        if not isinstance(
            result,
            dict
        ):

            raise RuntimeError(
                "ARC response must be a JSON object."
            )

        if "arc" not in result:

            raise RuntimeError(
                "ARC response is missing 'arc'."
            )

        arc = result["arc"]

        if not isinstance(
            arc,
            dict
        ):

            raise RuntimeError(
                "'arc' must be a JSON object."
            )

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

            "mysteries",

            "episodes",

            "central_mysteries",

            "foreshadowing",

            "major_events",

            "arc_climax",

            "arc_consequences",

            "future_arc_hook"
        ]

        # ----------------------------------------------------
        # Required fields
        # ----------------------------------------------------

        for field in required_fields:

            if field not in arc:

                raise RuntimeError(
                    f"ARC missing field: "
                    f"{field}"
                )

        # ----------------------------------------------------
        # Episode validation
        # ----------------------------------------------------

        episodes = (
            arc["episodes"]
        )

        if not isinstance(
            episodes,
            list
        ):

            raise RuntimeError(
                "ARC episodes must be an array."
            )

        episode_count = (
            len(episodes)
        )

        if episode_count < 6:

            raise RuntimeError(
                "ARC must contain at least "
                "6 episodes."
            )

        if episode_count > 10:

            raise RuntimeError(
                "ARC cannot contain more than "
                "10 episodes."
            )

        # ----------------------------------------------------
        # Planned count
        # ----------------------------------------------------

        planned_count = (
            arc[
                "planned_episode_count"
            ]
        )

        if planned_count != episode_count:

            raise RuntimeError(
                "planned_episode_count does not "
                "match the actual number of episodes."
            )

        # ----------------------------------------------------
        # Episode numbering
        # ----------------------------------------------------

        expected_number = 1

        for episode in episodes:

            if not isinstance(
                episode,
                dict
            ):

                raise RuntimeError(
                    "Every episode must be an object."
                )

            number = (
                episode.get(
                    "episode_number"
                )
            )

            if number != expected_number:

                raise RuntimeError(
                    "Episode numbering is invalid. "
                    f"Expected {expected_number}, "
                    f"got {number}."
                )

            expected_number += 1

        # ----------------------------------------------------
        # New character validation
        # ----------------------------------------------------

        new_characters = (
            arc["new_characters"]
        )

        if not isinstance(
            new_characters,
            list
        ):

            raise RuntimeError(
                "new_characters must be an array."
            )

        for character in new_characters:

            if not isinstance(
                character,
                dict
            ):

                raise RuntimeError(
                    "Every new character must "
                    "be an object."
                )

            required_character_fields = [

                "name",

                "type",

                "appearance",

                "personality",

                "goal",

                "motivation",

                "strengths",

                "weaknesses",

                "abilities",

                "relationships",

                "voice_style",

                "story_role"
            ]

            for field in required_character_fields:

                if field not in character:

                    raise RuntimeError(
                        "New character "
                        f"'{character.get('name', 'unknown')}' "
                        f"is missing field: "
                        f"{field}"
                    )

        # ----------------------------------------------------
        # Basic arc text validation
        # ----------------------------------------------------

        if not str(
            arc["title"]
        ).strip():

            raise RuntimeError(
                "ARC title is empty."
            )

        if not str(
            arc["summary"]
        ).strip():

            raise RuntimeError(
                "ARC summary is empty."
            )

        if not str(
            arc["central_conflict"]
        ).strip():

            raise RuntimeError(
                "ARC central conflict is empty."
            )

        if not str(
            arc["future_arc_hook"]
        ).strip():

            raise RuntimeError(
                "ARC future hook is empty."
            )

        print()
        print(
            "✅ ARC validation passed."
        )

        print(
            f"📚 Episodes: "
            f"{episode_count}"
        )

        print(
            f"👤 New characters: "
            f"{len(new_characters)}"
        )

        print(
            f"❓ Mysteries: "
            f"{len(arc['mysteries'])}"
        )

        print(
            f"🔮 Foreshadowing clues: "
            f"{len(arc['foreshadowing'])}"
        )


    # ========================================================
    # SAVE ARC
    # ========================================================

    def save_arc(
        self,
        result
    ):

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
            "💾 ARC saved to:"
        )

        print(
            ARC_OUTPUT_FILE
        )


# ============================================================
# MAIN
# ============================================================

def main():

    director = ArcDirector()

    result = (
        director.generate_arc()
    )

    director.save_arc(
        result
    )

    arc = result["arc"]

    print()
    print(
        "============================================"
    )

    print(
        "🎬 ARC CREATED"
    )

    print(
        "============================================"
    )

    print()

    print(
        f"Title: "
        f"{arc['title']}"
    )

    print(
        f"Theme: "
        f"{arc['theme']}"
    )

    print(
        f"Episodes: "
        f"{len(arc['episodes'])}"
    )

    print(
        f"New characters: "
        f"{len(arc['new_characters'])}"
    )

    print(
        f"Mysteries: "
        f"{len(arc['mysteries'])}"
    )

    print(
        f"Foreshadowing clues: "
        f"{len(arc['foreshadowing'])}"
    )

    print()

    print(
        "Episode roadmap:"
    )

    for episode in arc["episodes"]:

        print(
            f"  EP "
            f"{episode['episode_number']}: "
            f"{episode['title']}"
        )

    print()

    print(
        "Future arc hook:"
    )

    print(
        arc["future_arc_hook"]
    )

    print()

    print(
        "============================================"
    )

    print(
        "✅ ARC DIRECTOR TEST COMPLETE"
    )

    print(
        "============================================"
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
