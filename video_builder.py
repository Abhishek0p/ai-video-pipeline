import os
import re
from moviepy import (
    VideoFileClip,
    AudioFileClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
)


def parse_vtt(vtt_path):
    """Parse a WebVTT / SRT subtitle file and return a list of (start, end, text) tuples."""
    cues = []
    with open(vtt_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Normalize line endings
    content = content.replace("\r\n", "\n")

    # Match blocks like:
    #   1
    #   00:00:00,050 --> 00:00:06,150
    #   Some subtitle text here
    # Timestamps may use comma or dot as decimal separator
    pattern = re.compile(
        r"(\d{2}:\d{2}:\d{2}[.,]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[.,]\d{3})\s*\n(.+?)(?=\n\n|\n\d+\n|\Z)",
        re.DOTALL,
    )

    def ts_to_seconds(ts):
        ts = ts.replace(",", ".")  # normalize comma to dot
        h, m, s = ts.split(":")
        return int(h) * 3600 + int(m) * 60 + float(s)

    for match in pattern.finditer(content):
        start = ts_to_seconds(match.group(1))
        end = ts_to_seconds(match.group(2))
        text = match.group(3).strip().replace("\n", " ")
        if text:
            cues.append((start, end, text))

    return cues


def crop_to_center(clip, target_w, target_h):
    """Scale clip to fill the target frame, then center-crop to exact dimensions.
    This avoids stretching/squeezing -- instead it cuts the extra edges."""
    clip_w, clip_h = clip.size

    # Scale factor so the clip fully COVERS the target area (no black bars)
    scale = max(target_w / clip_w, target_h / clip_h)
    new_w = int(clip_w * scale)
    new_h = int(clip_h * scale)

    clip = clip.resized((new_w, new_h))

    # Crop from center
    x_center = new_w / 2
    y_center = new_h / 2
    x1 = int(x_center - target_w / 2)
    y1 = int(y_center - target_h / 2)

    clip = clip.cropped(x1=x1, y1=y1, width=target_w, height=target_h)
    return clip


def build_video():
    video_dir = "assets/videos"
    audio_path = "assets/audio/voice.mp3"
    output_path = "output/final_video.mp4"

    audio = AudioFileClip(audio_path)
    target_duration = audio.duration
    print(f"Audio duration: {target_duration:.1f}s")

    # Load all downloaded video clips
    video_files = sorted(
        [os.path.join(video_dir, f) for f in os.listdir(video_dir) if f.endswith(".mp4")]
    )

    if not video_files:
        print("No video clips found in assets/videos/")
        return

    MAX_CLIP_DURATION = 7  # seconds – keep each clip short for shorts format

    clips = []
    for vf in video_files:
        try:
            clip = VideoFileClip(vf)
            # Trim long clips to max duration
            if clip.duration > MAX_CLIP_DURATION:
                clip = clip.with_duration(MAX_CLIP_DURATION)
            clips.append(clip)
        except Exception as e:
            print(f"Skipping {vf}: {e}")

    if not clips:
        print("Could not load any video clips.")
        return

    # Shorts format: 1080x1920 (9:16 portrait)
    target_w, target_h = 1080, 1920

    # Center-crop each clip to fill the shorts frame without stretching
    resized_clips = []
    for clip in clips:
        clip = crop_to_center(clip, target_w, target_h)
        resized_clips.append(clip)

    # Concatenate all clips
    combined = concatenate_videoclips(resized_clips, method="compose")
    total_video_duration = combined.duration
    print(f"Combined video duration: {total_video_duration:.1f}s")

    # If combined video is still shorter than audio, loop it
    if total_video_duration < target_duration:
        loops_needed = int(target_duration // total_video_duration) + 1
        print(f"Looping video {loops_needed}x to cover audio duration...")
        combined = concatenate_videoclips([combined] * loops_needed, method="compose")

    # Trim to exactly match audio duration
    combined = combined.with_duration(target_duration)

    # Attach the audio
    final = combined.with_audio(audio)

    # --- Overlay subtitles ---
    subtitle_path = "assets/audio/voice.vtt"
    if os.path.exists(subtitle_path):
        print("Adding subtitles...")
        cues = parse_vtt(subtitle_path)
        subtitle_clips = []
        for start, end, text in cues:
            # Skip cues that fall outside the video duration
            if start >= target_duration:
                continue
            end = min(end, target_duration)

            txt_clip = (
                TextClip(
                    text=text,
                    font_size=50,
                    color="white",
                    font="C:/Windows/Fonts/arialbd.ttf",
                    stroke_color="black",
                    stroke_width=2,
                    method="caption",
                    size=(target_w - 100, None),  # wrap text within frame
                )
                .with_start(start)
                .with_duration(end - start)
                .with_position(("center", target_h - 300))  # near bottom
            )
            subtitle_clips.append(txt_clip)

        if subtitle_clips:
            final = CompositeVideoClip([final] + subtitle_clips)
            print(f"Overlaid {len(subtitle_clips)} subtitle cues.")
    else:
        print("No subtitle file found, skipping subtitles.")

    final.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",   # Much faster encoding on CPU (trades file size for speed)
        threads=4,            # Use multiple CPU cores
        fps=24,               # Standard frame rate, avoid unnecessarily high fps
        bitrate="2000k",      # Lower bitrate = less encoding work
    )

    # Clean up
    for clip in clips:
        clip.close()
    audio.close()

    print("Final video created successfully!")
