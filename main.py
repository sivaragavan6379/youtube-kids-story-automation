from datetime import datetime
from app.story_generator import generate_story
from app.image_generator import generate_image


def main():
    print("=" * 60)
    print("🎬 YouTube Kids Story Automation")
    print("=" * 60)

    print(f"⏰ Started: {datetime.now()}")

    # Generate story
    print("\n📖 Generating Tamil story...")
    story = generate_story()

    print(f"✅ Story: {story['title']}")
    print(f"✅ Scenes: {len(story['scenes'])}")

    # Get Scene 1
    scene = story["scenes"][0]

    print("\n🎨 Generating image for Scene 1...")
    print(f"📝 Prompt: {scene['visual_prompt']}")

    output_path = "scene_01.png"

    generate_image(
        scene["visual_prompt"],
        output_path
    )

    print("\n" + "=" * 60)
    print("✅ IMAGE GENERATION SUCCESSFUL")
    print("=" * 60)
    print(f"🖼️ Image saved as: {output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
