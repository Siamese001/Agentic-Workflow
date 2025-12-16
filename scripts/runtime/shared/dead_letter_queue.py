"""Dead Letter Queue - Handling permanently failed envelopes.

This module implements a dead letter queue (DLQ) to capture and manage
envelopes that have permanently failed processing, ensuring no data
is lost and enabling debugging and manual recovery.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles

LOGGER = logging.getLogger(__name__)


class FailureReason(str, Enum):
    """Reasons for envelope failure."""
    VALIDATION_FAILED = "validation_failed"
    PROCESSING_ERROR = "processing_error"
    TIMEOUT = "timeout"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    MAX_RETRIES_EXCEEDED = "max_retries_exceeded"
    CORRUPTED_PAYLOAD = "corrupted_payload"
    UNKNOWN = "unknown"


class DeadLetterStatus(str, Enum):
    """Status of dead letter items."""
    PENDING_REVIEW = "pending_review"
    UNDER_INVESTIGATION = "under_investigation"
    RESOLVED = "resolved"
    PERMANENTLY_FAILED = "permanently_failed"
    REQUEUED = "requeued"


@dataclass
class DeadLetterItem:
    """An item in the dead letter queue."""
    envelope: "SignalEnvelope"  # Forward declaration for SignalEnvelope
    failure_reason: FailureReason
    failure_stage: str
    error_message: str
    timestamp: datetime
    retry_count: int = 0
    max_retries: int = 3
    status: DeadLetterStatus = DeadLetterStatus.PENDING_REVIEW
    investigation_notes: Optional[str] = None
    resolved_by: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            "envelope": self.envelope.dict() if hasattr(self.envelope,
                'dict') else self.envelope.to_dict(),

            "failure_reason": self.failure_reason.value,
            "failure_stage": self.failure_stage,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat(),
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "status": self.status.value,
            "investigation_notes": self.investigation_notes,
            "resolved_by": self.resolved_by,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeadLetterItem":
        """Create from dictionary.

        Args:
            data: Dictionary data

        Returns:
            DeadLetterItem instance
        """
        envelope_data = data["envelope"]
        # Assuming SignalEnvelope has a classmethod from_dict
        if hasattr(SignalEnvelope, "from_dict"):
            ENVELOPE = SignalEnvelope.from_dict(envelope_data)
        elif hasattr(SignalEnvelope, "parse_obj"): # Common in Pydantic models
            ENVELOPE = SignalEnvelope.parse_obj(envelope_data)
        else:
            # Fallback or raise an error if SignalEnvelope structure is unknown
            raise NotImplementedError("SignalEnvelope.from_dict or SignalEnvelope.parse_obj not found")

        return cls(
            envelope=ENVELOPE,
            failure_reason=FailureReason(data["failure_reason"]),
            failure_stage=data["failure_stage"],
            error_message=data["error_message"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
            status=DeadLetterStatus(data.get("status", "pending_review")),
            investigation_notes=data.get("investigation_notes"),
            resolved_by=data.get("resolved_by"),
            metadata=data.get("metadata", {})
        )

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # Forward declaration for SignalEnvelope if it's defined elsewhere
    # This is a placeholder, replace with the actual import if SignalEnvelope is in another file
    class SignalEnvelope:
        trace_id: str
        def dict(self) -> Dict[str, Any]: ...
        def to_dict(self) -> Dict[str, Any]: ...
        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> "SignalEnvelope": ...
        @classmethod
        def parse_obj(cls, data: Dict[str, Any]) -> "SignalEnvelope": ...

class DeadLetterStorage(ABC):
    """Abstract base for dead letter storage."""

    @abstractmethod
    async def add(self, item: DeadLetterItem) -> bool:
        """Add item to dead letter queue.

        Args:
            item: Dead letter item

        Returns:
            True if added successfully
        """
        pass

    @abstractmethod
    async def get(self, item_id: str) -> Optional[DeadLetterItem]:
        """Get item by ID.

        Args:
            item_id: Item ID

        Returns:
            Dead letter item if found
        """
        pass

    @abstractmethod
    async def list(
        self,
        status: Optional[DeadLetterStatus] = None,
        limit: int = 100
    ) -> List[DeadLetterItem]:
        """List items in queue.

        Args:
            status: Optional status filter
            limit: Maximum items to return

        Returns:
            List of dead letter items
        """
        pass

    @abstractmethod
    async def update_status(self,
        item_id: str,
        status: DeadLetterStatus,
        notes: Optional[str] = None) -> bool:
        """Update item status.

        Args:
            item_id: Item ID
            status: New status
            notes: Optional investigation notes

        Returns:
            True if updated successfully
        """
        pass

    @abstractmethod
    async def delete(self, item_id: str) -> bool:
        """Delete item from queue.

        Args:
            item_id: Item ID

        Returns:
            True if deleted successfully
        """
        pass

    @abstractmethod
    async def cleanup(self, older_than: timedelta) -> int:
        """Clean up old resolved items.

        Args:
            older_than: Age threshold for cleanup

        Returns:
            Number of items cleaned up
        """
        pass

class FileDeadLetterStorage(DeadLetterStorage):
    """File-based dead letter storage."""

    def __init__(self, storage_path: str):
        """Initialize file storage.

        Args:
            storage_path: Directory to store dead letters
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (self.storage_path / "pending").mkdir(exist_ok=True)
        (self.storage_path / "investigation").mkdir(exist_ok=True)
        (self.storage_path / "resolved").mkdir(exist_ok=True)

    def _get_item_path(self, item: DeadLetterItem) -> Path:
        """Get file path for item.

        Args:
            item: Dead letter item

        Returns:
            File path
        """
        status_dir = {
            DeadLetterStatus.PENDING_REVIEW: "pending",
            DeadLetterStatus.UNDER_INVESTIGATION: "investigation",
            DeadLetterStatus.RESOLVED: "resolved",
            DeadLetterStatus.PERMANENTLY_FAILED: "resolved",
            DeadLetterStatus.REQUEUED: "resolved"
        }.get(item.status, "pending")

        return self.storage_path / status_dir / f"{item.envelope.trace_id}.json"

    async def add(self, item: DeadLetterItem) -> bool:
        """Add item to dead letter queue.

        Args:
            item: Dead letter item

        Returns:
            True if added successfully
        """
        try:
            path = self._get_item_path(item)
            data = item.to_dict()

            # Atomic write
            temp_path = path.with_suffix(".tmp")
            async with aiofiles.open(temp_path, 'w') as f:
                await f.write(json.dumps(data, indent=2))

            await aiofiles.os.rename(temp_path, path)

            LOGGER.warning(f"Added envelope {item.envelope.trace_id} to dead letter queue: {item.failure_reason}")
            return True

        except Exception as e:
