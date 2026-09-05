import os
import requests


def generate_story():
    api_key = os.environ["OPENROUTER_API_KEY"]

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "openrouter/free",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a professional children's story writer. "
                    "Write safe, educational and entertaining stories for children."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Create a very short Tamil children's story about "
                    "a little rabbit helping a bird. "
                    "Return only the story."
                ),
            },
        ],
    }

    response = requests.post(
        url,
        headers=headers,
        json=data,
        timeout=60,
    )

    response.raise_for_status()

    result = response.json()

    story = result["choices"][0]["message"]["content"]

    return story
