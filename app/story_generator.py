import os
import json
import requests
import time
from app.character_config import CHARACTER_BIBLE


def clean_json_response(content):
    """Clean common formatting problems from the model response."""

    if not content:
        raise ValueError("Empty response received from OpenRouter.")

    content = content.strip()

    # Remove markdown code fences if present
    if content.startswith("```"):
        content = content.replace("```json", "", 1)
        content = content.replace("```", "", 1)
        content = content.strip()

    # Find the JSON object if the model added extra text
    start = content.find("{")
    end = content.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError("No complete JSON object found in response.")

    return content[start:end + 1]


def validate_story(story):
    """Validate the generated story structure."""

    required_fields = [
        "title",
        "description",
        "moral",
        "characters",
        "scenes",
    ]

    for field in required_fields:
        if field not in story:
            raise ValueError(f"Missing field: {field}")

    if not isinstance(story["characters"], list):
        raise ValueError("characters must be a list.")

    if not isinstance(story["scenes"], list):
        raise ValueError("scenes must be a list.")

    if len(story["scenes"]) != 10:
        raise ValueError(
            f"Expected 10 scenes, got {len(story['scenes'])}"
        )

    for index, scene in enumerate(story["scenes"], start=1):

        required_scene_fields = [
            "scene",
            "narration",
            "visual_prompt",
        ]

        for field in required_scene_fields:
            if field not in scene:
                raise ValueError(
                    f"Scene {index} missing field: {field}"
                )

        if not scene["narration"].strip():
            raise ValueError(
                f"Scene {index} has empty narration."
            )

        if not scene["visual_prompt"].strip():
            raise ValueError(
                f"Scene {index} has empty visual_prompt."
            )

    return True


