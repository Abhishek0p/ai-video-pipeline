import os
import base64
import requests
from io import BytesIO
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")


def generate_thumbnail(topic, output_path="output/thumbnail.jpg"):
    """
    Generate a YouTube thumbnail with an AI/stock background + styled topic text.
    Tries Pexels first (reliable), then Gemini image generation, then gradient fallback.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print("Generating thumbnail...")

    # Try sources in order of reliability
    img = _try_pexels_background(topic)
    if img is None:
        img = _try_gemini_background(topic)
    if img is None:
        print("  Using gradient fallback...")
        img = _create_gradient_fallback()

    # --- Add a dark gradient overlay for text readability ---
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)

    for y in range(img.height):
        if y > img.height * 0.4:
            alpha = int(180 * (y - img.height * 0.4) / (img.height * 0.6))
        else:
            alpha = 0
        draw_overlay.rectangle([(0, y), (img.width, y)], fill=(0, 0, 0, alpha))

    img = Image.alpha_composite(img, overlay)

    # --- Draw the topic text ---
    draw = ImageDraw.Draw(img)

    font_size = 72
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", font_size)
    except OSError:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
        except OSError:
            font = ImageFont.load_default()

    title_text = topic.upper()

    max_width = img.width - 160
    lines = _wrap_text(draw, title_text, font, max_width)
    text_block = "\n".join(lines)

    bbox = draw.multiline_textbbox((0, 0), text_block, font=font, align="center")
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (img.width - text_w) // 2
    y = img.height - text_h - 100

    draw.multiline_text(
        (x, y), text_block, font=font, fill="white",
        align="center", stroke_width=4, stroke_fill="black"
    )

    img = img.convert("RGB")
    img.save(output_path, "JPEG", quality=95)
    print(f"Thumbnail saved to {output_path}")
    return output_path


def _try_pexels_background(topic):
    """Fetch a high-quality photo from Pexels as thumbnail background."""
    if not PEXELS_API_KEY:
        return None

    print("  Fetching background from Pexels...")
    try:
        url = f"https://api.pexels.com/v1/search?query={topic}&per_page=1&orientation=landscape"
        headers = {"Authorization": PEXELS_API_KEY}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        photos = data.get("photos", [])
        if not photos:
            print("  No Pexels photos found.")
            return None

        # Get the large image URL
        photo_url = photos[0]["src"]["large2x"]
        img_response = requests.get(photo_url, timeout=30)
        img_response.raise_for_status()

        img = Image.open(BytesIO(img_response.content)).convert("RGBA")
        img = img.resize((1280, 720), Image.LANCZOS)
        print("  Pexels background loaded!")
        return img

    except Exception as e:
        print(f"  Pexels failed: {e}")
        return None


def _try_gemini_background(topic):
    """Generate a background image using Gemini's image generation."""
    if not GEMINI_API_KEY:
        return None

    print("  Generating background via Gemini...")
    try:
        from google import genai

        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = (
            f"Generate a cinematic background image about '{topic}'. "
            f"Dramatic lighting, vibrant colors. No text or words."
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt],
        )

        for part in response.parts:
            if part.inline_data is not None:
                img = part.as_image().convert("RGBA")
                img = img.resize((1280, 720), Image.LANCZOS)
                print("  Gemini background generated!")
                return img

        print("  Gemini returned no image.")
        return None

    except Exception as e:
        print(f"  Gemini failed: {e}")
        return None


def _wrap_text(draw, text, font, max_width):
    """Break text into lines that fit within max_width pixels."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def _create_gradient_fallback():
    """Create a dark gradient background as fallback."""
    img = Image.new("RGBA", (1280, 720))
    draw = ImageDraw.Draw(img)

    for y in range(720):
        r = int(10 + (30 * y / 720))
        g = int(5 + (10 * y / 720))
        b = int(40 + (80 * y / 720))
        draw.rectangle([(0, y), (1280, y)], fill=(r, g, b, 255))

    return img


if __name__ == "__main__":
    topic = input("Enter topic for thumbnail: ").strip() or "Space Exploration"
    generate_thumbnail(topic)
