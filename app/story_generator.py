import os
import json
import requests
import time


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

Target age: 5-10 years old.

Create EXACTLY 10 scenes.

The story must contain:
- A simple beginning
- A small problem or adventure
- Helpful and positive behavior
- A happy ending
- Simple Tamil suitable for children

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
      "visual_prompt": "Detailed English visual prompt"
    }
  ]
}

There must be exactly 10 scene objects.

VISUAL STYLE:
- 3D children's animated movie style
- Cute expressive characters
- Bright colorful environment
- Soft cinematic lighting
- Consistent character appearance across all scenes
- Family friendly
- No text or letters inside generated images

IMPORTANT OUTPUT RULES:
- Every JSON string must be complete.
- Never stop in the middle of a sentence.
- Keep narration concise.
- Keep visual_prompt concise but detailed.
- Make the complete JSON fit within the response limit.
"""

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
