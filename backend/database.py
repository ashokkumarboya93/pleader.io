"""
Database connection module for Supabase
Replaces previous MongoDB/Motor client
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging
from pathlib import Path

# Load env
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

# Initialize Supabase Client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    logger.error("Supabase credentials missing in .env")
    supabase: Client = None
else:
    try:
        supabase: Client = create_client(url, key)
        logger.info("Supabase client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        supabase = None

def get_supabase() -> Client:
    """Get the initialized Supabase client"""
    if not supabase:
        raise Exception("Supabase client not initialized. Check your credentials.")
    return supabase
