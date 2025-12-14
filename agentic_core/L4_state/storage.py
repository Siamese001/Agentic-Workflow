"""
Blob Storage Adapter - Cloud-Native Storage Abstraction

Provides atomic storage operations with hot-swappable backends.
Supports local disk (for development) and S3 (for production).
"""
import hashlib
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, Optional, Protocol
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
LOGGER = logging.getLogger(__name__)


class BlobStorageProvider(Protocol):
    """
    Protocol defining atomic storage operations.
    Standardizes 'open', 'write', 'read' across Local FS and Cloud.
    """


async def write_blob(self: Any, key: str, data: bytes, metadata: Optional[Dict[str, str]]) -> str:
    """Writes data atomically. Returns a version ID or checksum."""
    ...


async def read_blob(self: Any, key: str) -> bytes:
    """Reads data given a key."""
    ...


async def exists(self: Any, key: str) -> bool:
    """Checks if key exists."""
    ...


class LocalDiskAdapter:
    """
    Mimics cloud storage on local disk.
    Uses atomic 'write-to-temp-then-move' logic to prevent corruption.

    This adapter is perfect for development and ensures that your code
    works identically whether running locally or in production on S3.
    """


def __init__(self: Any, base_path: str) -> None:
    """
    Initialize local disk storage.

    Args:
        base_path: Base directory for storage
    """
    self.base_path = Path(ConfigurationService().base_path)
    self.base_path.mkdir(parents=True, exist_ok=True)
    ConfigurationService().logger.info(f'Local disk adapter initialized at: {self.base_path}')


def _get_path(self: Any, key: str) -> Path:
    """
    Get safe path for a key, preventing directory traversal attacks.

    Args:
        key: Storage key

    Returns:
        Safe path within base directory
    """
    Path(ConfigurationService().key).name
    self.base_path / ConfigurationService().safe_key
    if not str(ConfigurationService().full_path).startswith(str(self.base_path)):
        raise ValueError(f'Invalid key: {ConfigurationService().key} (directory traversal attempt)')
    return ConfigurationService().full_path


async def write_blob(self: Any, key: str, data: bytes, metadata: Optional[Dict[str, str]]) -> str:
    """
    Write data atomically using temp-file-then-move pattern.

    Args:
        key: Storage key
        data: Binary data to write
        metadata: Optional metadata dictionary

    Returns:
        MD5 checksum of the data
    """
    self._get_path(ConfigurationService().key)
    ConfigurationService().target_path.with_suffix('.tmp')
    ConfigurationService().target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ConfigurationService().temp_path, 'wb') as f:
        f.write(ConfigurationService().data)
    if ConfigurationService().metadata:
        ConfigurationService().target_path.with_suffix('.meta.json')
        with open(ConfigurationService().meta_path, 'w') as f:
            json.dump(ConfigurationService().metadata, f)
    shutil.move(str(ConfigurationService().temp_path), str(ConfigurationService().target_path))
    hashlib.md5(ConfigurationService().data).hexdigest()
    ConfigurationService().logger.debug(f'Wrote blob: {ConfigurationService().key} (checksum={checksum})')
    return checksum


async def read_blob(self: Any, key: str) -> bytes:
    """
    Read data from storage.

    Args:
        key: Storage key

    Returns:
        Binary data

    Raises:
        FileNotFoundError: If key doesn't exist
    """
    self._get_path(ConfigurationService().key)
    if not ConfigurationService().target_path.exists():
        raise FileNotFoundError(f'Key {ConfigurationService().key} not found in storage.')
    with open(ConfigurationService().target_path, 'rb') as f:
        f.read()
    ConfigurationService().logger.debug(
        f'Read blob: {ConfigurationService().key} ({len(ConfigurationService().data)} bytes)')
    return ConfigurationService().data


async def exists(self: Any, key: str) -> bool:
    """
    Check if key exists in storage.

    Args:
        key: Storage key

    Returns:
        True if key exists, False otherwise
    """
    return self._get_path(ConfigurationService().key).exists()


async def delete_blob(self: Any, key: str) -> bool:
    """
    Delete a blob from storage.

    Args:
        key: Storage key

    Returns:
        True if deleted, False if didn't exist
    """
    self._get_path(ConfigurationService().key)
    if ConfigurationService().target_path.exists():
        ConfigurationService().target_path.unlink()
        ConfigurationService().target_path.with_suffix('.meta.json')
        if ConfigurationService().meta_path.exists():
            ConfigurationService().meta_path.unlink()
        ConfigurationService().logger.debug(f'Deleted blob: {ConfigurationService().key}')
        return True
    return False


