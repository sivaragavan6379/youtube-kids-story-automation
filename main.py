from datetime import datetime
import os

from app.story_generator import generate_story
from app.image_generator import generate_image
from app.video_generator import animate_image
from app.tts_generator import generate_tamil_voice


def build_motion_prompt(scene):
    """
    Create a strong motion prompt for Pixazo LTX.

    The input image is the source of truth.
    Characters and environment must remain consistent.
    """

    return (
        "Animate this exact scene from the input image. "

        "The input image is the visual source of truth. "

        "Preserve every character exactly as shown, including "
        "identity, species, face, eyes, hair, clothing, colors, "
        "body shape, body proportions, size, and number of characters. "

        "Do not add new characters. "
        "Do not remove characters. "
        "Do not replace one character with another. "
        "Do not transform characters into different animals or people. "

        "Keep the original environment, objects, colors, "
        "and composition consistent. "

        "Create natural continuous movement based on the "
        "action described in the scene. "

        "Characters should have believable body movement, "
        "head movement, eye movement, facial movement, "
        "arm movement, leg movement, wing movement, or "
        "tail movement when appropriate. "

        "For speaking characters, use subtle natural facial "
        "movement and mouth movement while keeping the face "
        "clearly recognizable. "

        "Animate environmental elements that are already visible, "
        "such as leaves gently moving in the breeze, grass softly "
        "swaying, water naturally flowing, clouds slowly moving, "
        "or birds and butterflies flying. "

        "Only animate environmental elements that are already "
        "present in the input image. "

        "Use subtle cinematic camera movement such as a gentle "
        "tracking shot, slow push-in, or slight camera movement "
        "while keeping the main character clearly visible. "

        "Do not drastically change the camera angle. "

        "Do not change the character design. "

        "Do not change the environment. "

        "Natural continuous motion, smooth character animation, "
        "high-quality 3D children's animated movie style, "
        "colorful, cute, family friendly, no text. "

        f"Scene description: {scene['visual_prompt']}"
    )


