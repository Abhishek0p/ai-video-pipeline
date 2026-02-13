import requests
import os
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")


def _pick_medium_resolution(video_files, target_height=720):
    """Pick the video file closest to target resolution (720p by default).
    This avoids downloading massive 4K files on a CPU-only machine."""
    scored = []
    for vf in video_files:
        h = vf.get("height", 0)
        w = vf.get("width", 0)
        if h == 0 and w == 0:
            continue
        # Prefer the file whose height is closest to target_height
        scored.append((abs(h - target_height), vf))
    if not scored:
        # Fallback: just pick the smallest file
        return min(video_files, key=lambda f: f.get("width", 0) * f.get("height", 0))
    scored.sort(key=lambda x: x[0])
    return scored[0][1]


def fetch_videos(topic, count=8):
    """Fetch videos from Pexels — fewer clips at medium resolution for faster processing."""
    url = f"https://api.pexels.com/videos/search?query={topic}&per_page={count}"

    headers = {
        "Authorization": PEXELS_API_KEY
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Error fetching videos:", response.text)
        return []

    data = response.json()
    videos = data.get("videos", [])

    if not videos:
        print("No videos found.")
        return []

    # Clean out old videos
    video_dir = "assets/videos"
    for old_file in os.listdir(video_dir):
        old_path = os.path.join(video_dir, old_file)
        if os.path.isfile(old_path):
            os.remove(old_path)

    downloaded_paths = []

    for i, video in enumerate(videos):
        video_files = video.get("video_files", [])
        if not video_files:
            continue

        # Pick medium resolution (~720p) instead of max resolution
        chosen_file = _pick_medium_resolution(video_files)
        video_url = chosen_file["link"]

        # Stream download to avoid buffering huge files in RAM
        output_path = os.path.join(video_dir, f"video_{i}.mp4")
        video_response = requests.get(video_url, stream=True)
        with open(output_path, "wb") as f:
            for chunk in video_response.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)

        downloaded_paths.append(output_path)
        print(f"Downloaded video {i + 1}/{len(videos)}")

    print(f"Total videos downloaded: {len(downloaded_paths)}")
    return downloaded_paths
