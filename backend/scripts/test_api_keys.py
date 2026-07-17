"""Quick smoke test — validates Gemini and DeepSeek API keys are active."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import settings

print("=" * 50)
print("API Key Smoke Test")
print("=" * 50)

# ── Test 1: Gemini (google.genai) ─────────────────────
print("\n[1] Gemini text-embedding-004 ... ", end="", flush=True)
try:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.gemini_api_key)
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents="hello world",
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=768,
        ),
    )
    dims = len(result.embeddings[0].values)
    print(f"PASS  (dims={dims})")
except Exception as e:
    print(f"FAIL\n    {e}")

# ── Test 2: DeepSeek ──────────────────────────────────
print("\n[2] DeepSeek deepseek-chat ... ", end="", flush=True)
try:
    from langchain_deepseek import ChatDeepSeek

    llm = ChatDeepSeek(
        model="deepseek-chat",
        temperature=0,
        api_key=settings.deepseek_api_key,
        max_tokens=5,
    )
    response = llm.invoke("Say OK")
    print(f"PASS  (response='{response.content.strip()}')")
except Exception as e:
    print(f"FAIL\n    {e}")

print("\n" + "=" * 50)
