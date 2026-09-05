from datetime import datetime
from app.story_generator import generate_story


def main():
    print("=" * 60)
    print("🎬 YouTube Kids Story Automation")
    print("=" * 60)

    print(f"⏰ Started: {datetime.now()}")
    print("📖 Generating structured Tamil story using OpenRouter...")

    story = generate_story()

    print("\n" + "=" * 60)
    print("📖 STORY")
    print("=" * 60)

    print(f"\n🎬 Title: {story['title']}")
    print(f"\n📝 Description: {story['description']}")
    print(f"\n💡 Moral: {story['moral']}")

    print("\n🎭 CHARACTERS")
    print("-" * 60)

    for character in story["characters"]:
        print(f"• {character['name']}: {character['description']}")

    print("\n🎬 SCENES")
    print("=" * 60)

    for scene in story["scenes"]:
        print(f"\nScene {scene['scene_number']}")
        print(f"🗣️ Narration: {scene['narration']}")
        print(f"🎨 Visual Prompt: {scene['visual_prompt']}")

    print("\n" + "=" * 60)
    print(f"✅ Generated {len(story['scenes'])} scenes successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()
