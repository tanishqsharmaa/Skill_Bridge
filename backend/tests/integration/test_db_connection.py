"""Integration tests for the Supabase connection and schema.

Requires real credentials in build/backend/.env  — do NOT run in CI without secrets.
Run manually:
    cd build/backend
    pytest tests/integration/test_db_connection.py -v
"""
import pytest
from src.db.client import get_supabase


@pytest.fixture(scope="module")
def supabase():
    return get_supabase()


def test_supabase_ping(supabase):
    """Can connect to Supabase and query profiles table without error."""
    result = supabase.table("profiles").select("id").limit(1).execute()
    # execute() raises on connection error; reaching here means connection is OK
    assert result is not None


def test_all_six_tables_exist(supabase):
    """All 6 required tables are present and queryable (schema applied correctly)."""
    tables = [
        "profiles",
        "skill_gaps",
        "learning_plans",
        "quiz_results",
        "job_skills",
        "weekly_reports",
    ]
    for table in tables:
        result = supabase.table(table).select("*").limit(0).execute()
        assert result is not None, f"Table '{table}' is missing or unreachable"


def test_job_skills_populated(supabase):
    """job_skills table has at least 100 rows after running embed_job_skills.py."""
    result = supabase.table("job_skills").select("id", count="exact").execute()
    assert result.count >= 100, (
        f"Expected >= 100 rows in job_skills, got {result.count}. "
        "Run scripts/embed_job_skills.py first."
    )


def test_match_job_skills_function_callable(supabase):
    """match_job_skills RPC function exists and returns a list."""
    dummy_vector = [0.0] * 768
    result = supabase.rpc(
        "match_job_skills",
        {"query_embedding": dummy_vector, "match_count": 5},
    ).execute()
    assert isinstance(result.data, list), (
        "match_job_skills should return a list. "
        "Ensure the SQL function was created in schema.sql."
    )
