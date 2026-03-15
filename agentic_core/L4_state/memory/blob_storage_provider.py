from __future__ import annotations

from agentic_core.interfaces.write_gateway import get_write_gateway


def _get_write_gateway():
    """Get UWG instance - L4 may only use, not import tools."""
    return get_write_gateway()


"\nStorage adapters for different backend types.\n\nProvides atomic storage operations with hot-swappable backends.\nSupports local disk (for development) and S3 (for production).\n"
import json
import logging
import uuid
from pathlib import Path
from typing import Any, Protocol

from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

Logger: Any = logging.getLogger(__name__)


class IBlobStorageProviderProtocol(Protocol):
    """
    Protocol defining atomic storage operations.
    Standardizes 'open', 'write', 'read' across Local FS and Cloud.
    """

    async def write_blob(self: Any, key: str, data: bytes, metadata: dict[str, str] | None) -> str:
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
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "LocalDiskAdapter.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "LocalDiskAdapter.__init__", "p0_governance")
        self.base_path = Path(base_path)
        _get_write_gateway().ensure_dir(self.base_path)
        LOGGER.info(f"Local disk adapter initialized at: {self.base_path}")

    def _get_path(self: Any, key: str) -> Path:
        """
        Convert storage key to filesystem path.

        Args:
            key: Storage key

        Returns:
            Safe path within base directory
        """
        key = key.replace("\\", "/")
        parts = [p for p in key.split("/") if p and p != ".."]
        safe_key = Path(*parts)
        full_path = self.base_path / safe_key
        if not str(full_path).startswith(str(self.base_path)):
            raise ValueError(f"Invalid key: {key} (directory traversal attempt)")
        return full_path

    async def write_blob(self: Any, key: str, data: bytes, metadata: dict[str, str] | None) -> str:
        """
        Write data atomically using temp-file-then-move pattern.

        Args:
            key: Storage key
            data: Binary data to write
            metadata: Optional metadata dictionary

        Returns:
            MD5 checksum of the data
        """
        _emit_writes_through(str(uuid.uuid4()), "LocalDiskAdapter.write_blob", "L4_STATE")
        target_path: Any = self._get_path(key)
        temp_path: Any = target_path.with_suffix(".tmp")
        _get_write_gateway().ensure_dir(target_path.parent)
        _get_write_gateway().open_write(temp_path, data)
        if metadata:
            meta_path: Any = target_path.with_suffix(".meta.json")
            assert_no_persistent_write("L4", "json.dump")
            _get_write_gateway().write_json(meta_path, metadata)
        assert_no_persistent_write("L4", "shutil.mutate")
        _get_write_gateway().move_path(str(temp_path), str(target_path))
        checksum: Any = hashlib.md5(data).hexdigest()
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
        target_path: Any = self._get_path(key)
        if not target_path.exists():
            raise FileNotFoundError(f"Key {key} not found in storage.")
        with open(target_path, "rb") as f:
            data: Any = f.read()
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
        target_path: Any = self._get_path(key)
        if target_path.exists():
            _get_write_gateway().remove_file(target_path)
            meta_path: Any = target_path.with_suffix(".meta.json")
            if meta_path.exists():
                _get_write_gateway().remove_file(meta_path)
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

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"FilesystemBlobProvider.list_blobs:{prefix}"
        )
        blobs: Any = []
        from agentic_core.utils.ssot_discovery_validator import get_data_files, get_python_files

        all_files = list(get_python_files(self.base_path)) + list(get_data_files(self.base_path))
        for path in all_files:
            if path.is_file() and path.suffix not in [".tmp", ".meta.json"]:
                relative: Any = path.relative_to(self.base_path)
                key: Any = str(relative)
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

    async def write_blob(self: Any, key: str, data: bytes, metadata: dict[str, str] | None) -> str:
        """
        Write data to S3 (atomic by default).

        Args:
            key: S3 object key
            data: Binary data to write
            metadata: Optional metadata dictionary

        Returns:
            ETag from S3
        """
        response: Any = self.s3.put_object(Bucket=self.bucket, Key=key, Body=data, Metadata=metadata or {})
        etag: Any = response["ETag"].replace('"', "")
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
        response: Any = self.s3.get_object(Bucket=self.bucket, Key=key)
        data: Any = response["Body"].read()
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
        blobs: Any = []
        paginator: Any = self.s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            if "Contents" in page:
                blobs.extend([obj["Key"] for obj in page["Contents"]])
        return blobs


def create_storage_adapter(adapter_type: str = "local", **kwargs) -> IBlobStorageProviderProtocol:
    """
    Factory function to create storage adapters.

    Args:
        adapter_type: "local" or "s3"
        **kwargs: Adapter-specific arguments

    Returns:
        Storage adapter instance
    """
    if adapter_type == "local":
        base_path: Any = kwargs.get("base_path", "./agent_data_store")
        return LocalDiskAdapter(base_path=base_path)
    elif adapter_type == "s3":
        bucket_name: Any = kwargs.get("bucket_name")
        if not bucket_name:
            raise ValueError("bucket_name required for S3 adapter")
        region: Any = kwargs.get("region", "us-east-1")
        return S3Adapter(bucket_name=bucket_name, region=region)
    else:
        raise ValueError(f"Unknown adapter type: {adapter_type}")


