from script_generator import generate_script
from voice_generator import generate_voice
from video_fetcher import fetch_videos
from video_builder import build_video
from thumbnail_generator import generate_thumbnail

if __name__ == "__main__":
    topic = input("Enter topic: ")

    generate_script(topic)
    generate_voice()
    fetch_videos(topic)
    build_video()
    # Auto-generate a YouTube thumbnail using AI
    generate_thumbnail(topic)
