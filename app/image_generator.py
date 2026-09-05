import os
import requests


def generate_image(prompt, output_path):
    api_key = os.environ["PIXAZO_API_KEY"]

    url = "https://gateway.pixazo.ai/flux-1-schnell"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    data = {
        "prompt": prompt,
    }

    response = requests.post(
        url,
        headers=headers,
        json=data,
        timeout=120,
    )

    response.raise_for_status()

    result = response.json()

    image_url = result["output"]

    image_response = requests.get(
        image_url,
        timeout=120,
    )

    image_response.raise_for_status()

    with open(output_path, "wb") as image_file:
        image_file.write(image_response.content)

    return output_path
