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
      "description": "Short character description"
    }
  ],
  "scenes": [
    {
      "scene_number": 1,
      "narration": "Tamil narration for this scene",
      "visual_prompt": "Detailed English description of the scene for an AI image generator"
    }
  ]
}

The scenes array MUST contain exactly 10 scenes.
"""

    data = {
        "model": "openrouter/free",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert children's story writer "
                    "who creates safe Tamil educational stories."
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

    # Remove markdown code fences if the model accidentally adds them
    if content.startswith("```"):
        content = content.replace("```json", "", 1)
        content = content.replace("```", "", 1)
        content = content.strip()

    story = json.loads(content)

    return story
