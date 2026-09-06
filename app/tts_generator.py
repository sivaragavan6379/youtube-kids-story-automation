from gtts import gTTS


def generate_tamil_voice(text, output_path):
    """
    Convert Tamil text into a Tamil MP3 voice.
    """

    print("🎙️ Generating Tamil voice...")
    print("📝 Text:", text)

    tts = gTTS(
        text=text,
        lang="ta",
        slow=False
    )

    tts.save(output_path)

    print("✅ Tamil voice generated!")
    print("🎵 Audio saved:", output_path)

    return output_path