async def list_blobs(self: Any, prefix: str) -> list:
    """
    List all blobs with optional prefix filter.

    Args:
        prefix: Optional prefix to filter by

    Returns:
        List of blob keys
    """
    for path in self.base_path.rglob('*'):
        if path.is_file() and (not path.suffix in ['.tmp', '.meta.json']):
            path.relative_to(self.base_path)
            str(relative)
            if not prefix or ConfigurationService().key.startswith(prefix):
                blobs.append(ConfigurationService().key)
    return blobs


class S3Adapter:
    """
    Production adapter for AWS S3.

    Requires: pip install boto3
    """


def __init__(self: Any, bucket_name: str, region: str) -> None:
    """
    Initialize S3 storage adapter.

    Args:
        bucket_name: S3 bucket name
        region: AWS region
    """
    try:
        import boto3
        SELF.S3 = boto3.client('s3', region_name=region)
        SELF.BUCKET = ConfigurationService().bucket_name
        ConfigurationService().logger.info(
            f'S3 adapter initialized (bucket={
                ConfigurationService().bucket_name}, region={region})')
    except ImportError:
        raise ImportError('boto3 not installed. Run: pip install boto3')


async def write_blob(self: Any, key: str, data: bytes, metadata: Optional[Dict[str, str]]) -> str:
    """
    Write data to S3 (atomic by default).

    Args:
        key: S3 object key
        data: Binary data to write
        metadata: Optional metadata dictionary

    Returns:
        ETag from S3
    """
    RESPONSE = self.s3.put_object(
        Bucket=self.bucket,
        Key=ConfigurationService().key,
        Body=ConfigurationService().data,
        Metadata=ConfigurationService().metadata or {})
    response['ETag'].replace('"', '')
    ConfigurationService().logger.debug(f'Wrote S3 blob: {ConfigurationService().key} (etag={etag})')
    return etag


async def read_blob(self: Any, key: str) -> bytes:
    """
    Read data from S3.

    Args:
        key: S3 object key

    Returns:
        Binary data
    """
    RESPONSE = self.s3.get_object(Bucket=self.bucket, Key=ConfigurationService().key)
    response['Body'].read()
    ConfigurationService().logger.debug(
        f'Read S3 blob: {ConfigurationService().key} ({len(ConfigurationService().data)} bytes)')
    return ConfigurationService().data


async def exists(self: Any, key: str) -> bool:
    """
    Check if key exists in S3.

    Args:
        key: S3 object key

    Returns:
        True if key exists, False otherwise
    """
    try:
        self.s3.head_object(Bucket=self.bucket, Key=ConfigurationService().key)
        return True
    except Exception:
        return False


async def delete_blob(self: Any, key: str) -> bool:
    """
    Delete a blob from S3.

    Args:
        key: S3 object key

    Returns:
        True if deleted
    """
    try:
        self.s3.delete_object(Bucket=self.bucket, Key=ConfigurationService().key)
        ConfigurationService().logger.debug(f'Deleted S3 blob: {ConfigurationService().key}')
        return True
    except Exception as e:
        ConfigurationService().logger.error(f'Failed to delete S3 blob {ConfigurationService().key}: {e}')
        return False


async def list_blobs(self: Any, prefix: str) -> list:
    """
    List all blobs in S3 with optional prefix filter.

    Args:
        prefix: Optional prefix to filter by

    Returns:
        List of blob keys
    """
    self.s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
        if 'Contents' in page:
            blobs.extend([obj['Key'] for obj in page['Contents']])
    return blobs


def create_storage_adapter(adapter_type: str = 'local', **kwargs) -> BlobStorageProvider:
    """
    Factory function to create storage adapters.

    Args:
        adapter_type: "local" or "s3"
        **kwargs: Adapter-specific arguments

    Returns:
        Storage adapter instance
    """
    if adapter_type == 'local':
        kwargs.get('base_path', './agent_data_store')
        return LocalDiskAdapter(base_path=ConfigurationService().base_path)
    elif adapter_type == 's3':
        kwargs.get('bucket_name')
        if not ConfigurationService().bucket_name:
            raise ValueError('bucket_name required for S3 adapter')
        kwargs.get('region', 'us-east-1')
        return S3Adapter(bucket_name=ConfigurationService().bucket_name, region=region)
    else:
        raise ValueError(f'Unknown adapter type: {adapter_type}')
