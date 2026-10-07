import sys
import time

from google import genai
from google.genai import types

from app.config import settings

models = sys.argv[1:] or [settings.gemini_model]

client = genai.Client(
    api_key=settings.gemini_api_key,
    http_options=types.HttpOptions(timeout=30_000),
)
config = types.GenerateContentConfig(
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
)

for model in models:
    start = time.time()
    try:
        resp = client.models.generate_content(
            model=model, contents="Reply with just: OK", config=config
        )
        print(f"OK    {model}: {resp.text.strip()!r} ({time.time() - start:.1f}s)")
    except Exception as e:
        print(f"FAIL  {model}: {str(e)[:100]}")