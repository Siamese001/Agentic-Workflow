"""Canonical Store - Original File Storage

Implements spec-compliant Canonical Store from Agentic Retrieval Models v9:
- Stores original files, telemetry, and blobs
- Supports S3 and PostgreSQL backends
- Content-addressable storage
- Immutable artifact persistence
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

# Lazy import for optional S3 dependencies
try:
    import botocore.exceptions

    _HAS_BOTOCORE = True
except ImportError:
    _HAS_BOTOCORE = False
    botocore = None  # type: ignore

Logger = logging.getLogger(__name__)


@dataclass
class StoredArtifact:
    """Stored artifact metadata."""

    artifact_id: str  # SHA-256 content hash
    content_hash: str
    storage_backend: str
    storage_path: str
    content_type: str
    size_bytes: int
    metadata: dict[str, Any] = field(default_factory=dict)
    stored_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    retention_days: int = 365


class StorageBackend(ABC):
    """Abstract storage backend."""

    @abstractmethod
    def store(self, content: bytes, metadata: dict[str, Any]) -> StoredArtifact:
        """Store content and return artifact info."""
        pass

    @abstractmethod
    def retrieve(self, artifact_id: str) -> bytes | None:
        """Retrieve content by artifact ID."""
        pass

    @abstractmethod
    def exists(self, artifact_id: str) -> bool:
        """Check if artifact exists."""
        pass

    @abstractmethod
    def delete(self, artifact_id: str) -> bool:
        """Delete artifact."""
        pass


class LocalFileBackend(StorageBackend):
    """Local filesystem storage backend."""

    def __init__(self, base_path: str = "artifacts/canonical_store"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._metadata_path = self.base_path / "metadata.json"
        self._metadata: dict[str, dict] = self._load_metadata()

    @staticmethod
    def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
        temp_path = path.with_suffix(f"{path.suffix}.tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, path)

    def _validated_content_path(self, artifact_id: str) -> Path:
        record = self._metadata[artifact_id]
        content_hash = record.get("content_hash", artifact_id)
        if not isinstance(content_hash, str) or len(content_hash) != 64:
            raise ValueError(f"Invalid content hash for artifact {artifact_id}")
        if any(ch not in "0123456789abcdef" for ch in content_hash):
            raise ValueError(f"Non-hex content hash for artifact {artifact_id}")
        return self._content_path(content_hash)

    def _load_metadata(self) -> dict:
        if self._metadata_path.exists():
            with open(self._metadata_path, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_metadata(self) -> None:
        self._atomic_write_json(self._metadata_path, self._metadata)

    def _content_path(self, content_hash: str) -> Path:
        # Use first 2 chars as subdir for distribution
        subdir = content_hash[:2]
        return self.base_path / "data" / subdir / content_hash

    def store(self, content: bytes, metadata: dict[str, Any]) -> StoredArtifact:
        content_hash = hashlib.sha256(content).hexdigest()
        artifact_id = content_hash

        path = self._content_path(content_hash)
        path.parent.mkdir(parents=True, exist_ok=True)

        temp_path = path.with_suffix(".tmp")
        with open(temp_path, "wb") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, path)

        artifact = StoredArtifact(
            artifact_id=artifact_id,
            content_hash=content_hash,
            storage_backend="local_file",
            storage_path=str(path),
            content_type=metadata.get("content_type", "application/octet-stream"),
            size_bytes=len(content),
            metadata=metadata,
        )

        self._metadata[artifact_id] = {
            "content_hash": content_hash,
            "storage_path": str(path),
            "content_type": artifact.content_type,
            "size_bytes": artifact.size_bytes,
            "metadata": metadata,
            "stored_at": artifact.stored_at,
        }
        self._save_metadata()

        Logger.info(f"Stored artifact: {artifact_id[:16]}... ({len(content)} bytes)")
        return artifact

    def retrieve(self, artifact_id: str) -> bytes | None:
        if artifact_id not in self._metadata:
            return None

        path = self._validated_content_path(artifact_id)
        if not path.exists():
            return None

        with open(path, "rb") as f:
            return f.read()

    def exists(self, artifact_id: str) -> bool:
        return artifact_id in self._metadata

    def delete(self, artifact_id: str) -> bool:
        if artifact_id not in self._metadata:
            return False

        path = self._validated_content_path(artifact_id)
        if path.exists():
            path.unlink()

        del self._metadata[artifact_id]
        self._save_metadata()
        return True


class PostgresBackend(StorageBackend):
    """PostgreSQL storage backend (for metadata and small blobs)."""

    def __init__(self, connection_string: str | None = None):
        self.connection_string = connection_string or "postgresql://localhost/canonical_store"
        self._init_db()

    def _init_db(self) -> None:
        try:
            import psycopg2

            conn = psycopg2.connect(self.connection_string)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS artifacts (
                    artifact_id VARCHAR(64) PRIMARY KEY,
                    content_hash VARCHAR(64) NOT NULL,
                    content_type VARCHAR(128),
                    size_bytes INTEGER,
                    content BYTEA,
                    metadata JSONB,
                    stored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    retention_days INTEGER DEFAULT 365
                )
            """)

            # Index on content_hash for deduplication
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_content_hash ON artifacts(content_hash)
            """)

            conn.commit()
            conn.close()
            Logger.info("Initialized PostgreSQL canonical store")

        except ImportError:  # guardian: allow-log-and-swallow -- psycopg2 optional: Postgres backend disabled, other backends continue
            Logger.warning("psycopg2 not available, Postgres backend disabled")
        except (  # guardian: allow-log-and-swallow -- Postgres init: non-fatal, store operates without Postgres backend
            psycopg2.Error,
            OSError,
            ValueError,
            RuntimeError,
        ) as e:
            Logger.error(f"Failed to init PostgreSQL backend: {e}")

    def store(self, content: bytes, metadata: dict[str, Any]) -> StoredArtifact:
        import psycopg2

        content_hash = hashlib.sha256(content).hexdigest()
        artifact_id = content_hash

        conn = psycopg2.connect(self.connection_string)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO artifacts (
                artifact_id, content_hash, content_type, size_bytes,
                content, metadata, retention_days
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (artifact_id) DO NOTHING
        """,
            (
                artifact_id,
                content_hash,
                metadata.get("content_type", "application/octet-stream"),
                len(content),
                content,
                json.dumps(metadata),
                metadata.get("retention_days", 365),
            ),
        )

        conn.commit()
        conn.close()

        artifact = StoredArtifact(
            artifact_id=artifact_id,
            content_hash=content_hash,
            storage_backend="postgresql",
            storage_path=f"pg://artifacts/{artifact_id}",
            content_type=metadata.get("content_type", "application/octet-stream"),
            size_bytes=len(content),
            metadata=metadata,
        )

        Logger.info(f"Stored artifact to Postgres: {artifact_id[:16]}...")
        return artifact

    def retrieve(self, artifact_id: str) -> bytes | None:
        try:
            import psycopg2

            conn = psycopg2.connect(self.connection_string)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT content FROM artifacts WHERE artifact_id = %s
            """,
                (artifact_id,),
            )

            row = cursor.fetchone()
            conn.close()

            return row[0] if row else None

        except ImportError as e:  # guardian: allow-return-none-swallow -- psycopg2 unavailable: non-fatal, treated as cache miss
            Logger.error(f"Failed to retrieve from Postgres: {e}")
            return None
        except (  # guardian: allow-return-none-swallow -- Postgres retrieve: non-fatal, treated as cache miss
            psycopg2.Error,
            OSError,
            ValueError,
            RuntimeError,
        ) as e:
            Logger.error(f"Failed to retrieve from Postgres: {e}")
            return None

    def exists(self, artifact_id: str) -> bool:
        try:
            import psycopg2

            conn = psycopg2.connect(self.connection_string)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT 1 FROM artifacts WHERE artifact_id = %s
            """,
                (artifact_id,),
            )

            exists = cursor.fetchone() is not None
            conn.close()
            return exists

        except psycopg2.Error as e:
            Logger.debug(f"Postgres exists check failed: {e}")
            return False
        except ImportError as e:
            Logger.error(f"Postgres exists check failed: {e}")
            return False
        except (OSError, ValueError, RuntimeError) as e:
            Logger.error(f"Postgres exists check failed: {e}")
            return False

    def delete(self, artifact_id: str) -> bool:
        try:
            import psycopg2

            conn = psycopg2.connect(self.connection_string)
            cursor = conn.cursor()

            cursor.execute(
                """
                DELETE FROM artifacts WHERE artifact_id = %s
            """,
                (artifact_id,),
            )

            deleted = cursor.rowcount > 0
            conn.commit()
            conn.close()
            return deleted

        except psycopg2.Error as e:
            Logger.debug(f"Postgres delete failed: {e}")
            return False
        except ImportError as e:
            Logger.error(f"Postgres delete failed: {e}")
            return False
        except (OSError, ValueError, RuntimeError) as e:
            Logger.error(f"Postgres delete failed: {e}")
            return False


