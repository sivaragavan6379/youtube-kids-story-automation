import os
import time
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
        "width": 768,
        "height": 432,
    }

    max_attempts = 3

    for attempt in range(1, max_attempts + 1):
        try:
            print(
                f"🖼️ Pixazo image attempt "
                f"{attempt}/{max_attempts}"
            )

            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=(30, 240),
            )

            response.raise_for_status()

            result = response.json()
            image_url = result["output"]

            print("⬇️ Downloading generated image...")

            image_response = requests.get(
                image_url,
                timeout=(30, 180),
            )

            image_response.raise_for_status()

            with open(output_path, "wb") as image_file:
                image_file.write(image_response.content)

            print("✅ Image generated successfully")
            return output_path, image_url

        except requests.exceptions.RequestException as error:
            print(f"⚠️ Pixazo attempt {attempt} failed: {error}")

            if attempt == max_attempts:
                raise RuntimeError(
                    "Pixazo failed after 3 attempts. "
                    "The service may be temporarily busy."
                ) from error

            wait_seconds = attempt * 20
            print(
                f"⏳ Waiting {wait_seconds} seconds "
                "before retrying..."
            )
            time.sleep(wait_seconds)
