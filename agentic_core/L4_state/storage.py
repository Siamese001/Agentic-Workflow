""" """
import hashlib
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, Optional, Protocol, Any

from services.configuration import ConfigurationService

LOGGER = logging.getLogger(__name__)


class BlobStorageProvider(Protocol):
    """ Standardizes 'open', 'write', 'read' across Local FS and Cloud.
    """

    def write_blob(self, key: str, data: bytes, metadata: Optional[Dict[str, str]]) -> str:
        """Writes data atomically. Returns a version ID or checksum."""
        ...

    async def read_blob(self, key: str) -> bytes:
        """Reads data given a key."""
        ...

    async def exists(self, key: str) -> bool:
        """Checks if key exists."""
        ...

    async def delete_blob(self, key: str) -> bool:
        """Deletes a blob by key."""
        ...

    async def list_blobs(self, prefix: str) -> list:
        """Lists blobs with a given prefix."""
        ...


class LocalDiskAdapter:
    """ Uses atomic 'write-to-temp-then-move' logic to prevent corruption.

    This adapter is perfect for development and ensures that your code
    works identically whether running locally or in production on S3.
    """

    def __init__(self, base_path: str):
        """
        Initialize local disk storage.

        Args:
            base_path: Base directory for storage
        """
        self.base_path = Path(base_path)
        ConfigurationService().logger.info(f'Local disk adapter initialized at: {self.base_path}')

    def _get_path(self, key: str) -> Path:
        """ """
        target_path = self.base_path / key
        if not str(target_path).startswith(str(self.base_path)):
            raise ValueError(
                f'Invalid key: {key} (directory traversal attempt)')
        return target_path

    async def write_blob(self, key: str, data: bytes, metadata: Optional[Dict[str, str]]) -> str:
        """ """
        target_path = self._get_path(key)
        temp_path = target_path.with_suffix('.tmp')
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_path, 'wb') as f:
            f.write(data)
        if metadata:
            meta_path = target_path.with_suffix('.meta.json')
            with open(meta_path, 'w') as f:
                json.dump(metadata, f)
        shutil.move(str(temp_path), str(target_path))
        checksum = hashlib.md5(data).hexdigest()
        ConfigurationService().logger.debug(
            f'Wrote blob: {key} (checksum={checksum})')
        return checksum

    async def read_blob(self, key: str) -> bytes:
        """ FileNotFoundError: If key doesn't exist
        """
        target_path = self._get_path(key)
        if not target_path.exists():
            raise FileNotFoundError(f'Key {key} not found in storage.')
        with open(target_path, 'rb') as f:
            data = f.read()
        ConfigurationService().logger.debug(
            f'Read blob: {key} ({len(data)} bytes)')
        return data

    async def exists(self, key: str) -> bool:
        """ """
        return self._get_path(key).exists()

    async def delete_blob(self, key: str) -> bool:
        """ True if deleted, False if didn't exist
        """
        target_path = self._get_path(key)
        meta_path = target_path.with_suffix('.meta.json')
        if target_path.exists():
            if meta_path.exists():
                meta_path.unlink()
            target_path.unlink()
            ConfigurationService().logger.debug(f'Deleted blob: {key}')
            return True
        return False

    async def list_blobs(self, prefix: str) -> list:
        """ """
        blobs = []
        for path in self.base_path.rglob('*'):
            if path.is_file() and (not path.suffix in ['.tmp', '.meta.json']):
                relative = path.relative_to(self.base_path)
                key = str(relative)
                if not prefix or key.startswith(prefix):
                    blobs.append(key)
        return blobs


class S3Adapter:
    """ """

    def __init__(self, bucket_name: str, region: str) -> None:
        """ """
        try:
            import boto3
            self.s3 = boto3.client('s3', region_name=region)
            self.bucket = bucket_name
            ConfigurationService().logger.info(
                f'S3 adapter initialized (bucket={bucket_name}, region={region})')
        except ImportError:
            raise ImportError('boto3 not installed. Run: pip install boto3')

    async def write_blob(self, key: str, data: bytes, metadata: Optional[Dict[str, str]]) -> str:
        """ """
        response = self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            Metadata=metadata or {})
        etag = response['ETag'].replace('"', '')
        ConfigurationService().logger.debug(f'Wrote S3 blob: {key} (etag={etag})')
        return etag

    async def read_blob(self, key: str) -> bytes:
        """ """
        response = self.s3.get_object(Bucket=self.bucket, Key=key)
        data = response['Body'].read()
        ConfigurationService().logger.debug(
            f'Read S3 blob: {key} ({len(data)} bytes)')
        return data

    async def exists(self, key: str) -> bool:
        """ """
        try:
            self.s3.head_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False

    async def delete_blob(self, key: str) -> bool:
        """ """
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=key)
            ConfigurationService().logger.debug(f'Deleted S3 blob: {key}')
            return True
        except Exception as e:
            ConfigurationService().logger.error(f'Failed to delete S3 blob {key}: {e}')
            return False

    async def list_blobs(self, prefix: str) -> list:
        """ """
        blobs = []
        paginator = self.s3.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            if 'Contents' in page:
                blobs.extend([obj['Key'] for obj in page['Contents']])
        return blobs


def create_storage_adapter(adapter_type: str = 'local', **kwargs) -> BlobStorageProvider:
    """ adapter_type: "local" or "s3"
        **kwargs: Adapter-specific arguments

    Returns:
        Storage adapter instance
    """
    if adapter_type == 'local':
        base_path = kwargs.get('base_path', './agent_data_store')
        return LocalDiskAdapter(base_path=base_path)
    elif adapter_type == 's3':
        bucket_name = kwargs.get('bucket_name')
        if not bucket_name:
            raise ValueError('bucket_name required for S3 adapter')
        region = kwargs.get('region', 'us-east-1')
        return S3Adapter(bucket_name=bucket_name, region=region)
    else:
        raise ValueError(f'Unknown adapter type: {adapter_type}')