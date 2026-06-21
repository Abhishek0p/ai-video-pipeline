# AI Video Pipeline: Automated Short-Form Content Generator

An end-to-end automated Python pipeline that generates ready-to-publish short-form videos (YouTube Shorts, Instagram Reels, TikToks) and YouTube thumbnails from a single topic or prompt. The project leverages generative AI (Google Gemini) for content scripting and thumbnail generation, cloud APIs (Pexels) for B-roll footage, and programmatic video/image editing libraries (`moviepy`, `Pillow`) to stitch it all together.

---

## 🌟 Features

*   **AI-Powered Scriptwriting**: Generates natural, engaging narration scripts optimized for a 1-minute video using the **Google Gemini 2.5 Flash** model.
*   **Realistic Text-to-Speech (TTS)**: Converts the generated script into high-quality spoken audio using Microsoft's `edge-tts`, simultaneously generating synced subtitle files (WebVTT format).
*   **Automated B-Roll Gathering**: Queries the Pexels Video Search API to fetch clips relevant to the topic. Includes a resolution-filtering algorithm to select medium-resolution (720p) clips, optimizing bandwidth and rendering speed on CPU-only machines.
*   **Smart Video Composing**:
    *   Crops horizontal stock video clips to a vertical **9:16 portrait format (1080x1920)** using center-cropping (avoiding stretching or distortion).
    *   Trims clips to a maximum duration (e.g., 7 seconds) for fast-paced sequencing.
    *   Matches the exact length of the voiceover, looping the composite sequence if necessary.
*   **Dynamic Subtitle Overlay**: Parses subtitles from the WebVTT file and overlays styled, word-wrapped, stroke-outlined captions near the bottom of the video.
*   **AI & Stock Thumbnail Generator**:
    *   Retrieves background images from Pexels or generates a custom backdrop via Gemini's image generation model.
    *   Applies a dark gradient overlay for text readability.
    *   Draws stylized, wrapped topic titles with a professional stroke outline.

---

## 🛠️ Tech Stack & Dependencies

*   **Language**: Python 3.10+
*   **Generative AI**: `google-genai` (Gemini 2.5 Flash & Gemini Flash Image)
*   **Stock APIs**: Pexels Video & Image API
*   **Audio & Subtitles**: `edge-tts` (Microsoft Edge Text-To-Speech)
*   **Video Processing**: `moviepy` (FFmpeg wrapper for video concatenations, crops, and compositing)
*   **Image Processing**: `Pillow` (PIL) for thumbnail composing and text rendering
*   **Configuration**: `python-dotenv` for local environment variables

---

## 📁 Project Structure

```text
ai-video-pipeline/
├── assets/                  # Runtime assets directory
│   ├── audio/               # Voice audio (.mp3) and subtitle files (.vtt)
│   ├── videos/              # Downloaded B-roll stock clips (.mp4)
│   ├── script.txt           # Generated narration script
│   └── cleaned_script.txt   # Cleaned script passed to the TTS engine
├── output/                  # Ready-to-publish exports
│   ├── final_video.mp4      # Completed vertical video with captions
│   └── thumbnail.jpg        # Stylized YouTube thumbnail
├── main.py                  # Entrypoint script orchestrating the pipeline
├── script_generator.py      # Core module for Gemini script generation
├── voice_generator.py       # Core module for edge-tts and script cleaning
├── video_fetcher.py         # Core module for fetching/downloading Pexels videos
├── video_builder.py         # Core module for editing, formatting, and subtitle overlay
├── thumbnail_generator.py   # Core module for image assets and title generation
├── requirements.txt         # Package dependencies
├── .env                     # Local API keys and environment configurations (ignored)
└── .gitignore               # Excludes virtualenvs, cache, assets, and outputs
```

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your system.

### 2. Setup Directory and Virtual Environment
Clone this repository or navigate to the project folder, then set up a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
Install all required libraries via pip:

```bash
pip install -r requirements.txt
```

> **Note:** MoviePy relies on FFmpeg. It usually handles its download automatically, but you may need system-level installation of FFmpeg if prompted.

### 4. Configuration
Create a `.env` file in the root directory (based on the system variables) and fill in your API credentials:

```ini
GEMINI_API_KEY=your_google_gemini_api_key_here
PEXELS_API_KEY=your_pexels_api_key_here
```

### 5. Running the Pipeline
Run the main script and follow the prompt to enter your video topic:

```bash
python main.py
```

*   Input a topic (e.g., `Space Exploration`, `Artificial Intelligence`, `Ancient Egypt`).
*   The script will print out status updates for each step of the pipeline.
*   Once finished, look inside the `output/` directory for `final_video.mp4` and `thumbnail.jpg`.

---

## 🔧 Component Details

1.  **Script Generator (`script_generator.py`)**: Instructs Gemini via custom prompting to return *only* narration words (stripping markdown, host names, stage directions, and titles) for a cleaner TTS input.
2.  **Voice Generator (`voice_generator.py`)**: Implements strict regex filters to clean any rogue characters, parentheses, or symbols before running `edge-tts`.
3.  **Video Fetcher (`video_fetcher.py`)**: Uses a custom selection algorithm (`_pick_medium_resolution`) to calculate file heights and retrieve clips closest to 720p. Streams large chunks to prevent RAM overhead.
4.  **Video Builder (`video_builder.py`)**:
    *   Features `crop_to_center` to dynamically resize landscape video files to portrait.
    *   Builds custom `TextClip` objects with custom outline strokes, font scaling, and padding.
    *   Utilizes optimized FFmpeg preset settings (`preset="ultrafast"`, `bitrate="2000k"`, multi-threading) to run quickly on standard laptops.
5.  **Thumbnail Generator (`thumbnail_generator.py`)**: Uses a fallback chain (Pexels -> Gemini Imagen model -> Custom Gradient) to ensure the thumbnail always has a relevant high-quality background.
