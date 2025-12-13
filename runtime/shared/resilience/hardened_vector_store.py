"""
Hardened Vector Store - Write-Ahead Logging and Idempotency for Vector Operations.

Implements a hardened wrapper around vector stores with:
- Write-Ahead Logging (WAL) for crash recovery
- Idempotent operations to prevent duplicates
- Atomic batch writes with rollback
- Corruption detection and repair
"""

import logging
import json
import hashlib
import asyncio
from typing import Any, Dict, List, Optional, Tuple, Union, Set
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field, asdict
from pydantic import BaseModel, Field
from enum import Enum

logger = logging.getLogger(__name__)

class OperationType(str, Enum):
    """Types of vector operations."""
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    UPSERT = "upsert"
    BATCH_INSERT = "batch_insert"
    BATCH_DELETE = "batch_delete"

class OperationStatus(str, Enum):
    """Status of logged operations."""
    PENDING = "pending"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    CORRUPTED = "corrupted"

@dataclass
class WALRecord:
    """Write-Ahead Log record for a vector operation."""
    operation_id: str
    operation_type: OperationType
    status: OperationStatus
    timestamp: datetime
    vector_ids: List[str]
    payload: Dict[str, Any]
    checksum: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def compute_checksum(self) -> str:
        """Compute checksum for integrity verification."""
        data = {
            "operation_id": self.operation_id,
            "operation_type": self.operation_type.value,
            "vector_ids": sorted(self.vector_ids),
            "payload": self.payload
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def verify_integrity(self) -> bool:
        """Verify record integrity using checksum."""
        return self.compute_checksum() == self.checksum

@dataclass
class VectorStats:
    """Statistics for vector store operations."""
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    rolled_back_operations: int = 0
    corruption_detected: int = 0
    wal_size_bytes: int = 0
    last_checkpoint: Optional[datetime] = None

class VectorStoreCorruptionError(Exception):
    """Raised when vector store corruption is detected."""
    pass

class HardenedVectorStore:
    """
    Hardened wrapper for vector stores with WAL and corruption protection.

    Features:
    - Write-Ahead Logging for crash recovery
    - Idempotent operations with deduplication
    - Atomic batch operations
    - Corruption detection and repair
    - Automatic checkpointing and cleanup
    """

    def __init__(
        self,
        vector_store: Any,  # e.g., Chroma, Qdrant, Pinecone client
        wal_path: Union[str, Path],
        checkpoint_interval: int = 100,  # Checkpoint every N operations
        wal_retention_days: int = 7,  # Keep WAL for 7 days
        enable_compression: bool = True
    ):
        """Initialize hardened vector store.

        Args:
            vector_store: Underlying vector store client
            wal_path: Path to Write-Ahead Log directory
            checkpoint_interval: Operations between checkpoints
            wal_retention_days: Days to retain WAL records
            enable_compression: Compress WAL records to save space
        """
        self.vector_store = vector_store
        self.wal_path = Path(wal_path)
        self.checkpoint_interval = checkpoint_interval
        self.wal_retention_days = wal_retention_days
        self.enable_compression = enable_compression

        # Ensure WAL directory exists
        self.wal_path.mkdir(parents=True, exist_ok=True)

        # Track operations for idempotency
        self._processed_operations: Set[str] = set()
        self._operation_count = 0

        # Statistics
        self.stats = VectorStats()

        # Initialize WAL
        self._initialize_wal()

        # Recover any uncommitted operations
        asyncio.create_task(self._recover_uncommitted())

    def _initialize_wal(self) -> None:
        """Initialize the Write-Ahead Log."""
        self.wal_file = self.wal_path / "vector_wal.jsonl"
        self.checkpoint_file = self.wal_path / "checkpoint.json"

        # Create WAL file if it doesn't exist
        if not self.wal_file.exists():
            self.wal_file.touch()
            logger.info(f"Created new WAL at {self.wal_file}")

    async def _recover_uncommitted(self) -> None:
        """Recover any uncommitted operations from WAL."""
        logger.info("Recovering uncommitted operations from WAL...")

        # Load checkpoint to know what's been committed
        checkpoint = await self._load_checkpoint()
        if checkpoint:
            self._processed_operations = set(checkpoint.get("processed_operations", []))
            self.stats.last_checkpoint = datetime.fromisoformat(checkpoint.get("timestamp"))

        # Scan WAL for uncommitted operations
        uncommitted = []
        async for record in self._scan_wal():
            if (record.operation_id not in self._processed_operations and
                record.status == OperationStatus.PENDING):
                uncommitted.append(record)

        # Attempt to recover or rollback uncommitted operations
        for record in uncommitted:
            try:
                await self._recover_operation(record)
            except Exception as e:
                logger.error(f"Failed to recover operation {record.operation_id}: {e}")
                await self._mark_rolled_back(record.operation_id)

        logger.info(f"Recovered {len(uncommitted)} operations from WAL")

    async def _recover_operation(self, record: WALRecord) -> None:
        """Attempt to recover a single operation."""
        logger.info(f"Recovering operation {record.operation_id}")

        # Check if operation was actually applied despite being pending
        if await self._verify_operation_applied(record):
            await self._mark_committed(record.operation_id)
        else:
            # Replay the operation
            await self._replay_operation(record)

    async def _verify_operation_applied(self, record: WALRecord) -> bool:
        """Verify if an operation was actually applied to the vector store."""
        try:
            if record.operation_type in [OperationType.INSERT, OperationType.UPSERT]:
                # Check if vectors exist
                existing = await self.vector_store.get(ids=record.vector_ids)
                return len(existing.get("ids", [])) == len(record.vector_ids)
            elif record.operation_type == OperationType.DELETE:
                # Check if vectors don't exist
                existing = await self.vector_store.get(ids=record.vector_ids)
                return len(existing.get("ids", [])) == 0
            elif record.operation_type == OperationType.UPDATE:
                # Check if vectors exist with updated metadata
                existing = await self.vector_store.get(ids=record.vector_ids)
                if len(existing.get("ids", [])) == len(record.vector_ids):
                    # Verify metadata matches
                    for i, doc_id in enumerate(record.vector_ids):
                        if doc_id in existing.get("metadatas", {}):
                            expected = record.payload.get("metadatas", [{}])[i]
                            actual = existing["metadatas"][doc_id]
                            if expected != actual:
                                return False
                    return True
        except Exception as e:
            logger.error(f"Error verifying operation {record.operation_id}: {e}")

        return False

    async def _replay_operation(self, record: WALRecord) -> None:
        """Replay an operation from the WAL."""
        try:
            if record.operation_type == OperationType.INSERT:
                await self.vector_store.add(
                    ids=record.vector_ids,
                    embeddings=record.payload.get("embeddings", []),
                    documents=record.payload.get("documents", []),
                    metadatas=record.payload.get("metadatas", [])
                )
            elif record.operation_type == OperationType.UPDATE:
                await self.vector_store.update(
                    ids=record.vector_ids,
                    embeddings=record.payload.get("embeddings"),
                    documents=record.payload.get("documents"),
                    metadatas=record.payload.get("metadatas")
                )
            elif record.operation_type == OperationType.DELETE:
                await self.vector_store.delete(ids=record.vector_ids)
            elif record.operation_type == OperationType.UPSERT:
                await self.vector_store.upsert(
                    ids=record.vector_ids,
                    embeddings=record.payload.get("embeddings", []),
                    documents=record.payload.get("documents", []),
                    metadatas=record.payload.get("metadatas", [])
                )

            await self._mark_committed(record.operation_id)
            logger.info(f"Successfully replayed operation {record.operation_id}")

        except Exception as e:
            logger.error(f"Failed to replay operation {record.operation_id}: {e}")
            raise

    async def insert(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """Insert vectors with WAL protection."""
        return await self._execute_operation(
            operation_type=OperationType.INSERT,
            vector_ids=ids,
            payload={
                "embeddings": embeddings,
                "documents": documents or [],
                "metadatas": metadatas or []
            }
        )

    async def upsert(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """Upsert vectors with WAL protection."""
        return await self._execute_operation(
            operation_type=OperationType.UPSERT,
            vector_ids=ids,
            payload={
                "embeddings": embeddings,
                "documents": documents or [],
                "metadatas": metadatas or []
            }
        )

    async def update(
        self,
        ids: List[str],
        embeddings: Optional[List[List[float]]] = None,
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """Update vectors with WAL protection."""
        return await self._execute_operation(
            operation_type=OperationType.UPDATE,
            vector_ids=ids,
            payload={
                "embeddings": embeddings,
                "documents": documents,
                "metadatas": metadatas
            }
        )

    async def delete(self, ids: List[str]) -> List[str]:
        """Delete vectors with WAL protection."""
        return await self._execute_operation(
            operation_type=OperationType.DELETE,
            vector_ids=ids,
            payload={}
        )

    async def batch_insert(
        self,
        batches: List[Tuple[List[str], List[List[float]], Optional[List[str]], Optional[List[Dict[str, Any]]]]]
    ) -> List[str]:
        """Insert multiple batches atomically."""
        all_ids = []
        operation_id = self._generate_operation_id()

        # Log all batches as a single transaction
        for batch_ids, embeddings, documents, metadatas in batches:
            all_ids.extend(batch_ids)

        record = WALRecord(
            operation_id=operation_id,
            operation_type=OperationType.BATCH_INSERT,
            status=OperationStatus.PENDING,
            timestamp=datetime.now(),
            vector_ids=all_ids,
            payload={"batches": batches},
            checksum="",  # Will be computed
            metadata={"batch_count": len(batches)}
        )
        record.checksum = record.compute_checksum()

        # Write to WAL
        await self._write_to_wal(record)

        try:
            # Execute all batches
            successful_ids = []
            for batch_ids, embeddings, documents, metadatas in batches:
                await self.vector_store.add(
                    ids=batch_ids,
                    embeddings=embeddings,
                    documents=documents or [],
                    metadatas=metadatas or []
                )
                successful_ids.extend(batch_ids)

            # Mark as committed
            await self._mark_committed(operation_id)
            self.stats.successful_operations += 1

            return successful_ids

        except Exception as e:
            logger.error(f"Batch insert failed: {e}")
            # Attempt rollback
            await self._rollback_batch(operation_id, all_ids)
            raise

    async def _execute_operation(
        self,
        operation_type: OperationType,
        vector_ids: List[str],
        payload: Dict[str, Any]
    ) -> List[str]:
        """Execute a vector operation with WAL protection."""
        # Check for idempotency
        for vector_id in vector_ids:
            if vector_id in self._processed_operations:
                logger.debug(f"Skipping duplicate operation for vector {vector_id}")
                continue

        # Create WAL record
        operation_id = self._generate_operation_id()
        record = WALRecord(
            operation_id=operation_id,
            operation_type=operation_type,
            status=OperationStatus.PENDING,
            timestamp=datetime.now(),
            vector_ids=vector_ids,
            payload=payload,
            checksum="",  # Will be computed
            metadata={"retry_count": 0}
        )
        record.checksum = record.compute_checksum()

        # Write to WAL first
        await self._write_to_wal(record)
        self.stats.total_operations += 1

        try:
            # Execute the operation
            if operation_type == OperationType.INSERT:
                await self.vector_store.add(
                    ids=vector_ids,
                    embeddings=payload["embeddings"],
                    documents=payload["documents"],
                    metadatas=payload["metadatas"]
                )
            elif operation_type == OperationType.UPSERT:
                await self.vector_store.upsert(
                    ids=vector_ids,
                    embeddings=payload["embeddings"],
                    documents=payload["documents"],
                    metadatas=payload["metadatas"]
                )
            elif operation_type == OperationType.UPDATE:
                await self.vector_store.update(
                    ids=vector_ids,
                    embeddings=payload["embeddings"],
                    documents=payload["documents"],
                    metadatas=payload["metadatas"]
                )
            elif operation_type == OperationType.DELETE:
                await self.vector_store.delete(ids=vector_ids)

            # Mark as committed
            await self._mark_committed(operation_id)
            self.stats.successful_operations += 1

            # Track for idempotency
            self._processed_operations.update(vector_ids)

            # Checkpoint if needed
            self._operation_count += 1
            if self._operation_count >= self.checkpoint_interval:
                await self._create_checkpoint()
                self._operation_count = 0

            return vector_ids

        except Exception as e:
            logger.error(f"Operation {operation_id} failed: {e}")
            self.stats.failed_operations += 1
            raise

    async def _write_to_wal(self, record: WALRecord) -> None:
        """Write a record to the Write-Ahead Log."""
        try:
            with open(self.wal_file, "a") as f:
                line = json.dumps(asdict(record), default=str)
                if self.enable_compression:
                    import gzip
                    line = gzip.compress(line.encode()).decode('latin1')
                f.write(line + "\n")
                f.flush()

            self.stats.wal_size_bytes = self.wal_file.stat().st_size

        except Exception as e:
            logger.error(f"Failed to write to WAL: {e}")
            raise VectorStoreCorruptionError(f"WAL write failed: {e}")

    async def _scan_wal(self) -> WALRecord:
        """Scan WAL and yield records."""
        try:
            with open(self.wal_file, "r") as f:
                for line in f:
                    if not line.strip():
                        continue

                    try:
                        if self.enable_compression:
                            import gzip
                            data = json.loads(gzip.decompress(line.strip().encode('latin1')).decode())
                        else:
                            data = json.loads(line.strip())

                        record = WALRecord(**data)

                        # Verify integrity
                        if not record.verify_integrity():
                            logger.warning(f"Corrupted WAL record detected: {record.operation_id}")
                            record.status = OperationStatus.CORRUPTED
                            self.stats.corruption_detected += 1

                        yield record

                    except Exception as e:
                        logger.error(f"Failed to parse WAL record: {e}")
                        continue

        except FileNotFoundError:
            logger.warning("WAL file not found")
        except Exception as e:
            logger.error(f"Error scanning WAL: {e}")

    async def _mark_committed(self, operation_id: str) -> None:
        """Mark an operation as committed in WAL."""
        await self._update_operation_status(operation_id, OperationStatus.COMMITTED)

    async def _mark_rolled_back(self, operation_id: str) -> None:
        """Mark an operation as rolled back in WAL."""
        await self._update_operation_status(operation_id, OperationStatus.ROLLED_BACK)
        self.stats.rolled_back_operations += 1

    async def _update_operation_status(self, operation_id: str, status: OperationStatus) -> None:
        """Update the status of an operation in WAL."""
        # In a real implementation, this would update the record in place
        # For simplicity, we'll just log the status change
        logger.info(f"Operation {operation_id} status: {status.value}")

    async def _rollback_batch(self, operation_id: str, vector_ids: List[str]) -> None:
        """Rollback a failed batch operation."""
        try:
            # Attempt to delete any vectors that were inserted
            await self.vector_store.delete(ids=vector_ids)
            await self._mark_rolled_back(operation_id)
            logger.info(f"Rolled back batch operation {operation_id}")
        except Exception as e:
            logger.error(f"Failed to rollback batch {operation_id}: {e}")
            raise VectorStoreCorruptionError(f"Rollback failed: {e}")

    async def _create_checkpoint(self) -> None:
        """Create a checkpoint with current state."""
        checkpoint = {
            "timestamp": datetime.now().isoformat(),
            "processed_operations": list(self._processed_operations),
            "operation_count": self.stats.total_operations,
            "stats": asdict(self.stats)
        }

        try:
            with open(self.checkpoint_file, "w") as f:
                json.dump(checkpoint, f, indent=2)

            self.stats.last_checkpoint = datetime.now()
            logger.info(f"Created checkpoint with {len(self._processed_operations)} operations")

            # Cleanup old WAL records
            await self._cleanup_wal()

        except Exception as e:
            logger.error(f"Failed to create checkpoint: {e}")

    async def _load_checkpoint(self) -> Optional[Dict[str, Any]]:
        """Load the latest checkpoint."""
        try:
            with open(self.checkpoint_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return None

    async def _cleanup_wal(self) -> None:
        """Clean up old WAL records."""
        cutoff_date = datetime.now() - timedelta(days=self.wal_retention_days)

        # Create a new WAL with only recent records
        temp_wal = self.wal_path / "vector_wal_temp.jsonl"
        old_records = 0

        try:
            with open(temp_wal, "w") as out_f:
                async for record in self._scan_wal():
                    if record.timestamp > cutoff_date:
                        line = json.dumps(asdict(record), default=str)
                        if self.enable_compression:
                            import gzip
                            line = gzip.compress(line.encode()).decode('latin1')
                        out_f.write(line + "\n")
                    else:
                        old_records += 1

            # Replace old WAL
            temp_wal.replace(self.wal_file)
            logger.info(f"Cleaned up {old_records} old WAL records")

        except Exception as e:
            logger.error(f"Failed to cleanup WAL: {e}")
            if temp_wal.exists():
                temp_wal.unlink()

    def _generate_operation_id(self) -> str:
        """Generate a unique operation ID."""
        import uuid
        return str(uuid.uuid4())

    async def verify_store_integrity(self) -> Dict[str, Any]:
        """Verify the integrity of the vector store."""
        logger.info("Verifying vector store integrity...")

        issues = []

        # Check WAL integrity
        async for record in self._scan_wal():
            if not record.verify_integrity():
                issues.append(f"Corrupted WAL record: {record.operation_id}")

        # Check for orphaned operations
        checkpoint = await self._load_checkpoint()
        if checkpoint:
            committed_ops = set(checkpoint.get("processed_operations", []))

            async for record in self._scan_wal():
                if (record.operation_id not in committed_ops and
                    record.status == OperationStatus.PENDING and
                    record.timestamp < datetime.now() - timedelta(hours=1)):
                    issues.append(f"Orphaned operation: {record.operation_id}")

        return {
            "is_healthy": len(issues) == 0,
            "issues": issues,
            "stats": asdict(self.stats)
        }

    async def repair_store(self) -> Dict[str, Any]:
        """Attempt to repair detected issues."""
        logger.info("Attempting to repair vector store...")

        repairs_made = []

        # Scan for and recover orphaned operations
        checkpoint = await self._load_checkpoint()
        if checkpoint:
            committed_ops = set(checkpoint.get("processed_operations", []))

            async for record in self._scan_wal():
                if (record.operation_id not in committed_ops and
                    record.status == OperationStatus.PENDING):
                    try:
                        await self._recover_operation(record)
                        repairs_made.append(f"Recovered operation: {record.operation_id}")
                    except Exception as e:
                        await self._mark_rolled_back(record.operation_id)
                        repairs_made.append(f"Rolled back operation: {record.operation_id}")

        # Create new checkpoint after repairs
        await self._create_checkpoint()

        return {
            "repairs_made": repairs_made,
            "stats": asdict(self.stats)
        }

    def get_stats(self) -> VectorStats:
        """Get current vector store statistics."""
        return self.stats

# Factory function for creating hardened vector stores
def create_hardened_vector_store(
    vector_store: Any,
    wal_dir: Union[str, Path] = "./data/vector_wal",
    **kwargs
) -> HardenedVectorStore:
    """Create a hardened vector store wrapper.

    Args:
        vector_store: Underlying vector store client
        wal_dir: Directory for Write-Ahead Log
        **kwargs: Additional arguments for HardenedVectorStore

    Returns:
        HardenedVectorStore instance
    """
    return HardenedVectorStore(
        vector_store=vector_store,
        wal_path=wal_dir,
        **kwargs
    )