class S3Backend(StorageBackend):
    """S3-compatible object storage backend."""

    def __init__(
        self,
        bucket: str = "canonical-store",
        endpoint: str | None = None,
        region: str = "us-east-1",
    ):
        self.bucket = bucket
        self.endpoint = endpoint
        self.region = region
        self._s3 = None

    def _get_s3_client(self):
        if self._s3 is None:
            try:
                import boto3

                self._s3 = boto3.client(
                    "s3",
                    region_name=self.region,
                    endpoint_url=self.endpoint,
                )
            except ImportError:
                raise ImportError("boto3 is required for S3 backend")
        return self._s3

    def store(self, content: bytes, metadata: dict[str, Any]) -> StoredArtifact:
        content_hash = hashlib.sha256(content).hexdigest()
        artifact_id = content_hash

        key = f"artifacts/{content_hash[:2]}/{content_hash}"

        s3 = self._get_s3_client()
        s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=content,
            ContentType=metadata.get("content_type", "application/octet-stream"),
            Metadata={k: str(v) for k, v in metadata.items()},
        )

        artifact = StoredArtifact(
            artifact_id=artifact_id,
            content_hash=content_hash,
            storage_backend="s3",
            storage_path=f"s3://{self.bucket}/{key}",
            content_type=metadata.get("content_type", "application/octet-stream"),
            size_bytes=len(content),
            metadata=metadata,
        )

        Logger.info(f"Stored artifact to S3: {artifact_id[:16]}...")
        return artifact

    def retrieve(self, artifact_id: str) -> bytes | None:
        key = f"artifacts/{artifact_id[:2]}/{artifact_id}"

        try:
            s3 = self._get_s3_client()
            response = s3.get_object(Bucket=self.bucket, Key=key)
            return response["Body"].read()
        except botocore.exceptions.ClientError as e:  # guardian: allow-return-none-swallow -- S3 client error: 404 treated as miss, other errors logged and returned as miss
            code = e.response.get("Error", {}).get("Code")
            if code in {"404", "NoSuchKey"}:
                return None
            Logger.error(f"Failed to retrieve from S3: {e}")
            return None
        except (  # guardian: allow-return-none-swallow -- S3 retrieve: non-fatal, treated as cache miss
            ImportError,
            OSError,
            KeyError,
            TypeError,
            ValueError,
        ) as e:
            Logger.error(f"Failed to retrieve from S3: {e}")
            return None

    def exists(self, artifact_id: str) -> bool:
        key = f"artifacts/{artifact_id[:2]}/{artifact_id}"

        try:
            s3 = self._get_s3_client()
            s3.head_object(Bucket=self.bucket, Key=key)
            return True
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            else:
                Logger.debug(f"S3 exists check failed: {e}")
                return False
        except (ImportError, OSError, KeyError, TypeError, ValueError) as e:
            Logger.error(f"S3 exists check failed: {e}")
            return False

    def delete(self, artifact_id: str) -> bool:
        key = f"artifacts/{artifact_id[:2]}/{artifact_id}"

        try:
            s3 = self._get_s3_client()
            s3.delete_object(Bucket=self.bucket, Key=key)
            return True
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            else:
                Logger.debug(f"S3 delete failed: {e}")
                return False
        except (ImportError, OSError, KeyError, TypeError, ValueError) as e:
            Logger.error(f"S3 delete failed: {e}")
            return False


