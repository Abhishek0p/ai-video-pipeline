from script_generator import generate_script
from voice_generator import generate_voice
from video_fetcher import fetch_videos
from video_builder import build_video

if __name__ == "__main__":
    topic = input("Enter topic: ")

    generate_script(topic)
    generate_voice()
    fetch_videos(topic)
    build_video()
