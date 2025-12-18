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
from typing import Any, Dict, Optional, Protocol

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
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        LOGGER.info(f"Local disk adapter initialized at: {self.base_path}")

    def _get_path(self: Any, key: str) -> Path:
        """
        Get safe path for a key, preventing directory traversal attacks.

        Args:
            key: Storage key

        Returns:
            Safe path within base directory
        """
        safe_key = Path(key).name
        full_path = self.base_path / safe_key

        if not str(full_path).startswith(str(self.base_path)):
            raise ValueError(f"Invalid key: {key} (directory traversal attempt)")

        return full_path

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
        target_path = self._get_path(key)
        temp_path = target_path.with_suffix(".tmp")

        target_path.parent.mkdir(parents=True, exist_ok=True)

        with open(temp_path, "wb") as f:
            f.write(data)

        if metadata:
            meta_path = target_path.with_suffix(".meta.json")
            with open(meta_path, "w") as f:
                json.dump(metadata, f)

        shutil.move(str(temp_path), str(target_path))

        checksum = hashlib.md5(data).hexdigest()

        LOGGER.debug(f"Wrote blob: {key} (checksum={checksum})")

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
        target_path = self._get_path(key)

        if not target_path.exists():
            raise FileNotFoundError(f"Key {key} not found in storage.")

        with open(target_path, "rb") as f:
            data = f.read()

        LOGGER.debug(f"Read blob: {key} ({len(data)} bytes)")

        return data

    async def exists(self: Any, key: str) -> bool:
        """
        Check if key exists in storage.

        Args:
            key: Storage key

        Returns:
            True if key exists, False otherwise
        """
        return self._get_path(key).exists()

    async def delete_blob(self: Any, key: str) -> bool:
        """
        Delete a blob from storage.

        Args:
            key: Storage key

        Returns:
            True if deleted, False if didn't exist
        """
        target_path = self._get_path(key)

        if target_path.exists():
            target_path.unlink()

            meta_path = target_path.with_suffix(".meta.json")
            if meta_path.exists():
                meta_path.unlink()

            LOGGER.debug(f"Deleted blob: {key}")
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
        blobs = []
        for path in self.base_path.rglob("*"):
            if path.is_file() and not path.suffix in [".tmp", ".meta.json"]:
                relative = path.relative_to(self.base_path)
                key = str(relative)

                if not prefix or key.startswith(prefix):
                    blobs.append(key)

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

            self.s3 = boto3.client("s3", region_name=region)
            self.bucket = bucket_name
            LOGGER.info(f"S3 adapter initialized (bucket={bucket_name}, region={region})")
        except ImportError:
            raise ImportError("boto3 not installed. Run: pip install boto3")

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
        response = self.s3.put_object(Bucket=self.bucket, Key=key, Body=data, Metadata=metadata or {})

        etag = response["ETag"].replace('"', "")
        LOGGER.debug(f"Wrote S3 blob: {key} (etag={etag})")

        return etag

    async def read_blob(self: Any, key: str) -> bytes:
        """
        Read data from S3.

        Args:
            key: S3 object key

        Returns:
            Binary data
        """
        response = self.s3.get_object(Bucket=self.bucket, Key=key)
        data = response["Body"].read()

        LOGGER.debug(f"Read S3 blob: {key} ({len(data)} bytes)")

        return data

    async def exists(self: Any, key: str) -> bool:
        """
        Check if key exists in S3.

        Args:
            key: S3 object key

        Returns:
            True if key exists, False otherwise
        """
        try:
            self.s3.head_object(Bucket=self.bucket, Key=key)
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
            self.s3.delete_object(Bucket=self.bucket, Key=key)
            LOGGER.debug(f"Deleted S3 blob: {key}")
            return True
        except Exception as e:
            LOGGER.error(f"Failed to delete S3 blob {key}: {e}")
            return False

    async def list_blobs(self: Any, prefix: str) -> list:
        """
        List all blobs in S3 with optional prefix filter.

        Args:
            prefix: Optional prefix to filter by

        Returns:
            List of blob keys
        """
        blobs = []
        paginator = self.s3.get_paginator("list_objects_v2")

        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            if "Contents" in page:
                blobs.extend([obj["Key"] for obj in page["Contents"]])

        return blobs


def create_storage_adapter(adapter_type: str = "local", **kwargs) -> BlobStorageProvider:
    """
    Factory function to create storage adapters.

    Args:
        adapter_type: "local" or "s3"
        **kwargs: Adapter-specific arguments

    Returns:
        Storage adapter instance
    """
    if adapter_type == "local":
        base_path = kwargs.get("base_path", "./agent_data_store")
        return LocalDiskAdapter(base_path=base_path)

    elif adapter_type == "s3":
        bucket_name = kwargs.get("bucket_name")
        if not bucket_name:
            raise ValueError("bucket_name required for S3 adapter")

        region = kwargs.get("region", "us-east-1")
        return S3Adapter(bucket_name=bucket_name, region=region)

    else:
        raise ValueError(f"Unknown adapter type: {adapter_type}")


class SignalLedger:
    """
    Simple ledger that logs ExecutionResults to a permanent log file.
    """
    
    def __init__(self, storage_adapter: BlobStorageProvider, session_id: str):
        """
        Initialize the signal ledger.
        
        Args:
            storage_adapter: Storage adapter for persistence
            session_id: Session identifier for this ledger
        """
        self.storage = storage_adapter
        self.session_id = session_id
        self.ledger_key = f"signal_ledger_{session_id}.jsonl"
        
    async def append_result(self, result: Any) -> None:
        """
        Append an ExecutionResult to the ledger.
        
        Args:
            result: ExecutionResult to log
        """
        import time
        from datetime import datetime
        
        # Convert result to dictionary
        if hasattr(result, '__dict__'):
            result_dict = result.__dict__
        else:
            result_dict = result
            
        # Add timestamp
        result_dict['timestamp'] = datetime.utcnow().isoformat()
        result_dict['session_id'] = self.session_id
        
        # Convert to JSON line
        json_line = json.dumps(result_dict) + '\n'
        
        # Read existing ledger
        try:
            existing_data = await self.storage.read_blob(self.ledger_key)
            existing_lines = existing_data.decode('utf-8')
        except FileNotFoundError:
            existing_lines = ''
            
        # Append new entry
        updated_data = existing_lines + json_line
        
        # Write back to storage
        await self.storage.write_blob(
            self.ledger_key,
            updated_data.encode('utf-8'),
            metadata={'type': 'signal_ledger', 'session_id': self.session_id}
        )
        
        LOGGER.debug(f"Appended result to signal ledger: {self.ledger_key}")
        
    async def get_results(self) -> list:
        """
        Get all results from the ledger.
        
        Returns:
            List of result dictionaries
        """
        try:
            data = await self.storage.read_blob(self.ledger_key)
            lines = data.decode('utf-8').strip().split('\n')
            
            results = []
            for line in lines:
                if line.strip():
                    results.append(json.loads(line))
                    
            return results
        except FileNotFoundError:
            return []