from google import genai
from app.config import settings

client = genai.Client(api_key=settings.gemini_api_key)
skip = ("tts", "live", "audio", "image", "gemma")

for m in client.models.list():
    actions = m.supported_actions or []
    if "generateContent" in actions and not any(s in m.name for s in skip):
        print("TEXT :", m.name)
    if "embedContent" in actions:
        print("EMBED:", m.name)