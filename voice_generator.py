import subprocess
import re

def clean_script(text):
    # Remove markdown symbols
    text = re.sub(r"\*\*.*?\*\*", "", text)  # remove bold sections like **HOST**
    text = re.sub(r"\(.*?\)", "", text)      # remove anything inside ()
    text = re.sub(r"---", "", text)          # remove separators
    text = re.sub(r"#+", "", text)           # remove ### headings
    text = re.sub(r"\n+", "\n", text)        # clean extra newlines
    
    return text.strip()

def generate_voice():
    input_file = "assets/script.txt"
    output_file = "assets/audio/voice.mp3"
    subtitle_file = "assets/audio/voice.vtt"

    # Read original script
    with open(input_file, "r", encoding="utf-8") as f:
        original_text = f.read()

    # Clean it
    cleaned_text = clean_script(original_text)

    # Save cleaned version temporarily
    cleaned_file = "assets/cleaned_script.txt"
    with open(cleaned_file, "w", encoding="utf-8") as f:
        f.write(cleaned_text)

    # Run edge-tts (also generates subtitles)
    command = [
        "edge-tts",
        "--file", cleaned_file,
        "--write-media", output_file,
        "--write-subtitles", subtitle_file,
    ]

    try:
        subprocess.run(command, check=True)
        print("Voice and subtitles generated successfully!")
    except subprocess.CalledProcessError as e:
        print("Error generating voice:", e)
