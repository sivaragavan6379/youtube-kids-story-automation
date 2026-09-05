from datetime import datetime
from app.story_generator import generate_story


def main():
    print("=" * 50)
    print("🎬 YouTube Kids Story Automation")
    print("=" * 50)

    print(f"⏰ Started: {datetime.now()}")

    print("📖 Generating Tamil story using OpenRouter...")
    
    story = generate_story()

    print("\n" + "=" * 50)
    print("📖 GENERATED STORY")
    print("=" * 50)
    print(story)
    print("=" * 50)

    print("✅ Story generation completed.")


if __name__ == "__main__":
    main()
