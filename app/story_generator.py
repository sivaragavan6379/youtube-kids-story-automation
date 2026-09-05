import os
import json
import requests


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

Create exactly 10 scenes.

The story should have:
- A simple beginning
- A small problem or adventure
- Helpful and positive behavior
- A happy ending
- Simple Tamil suitable for children

IMPORTANT VISUAL STYLE:

All scenes must look like they belong to the SAME 3D animated
children's movie.

Use this visual style for EVERY visual_prompt:
- 3D animated children's movie style
- Cute and colorful characters
- Soft rounded cartoon features
- Expressive friendly faces
- Vibrant colors
- Warm cinematic lighting
- Beautiful child-friendly environments
- High-quality 3D animation
- Family-friendly
- No photorealism
- No realistic photography
- No scary or disturbing elements
- 16:9 landscape composition

CHARACTER CONSISTENCY:

The same character must look the same in every scene.

When describing a character, keep their:
- Name
- Age
- Appearance
- Hair/fur color
- Clothing
- Body shape
- Important visual features

consistent throughout all scenes.

Each visual_prompt must clearly describe the characters
and environment needed for that particular scene.

Return ONLY valid JSON.
Do not use markdown.
Do not add ```json or ```.

Use exactly this structure:

{
  "title": "Tamil story title",
  "description": "Short Tamil description",
  "moral": "Tamil moral of the story",
  "characters": [
    {
      "name": "Character name",
      "description": "Detailed consistent visual description"
    }
  ],
  "scenes": [
    {
      "scene_number": 1,
      "narration": "Tamil narration for this scene",
      "visual_prompt": "Detailed English 3D animated visual prompt for this scene"
    }
  ]
}

The scenes array MUST contain exactly 10 scenes.

Every visual_prompt MUST include the 3D animated
children's movie style and maintain character consistency.
"""

    data = {
        "model": "openrouter/free",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert children's story writer "
                    "and visual story director. "
                    "Create safe, colorful and consistent "
                    "Tamil children's animated stories."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.8,
    }

    response = requests.post(
        url,
        headers=headers,
        json=data,
        timeout=120,
    )

    response.raise_for_status()

    result = response.json()

    content = result["choices"][0]["message"]["content"].strip()

    if content.startswith("```"):
        content = content.replace("```json", "", 1)
        content = content.replace("```", "", 1)
        content = content.strip()

    story = json.loads(content)

    return story
