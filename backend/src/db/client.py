from supabase import create_client, Client
from src.core.config import settings


def get_supabase() -> Client:
    """Return a Supabase client authenticated with the service role key.

    The service role key bypasses RLS — only use server-side. Never expose to
    the frontend.
    """
    return create_client(settings.supabase_url, settings.supabase_service_key)