LOGGER.error(f"Failed to add to dead letter queue: {e}")
            return False

    async def get(self, item_id: str) -> Optional[DeadLetterItem]:
        """Get item by ID.

        Args:
            item_id: Item ID (trace_id)

        Returns:
            Dead letter item if found
        """
        # Search all status directories
        for status_dir in ["pending", "investigation", "resolved"]:
            path = self.storage_path / status_dir / f"{item_id}.json"
            if path.exists():
                try:
                    async with aiofiles.open(path, 'r') as f:
                        content = await f.read()
                    data = json.loads(content)
                    return DeadLetterItem.from_dict(data)
                except Exception as e:
LOGGER.error(f"Failed to read dead letter item {item_id}: {e}")

        return None

    async def list(
        self,
        status: Optional[DeadLetterStatus] = None,
        limit: int = 100
    ) -> List[DeadLetterItem]:
        """List items in queue.

        Args:
            status: Optional status filter
            limit: Maximum items to return

        Returns:
            List of dead letter items
        """
        items = []

        # Determine which directories to search
        if status:
            status_dirs = {
                DeadLetterStatus.PENDING_REVIEW: ["pending"],
                DeadLetterStatus.UNDER_INVESTIGATION: ["investigation"],
                DeadLetterStatus.RESOLVED: ["resolved"],
                DeadLetterStatus.PERMANENTLY_FAILED: ["resolved"],
                DeadLetterStatus.REQUEUED: ["resolved"]
            }.get(status, ["pending", "investigation", "resolved"])
        else:
            status_dirs = ["pending", "investigation", "resolved"]

        # Search directories
        for status_dir in status_dirs:
            dir_path = self.storage_path / status_dir
            if not dir_path.exists():
                continue

            for file_path in dir_path.glob("*.json"):
                if len(items) >= limit:
                    break

                try:
                    async with aiofiles.open(file_path, 'r') as f:
                        content = await f.read()
                    data = json.loads(content)
                    item = DeadLetterItem.from_dict(data)

                    # Filter by status if specified
                    if not status or item.status == status:
                        items.append(item)

                except Exception as e:
