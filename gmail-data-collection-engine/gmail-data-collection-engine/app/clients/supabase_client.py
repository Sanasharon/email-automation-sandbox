from supabase import create_client, Client
from app.config import settings
import time
import logging

logger = logging.getLogger(__name__)

def get_supabase_client() -> Client:
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise ValueError("Supabase URL and Service Role Key must be set in the environment.")
    return create_client(settings.supabase_url, settings.supabase_service_role_key)

def ensure_bucket_exists(client: Client, bucket_name: str):
    try:
        buckets = client.storage.list_buckets()
        bucket_names = [b.name for b in buckets]
        if bucket_name not in bucket_names:
            client.storage.create_bucket(bucket_name)
            logger.info(f"Created Supabase storage bucket: {bucket_name}")
    except Exception as e:
        logger.warning(f"Could not verify/create bucket {bucket_name}. Ensure you have correct permissions: {e}")

def upload_attachment_with_retry(client: Client, bucket_name: str, storage_path: str, file_bytes: bytes, mime_type: str, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            client.storage.from_(bucket_name).upload(
                path=storage_path,
                file=file_bytes,
                file_options={"content-type": mime_type}
            )
            return storage_path
        except Exception as e:
            logger.warning(f"Supabase upload attempt {attempt + 1} failed: {e}")
            if attempt == retries - 1:
                raise e
            time.sleep(1)
    raise Exception("Supabase upload failed after retries.")
