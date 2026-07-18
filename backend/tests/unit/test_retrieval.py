"""Unit tests for the retrieval layer (embeddings + vector_store).

All network calls (Gemini, Supabase) are mocked — runs offline.
"""
from unittest.mock import MagicMock, patch


def test_embed_query_returns_correct_dims():
    """embed_query must return a vector of EXPECTED_DIM floats."""
    # Mock the new google-genai SDK response shape
    mock_embedding = MagicMock()
    mock_embedding.values = [0.1] * 768
    mock_result = MagicMock()
    mock_result.embeddings = [mock_embedding]

    with patch("src.retrieval.embeddings._client") as mock_client:
        mock_client.models.embed_content.return_value = mock_result
        from src.retrieval.embeddings import embed_query, EXPECTED_DIM
        vec = embed_query("backend developer")

    assert isinstance(vec, list)
    assert len(vec) == EXPECTED_DIM


def test_embed_query_raises_on_wrong_dims():
    """embed_query must raise AssertionError if Gemini returns unexpected dims."""
    mock_embedding = MagicMock()
    mock_embedding.values = [0.1] * 512  # wrong dimension
    mock_result = MagicMock()
    mock_result.embeddings = [mock_embedding]

    import pytest
    with patch("src.retrieval.embeddings._client") as mock_client:
        mock_client.models.embed_content.return_value = mock_result
        from src.retrieval.embeddings import embed_query
        with pytest.raises(AssertionError, match="Expected"):
            embed_query("backend developer")


def test_search_job_skills_returns_list():
    """search_job_skills must return list[dict] from Supabase RPC response."""
    mock_data = [
        {"role": "Backend Dev", "skill": "Python", "importance_level": 5, "similarity": 0.92},
        {"role": "Backend Dev", "skill": "FastAPI", "importance_level": 4, "similarity": 0.87},
    ]

    import src.retrieval.vector_store as vs
    vs._supabase = None  # reset singleton

    with patch("src.retrieval.vector_store.get_supabase") as mock_get:
        mock_client = MagicMock()
        mock_client.rpc.return_value.execute.return_value.data = mock_data
        mock_get.return_value = mock_client

        from src.retrieval.vector_store import search_job_skills
        result = search_job_skills([0.1] * 768, limit=20)

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["skill"] == "Python"


def test_search_job_skills_passes_correct_rpc_args():
    """search_job_skills must call the RPC with query_embedding and match_count."""
    import src.retrieval.vector_store as vs
    vs._supabase = None  # reset singleton

    with patch("src.retrieval.vector_store.get_supabase") as mock_get:
        mock_client = MagicMock()
        mock_client.rpc.return_value.execute.return_value.data = []
        mock_get.return_value = mock_client

        query_vec = [0.5] * 768
        from src.retrieval.vector_store import search_job_skills
        search_job_skills(query_vec, limit=15)

    mock_client.rpc.assert_called_once_with(
        "match_job_skills",
        {"query_embedding": query_vec, "match_count": 15},
    )