LOGGER.error(f"Failed to read dead letter file {file_path}: {e}")

        # Sort by timestamp (newest first)
        items.sort(key=lambda x: x.timestamp, reverse=True)
        return items[:limit]

    async def update_status(self,
        item_id: str,
        status: DeadLetterStatus,
        notes: Optional[str] = None) -> bool:
        """Update item status.

        Args:
            item_id: Item ID
            status: New status
            notes: Optional investigation notes

        Returns:
            True if updated successfully
        """
        item = await self.get(item_id)
        if not item:
            return False

        # Update item
        item.status = status
        if notes:
            item.investigation_notes = notes

        # Get old and new paths based on the potentially updated status
        old_path = self._get_item_path(item) # This needs to be before updating item.status if status affects dir
        item.status = status # Ensure status is updated before getting new path
        new_path = self._get_item_path(item)


        try:
            # Save updated data
            data = item.to_dict()
            # If the status changed, the item will be moved. We should write to the new path.
            async with aiofiles.open(new_path, 'w') as f:
                await f.write(json.dumps(data, indent=2))

            # Move if directory changed
            if old_path.parent != new_path.parent:
                await aiofiles.os.rename(old_path, new_path)

            LOGGER.info(f"Updated dead letter item {item_id} to status {status.value}")
            return True

        except Exception as e:
LOGGER.error(f"Failed to update dead letter item {item_id}: {e}")
            return False

    async def delete(self, item_id: str) -> bool:
        """Delete item from queue.

        Args:
            item_id: Item ID

        Returns:
            True if deleted successfully
        """
        item = await self.get(item_id)
        if not item:
            return False

        try:
            path = self._get_item_path(item)
            await aiofiles.os.remove(path)
            LOGGER.info(f"Deleted dead letter item {item_id}")
            return True

        except Exception as e:
LOGGER.error(f"Failed to delete dead letter item {item_id}: {e}")
            return False

    async def cleanup(self, older_than: timedelta) -> int:
        """Clean up old resolved items.

        Args:
            older_than: Age threshold for cleanup

        Returns:
            Number of items cleaned up
        """
        count = 0
        cutoff = datetime.utcnow() - older_than

        # Only clean resolved directory
        resolved_dir = self.storage_path / "resolved"
        if not resolved_dir.exists():
            return 0

        for file_path in resolved_dir.glob("*.json"):
            try:
                # Check file modification time
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mtime < cutoff:
                    await aiofiles.os.remove(file_path)
                    count += 1

            except Exception as e:
LOGGER.error(f"Failed to cleanup dead letter file {file_path}: {e}")

        LOGGER.info(f"Cleaned up {count} old dead letter items")
        return count

