import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

def generate_script(topic):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={API_KEY}"

    headers = {
        "Content-Type": "application/json"
    }

    prompt = f"""
    Write ONLY the spoken narration for a 1-minute YouTube video on: {topic}.

    Do NOT include:
    - Stage directions
    - Headings
    - Markdown
    - Section titles
    - Words like 'Hook', 'Point 1', 'Conclusion'
    - Any explanations

    Return ONLY the exact words the narrator should speak.
    Make it natural and engaging.
    """


    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        print("Error:", response.text)
        return None

    result = response.json()

    script_text = result["candidates"][0]["content"]["parts"][0]["text"]

    with open("assets/script.txt", "w", encoding="utf-8") as f:
        f.write(script_text)

    print("Script generated successfully!")
    return script_text
