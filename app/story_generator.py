import os
import json
import requests
import time

from app.character_config import CHARACTER_BIBLE


def clean_json_response(content):
    """Clean common formatting problems from the model response."""

    if not content:
        raise ValueError(
            "Empty response received from OpenRouter."
        )

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
        raise ValueError(
            "No complete JSON object found in response."
        )

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
            raise ValueError(
                f"Missing field: {field}"
            )

    if not isinstance(story["characters"], list):
        raise ValueError(
            "characters must be a list."
        )

    if not isinstance(story["scenes"], list):
        raise ValueError(
            "scenes must be a list."
        )

    if len(story["scenes"]) != 10:
        raise ValueError(
            f"Expected 10 scenes, got {len(story['scenes'])}"
        )

    for index, scene in enumerate(
        story["scenes"],
        start=1
    ):

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

        if not isinstance(
            scene["narration"],
            str
        ):
            raise ValueError(
                f"Scene {index} narration must be text."
            )

        if not scene["narration"].strip():
            raise ValueError(
                f"Scene {index} has empty narration."
            )

        if not isinstance(
            scene["visual_prompt"],
            str
        ):
            raise ValueError(
                f"Scene {index} visual_prompt must be text."
            )

        if not scene["visual_prompt"].strip():
            raise ValueError(
                f"Scene {index} has empty visual_prompt."
            )

    return True


