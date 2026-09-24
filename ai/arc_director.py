import os
import json
import time
from pathlib import Path

from google import genai
from google.genai import types


# ============================================================
# CONFIGURATION
# ============================================================

PRIMARY_MODEL = "gemini-3.8-flash"
FALLBACK_MODEL = "gemini-3.5-flash-lite"

# Gemini models are tried in this order for each API key.
GEMINI_MODELS = [
    PRIMARY_MODEL,
    FALLBACK_MODEL,
    "gemini-3.6-flash",
]

# Gemini 3.8 migration: do not send deprecated
# sampling parameters such as temperature/top_p/top_k.

# Maximum retries for a retryable error on one model/key combination.
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

        # Keep API keys in environment variables only.
        # Never print or store the actual key values in logs/files.
        configured_keys = [
            os.getenv("GEMINI_API_KEY"),
            os.getenv("GEMINI_API_KEY_2"),
        ]

        # Remove empty values and accidental duplicates.
        self.api_keys = list(
            dict.fromkeys(
                key.strip()
                for key in configured_keys
                if key and key.strip()
            )
        )

        if not self.api_keys:

            raise RuntimeError(
                "No Gemini API keys were found. "
                "Set GEMINI_API_KEY and/or GEMINI_API_KEY_2."
            )

        print(
            f"🔑 Gemini API keys available: "
            f"{len(self.api_keys)}"
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
- returning characters when relevant
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
RETURNING CHARACTER SYSTEM
============================================================

Before creating a new character, inspect the existing
characters in the AUTHORITATIVE UNIVERSE MEMORY.

Reuse an existing character whenever that character can
naturally participate in the new arc.

Every returning character MUST be listed in
"returning_characters".

For every returning character provide:

- name
- reason_for_return
- role_in_arc
- continuity_connection

The reason_for_return must explain why the character is
involved in the current arc.

The continuity_connection must identify the previous event,
relationship, mystery, artifact, location, or other
established story element that connects the character
to this arc.

IMPORTANT RULES:

1. A returning character MUST already exist in the
   AUTHORITATIVE UNIVERSE MEMORY.

2. Do NOT invent a returning character.

3. Do NOT list a new character as returning.

4. Do NOT include returning characters only for fan service.

5. If no existing character naturally needs to return,
   return an empty "returning_characters" array.

6. New characters belong in "new_characters".

7. Existing characters who return belong in
   "returning_characters".

8. Keep the established identity, appearance, history,
   relationships, and important facts of returning
   characters unchanged unless the story explicitly
   and naturally develops them.

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
OUTPUT SIZE RULES:

Keep the response detailed but compact.

Do not write excessively long descriptions.

For character appearance, use approximately 2-4 sentences.

For personality, use 5-8 concise traits.

For goals and motivations, use 1-2 sentences each.

For relationships, use concise descriptions.

For locations and artifacts, use approximately 2-3 sentences.

Episode descriptions should be concise but contain the important story progression.

Never repeat the same information in multiple fields.

The complete JSON must fit within the output limit.
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
                        "returning_characters": {

    "type": "ARRAY",

    "items": {

        "type": "OBJECT",

        "properties": {

            "name": {
                "type": "STRING"
            },

            "reason_for_return": {
                "type": "STRING"
            },

            "role_in_arc": {
                "type": "STRING"
            },

            "continuity_connection": {
                "type": "STRING"
            }
        },

        "required": [
            "name",
            "reason_for_return",
            "role_in_arc",
            "continuity_connection"
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
                        "returning_characters",
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
        schema,
        api_key,
        key_number
    ):

        last_error = None

        # A fresh client is created for the selected key.
        # This makes API-key fallback explicit and predictable.
        client = genai.Client(
            api_key=api_key
        )

        print(
            f"🔑 Using Gemini API key {key_number}"
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
                    client.models.generate_content(

                        model=model_name,

                        contents=prompt,

                        config=(
                            types.GenerateContentConfig(

                                response_mime_type=(
                                    "application/json"
                                ),

                                response_schema=schema,

                                max_output_tokens=32768
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
                    f"from {model_name} "
                    f"using API key {key_number}"
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
                    "UNAVAILABLE" in error_text
                    or
                    "429" in error_text
                    or
                    "RESOURCE_EXHAUSTED" in error_text
                    or
                    "500" in error_text
                    or
                    "INTERNAL" in error_text
                )

                if not retryable:

                    print(
                        "❌ Error is not retryable "
                        "for this model/key."
                    )

                    break

                if attempt < MAX_RETRIES:

                    # Exponential backoff for temporary Gemini
                    # service/capacity errors.
                    wait_seconds = (
                        8 * (
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
            f"with API key {key_number} "
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

        models_to_try = list(
            GEMINI_MODELS
        )

        response_text = None

        last_error = None

        # Try every configured API key with the model fallback chain.
        #
        # Key 1 -> primary model -> fallback model
        # Key 2 -> primary model -> fallback model

        for key_index, api_key in enumerate(
            self.api_keys,
            start=1
        ):

            for model_name in models_to_try:

                print()
                print(
                    "--------------------------------------------"
                )
                print(
                    f"🔑 API key {key_index}/"
                    f"{len(self.api_keys)}"
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

                            schema=schema,

                            api_key=api_key,

                            key_number=key_index
                        )
                    )

                    # Successful response.
                    break

                except Exception as error:

                    last_error = error

                    print()
                    print(
                        f"⚠️ Model "
                        f"{model_name} failed "
                        f"with API key {key_index}."
                    )

                    print(
                        f"Reason: {error}"
                    )

                    continue

            if response_text:

                break

            if key_index < len(self.api_keys):

                print()
                print(
                    f"➡️ Switching to Gemini API key "
                    f"{key_index + 1}..."
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
        # Returning character validation
        # ----------------------------------------------------

        returning_characters = (
            arc["returning_characters"]
        )

        if not isinstance(
            returning_characters,
            list
        ):

            raise RuntimeError(
                "returning_characters must be an array."
            )

        # Load the authoritative character registry.
        # A returning character must already exist there.
        universe = self.load_universe()

        stored_characters = universe.get(
            "characters",
            {}
        )

        if not isinstance(
            stored_characters,
            dict
        ):

            stored_characters = {}

        known_character_names = set()

        for character_id, character_data in stored_characters.items():

            if not isinstance(
                character_data,
                dict
            ):

                continue

            known_character_names.add(
                str(character_id).strip().lower()
            )

            character_name = character_data.get(
                "name"
            )

            if character_name:

                known_character_names.add(
                    str(character_name).strip().lower()
                )

        for character in returning_characters:

            if not isinstance(
                character,
                dict
            ):

                raise RuntimeError(
                    "Every returning character must "
                    "be an object."
                )

            required_returning_fields = [
                "name",
                "reason_for_return",
                "role_in_arc",
                "continuity_connection"
            ]

            for field in required_returning_fields:

                if field not in character:

                    raise RuntimeError(
                        "Returning character "
                        f"'{character.get('name', 'unknown')}' "
                        f"is missing field: {field}"
                    )

                if not str(
                    character[field]
                ).strip():

                    raise RuntimeError(
                        "Returning character "
                        f"'{character.get('name', 'unknown')}' "
                        f"has an empty field: {field}"
                    )

            returning_name = str(
                character["name"]
            ).strip().lower()

            if returning_name not in known_character_names:

                raise RuntimeError(
                    "Returning character "
                    f"'{character['name']}' does not exist "
                    "in the authoritative universe memory."
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