from agentic_core.L0_routing.config import TESTS_DIR
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_writes_through,
)


class _TombstonedRedisDistributedLock:
    """Tombstoned — see module comment above."""

    def __init__(self, *args, **kwargs):
        raise RuntimeError(
            "RedisDistributedLock is tombstoned. Use agentic_core.cache.get_coordination_cache() for coordination."
        )


def _run_self_tests(self) -> dict:
    """Run internal self-tests."""
    results = {"passed": 0, "failed": 0, TESTS_DIR: []}
    try:
        assert self is not None
        results["passed"] += 1
        results[TESTS_DIR].append({"name": "test_instantiation", "status": "passed"})
    except AssertionError as e:
        results["failed"] += 1
        results[TESTS_DIR].append({"name": "test_instantiation", "status": "failed", "error": str(e)})
    return results


class _TombstonedRedisHotCache:
    """Tombstoned — see module comment above."""

    def __init__(self, *args, **kwargs):
        raise RuntimeError("RedisHotCache is tombstoned. Use agentic_core.cache.get_hot_cache() instead.")


class SignalLedger:
    """
    Simple ledger that logs ExecutionResults to a permanent log file.
    """

    def __init__(self, storage_adapter: IBlobStorageProviderProtocol, session_id: str):
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
        from datetime import datetime

        if hasattr(result, "__dict__"):
            result_dict: Any = result.__dict__
        else:
            result_dict: Any = result
        result_dict["timestamp"] = datetime.utcnow().isoformat()
        result_dict["session_id"] = self.session_id
        json_line: Any = json.dumps(result_dict) + "\n"
        try:
            existing_data: Any = await self.storage.read_blob(self.ledger_key)
            existing_lines: Any = existing_data.decode("utf-8")
        except FileNotFoundError:
            existing_lines: Any = ""
        updated_data: Any = existing_lines + json_line
        await self.storage.write_blob(
            self.ledger_key,
            updated_data.encode("utf-8"),
            metadata={"type": "SignalLedger", "session_id": self.session_id},
        )
        LOGGER.debug(f"Appended result to signal ledger: {self.ledger_key}")

    async def get_results(self) -> list:
        """
        Get all results from the ledger.

        Returns:
            List of result dictionaries
        """
        try:
            data: Any = await self.storage.read_blob(self.ledger_key)
            lines: Any = data.decode("utf-8").strip().split("\n")
            results: Any = []
            for line in lines:
                if line.strip():
                    results.append(json.loads(line))
            return results
        except FileNotFoundError:
            return []

    async def get_phase_summary(self, phase_name: str | None = None) -> dict[str, Any]:
        """
        Get a summary of signals from a specific phase or the most recent phase.

        Args:
            phase_name: Specific phase to get summary for, or None for most recent

        Returns:
            Dictionary with phase summary including signals, results, and recommendations
        """
        results: Any = await self.get_results()
        if not results:
            return {}
        if phase_name:
            phase_results: Any = [r for r in results if r.get("phase") == phase_name]
        else:
            phase_results: Any = []
            if results:
                latest_result: Any = max(results, key=lambda x: x.get("timestamp", ""))
                latest_phase: Any = latest_result.get("phase")
                if latest_phase:
                    phase_results: Any = [r for r in results if r.get("phase") == latest_phase]
        if not phase_results:
            return {}
        summary: Any = {
            "phase": phase_results[0].get("phase", "unknown"),
            "timestamp": phase_results[0].get("timestamp"),
            "total_results": len(phase_results),
            "passed_count": sum(1 for r in phase_results if r.get("passed", False)),
            "failed_count": sum(1 for r in phase_results if not r.get("passed", False)),
            "signals": [],
            "failed_agents": [],
            "recommendations": [],
        }
        for result in phase_results:
            if "result" in result and isinstance(result["result"], dict):
                signals: Any = result["result"].get("signals", [])
                if signals:
                    summary["signals"].extend(signals)
            if not result.get("passed", False):
                agent_name: Any = result.get("agent", "unknown")
                summary["failed_agents"].append(
                    {
                        "agent": agent_name,
                        "error": result.get("error", "Unknown error"),
                        "details": result.get("details", ""),
                    }
                )
        if summary["failed_count"] > 0:
            summary["recommendations"].append(
                f"Phase {summary['phase']} had {summary['failed_count']} failures"
            )
            summary["recommendations"].append("Consider re-running failed agents before proceeding")
        if summary["phase"] == "integrity_seq" and summary["failed_count"] > 0:
            summary["recommendations"].append(
                "CRITICAL: Integrity failures must be resolved before continuing"
            )
        return summary


class _TombstonedHotBrainCache:
    """Tombstoned — see module comment above."""

    def __init__(self, *args, **kwargs):
        raise RuntimeError(
            "HotBrainCache is tombstoned. Use agentic_core.cache.get_coordination_cache() for coordination, or agentic_core.cache.get_hot_cache() for hot caching."
        )