def generate_story():

    api_key = os.environ["OPENROUTER_API_KEY"]

    url = (
        "https://openrouter.ai/api/v1/chat/completions"
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    prompt = """
Create a safe, educational and entertaining Tamil
children's story.

CHARACTER DESIGN BIBLE:
{CHARACTER_BIBLE}

IMPORTANT CHARACTER CONSISTENCY RULE:

The character design described in the CHARACTER DESIGN
BIBLE is FIXED.

The image generator will generate every scene independently.

Therefore, EVERY scene's visual_prompt MUST repeat the
important character identity details instead of using vague
references such as:

- "same girl"
- "same character"
- "as before"
- "the girl from previous scene"
- "same puppy"

Each visual_prompt must contain enough character information
for the image generator to recreate the same characters
independently in every scene.

TARGET AGE:
5-10 years old.


STORY REQUIREMENTS:

Create EXACTLY 10 scenes.

The story must contain:

- A simple beginning
- A small problem or adventure
- Helpful and positive behavior
- A happy ending
- Simple Tamil suitable for children
- Family-friendly content
- Educational or positive message


MAIN CHARACTER:

Use Thamarai as the main character throughout the story.

Thamarai must remain the same character in every scene.

Use the puppy as her companion whenever appropriate.

Do not create unnecessary additional human characters.

Do not change Thamarai's appearance between scenes.

Do not change the puppy's appearance between scenes.


VISUAL PROMPT RULES:

Every visual_prompt MUST be written in English.

Every visual_prompt MUST explicitly describe the
characters when they appear in that scene.

Whenever Thamarai appears, include this complete identity
description:

"Thamarai, an 8-year-old Tamil village girl with warm
medium-brown skin, a round friendly child face, large
expressive dark-brown eyes, small black nose, straight
black hair in exactly two short braids, a red ribbon bow
on each braid, bright yellow short-sleeve shirt, blue
knee-length skirt, and small brown sandals."

Whenever the puppy appears, include this complete identity
description:

"one small cute white-and-brown puppy with white fur,
brown patches, floppy ears, round black eyes, small black
nose, and a small red collar."

Do NOT use vague character references such as:

- "the girl"
- "the child"
- "the puppy"
- "same girl"
- "same character"
- "same puppy"

Instead, use the complete identity description.

Every visual_prompt must also describe:

- Character action
- Facial expression
- Body pose
- Environment
- Important objects
- Camera shot
- Lighting
- Animation style


CAMERA RULES:

For scenes where Thamarai is speaking or her facial
expression is important:

- Use a medium shot, medium close-up, or close-up.
- Make her face large enough to clearly see.
- Face the camera or slightly toward the camera.
- Both eyes must be visible.
- Nose and mouth must be clearly visible.
- Do not use an extreme side profile.
- Do not place her very far away.
- Keep the face unobstructed.

These rules are important because the generated videos
may later be used for audio-driven lip synchronization.

For action scenes:

- A medium or wide shot may be used.
- Keep Thamarai clearly recognizable.
- Do not hide her face unnecessarily.
- Keep important characters visible.


VISUAL STYLE:

Every scene must use:

- High-quality 3D children's animated movie style
- Cute expressive characters
- Polished 3D character modeling
- Colorful Tamil village environment
- Bright natural colors
- Soft cinematic lighting
- Gentle depth of field
- Family-friendly appearance
- Consistent character proportions
- Consistent facial design
- Consistent clothing
- Consistent puppy design
- Cinematic composition
- Natural-looking environment
- No text
- No letters
- No subtitles
- No watermark
- No logo


CHARACTER CONSISTENCY RULES:

Thamarai must always remain:

- 8 years old
- Warm medium-brown skin
- Round friendly child face
- Large dark-brown eyes
- Small black nose
- Straight black hair
- Exactly two short braids
- One red ribbon bow on each braid
- Yellow short-sleeve shirt
- Blue knee-length skirt
- Small brown sandals
- Small child body proportions

The puppy must always remain:

- Small
- White and brown
- Same brown patch pattern
- Floppy ears
- Round black eyes
- Small black nose
- Red collar

Only these things may change:

- Pose
- Action
- Facial expression
- Location
- Camera position
- Environment
- Appropriate lighting

Do NOT redesign the characters.

Do NOT introduce a different girl.

Do NOT introduce a different puppy.


ANIMATION-FRIENDLY SCENE DESIGN:

Create scenes that can later be animated from the
generated image.

Use clear physical actions such as:

- Walking
- Running
- Waving
- Looking
- Smiling
- Talking
- Pointing
- Helping
- Sitting
- Standing
- Gently moving
- Playing

Avoid scenes where characters are completely hidden.

Avoid extremely complicated compositions.

Keep the main character clearly visible.


IMPORTANT LIP-SYNC RULE:

When the narration represents Thamarai speaking:

- Show Thamarai clearly.
- Use a medium close-up or close-up.
- Keep her face large.
- Keep her mouth visible.
- Keep both eyes visible.
- Face camera or slightly toward camera.
- Avoid profile shots.

Do not make every scene a close-up.
Use close-ups only when appropriate for speaking
or facial-expression scenes.


STORY FLOW:

Use a natural 10-scene progression:

Scene 1:
Introduce Thamarai and the environment.

Scene 2:
Introduce the puppy or the main situation.

Scene 3:
The small problem or adventure begins.

Scene 4:
Thamarai discovers the problem.

Scene 5:
Thamarai and the puppy try to help.

Scene 6:
The situation becomes more interesting.

Scene 7:
Thamarai finds a positive solution.

Scene 8:
The solution begins to work.

Scene 9:
The problem is resolved.

Scene 10:
Happy ending with a simple moral message.


IMPORTANT OUTPUT RULES:

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


IMPORTANT OUTPUT LIMIT RULES:

- Every JSON string must be complete.
- Never stop in the middle of a sentence.
- Keep Tamil narration concise.
- Keep each visual_prompt detailed but reasonably concise.
- Do not make visual_prompt unnecessarily long.
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
                    "You are an expert children's story "
                    "writer and strict JSON generator. "
                    "You must follow the supplied character "
                    "design bible exactly. "
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
                "message",
                {}
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

        except json.JSONDecodeError as error:

            print(
                f"⚠️ Attempt {attempt + 1} JSON error: "
                f"{error}"
            )

        except Exception as error:

            print(
                f"⚠️ Attempt {attempt + 1} failed: "
                f"{error}"
            )

        if attempt < 2:

            print("⏳ Retrying...")
            time.sleep(3)

    raise RuntimeError(
        "❌ Story generation failed after 3 attempts."
    )
