from google import genai
from google.genai import types
from src.core.config import settings

# Dimension must match output_dimensionality used in embed_job_skills.py (768).
# Gemini embedding-001 native output is 3072-dim; MRL truncates it to 768.
EXPECTED_DIM = 768

_client = genai.Client(api_key=settings.gemini_api_key)


def embed_query(text: str) -> list[float]:
    """Embed a query string using Gemini embedding-001 (RETRIEVAL_QUERY task type).

    Uses the same SDK (google-genai) and same output_dimensionality=768 as
    embed_job_skills.py, so query and document vectors are in the same space.

    Returns a float list of length 768.

    Raises:
        AssertionError: if the returned vector has an unexpected dimension.
    """
    result = _client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=EXPECTED_DIM,
        ),
    )
    vector: list[float] = result.embeddings[0].values
    assert len(vector) == EXPECTED_DIM, (
        f"Expected {EXPECTED_DIM}-dim embedding, got {len(vector)}. "
        f"Check output_dimensionality in EmbedContentConfig."
    )
    return vector

