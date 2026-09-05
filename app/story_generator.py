import os
import json
import requests
import time


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
- No text or letters inside the generated images

Make the visual_prompt detailed enough for an AI image generator.
"""

    data = {
        "model": "openrouter/free",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert children's story writer and "
                    "structured JSON generator. Always return valid JSON."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.7,
        "max_tokens": 6000,
    }

    for attempt in range(3):
        try:
            print(f"🔄 Story generation attempt {attempt + 1}/3...")

            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=120,
            )

            response.raise_for_status()

            result = response.json()

            content = result["choices"][0]["message"]["content"].strip()

            # Remove accidental markdown fences
            if content.startswith("```"):
                content = content.replace("```json", "", 1)
                content = content.replace("```", "", 1)
                content = content.strip()

            story = json.loads(content)

            # Validate required fields
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

            # Validate exactly 10 scenes
            if len(story["scenes"]) != 10:
                raise ValueError(
                    f"Expected 10 scenes, got {len(story['scenes'])}"
                )

            print("✅ Valid story JSON received.")
            return story

        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed: {e}")

            if attempt < 2:
                print("⏳ Retrying...")
                time.sleep(3)
            else:
                raise RuntimeError(
                    "❌ Story generation failed after 3 attempts."
                ) from e