class DeadLetterQueue:
    """Manages dead letter envelopes for debugging and recovery."""

    def __init__(self, storage: Optional[DeadLetterStorage] = None):
        """Initialize dead letter queue.

        Args:
            storage: Storage backend (uses file storage if not provided)
        """
        self._storage = storage or FileDeadLetterStorage("./dead_letters")

        # Statistics
        self._stats = {
            "total_failed": 0,
            "by_reason": {},
            "by_status": {},
            "resolved": 0,
            "requeued": 0
        }

        LOGGER.info("Initialized DeadLetterQueue")

    async def add_failed_envelope(
        self,
        envelope: "SignalEnvelope",
        failure_reason: FailureReason,
        failure_stage: str,
        error_message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add failed envelope to dead letter queue.

        Args:
            envelope: Failed envelope
            failure_reason: Reason for failure
            failure_stage: Stage where failure occurred
            error_message: Error message
            metadata: Optional metadata

        Returns:
            True if added successfully
        """
        item = DeadLetterItem(
            envelope=envelope,
            failure_reason=failure_reason,
            failure_stage=failure_stage,
            error_message=error_message,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )

        success = await self._storage.add(item)

        if success:
            self._stats["total_failed"] += 1
            reason_key = failure_reason.value
            self._stats["by_reason"][reason_key] = self._stats["by_reason"].get(reason_key, 0) + 1
            status_key = item.status.value
            self._stats["by_status"][status_key] = self._stats["by_status"].get(status_key, 0) + 1

        return success

    async def get_failed_envelope(self, trace_id: str) -> Optional[DeadLetterItem]:
        """Get failed envelope by trace ID.

        Args:
            trace_id: Trace ID of envelope

        Returns:
            Dead letter item if found
        """
        return await self._storage.get(trace_id)

    async def list_failed_envelopes(
        self,
        status: Optional[DeadLetterStatus] = None,
        limit: int = 100
    ) -> List[DeadLetterItem]:
        """List failed envelopes.

        Args:
            status: Optional status filter
            limit: Maximum items to return

        Returns:
            List of dead letter items
        """
        return await self._storage.list(status, limit)

    async def investigate(self, trace_id: str, investigator: str) -> bool:
        """Mark envelope as under investigation.

        Args:
            trace_id: Trace ID of envelope
            investigator: Who is investigating

        Returns:
            True if updated successfully
        """
        success = await self._storage.update_status(
            trace_id,
            DeadLetterStatus.UNDER_INVESTIGATION,
            f"Investigation started by {investigator}"
        )
        if success:
            # Update stats if the item was successfully moved to investigation
            item = await self._storage.get(trace_id) # Re-fetch to get current status
            if item and item.status == DeadLetterStatus.UNDER_INVESTIGATION:
                old_status = DeadLetterStatus.PENDING_REVIEW # Assuming it was pending
                self._stats["by_status"][old_status.value] = self._stats["by_status"].get(old_status.value, 0) - 1
                self._stats["by_status"][DeadLetterStatus.UNDER_INVESTIGATION.value] = self._stats["by_status"].get(DeadLetterStatus.UNDER_INVESTIGATION.value, 0) + 1
        return success


    async def resolve(self, trace_id: str, resolution: str, resolved_by: str) -> bool:
        """Mark envelope as resolved.

        Args:
            trace_id: Trace ID of envelope
            resolution: Resolution notes
            resolved_by: Who resolved it

        Returns:
            True if updated successfully
        """
        success = await self._storage.update_status(
            trace_id,
            DeadLetterStatus.RESOLVED,
            f"Resolved by {resolved_by}: {resolution}"
        )

        if success:
            # Update stats if the item was successfully moved to resolved
            item = await self._storage.get(trace_id) # Re-fetch to get current status
            if item and item.status == DeadLetterStatus.RESOLVED:
                # Deduct from previous status count (could be pending, investigation, or even requeued)
                # This is a simplification, a more robust solution would track the item's prior status.
                # For now, we'll decrement from a general 'active' count if applicable.
                self._stats["resolved"] += 1
                # We might also want to decrement from total_failed or a specific prior status
                # For simplicity, we'll assume it was not already counted in 'resolved'.
                # A more detailed stats update would be needed here.

        return success

    async def requeue(self, trace_id: str, notes: str) -> Optional["SignalEnvelope"]:
        """Requeue envelope for processing.

        Args:
            trace_id: Trace ID of envelope
            notes: Notes for requeue

        Returns:
            Envelope if found and requeued
        """
        item = await self._storage.get(trace_id)
        if not item:
            return None

        # Check retry limit
        if item.retry_count >= item.max_retries:
            LOGGER.warning(f"Envelope {trace_id} exceeded max retries ({item.max_retries})")
            return None

        # Update retry count
        item.retry_count += 1
        item.status = DeadLetterStatus.REQUEUED
        item.investigation_notes = notes if not item.investigation_notes else f"{item.investigation_notes}\n{notes}"


        # Save updated item
        await self._storage.add(item) # Use add to save the updated item, as _get_item_path might change

        # Update stats
        self._stats["requeued"] += 1
        # Decrement from previous status count and increment for requeued
        if item.status.value in self._stats["by_status"]:
             self._stats["by_status"][item.status.value] = self._stats["by_status"].get(item.status.value, 0) - 1
        self._stats["by_status"][DeadLetterStatus.REQUEUED.value] = self._stats["by_status"].get(DeadLetterStatus.REQUEUED.value, 0) + 1


        # Return envelope for reprocessing
        LOGGER.info(f"Requeued envelope {trace_id} (attempt {item.retry_count})")

        return item.envelope

    async def cleanup(self, older_than: Optional[timedelta] = None) -> int:
        """Clean up old resolved items.

        Args:
            older_than: Age threshold (uses 30 days if not provided)

        Returns:
            Number of items cleaned up
        """
        if older_than is None:
            older_than = timedelta(days=30)

        cleaned_count = await self._storage.cleanup(older_than)
        # Update stats for cleaned items if they were in resolved status
        self._stats["resolved"] -= cleaned_count
        # Potentially update by_status for resolved items if needed
        return cleaned_count

    def get_stats(self) -> Dict[str, Any]:
        """Get dead letter queue statistics.

        Returns:
            Statistics dictionary
        """
        # Ensure 'by_status' has entries for all defined statuses, even if zero
        all_statuses = {s.value for s in DeadLetterStatus}
        for status_val in all_statuses:
            self._stats["by_status"].setdefault(status_val, 0)
        return self._stats.copy()

    async def health_check(self) -> Dict[str, Any]:
        """Check health of dead letter queue.

        Returns:
            Health status
        """
        # Count items by status using the list method with a high limit for health check
        pending = await self.list_failed_envelopes(DeadLetterStatus.PENDING_REVIEW, 1000)
        investigation = await self.list_failed_envelopes(DeadLetterStatus.UNDER_INVESTIGATION, 1000)
        resolved = await self.list_failed_envelopes(DeadLetterStatus.RESOLVED, 1000)

        # Update internal stats based on current counts from storage
        # This ensures stats are relatively up-to-date, though not real-time transactional
        self._stats["by_status"][DeadLetterStatus.PENDING_REVIEW.value] = len(pending)
        self._stats["by_status"][DeadLetterStatus.UNDER_INVESTIGATION.value] = len(investigation)
        self._stats["by_status"][DeadLetterStatus.RESOLVED.value] = len(resolved)


        return {
            "status": "healthy",
            "pending_review": len(pending),
            "under_investigation": len(investigation),
            "resolved": len(resolved),
            "total_failed": self._stats["total_failed"], # This might not reflect current storage state perfectly
            "stats": self.get_stats()
        }

# Global dead letter queue
_dlq: Optional[DeadLetterQueue] = None
_dlq_lock = asyncio.Lock()

async def get_dead_letter_queue() -> DeadLetterQueue:
    """Get global dead letter queue instance.

    Returns:
        DeadLetterQueue instance
    """
    global _dlq
    async with _dlq_lock:
        if _dlq is None:
            _dlq = DeadLetterQueue()
    return _dlq

# Decorator for automatic dead letter handling
def dead_letter_handler(
    failure_reason: FailureReason = FailureReason.UNKNOWN,
    include_payload: bool = True
):
    """Decorator to automatically send failed envelopes to DLQ.

    Args:
        failure_reason: Default failure reason
        include_payload: Whether to include payload in DLQ

    Returns:
        Decorated function
    """
    def decorator(func):
        """TODO: Add docstring."""

        async def wrapper(envelope: "SignalEnvelope", *args, **kwargs):
            """Docstring."""
            try:
                return await func(envelope, *args, **kwargs)
            except Exception as e:
# Send to dead letter queue
                dlq = await get_dead_letter_queue()
                await dlq.add_failed_envelope(
                    envelope,
                    failure_reason,
                    func.__name__,
                    str(e),
                    {"args": str(args), "kwargs": str(kwargs)} if include_payload else None
                )
                raise
        return wrapper
    return decorator

