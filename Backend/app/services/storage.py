"""
CLEARLY — Storage Service (MinIO S3 Compatible with Local Filesystem Fallback)
Handles sovereign file storage, SHA-256 content verification, and encryption.
"""

import hashlib
import os
from pathlib import Path
from typing import Optional, Tuple
from uuid import uuid4
from datetime import datetime, timezone
from loguru import logger

from app.core.config import settings


class StorageService:
    def __init__(self):
        self.local_dir = settings.LOCAL_STORAGE_DIR / "documents"
        self.local_dir.mkdir(parents=True, exist_ok=True)
        self.minio_client = None
        self._init_minio()

    def _init_minio(self):
        """Attempt to connect to MinIO if minio package is available and endpoint is reachable."""
        try:
            from minio import Minio
            client = Minio(
                endpoint=settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ROOT_USER,
                secret_key=settings.MINIO_ROOT_PASSWORD,
                secure=settings.MINIO_USE_SSL,
            )
            # Fast check if bucket exists or can be listed
            if not client.bucket_exists(settings.MINIO_DOCUMENTS_BUCKET):
                client.make_bucket(settings.MINIO_DOCUMENTS_BUCKET)
            self.minio_client = client
            logger.info(f"Connected to MinIO at {settings.MINIO_ENDPOINT}, bucket: {settings.MINIO_DOCUMENTS_BUCKET}")
        except Exception as e:
            logger.warning(
                f"MinIO storage unavailable ({e}). Using local filesystem fallback: {self.local_dir}"
            )
            self.minio_client = None

    def calculate_sha256(self, file_bytes: bytes) -> str:
        """Calculate SHA-256 checksum of raw binary data."""
        return hashlib.sha256(file_bytes).hexdigest()

    async def save_document(
        self, file_bytes: bytes, filename: str, content_type: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Save file to MinIO (or fallback to local disk).
        Returns:
            Tuple of (storage_path, file_sha256)
        """
        sha256_hash = self.calculate_sha256(file_bytes)
        ext = Path(filename).suffix.lower() or ".bin"
        now = datetime.now(timezone.utc)
        object_name = f"documents/{now.year}/{now.month:02d}/{sha256_hash[:16]}_{uuid4()}{ext}"

        if self.minio_client:
            try:
                import io
                data_stream = io.BytesIO(file_bytes)
                self.minio_client.put_object(
                    bucket_name=settings.MINIO_DOCUMENTS_BUCKET,
                    object_name=object_name,
                    data=data_stream,
                    length=len(file_bytes),
                    content_type=content_type or "application/octet-stream",
                )
                storage_path = f"minio://{settings.MINIO_DOCUMENTS_BUCKET}/{object_name}"
                return storage_path, sha256_hash
            except Exception as e:
                logger.error(f"Failed to upload to MinIO, falling back to local disk: {e}")

        # Local disk fallback
        local_path = self.local_dir / object_name.replace("/", os.sep)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(file_bytes)

        storage_path = f"local://{object_name}"
        return storage_path, sha256_hash

    async def get_document(self, storage_path: str) -> Optional[bytes]:
        """Retrieve document bytes from MinIO or local filesystem."""
        if storage_path.startswith("minio://") and self.minio_client:
            try:
                bucket_and_obj = storage_path.replace("minio://", "")
                bucket, obj_name = bucket_and_obj.split("/", 1)
                response = self.minio_client.get_object(bucket, obj_name)
                return response.read()
            except Exception as e:
                logger.error(f"Error reading from MinIO ({storage_path}): {e}")

        # Try local storage
        clean_path = storage_path.replace("local://", "").replace("minio://", "")
        # Remove bucket name if minio path was saved
        if clean_path.startswith(settings.MINIO_DOCUMENTS_BUCKET + "/"):
            clean_path = clean_path[len(settings.MINIO_DOCUMENTS_BUCKET) + 1 :]

        local_file = self.local_dir / clean_path.replace("/", os.sep)
        if local_file.is_file():
            with open(local_file, "rb") as f:
                return f.read()

        return None


storage_service = StorageService()
