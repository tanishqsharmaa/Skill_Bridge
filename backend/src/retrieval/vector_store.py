from src.db.client import get_supabase

# Lazy singleton — avoids creating a new Supabase connection on every call.
_supabase = None


def _get_client():
    global _supabase
    if _supabase is None:
        _supabase = get_supabase()
    return _supabase


def search_job_skills(query_vector: list[float], limit: int = 20) -> list[dict]:
    """Cosine similarity search against job_skills via the match_job_skills RPC.

    Args:
        query_vector: The embedded query (must match the dimension stored in DB).
        limit: Maximum number of rows to return (default 20).

    Returns:
        list of dicts: each row has keys role, skill, importance_level, similarity.
    """
    client = _get_client()
    response = client.rpc(
        "match_job_skills",
        {"query_embedding": query_vector, "match_count": limit},
    ).execute()
    return response.data  # list[dict]
