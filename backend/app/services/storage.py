"""
Storage adapter so the rest of the app never imports boto3 or the
filesystem directly - swapping local disk for MinIO/S3 in production is a
one-line env var change (STORAGE_BACKEND), not a code change.
"""
import os
from abc import ABC, abstractmethod

from app.core.config import settings


class StorageBackend(ABC):
    @abstractmethod
    def save(self, key: str, data: bytes) -> str:
        """Persist bytes under `key`, return a retrievable URL/path."""

    @abstractmethod
    def read(self, key: str) -> bytes:
        """Read the bytes back, for verification/testing."""


class LocalStorage(StorageBackend):
    def __init__(self, base_path: str):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def save(self, key: str, data: bytes) -> str:
        path = os.path.join(self.base_path, key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
        return path

    def read(self, key: str) -> bytes:
        with open(os.path.join(self.base_path, key), "rb") as f:
            return f.read()


class S3Storage(StorageBackend):
    def __init__(self):
        import boto3  # imported lazily - only needed when this backend is selected

        self.client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
        )
        self.bucket = settings.S3_BUCKET

    def save(self, key: str, data: bytes) -> str:
        self.client.put_object(Bucket=self.bucket, Key=key, Body=data)
        return f"s3://{self.bucket}/{key}"

    def read(self, key: str) -> bytes:
        obj = self.client.get_object(Bucket=self.bucket, Key=key)
        return obj["Body"].read()


def get_storage() -> StorageBackend:
    if settings.STORAGE_BACKEND == "s3":
        return S3Storage()
    return LocalStorage(settings.STORAGE_LOCAL_PATH)
