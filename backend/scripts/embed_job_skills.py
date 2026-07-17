"""One-time seeding script.

Reads job_skills_dataset.csv, generates gemini-embedding-001 embeddings
(truncated to 768 dims via MRL) for each row, and batch-inserts into Supabase.

Run from build/backend/:
    python scripts/embed_job_skills.py

After this completes, run the IVFFlat index in Supabase SQL editor:
    CREATE INDEX IF NOT EXISTS job_skills_embedding_idx
        ON job_skills USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 10);
"""
import csv
import sys
import time
from pathlib import Path

from google import genai
from google.genai import types

# Add src/ to path so imports work when run directly
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import settings
from src.db.client import get_supabase

client = genai.Client(api_key=settings.gemini_api_key)
supabase = get_supabase()

CSV_PATH = Path(__file__).parent / "job_skills_dataset.csv"
BATCH_SIZE = 20   # Stay within Gemini free-tier RPM limits
SLEEP_BETWEEN_BATCHES = 1.5  # seconds


def embed_text(text: str, max_retries: int = 3) -> list[float]:
    """Embed text using gemini-embedding-001.

    output_dimensionality=768 uses Matryoshka Representation Learning (MRL)
    to truncate the default 3072-dim output to 768, matching vector(768) in schema.
    Retries on 429 RESOURCE_EXHAUSTED using the delay suggested by the API.
    """
    for attempt in range(1, max_retries + 1):
        try:
            result = client.models.embed_content(
                model="gemini-embedding-001",
                contents=text,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT",
                    output_dimensionality=768,
                ),
            )
            return result.embeddings[0].values
        except Exception as exc:
            err_str = str(exc)
            if "429" in err_str and attempt < max_retries:
                # Parse suggested retry delay from API response (e.g. "retryDelay": "31s")
                import re
                match = re.search(r"retry in (\d+(?:\.\d+)?)s", err_str)
                wait = float(match.group(1)) + 2 if match else 60.0
                print(f"\n    ⚠ Rate limited. Waiting {wait:.0f}s before retry {attempt}/{max_retries - 1}...", flush=True)
                time.sleep(wait)
            else:
                raise



def main() -> None:
    rows: list[dict] = []
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    total = len(rows)
    print(f"Loaded {total} rows from {CSV_PATH.name}")

    inserted = 0
    for i in range(0, total, BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        records = []

        for row in batch:
            text = f"{row['role']}: {row['skill']}"
            try:
                embedding = embed_text(text)
            except Exception as exc:
                print(f"  ✗ Failed to embed '{text}': {exc}")
                continue

            records.append({
                "role": row["role"],
                "skill": row["skill"],
                "importance_level": int(row["importance_level"]),
                "embedding": embedding,
            })

        if records:
            supabase.table("job_skills").insert(records).execute()
            inserted += len(records)
            batch_num = i // BATCH_SIZE + 1
            print(f"  ✓ Batch {batch_num}: inserted {len(records)} rows  (total: {inserted})")

        if i + BATCH_SIZE < total:
            time.sleep(SLEEP_BETWEEN_BATCHES)

    print(f"\nDone! Inserted {inserted}/{total} rows.")
    print("\nNext step — run this in the Supabase SQL editor:")
    print("  CREATE INDEX IF NOT EXISTS job_skills_embedding_idx")
    print("      ON job_skills USING ivfflat (embedding vector_cosine_ops)")
    print("      WITH (lists = 10);")


if __name__ == "__main__":
    main()