class CanonicalStore:
    """Canonical Store for original file storage.

    Provides content-addressable storage with multiple backend options.
    """

    def __init__(
        self,
        backend: str = "local",
        backend_config: dict[str, Any] | None = None,
    ):
        """Initialize canonical store.

        Args:
            backend: Backend type (local, postgres, s3)
            backend_config: Backend configuration
        """
        backend_config = backend_config or {}

        if backend == "local":
            self._backend: StorageBackend = LocalFileBackend(
                backend_config.get("path", "artifacts/canonical_store"),
            )
        elif backend == "postgres":
            self._backend = PostgresBackend(backend_config.get("connection_string"))
        elif backend == "s3":
            self._backend = S3Backend(
                bucket=backend_config.get("bucket", "canonical-store"),
                endpoint=backend_config.get("endpoint"),
                region=backend_config.get("region", "us-east-1"),
            )
        else:
            raise ValueError(f"Unknown backend: {backend}")

        self.backend_type = backend
        self._store_count = 0

    def store_file(
        self,
        file_path: str | Path,
        content_type: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> StoredArtifact:
        """Store a file in the canonical store.

        Args:
            file_path: Path to file
            content_type: Content type (auto-detected if None)
            metadata: Additional metadata

        Returns:
            StoredArtifact with artifact ID
        """
        _trace_id = f"canonical_store_{self._store_count}"
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "CanonicalStore.store_file")

        file_path = Path(file_path)

        with open(file_path, "rb") as f:
            content = f.read()

        # Auto-detect content type
        if content_type is None:
            content_type = self._detect_content_type(file_path)

        meta = {
            "original_path": str(file_path),
            "original_name": file_path.name,
            "content_type": content_type,
            **(metadata or {}),
        }

        artifact = self._backend.store(content, meta)

        # _emit_stores_artifact(_trace_id, artifact.artifact_id, str(file_path))

        self._store_count += 1
        Logger.info(f"Stored file: {file_path.name} -> {artifact.artifact_id[:16]}...")

        return artifact

    def store_content(
        self,
        content: bytes,
        content_type: str = "application/octet-stream",
        metadata: dict[str, Any] | None = None,
    ) -> StoredArtifact:
        """Store raw content.

        Args:
            content: Content bytes
            content_type: Content type
            metadata: Additional metadata

        Returns:
            StoredArtifact with artifact ID
        """
        _trace_id = f"canonical_store_{self._store_count}"
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "CanonicalStore.store_content")

        meta = {
            "content_type": content_type,
            **(metadata or {}),
        }

        artifact = self._backend.store(content, meta)

        # _emit_stores_artifact(_trace_id, artifact.artifact_id, "inline_content")

        self._store_count += 1

        return artifact

    def retrieve(self, artifact_id: str) -> bytes | None:
        """Retrieve content by artifact ID.

        Args:
            artifact_id: Artifact identifier

        Returns:
            Content bytes if found
        """
        return self._backend.retrieve(artifact_id)

    def exists(self, artifact_id: str) -> bool:
        """Check if artifact exists."""
        return self._backend.exists(artifact_id)

    def _detect_content_type(self, file_path: Path) -> str:
        """Auto-detect content type from extension."""
        ext = file_path.suffix.lower()

        mime_types = {
            ".txt": "text/plain",
            ".md": "text/markdown",
            ".py": "text/x-python",
            ".json": "application/json",
            ".pdf": "application/pdf",
            ".html": "text/html",
            ".csv": "text/csv",
            ".xml": "application/xml",
        }

        return mime_types.get(ext, "application/octet-stream")

    def get_stats(self) -> dict[str, Any]:
        """Get store statistics."""
        return {
            "backend": self.backend_type,
            "store_count": self._store_count,
        }


# Global instance
_global_canonical_store: CanonicalStore | None = None


def get_global_canonical_store() -> CanonicalStore:
    """Get or create global canonical store."""
    global _global_canonical_store
    if _global_canonical_store is None:
        _global_canonical_store = CanonicalStore()
    return _global_canonical_store


def store_file(file_path: str | Path) -> StoredArtifact:
    """Convenience function to store a file."""
    return get_global_canonical_store().store_file(file_path)


def store_content(content: bytes, content_type: str = "application/octet-stream") -> StoredArtifact:
    """Convenience function to store content."""
    return get_global_canonical_store().store_content(content, content_type)


def retrieve_artifact(artifact_id: str) -> bytes | None:
    """Convenience function to retrieve artifact."""
    return get_global_canonical_store().retrieve(artifact_id)
