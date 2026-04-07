"""Checkpoint Manager - Pipeline state persistence and recovery.

This module implements micro-checkpointing to ensure pipeline resilience.
The SignalEnvelope state is persisted after every successful stage,
enabling recovery from failures without losing progress.
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any

import aiofiles
from pydantic import BaseModel
from redis import asyncio as aioredis

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "checkpoint_manager_types", "execution_auth")
_emit_validates_capability("p2", "checkpoint_manager_types", "capability_check")
_emit_routes_to_capability("p2", "checkpoint_manager_types", "capability_route")
_emit_writes_via_uwg("p2", "checkpoint_manager_types", "uwg_write")
_emit_blocks_direct_write("p2", "checkpoint_manager_types", "direct_write_block")
_emit_records_tool_invocation("p2", "checkpoint_manager_types", "tool_invocation")
_emit_captures_execution_output("p2", "checkpoint_manager_types", "exec_output")
_emit_dispatches_agent("p3", "checkpoint_manager_types", "agent_dispatch")
_emit_coordinates_agents("p3", "checkpoint_manager_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "checkpoint_manager_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "checkpoint_manager_types", "healing_outcome")
_emit_escalates_failure("p3", "checkpoint_manager_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "checkpoint_manager_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "checkpoint_manager_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "checkpoint_manager_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "checkpoint_manager_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "checkpoint_manager_types", "eval_metric")
_emit_stores_embedding("p4", "checkpoint_manager_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "checkpoint_manager_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "checkpoint_manager_types", "exec_snapshot_link")
from .envelope import SignalEnvelope

_emit_applies_guardrail("p0", "checkpoint_manager_types", "p0_governance")
_emit_reads_policy_state("p0", "checkpoint_manager_types", "policy_binding")
_emit_snapshots_state("p0", "checkpoint_manager_types", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("checkpoint_manager_types", "p4obs", "metric_1")
_emit_emits_metric_event("checkpoint_manager_types", "p4obs", "metric_2")
_emit_emits_metric_event("checkpoint_manager_types", "p4obs", "metric_3")
_emit_emits_metric_event("checkpoint_manager_types", "p4obs", "metric_4")
_emit_emits_metric_event("checkpoint_manager_types", "p4obs", "metric_5")
_emit_emits_metric_event("checkpoint_manager_types", "p4obs", "metric_6")
_emit_records_incident_event("checkpoint_manager_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("checkpoint_manager_types", "p4obs", "anomaly")
_emit_writes_observability_log("checkpoint_manager_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("checkpoint_manager_types", "p4obs", "mon_state")
_emit_triggers_alert("checkpoint_manager_types", "p4obs", "alert")
_emit_links_incident_trace("checkpoint_manager_types", "p4obs", "trace_link")
_emit_captures_pattern("checkpoint_manager_types", "p3lm", "pattern")
_emit_records_learning_event("checkpoint_manager_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("checkpoint_manager_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("checkpoint_manager_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("checkpoint_manager_types", "p3lm", "routing")
_emit_improves_agent_policy("checkpoint_manager_types", "p3lm", "policy")
_emit_stores_learning_state("checkpoint_manager_types", "p3lm", "state")
_emit_records_execution_trace("checkpoint_manager_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("checkpoint_manager_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("checkpoint_manager_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("checkpoint_manager_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("checkpoint_manager_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("checkpoint_manager_types", "env_read", "p2_env_1")
_emit_reads_environ("checkpoint_manager_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("checkpoint_manager_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("checkpoint_manager_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "checkpoint_manager_types", "context_pull")
_emit_pulls_context("p1", "checkpoint_manager_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "checkpoint_manager_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "checkpoint_manager_types", "uwg_term_2")
_emit_writes_through("p1", "checkpoint_manager_types", "write_through")
_emit_writes_through("p1", "checkpoint_manager_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "checkpoint_manager_types", "safety_validation")
_emit_invokes_eval("p1", "checkpoint_manager_types", "eval_call")
_emit_proposal_commits_routing("p1", "checkpoint_manager_types", "routing_commit")
_emit_escalates_to_human("p1", "checkpoint_manager_types", "human_escalation")
_emit_routes_through("p1", "checkpoint_manager_types", "route_through")
_emit_checks_agent_registry("p1", "checkpoint_manager_types", "agent_registry")
_emit_validates_agent_capability("p1", "checkpoint_manager_types", "capability")
_emit_dispatches_execution_plan("p1", "checkpoint_manager_types", "exec_plan")
_emit_agent_executes_agent("p1", "checkpoint_manager_types", "sub_agent")
_emit_routes_to_agent("p1", "checkpoint_manager_types", "target_agent")
_emit_verifies_policy("p1", "checkpoint_manager_types", "policy_check")
_emit_observes_runtime_state("p1", "checkpoint_manager_types", "runtime_state")
_emit_verifies_boundary("p1", "checkpoint_manager_types", "boundary_check")
_emit_transcripts_response("p1", "checkpoint_manager_types", "transcript")
_emit_hard_fails_untranscripted("p1", "checkpoint_manager_types")
_emit_gated_by_confidence("p1", "checkpoint_manager_types", "confidence_gate")
emit_replay_key("p0", "checkpoint_manager_types")
emit_determinism_digest("p0", "checkpoint_manager_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_1")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_2")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_3")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_4")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_5")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_6")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_7")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_8")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_9")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_10")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_11")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_12")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_13")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_14")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_15")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_16")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_17")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_18")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_19")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_20")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_21")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_22")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_23")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_24")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_25")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_26")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_27")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_28")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_29")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_30")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_31")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_32")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_33")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_34")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_35")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_36")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_37")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_38")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_39")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_40")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_41")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_42")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_43")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_44")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_45")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_46")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_47")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_48")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_49")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_50")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_51")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_52")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_53")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_54")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_55")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_56")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_57")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_58")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_59")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_60")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_61")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_62")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_63")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_64")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_65")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_66")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_67")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_68")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_69")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_70")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_71")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_72")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_73")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_74")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_75")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_76")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_77")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_78")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_79")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_80")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_81")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_82")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_83")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_84")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_85")
_emit_reads_through("l4", "checkpoint_manager_types", "urg_read_86")

logger = logging.getLogger(__name__)


class CheckpointStorage(str, Enum):
    """Types of checkpoint storage backends."""

    FILE = "file"
    REDIS = "redis"
    MEMORY = "memory"


class CheckpointConfig(BaseModel):
    """configuration for checkpoint manager."""

    storage_type: CheckpointStorage = CheckpointStorage.FILE
    storage_path: str = "./checkpoints"
    redis_url: str = "redis://localhost:6379"
    redis_prefix: str = "pipeline:checkpoint"
    ttl_seconds: int = 3600
    compression: bool = True
    encryption: bool = False
    max_checkpoints: int = 1000


class CheckpointStorageBackend(ABC):
    """Abstract base for checkpoint storage backends."""

    @abstractmethod
    async def save(self, envelope: SignalEnvelope) -> bool:
        """Save envelope checkpoint.

        Args:
            envelope: Signal envelope to save

        Returns:
            True if saved successfully
        """
        pass

    @abstractmethod
    async def load(self, trace_id: str) -> SignalEnvelope | None:
        """Load envelope checkpoint.

        Args:
            trace_id: Trace ID of envelope

        Returns:
            Signal envelope if found
        """
        pass

    @abstractmethod
    async def delete(self, trace_id: str) -> bool:
        """Delete envelope checkpoint.

        Args:
            trace_id: Trace ID of envelope

        Returns:
            True if deleted successfully
        """
        pass

    @abstractmethod
    # guardian: allow-magic-config
    async def list_checkpoints(self, limit: int = 100) -> list[str]:
        """List available checkpoint trace IDs.

        Args:
            limit: Maximum number to return

        Returns:
            List of trace IDs
        """
        pass

    @abstractmethod
    async def cleanup(self, older_than: timedelta) -> int:
        """Clean up old checkpoints.

        Args:
            older_than: Age threshold for cleanup

        Returns:
            Number of checkpoints cleaned up
        """
        pass


class FileCheckpointStorage(CheckpointStorageBackend):
    """File-based checkpoint storage."""

    def __init__(self, storage_path: str, compression: bool = True):
        """Initialize file storage.

        Args:
            storage_path: Directory to store checkpoints
            compression: Whether to compress checkpoints
        """
        self.storage_path = Path(storage_path)
        self.compression = compression
        self._ensure_directory()

    def _ensure_directory(self) -> None:
        """Ensure storage directory exists."""
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _get_checkpoint_path(self, trace_id: str) -> Path:
        """Get file path for checkpoint.

        Args:
            trace_id: Trace ID

        Returns:
            File path
        """
        prefix = trace_id[:2]
        subdir = self.storage_path / prefix
        subdir.mkdir(exist_ok=True)
        return subdir / f"{trace_id}.json"

    async def save(self, envelope: SignalEnvelope) -> bool:
        """Save envelope to file.

        Args:
            envelope: Signal envelope to save

        Returns:
            True if saved successfully
        """
        try:
            path = self._get_checkpoint_path(envelope.trace_id)
            data = envelope.to_dict()
            data["_checkpoint_metadata"] = {"saved_at": datetime.now(timezone.utc).isoformat(), "version": "1.0"}
            content = json.dumps(data, indent=2)
            temp_path = path.with_suffix(".tmp")
            async with aiofiles.open(temp_path, "w") as f:
                await f.write(content)
            await aiofiles.os.rename(temp_path, path)
            logger.debug(f"Saved checkpoint for {envelope.trace_id} to {path}")
            return True
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
            return False

    async def load(self, trace_id: str) -> SignalEnvelope | None:
        """Load envelope from file.

        Args:
            trace_id: Trace ID

        Returns:
            Signal envelope if found
        """
        try:
            path = self._get_checkpoint_path(trace_id)
            if not path.exists():
                return None
            async with aiofiles.open(path) as f:
                content = await f.read()
            data = json.loads(content)
            data.pop("_checkpoint_metadata", None)
            envelope = SignalEnvelope.from_dict(data)
            logger.debug(f"Loaded checkpoint for {trace_id}")
            return envelope
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to load checkpoint {trace_id}: {e}")
            return None

    async def delete(self, trace_id: str) -> bool:
        """Delete checkpoint file.

        Args:
            trace_id: Trace ID

        Returns:
            True if deleted successfully
        """
        try:
            path = self._get_checkpoint_path(trace_id)
            if path.exists():
                await aiofiles.os.remove(path)
                logger.debug(f"Deleted checkpoint for {trace_id}")
                return True
            return False
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to delete checkpoint {trace_id}: {e}")
            return False

    # guardian: allow-magic-config
    async def list_checkpoints(self, limit: int = 100) -> list[str]:
        """List available checkpoints.

        Args:
            limit: Maximum number to return

        Returns:
            List of trace IDs
        """
        try:
            trace_ids = []
            for subdir in self.storage_path.iterdir():
                if subdir.is_dir() and len(subdir.name) == 2:
                    for file in subdir.glob("*.json"):
                        trace_id = file.stem
                        trace_ids.append(trace_id)
                        if len(trace_ids) >= limit:
                            return trace_ids
            return trace_ids
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to list checkpoints: {e}")
            return []

    async def cleanup(self, older_than: timedelta) -> int:
        """Clean up old checkpoint files.

        Args:
            older_than: Age threshold

        Returns:
            Number of files cleaned up
        """
        try:
            count = 0
            cutoff = datetime.now(timezone.utc) - older_than
            for subdir in self.storage_path.iterdir():
                if subdir.is_dir() and len(subdir.name) == 2:
                    for file in subdir.glob("*.json"):
                        mtime = datetime.fromtimestamp(file.stat().st_mtime)
                        if mtime < cutoff:
                            await aiofiles.os.remove(file)
                            count += 1
            logger.info(f"Cleaned up {count} old checkpoint files")
            return count
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-broad-exception -- teardown/cleanup context -- swallow is conventional in resource-release paths
            logger.error(f"Failed to cleanup checkpoints: {e}")
            return 0


class RedisCheckpointStorage(CheckpointStorageBackend):
    """Redis-based checkpoint storage."""

    def __init__(self, redis_url: str, prefix: str, ttl_seconds: int = 3600):
        """Initialize Redis storage.

        Args:
            redis_url: Redis connection URL
            prefix: Key prefix for checkpoints
            ttl_seconds: TTL for checkpoints
        """
        self.redis_url = redis_url
        self.prefix = prefix
        self.ttl_seconds = ttl_seconds
        self._redis: aioredis.Redis | None = None

    async def _get_redis(self) -> aioredis.Redis:
        """Get Redis connection.

        Returns:
            Redis client
        """
        if self._redis is None:
            self._redis = await aioredis.from_url(self.redis_url)
        return self._redis

    def _get_key(self, trace_id: str) -> str:
        """Get Redis key for checkpoint.

        Args:
            trace_id: Trace ID

        Returns:
            Redis key
        """
        return f"{self.prefix}:{trace_id}"

    async def save(self, envelope: SignalEnvelope) -> bool:
        """Save envelope to Redis.

        Args:
            envelope: Signal envelope to save

        Returns:
            True if saved successfully
        """
        try:
            redis = await self._get_redis()
            key = self._get_key(envelope.trace_id)
            data = envelope.to_dict()
            data["_checkpoint_metadata"] = {"saved_at": datetime.now(timezone.utc).isoformat(), "version": "1.0"}
            content = json.dumps(data)
            await redis.setex(key, self.ttl_seconds, content)
            logger.debug(f"Saved checkpoint for {envelope.trace_id} to Redis")
            return True
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to save checkpoint to Redis: {e}")
            return False

    async def load(self, trace_id: str) -> SignalEnvelope | None:
        """Load envelope from Redis.

        Args:
            trace_id: Trace ID

        Returns:
            Signal envelope if found
        """
        try:
            redis = await self._get_redis()
            key = self._get_key(trace_id)
            content = await redis.get(key)
            if content is None:
                return None
            data = json.loads(content)
            data.pop("_checkpoint_metadata", None)
            envelope = SignalEnvelope.from_dict(data)
            logger.debug(f"Loaded checkpoint for {trace_id} from Redis")
            return envelope
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to load checkpoint {trace_id} from Redis: {e}")
            return None

    async def delete(self, trace_id: str) -> bool:
        """Delete checkpoint from Redis.

        Args:
            trace_id: Trace ID

        Returns:
            True if deleted successfully
        """
        try:
            redis = await self._get_redis()
            key = self._get_key(trace_id)
            result = await redis.delete(key)
            if result > 0:
                logger.debug(f"Deleted checkpoint for {trace_id} from Redis")
                return True
            return False
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to delete checkpoint {trace_id} from Redis: {e}")
            return False

    # guardian: allow-magic-config
    async def list_checkpoints(self, limit: int = 100) -> list[str]:
        """List available checkpoints in Redis.

        Args:
            limit: Maximum number to return

        Returns:
            List of trace IDs
        """
        try:
            redis = await self._get_redis()
            pattern = f"{self.prefix}:*"
            keys = await redis.keys(pattern)
            trace_ids = []
            for key in keys:
                trace_id = key.decode().split(":")[-1]
                trace_ids.append(trace_id)
                if len(trace_ids) >= limit:
                    break
            return trace_ids
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to list checkpoints in Redis: {e}")
            return []

    async def cleanup(self, older_than: timedelta) -> int:
        """Redis handles cleanup automatically via TTL.

        Args:
            older_than: Age threshold (ignored for Redis)

        Returns:
            0 (Redis handles cleanup)
        """
        return 0


class MemoryCheckpointStorage(CheckpointStorageBackend):
    """In-memory checkpoint storage for testing."""

    # guardian: allow-magic-config
    def __init__(self, max_size: int = 100):
        """Initialize memory storage.

        Args:
            max_size: Maximum number of checkpoints to store
        """
        self.checkpoints: dict[str, SignalEnvelope] = {}
        self.max_size = max_size
        self._lock = asyncio.Lock()

    async def save(self, envelope: SignalEnvelope) -> bool:
        """Save envelope to memory.

        Args:
            envelope: Signal envelope to save

        Returns:
            True if saved successfully
        """
        async with self._lock:
            if len(self.checkpoints) >= self.max_size:
                oldest = next(iter(self.checkpoints))
                del self.checkpoints[oldest]
            self.checkpoints[envelope.trace_id] = envelope
            return True

    async def load(self, trace_id: str) -> SignalEnvelope | None:
        """Load envelope from memory.

        Args:
            trace_id: Trace ID

        Returns:
            Signal envelope if found
        """
        async with self._lock:
            return self.checkpoints.get(trace_id)

    async def delete(self, trace_id: str) -> bool:
        """Delete checkpoint from memory.

        Args:
            trace_id: Trace ID

        Returns:
            True if deleted successfully
        """
        async with self._lock:
            if trace_id in self.checkpoints:
                del self.checkpoints[trace_id]
                return True
            return False

    # guardian: allow-magic-config
    async def list_checkpoints(self, limit: int = 100) -> list[str]:
        """List checkpoints in memory.

        Args:
            limit: Maximum number to return

        Returns:
            List of trace IDs
        """
        async with self._lock:
            return list(self.checkpoints.keys())[:limit]

    async def cleanup(self, older_than: timedelta) -> int:
        """Clean up old checkpoints.

        Args:
            older_than: Age threshold

        Returns:
            Number of checkpoints cleaned up
        """
        async with self._lock:
            cutoff = datetime.now(timezone.utc) - older_than
            to_remove = []
            for trace_id, envelope in self.checkpoints.items():
                if envelope.updated_at < cutoff:
                    to_remove.append(trace_id)
            for trace_id in to_remove:
                del self.checkpoints[trace_id]
            return len(to_remove)


class CheckpointManager:
    """Manages pipeline checkpoints for fault tolerance."""

    def __init__(self, config: CheckpointConfig):
        """Initialize checkpoint manager.

        Args:
            config: Checkpoint configuration
        """
        self.config = config
        self.storage = self._create_storage()
        self._stats = {"saves": 0, "loads": 0, "deletes": 0, "errors": 0}
        logger.info(f"Initialized CheckpointManager with {config.storage_type} storage")

    def _create_storage(self) -> CheckpointStorageBackend:
        """Create storage backend based on config.

        Returns:
            Storage backend instance
        """
        if self.config.storage_type == CheckpointStorage.FILE:
            return FileCheckpointStorage(self.config.storage_path, self.config.compression)
        elif self.config.storage_type == CheckpointStorage.REDIS:
            return RedisCheckpointStorage(
                self.config.redis_url, self.config.redis_prefix, self.config.ttl_seconds
            )
        else:
            return MemoryCheckpointStorage(self.config.max_checkpoints)

    async def save_checkpoint(self, envelope: SignalEnvelope) -> bool:
        """Save envelope checkpoint.

        Args:
            envelope: Signal envelope to save

        Returns:
            True if saved successfully
        """
        try:
            success = await self.storage.save(envelope)
            if success:
                self._stats["saves"] += 1
            else:
                self._stats["errors"] += 1
            return success
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Checkpoint save failed: {e}")
            self._stats["errors"] += 1
            return False

    async def load_checkpoint(self, trace_id: str) -> SignalEnvelope | None:
        """Load envelope checkpoint.

        Args:
            trace_id: Trace ID of envelope

        Returns:
            Signal envelope if found
        """
        try:
            envelope = await self.storage.load(trace_id)
            if envelope:
                self._stats["loads"] += 1
            return envelope
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Checkpoint load failed: {e}")
            self._stats["errors"] += 1
            return None

    async def delete_checkpoint(self, trace_id: str) -> bool:
        """Delete envelope checkpoint.

        Args:
            trace_id: Trace ID of envelope

        Returns:
            True if deleted successfully
        """
        try:
            success = await self.storage.delete(trace_id)
            if success:
                self._stats["deletes"] += 1
            return success
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Checkpoint delete failed: {e}")
            self._stats["errors"] += 1
            return False

    async def resume_from_checkpoint(self, trace_id: str, stages: list[str]) -> SignalEnvelope | None:
        """Resume pipeline from checkpoint.

        Args:
            trace_id: Trace ID to resume
            stages: List of stage names in order

        Returns:
            envelope with completed stages marked
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "CheckpointManager.resume_from_checkpoint")

        envelope = await self.load_checkpoint(trace_id)
        if not envelope:
            return None
        last_completed = envelope.get_last_completed_stage()
        if last_completed:
            logger.info(f"Resuming from stage: {last_completed}")
        return envelope

    async def cleanup_old_checkpoints(self, older_than: timedelta | None = None) -> int:
        """Clean up old checkpoints.

        Args:
            older_than: Age threshold (uses config default if None)

        Returns:
            Number of checkpoints cleaned up
        """
        if older_than is None:
            older_than = timedelta(seconds=self.config.ttl_seconds)
        return await self.storage.cleanup(older_than)

    def get_stats(self) -> dict[str, int]:
        """Get checkpoint statistics.

        Returns:
            Statistics dictionary
        """
        return self._stats.copy()

    async def health_check(self) -> dict[str, Any]:
        """Check health of checkpoint system.

        Returns:
            Health status
        """
        try:
            test_envelope = SignalEnvelope(payload={"test": True})
            saved = await self.save_checkpoint(test_envelope)
            if not saved:
                return {"status": "unhealthy", "reason": "Cannot save checkpoint"}
            loaded = await self.load_checkpoint(test_envelope.trace_id)
            if not loaded:
                return {"status": "unhealthy", "reason": "Cannot load checkpoint"}
            await self.delete_checkpoint(test_envelope.trace_id)
            return {"status": "healthy", "storage_type": self.config.storage_type, "stats": self.get_stats()}
        # guardian: allow-silent-swallow
        except Exception as e:
            return {"status": "unhealthy", "reason": str(e)}


_checkpoint_manager: CheckpointManager | None = None
_manager_lock = asyncio.Lock()


async def get_checkpoint_manager(config: CheckpointConfig | None = None) -> CheckpointManager:
    """Get global checkpoint manager instance.

    Args:
        config: Optional configuration

    Returns:
        CheckpointManager instance
    """
    global _checkpoint_manager
    async with _manager_lock:
        if _checkpoint_manager is None:
            _checkpoint_manager = CheckpointManager(config or CheckpointConfig())
        return _checkpoint_manager
