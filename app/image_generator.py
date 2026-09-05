import os
import requests


def generate_image(prompt, output_path):
    api_key = os.environ["PIXAZO_API_KEY"]

    url = "https://gateway.pixazo.ai/flux-1-schnell/v1/getData"

    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "Ocp-Apim-Subscription-Key": api_key,
    }

    data = {
        "prompt": prompt,
        "num_steps": 4,
        "width": 1024,
        "height": 576,
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

    return output_path, image_url
