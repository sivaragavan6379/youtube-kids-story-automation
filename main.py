from datetime import datetime
import os

from app.story_generator import generate_story
from app.image_generator import generate_image
from app.video_generator import animate_image


def main():
    print("=" * 60)
    print("🎬 YouTube Kids Story Automation")
    print("=" * 60)

    print(f"⏰ Started: {datetime.now()}")

    # --------------------------------------------------
    # STEP 1: Generate Story
    # --------------------------------------------------

    print("\n📖 Generating Tamil story...")

    story = generate_story()

    print(f"✅ Story: {story['title']}")
    print(f"✅ Scenes: {len(story['scenes'])}")

    # --------------------------------------------------
    # STEP 2: Generate All 10 Scene Images
    # --------------------------------------------------

    print("\n🎨 Starting image generation for all scenes...")

    generated_images = []

    for index, scene in enumerate(story["scenes"], start=1):

        scene_number = f"{index:02d}"
        output_path = f"scene_{scene_number}.png"

        print("\n" + "-" * 60)
        print(f"🎨 Generating image for Scene {index}/10")
        print("-" * 60)

        print(f"📝 Prompt: {scene['visual_prompt']}")

        image_path, image_url = generate_image(
    scene["visual_prompt"],
    output_path
)
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)

            print("✅ IMAGE GENERATION SUCCESSFUL")
            print(f"🖼️ Image saved: {output_path}")
            print(f"📦 File size: {file_size} bytes")

           generated_images.append(image_path)

# Test real AI animation on Scene 1 only
if index == 1:
    print("\n🎬 Starting AI animation test for Scene 1...")

    motion_prompt = (
        "The boy walks naturally along the village path while "
        "the monkey walks beside him. Their arms and legs move "
        "naturally as they walk. The boy looks happily at the monkey. "
        "The monkey moves playfully beside him. Trees and leaves "
        "gently move in the breeze. Small birds fly naturally in "
        "the background. The camera smoothly tracks backward "
        "with cinematic movement. Natural continuous motion, "
        "3D children's animated movie style, colorful, cute, "
        "family friendly, smooth character movement, no text."
    )

    animate_image(
        image_url,
        motion_prompt,
        "scene_01_animated.mp4"
    )

    print("✅ Scene 1 AI animation test completed!")

        else:
            raise RuntimeError(
                f"❌ Image was not created: {output_path}"
            )

    # --------------------------------------------------
    # STEP 3: Verify
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("📊 IMAGE GENERATION SUMMARY")
    print("=" * 60)

    print(f"✅ Expected images : 10")
    print(f"✅ Generated images: {len(generated_images)}")

    for image in generated_images:
        print(f"   🖼️ {image}")

    if len(generated_images) != 10:
        raise RuntimeError(
            f"Expected 10 images but generated {len(generated_images)}"
        )

    print("\n🎉 ALL 10 SCENE IMAGES GENERATED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    main()