def main():

    print("=" * 60)
    print("🎬 YouTube Kids Story Automation")
    print("=" * 60)

    print(
        f"⏰ Started: {datetime.now()}"
    )

    # ============================================================
    # STEP 1: GENERATE STORY
    # ============================================================

    print()
    print("📖 Generating Tamil story...")

    story = generate_story()

    print(
        f"✅ Story: {story['title']}"
    )

    print(
        f"✅ Total scenes in story: "
        f"{len(story['scenes'])}"
    )

    # ============================================================
    # STEP 2: TEST ONLY ONE SCENE
    # ============================================================

    print()
    print("=" * 60)
    print("🧪 ONE-SCENE QUALITY TEST")
    print("=" * 60)

    # IMPORTANT:
    # Generate ONLY Scene 1 for this test.
    test_scenes = story["scenes"][:1]

    generated_images = []
    generated_videos = []
    generated_audios = []

    # ============================================================
    # PROCESS SCENE 1
    # ============================================================

    for index, scene in enumerate(
        test_scenes,
        start=1
    ):

        scene_number = f"{index:02d}"

        output_path = (
            f"scene_{scene_number}.png"
        )

        video_path = (
            f"scene_{scene_number}_animated.mp4"
        )

        audio_path = (
            f"scene_{scene_number}.mp3"
        )

        print()
        print("-" * 60)
        print(
            f"🎬 Processing TEST Scene "
            f"{index}/1"
        )
        print("-" * 60)

        print()
        print("📝 Visual prompt:")
        print(scene["visual_prompt"])

        # ========================================================
        # GENERATE IMAGE
        # ========================================================

        print()
        print("🖼️ Generating vertical scene image...")

        image_path, image_url = generate_image(
            scene["visual_prompt"],
            output_path
        )

        if not os.path.exists(
            image_path
        ):

            raise RuntimeError(
                f"❌ Image was not created: "
                f"{image_path}"
            )

        image_size = os.path.getsize(
            image_path
        )

        if image_size == 0:

            raise RuntimeError(
                f"❌ Generated image is empty: "
                f"{image_path}"
            )

        print()
        print(
            "✅ IMAGE GENERATION SUCCESSFUL"
        )

        print(
            f"🖼️ Image: {image_path}"
        )

        print(
            f"📦 Image size: "
            f"{image_size} bytes"
        )

        generated_images.append(
            image_path
        )

        # ========================================================
        # GENERATE TAMIL VOICE
        # ========================================================

        print()
        print(
            "🎙️ Generating Tamil voice..."
        )

        print(
            f"📝 Narration: "
            f"{scene['narration']}"
        )

        generate_tamil_voice(
            scene["narration"],
            audio_path
        )

        if not os.path.exists(
            audio_path
        ):

            raise RuntimeError(
                f"❌ Audio was not created: "
                f"{audio_path}"
            )

        audio_size = os.path.getsize(
            audio_path
        )

        if audio_size == 0:

            raise RuntimeError(
                f"❌ Generated audio is empty: "
                f"{audio_path}"
            )

        print()
        print(
            "✅ TAMIL VOICE GENERATION SUCCESSFUL"
        )

        print(
            f"🎵 Audio: {audio_path}"
        )

        print(
            f"📦 Audio size: "
            f"{audio_size} bytes"
        )

        generated_audios.append(
            audio_path
        )

        # ========================================================
        # GENERATE AI ANIMATION
        # ========================================================

        print()
        print(
            "🎬 Generating AI animation..."
        )

        motion_prompt = build_motion_prompt(
            scene
        )

        print()
        print("🎞️ Motion prompt:")
        print(motion_prompt)

        animate_image(
            image_url,
            motion_prompt,
            video_path
        )

        if not os.path.exists(
            video_path
        ):

            raise RuntimeError(
                f"❌ Animation video was not created: "
                f"{video_path}"
            )

        video_size = os.path.getsize(
            video_path
        )

        if video_size == 0:

            raise RuntimeError(
                f"❌ Generated video is empty: "
                f"{video_path}"
            )

        print()
        print(
            "✅ AI ANIMATION SUCCESSFUL"
        )

        print(
            f"🎬 Video: {video_path}"
        )

        print(
            f"📦 Video size: "
            f"{video_size} bytes"
        )

        generated_videos.append(
            video_path
        )

    # ============================================================
    # STEP 3: TEST SUMMARY
    # ============================================================

    print()
    print("=" * 60)
    print("📊 ONE-SCENE TEST SUMMARY")
    print("=" * 60)

    print()
    print(
        f"Expected images : 1"
    )

    print(
        f"Generated images: "
        f"{len(generated_images)}"
    )

    for image in generated_images:

        print(
            f"    🖼️ {image}"
        )

    print()
    print(
        f"Expected audio : 1"
    )

    print(
        f"Generated audio: "
        f"{len(generated_audios)}"
    )

    for audio in generated_audios:

        print(
            f"    🎵 {audio}"
        )

    print()
    print(
        f"Expected videos : 1"
    )

    print(
        f"Generated videos: "
        f"{len(generated_videos)}"
    )

    for video in generated_videos:

        print(
            f"    🎬 {video}"
        )

    # ============================================================
    # STEP 4: VALIDATION
    # ============================================================

    if len(generated_images) != 1:

        raise RuntimeError(
            "❌ One-scene image test failed."
        )

    if len(generated_audios) != 1:

        raise RuntimeError(
            "❌ One-scene audio test failed."
        )

    if len(generated_videos) != 1:

        raise RuntimeError(
            "❌ One-scene animation test failed."
        )

    # ============================================================
    # IMPORTANT:
    # DO NOT CREATE FINAL SHORT YET.
    #
    # We first need to inspect Scene 1 for:
    #
    # 1. Character consistency
    # 2. Vertical composition
    # 3. Face visibility
    # 4. Animation quality
    # 5. Tamil audio quality
    # 6. MuseTalk compatibility
    # ============================================================

    print()
    print("=" * 60)
    print("🎉 ONE-SCENE TEST SUCCESSFUL!")
    print("=" * 60)

    print()
    print(
        "✅ Scene 1 image generated"
    )

    print(
        "✅ Scene 1 Tamil audio generated"
    )

    print(
        "✅ Scene 1 AI animation generated"
    )

    print()
    print(
        "⏸️ Full 10-scene generation is "
        "intentionally paused."
    )

    print(
        "⏸️ Final Short creation is "
        "intentionally paused."
    )

    print()
    print(
        "🔍 Next step: inspect Scene 1 "
        "for character consistency and "
        "lip-sync compatibility."
    )

    print("=" * 60)


if __name__ == "__main__":
    main()
