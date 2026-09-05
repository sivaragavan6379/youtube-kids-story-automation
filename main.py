from datetime import datetime
import os

from app.story_generator import generate_story
from app.image_generator import generate_image
from app.video_generator import animate_image


def build_motion_prompt(scene):
    """
    Create a scene-specific AI animation prompt.

    The original image is treated as the visual source of truth.
    Characters should remain consistent while the scene action
    is animated naturally.
    """

    visual_prompt = scene["visual_prompt"]

    motion_prompt = (
        "Animate this exact scene from the input image. "
        "The input image is the visual source of truth. "
        "Preserve every character exactly as shown, including "
        "identity, species, face, eyes, hair, clothing, colors, "
        "body shape, size, and number of characters. "
        "Do not add new characters. Do not remove characters. "
        "Do not replace one character with another. "
        "Do not transform characters into different animals or people. "
        "Keep the original environment, objects, and composition consistent. "

        "Create natural continuous movement based on the action "
        "described in the scene. Characters should use believable "
        "body, head, eye, facial, arm, leg, wing, or tail movement "
        "when appropriate for their appearance and action. "

        "Animate environmental elements that are already visible, "
        "such as leaves gently moving in the breeze, grass softly "
        "swaying, water naturally flowing, clouds slowly moving, "
        "fireflies glowing, or birds and butterflies flying, "
        "but only when those elements are already present. "

        "Use subtle cinematic camera movement such as a smooth "
        "tracking shot, gentle push-in, pull-back, or side movement. "
        "Keep the main characters clearly visible and avoid sudden "
        "camera movements. "

        "The animation should feel like a polished 3D children's "
        "animated movie scene: colorful, cute, expressive, "
        "family friendly, natural motion, smooth movement, "
        "consistent characters, no text, no subtitles. "

        f"Scene action and visual description: {visual_prompt}"
    )

    return motion_prompt


def main():
    print("=" * 60)
    print("🎬 YouTube Kids Story Automation")
    print("=" * 60)

    print(f"⏰ Started: {datetime.now()}")

    # ============================================================
    # STEP 1: Generate Story
    # ============================================================

    print("\n📖 Generating Tamil story...")

    story = generate_story()

    print(f"✅ Story: {story['title']}")
    print(f"✅ Scenes: {len(story['scenes'])}")

    # ============================================================
    # STEP 2: Generate Scene Images
    # ============================================================

    print("\n🎨 Starting image generation for all scenes...")

    generated_images = []

    for index, scene in enumerate(story["scenes"][:2], start=1):

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

            # ====================================================
            # STEP 3: AI ANIMATION FOR EVERY SCENE
            # ====================================================

            print(f"\n🎬 Starting AI animation for Scene {index}/10...")

            motion_prompt = build_motion_prompt(scene)

            print(f"🎞️ Motion prompt: {motion_prompt}")

            animated_output = f"scene_{scene_number}_animated.mp4"

            animate_image(
                image_url,
                motion_prompt,
                animated_output
            )

            if os.path.exists(animated_output):

                video_size = os.path.getsize(animated_output)

                print("✅ AI ANIMATION SUCCESSFUL")
                print(f"🎬 Video saved: {animated_output}")
                print(f"📦 Video size: {video_size} bytes")

            else:

                raise RuntimeError(
                    f"❌ Animation video was not created: "
                    f"{animated_output}"
                )

        else:

            raise RuntimeError(
                f"❌ Image was not created: {output_path}"
            )

    # ============================================================
    # STEP 4: Verify Images
    # ============================================================

    print("\n" + "=" * 60)
    print("📊 IMAGE GENERATION SUMMARY")
    print("=" * 60)

    print("✅ Expected images : 10")
    print(f"✅ Generated images: {len(generated_images)}")

    for image in generated_images:
        print(f"    🖼️ {image}")

    if len(generated_images) != 10:

        raise RuntimeError(
            f"Expected 10 images but generated "
            f"{len(generated_images)}"
        )

    # ============================================================
    # STEP 5: Verify Animations
    # ============================================================

    print("\n" + "=" * 60)
    print("🎬 AI ANIMATION SUMMARY")
    print("=" * 60)

    generated_videos = []

    for index in range(1, 11):

        video_file = f"scene_{index:02d}_animated.mp4"

        if os.path.exists(video_file):

            video_size = os.path.getsize(video_file)

            generated_videos.append(video_file)

            print(
                f"    🎬 {video_file} "
                f"({video_size} bytes)"
            )

        else:

            raise RuntimeError(
                f"Expected animation not found: {video_file}"
            )

    print(f"\n✅ Expected videos : 10")
    print(f"✅ Generated videos: {len(generated_videos)}")

    if len(generated_videos) != 10:

        raise RuntimeError(
            f"Expected 10 videos but generated "
            f"{len(generated_videos)}"
        )

    print("\n🎉 ALL 10 SCENE ANIMATIONS GENERATED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    main()
