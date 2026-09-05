from datetime import datetime
import os

from app.story_generator import generate_story
from app.image_generator import generate_image
from app.video_generator import animate_image, combine_videos


def build_motion_prompt(scene):
    return (
        "Animate this exact scene from the input image. "
        "The input image is the visual source of truth. "
        "Preserve every character exactly as shown, including identity, "
        "species, face, eyes, hair, clothing, colors, body shape, size, "
        "and number of characters. "
        "Do not add new characters. "
        "Do not remove characters. "
        "Do not replace one character with another. "
        "Do not transform characters into different animals or people. "
        "Keep the original environment, objects, and composition consistent. "
        "Create natural continuous movement based on the action described "
        "in the scene. "
        "Characters should use believable body, head, eye, facial, arm, "
        "leg, wing, or tail movement when appropriate for their appearance "
        "and action. "
        "Animate environmental elements that are already visible, such as "
        "leaves gently moving in the breeze, grass softly swaying, water "
        "naturally flowing, clouds slowly moving, fireflies glowing, or "
        "birds and butterflies flying, but only when those elements are "
        "already present. "
        "Use subtle cinematic camera movement such as a gentle tracking "
        "shot or slow push-in while keeping the main characters clearly "
        "visible. "
        "Natural continuous motion, smooth character animation, "
        "3D children's animated movie style, colorful, cute, "
        "family friendly, no text. "
        f"Scene description: {scene['visual_prompt']}"
    )


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
    # STEP 2: TEST WITH FIRST 2 SCENES ONLY
    # ============================================================

    print("\n🎨 Starting image generation for test scenes...")

    generated_images = []
    generated_videos = []

    # TEST ONLY 2 SCENES
    test_scenes = story["scenes"][:2]

    for index, scene in enumerate(test_scenes, start=1):

        scene_number = f"{index:02d}"

        output_path = f"scene_{scene_number}.png"
        video_path = f"scene_{scene_number}_animated.mp4"

        print("\n" + "-" * 60)
        print(f"🎨 Generating image for Scene {index}/2")
        print("-" * 60)

        print(f"📝 Prompt: {scene['visual_prompt']}")

        # --------------------------------------------------------
        # Generate image
        # --------------------------------------------------------

        image_path, image_url = generate_image(
            scene["visual_prompt"],
            output_path
        )
        

        # --------------------------------------------------------
        # Verify image
        # --------------------------------------------------------

        if not os.path.exists(image_path):

            raise RuntimeError(
                f"❌ Image was not created: {image_path}"
            )

        file_size = os.path.getsize(image_path)

        print("✅ IMAGE GENERATION SUCCESSFUL")
        print(f"🖼️ Image saved: {image_path}")
        print(f"📦 File size: {file_size} bytes")

        generated_images.append(image_path)

        # --------------------------------------------------------
        # Generate real AI animation
        # --------------------------------------------------------

        print(f"\n🎬 Starting AI animation for Scene {index}/2...")

        motion_prompt = build_motion_prompt(scene)

        print(f"🎞️ Motion prompt: {motion_prompt}")

        animate_image(
            image_url,
            motion_prompt,
            video_path
        )
        

        # --------------------------------------------------------
        # Verify video
        # --------------------------------------------------------

        if not os.path.exists(video_path):

            raise RuntimeError(
                f"❌ Animation video was not created: {video_path}"
            )

        video_size = os.path.getsize(video_path)

        print("✅ AI ANIMATION SUCCESSFUL")
        print(f"🎬 Video saved: {video_path}")
        print(f"📦 Video size: {video_size} bytes")
        generated_videos.append(video_path)

        

    # ============================================================
    # STEP 3: TEST SUMMARY
    # ============================================================

    print("\n" + "=" * 60)
    print("📊 TEST GENERATION SUMMARY")
    print("=" * 60)

    print("✅ Expected images : 2")
    print(f"✅ Generated images: {len(generated_images)}")

    for image in generated_images:
        print(f"    🖼️ {image}")

    print("\n✅ Expected videos : 2")
    print(f"✅ Generated videos: {len(generated_videos)}")

    for video in generated_videos:
        print(f"    🎬 {video}")

    # ============================================================
    # STEP 4: FINAL VALIDATION
    # ============================================================

    if len(generated_images) != 2:

        raise RuntimeError(
            f"Expected 2 images but generated {len(generated_images)}"
        )

    if len(generated_videos) != 2:

        raise RuntimeError(
            f"Expected 2 videos but generated {len(generated_videos)}"
        )

    print("\n🎉 TEST SUCCESSFUL!")
    print("🎉 2 images generated successfully!")
    print("🎉 2 AI animated videos generated successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
