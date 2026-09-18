import os
import time
import requests


def generate_image(prompt, output_path):
    """
    Generate a vertical 9:16 children's animation scene
    using Pixazo Flux Schnell.
    """

    api_key = os.environ["PIXAZO_API_KEY"]

    url = "https://gateway.pixazo.ai/flux-1-schnell/v1/getData"

    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "Ocp-Apim-Subscription-Key": api_key,
    }

    # Vertical 9:16 image.
    # 576 x 1024 stays within the current free-tier
    # resolution guidance.
    data = {
        "prompt": prompt,

        # Flux Schnell supports up to 8 steps.
        # 4 is a good balance between speed and quality.
        "num_steps": 4,

        # Fixed seed improves reproducibility between runs.
        "seed": 12345,

        "width": 576,
        "height": 1024,
    }

    max_attempts = 3

    for attempt in range(1, max_attempts + 1):

        try:

            print(
                f"🖼️ Pixazo image attempt "
                f"{attempt}/{max_attempts}"
            )

            print(
                "📐 Image size: 576x1024 (9:16)"
            )

            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=(30, 240),
            )

            response.raise_for_status()

            result = response.json()

            # Make sure Pixazo returned an image URL.
            if "output" not in result:
                raise ValueError(
                    f"Pixazo response did not contain "
                    f"'output': {result}"
                )

            image_url = result["output"]

            if not image_url:
                raise ValueError(
                    "Pixazo returned an empty image URL."
                )

            print(
                "✅ Pixazo image generation completed."
            )

            print(
                "⬇️ Downloading generated image..."
            )

            image_response = requests.get(
                image_url,
                timeout=(30, 180),
            )

            image_response.raise_for_status()

            # Make sure we actually received image data.
            if not image_response.content:
                raise ValueError(
                    "Downloaded image is empty."
                )

            with open(
                output_path,
                "wb"
            ) as image_file:

                image_file.write(
                    image_response.content
                )

            print(
                "✅ Image generated successfully"
            )

            print(
                f"💾 Saved: {output_path}"
            )

            return output_path, image_url

        except requests.exceptions.RequestException as error:

            print(
                f"⚠️ Pixazo attempt "
                f"{attempt} failed: {error}"
            )

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

        except (ValueError, KeyError) as error:

            print(
                f"⚠️ Pixazo response error "
                f"on attempt {attempt}: {error}"
            )

            if attempt == max_attempts:

                raise RuntimeError(
                    "Pixazo returned an invalid response "
                    "after 3 attempts."
                ) from error

            wait_seconds = attempt * 20

            print(
                f"⏳ Waiting {wait_seconds} seconds "
                "before retrying..."
            )

            time.sleep(wait_seconds)