def generate_story():

    api_key = os.environ["OPENROUTER_API_KEY"]

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    prompt = """
Create a safe, educational and entertaining Tamil children's story.

CHARACTER DESIGN BIBLE:
{CHARACTER_BIBLE}

IMPORTANT:
The character design described in CHARACTER DESIGN BIBLE is FIXED.

The AI image generator will generate each scene independently.
Therefore, EVERY scene's visual_prompt MUST repeat the important
character identity details instead of saying things like:
- "same girl"
- "same character"
- "as before"
- "the girl from previous scene"

Each visual_prompt must contain enough character information for the
image generator to recreate the exact same characters independently.

Target age: 5-10 years old.

Create EXACTLY 10 scenes.

The story must contain:
- A simple beginning
- A small problem or adventure
- Helpful and positive behavior
- A happy ending
- Simple Tamil suitable for children

IMPORTANT STORY CHARACTER RULE:
Use Thamarai as the main character throughout the story.

Use the puppy as her companion whenever appropriate.

Do not create unnecessary additional human characters.
Do not change Thamarai's appearance between scenes.
Do not change the puppy's appearance between scenes.


VISUAL PROMPT RULES
===================

Every visual_prompt MUST be written in English.

Every visual_prompt MUST explicitly describe the characters
when they appear in that scene.

For Thamarai, include these identity details whenever she appears:

"Thamarai, an 8-year-old Tamil village girl with warm medium-brown
skin, a round friendly child face, large expressive dark-brown eyes,
small black nose, straight black hair in exactly two short braids,
a red ribbon bow on each braid, bright yellow short-sleeve shirt,
blue knee-length skirt, and small brown sandals."

For the puppy, include these identity details whenever it appears:

"one small cute white-and-brown puppy with white fur, brown patches,
floppy ears, round black eyes, small black nose, and a small red collar."

Do NOT use vague references such as:
- "the girl"
- "the child"
- "the puppy"
- "same girl"
- "same puppy"

Instead, use the complete identity description.

The visual_prompt must also describe:
- character action
- facial expression
- body pose
- environment
- important objects
- camera shot
- lighting
- animation style


CAMERA RULES
============

For scenes where Thamarai is speaking or her facial expression is
important:

- Use a medium shot, medium close-up, or close-up.
- Make her face large enough to clearly see.
- Face the camera or slightly toward the camera.
- Both eyes must be visible.
- Nose and mouth must be clearly visible.
- Do not use an extreme side profile.
- Do not place her very far away.

For action scenes:

- A medium or wide shot may be used.
- Keep Thamarai clearly recognizable.
- Do not hide her face unnecessarily.


VISUAL STYLE
============

Every scene must use:

- high-quality 3D children's animated movie style
- cute expressive characters
- polished 3D character modeling
- colorful Tamil village environment
- bright natural colors
- soft cinematic lighting
- gentle depth of field
- family-friendly appearance
- consistent character proportions
- consistent facial design
- consistent clothing
- consistent puppy design
- cinematic composition
- no text
- no letters
- no subtitles
- no watermark
- no logo


CHARACTER CONSISTENCY RULES
===========================

Thamarai must always remain:

- 8 years old
- warm medium-brown skin
- round friendly child face
- large dark-brown eyes
- straight black hair
- exactly two short braids
- one red ribbon bow on each braid
- yellow short-sleeve shirt
- blue knee-length skirt
- small brown sandals
- small child body proportions

The puppy must always remain:

- small
- white and brown
- same brown patch pattern
- floppy ears
- round black eyes
- small black nose
- red collar

Only these things may change:
- pose
- action
- facial expression
- location
- camera position
- environment
- lighting conditions appropriate to the scene

Do NOT redesign the characters.


IMPORTANT:
Return ONLY valid JSON.
Do NOT use markdown.
Do NOT use ```json.
Do NOT add any text before or after the JSON.

Use exactly this JSON structure:

{
  "title": "Tamil story title",
  "description": "Short Tamil description",
  "moral": "Tamil moral",
  "characters": [
    {
      "name": "Character name",
      "description": "Character appearance and personality"
    }
  ],
  "scenes": [
    {
      "scene": 1,
      "narration": "Tamil narration",
      "visual_prompt": "Detailed English visual prompt containing the complete character identity details required above"
    }
  ]
}

There must be exactly 10 scene objects.

IMPORTANT OUTPUT RULES:
- Every JSON string must be complete.
- Never stop in the middle of a sentence.
- Keep narration concise.
- Keep visual_prompt detailed but reasonably concise.
- Make the complete JSON fit within the response limit.
"""
    prompt = prompt.replace(
    "{CHARACTER_BIBLE}",
    CHARACTER_BIBLE
)

    data = {
        "model": "openrouter/free",

        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert children's story writer "
                    "and strict JSON generator. "
                    "Return only complete valid JSON."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],

        "temperature": 0.5,

        # Smaller output reduces the chance of truncation
        "max_tokens": 5000,
    }

    for attempt in range(3):

        try:

            print(
                f"🔄 Story generation attempt "
                f"{attempt + 1}/3..."
            )

            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=120,
            )

            response.raise_for_status()

            result = response.json()

            # Check OpenRouter response structure
            if "choices" not in result:
                raise ValueError(
                    f"OpenRouter returned no choices: {result}"
                )

            if not result["choices"]:
                raise ValueError(
                    "OpenRouter returned an empty choices list."
                )

            message = result["choices"][0].get(
                "message", {}
            )

            content = message.get("content")

            if not content:
                raise ValueError(
                    "OpenRouter returned empty message content."
                )

            # Clean response
            content = clean_json_response(content)

            # Parse JSON
            story = json.loads(content)

            # Validate structure
            validate_story(story)

            print("✅ Valid story JSON received.")

            return story

        except json.JSONDecodeError as e:

            print(
                f"⚠️ Attempt {attempt + 1} JSON error: {e}"
            )

        except Exception as e:

            print(
                f"⚠️ Attempt {attempt + 1} failed: {e}"
            )

        if attempt < 2:

            print("⏳ Retrying...")
            time.sleep(3)

    raise RuntimeError(
        "❌ Story generation failed after 3 attempts."
    )
