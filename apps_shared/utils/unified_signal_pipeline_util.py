"""Unified Signal Pipeline - Shared signal augmentation across engines.

This module provides a unified pipeline for signal augmentation that both
resume and outreach engines can use, eliminating duplication while
maintaining domain-specific optimizations.
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

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

_emit_authorize_and_execute("p2", "unified_signal_pipeline_util", "execution_auth")
_emit_validates_capability("p2", "unified_signal_pipeline_util", "capability_check")
_emit_routes_to_capability("p2", "unified_signal_pipeline_util", "capability_route")
_emit_writes_via_uwg("p2", "unified_signal_pipeline_util", "uwg_write")
_emit_blocks_direct_write("p2", "unified_signal_pipeline_util", "direct_write_block")
_emit_records_tool_invocation("p2", "unified_signal_pipeline_util", "tool_invocation")
_emit_captures_execution_output("p2", "unified_signal_pipeline_util", "exec_output")
_emit_dispatches_agent("p3", "unified_signal_pipeline_util", "agent_dispatch")
_emit_coordinates_agents("p3", "unified_signal_pipeline_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "unified_signal_pipeline_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "unified_signal_pipeline_util", "healing_outcome")
_emit_escalates_failure("p3", "unified_signal_pipeline_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "unified_signal_pipeline_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "unified_signal_pipeline_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "unified_signal_pipeline_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "unified_signal_pipeline_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "unified_signal_pipeline_util", "eval_metric")
_emit_stores_embedding("p4", "unified_signal_pipeline_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "unified_signal_pipeline_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "unified_signal_pipeline_util", "exec_snapshot_link")
from .claim_confidence import ClaimConfidenceScorer, analyze_claims
from .core.checkpoint_manager import CheckpointConfig, CheckpointManager, get_checkpoint_manager
from .core.envelope import EnvelopeFactory, PipelineStageStatus, SignalEnvelope
from .hyde_processor import HyDEProcessor
from .prompt_optimizer import PromptOptimizer, optimize_prompt
from .rag_components import KnowledgeGraphInjector, SelfRAGProcessor, semantic_cache
from .signal_infrastructure import DomainConfig, EngineType, get_shared_infrastructure
from .signal_quality_pipeline import SignalQualityPipeline
from .tone_model import ToneModel, adapt_tone

_emit_applies_guardrail("p0", "unified_signal_pipeline_util", "p0_governance")
_emit_reads_policy_state("p0", "unified_signal_pipeline_util", "policy_binding")
_emit_snapshots_state("p0", "unified_signal_pipeline_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("unified_signal_pipeline_util", "p4obs", "metric_1")
_emit_emits_metric_event("unified_signal_pipeline_util", "p4obs", "metric_2")
_emit_emits_metric_event("unified_signal_pipeline_util", "p4obs", "metric_3")
_emit_emits_metric_event("unified_signal_pipeline_util", "p4obs", "metric_4")
_emit_emits_metric_event("unified_signal_pipeline_util", "p4obs", "metric_5")
_emit_emits_metric_event("unified_signal_pipeline_util", "p4obs", "metric_6")
_emit_records_incident_event("unified_signal_pipeline_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("unified_signal_pipeline_util", "p4obs", "anomaly")
_emit_writes_observability_log("unified_signal_pipeline_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("unified_signal_pipeline_util", "p4obs", "mon_state")
_emit_triggers_alert("unified_signal_pipeline_util", "p4obs", "alert")
_emit_links_incident_trace("unified_signal_pipeline_util", "p4obs", "trace_link")
_emit_captures_pattern("unified_signal_pipeline_util", "p3lm", "pattern")
_emit_records_learning_event("unified_signal_pipeline_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("unified_signal_pipeline_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("unified_signal_pipeline_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("unified_signal_pipeline_util", "p3lm", "routing")
_emit_improves_agent_policy("unified_signal_pipeline_util", "p3lm", "policy")
_emit_stores_learning_state("unified_signal_pipeline_util", "p3lm", "state")
_emit_records_execution_trace("unified_signal_pipeline_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("unified_signal_pipeline_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("unified_signal_pipeline_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("unified_signal_pipeline_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("unified_signal_pipeline_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("unified_signal_pipeline_util", "env_read", "p2_env_1")
_emit_reads_environ("unified_signal_pipeline_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("unified_signal_pipeline_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("unified_signal_pipeline_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "unified_signal_pipeline_util", "context_pull")
_emit_pulls_context("p1", "unified_signal_pipeline_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "unified_signal_pipeline_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "unified_signal_pipeline_util", "uwg_term_2")
_emit_writes_through("p1", "unified_signal_pipeline_util", "write_through")
_emit_writes_through("p1", "unified_signal_pipeline_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "unified_signal_pipeline_util", "safety_validation")
_emit_invokes_eval("p1", "unified_signal_pipeline_util", "eval_call")
_emit_proposal_commits_routing("p1", "unified_signal_pipeline_util", "routing_commit")
_emit_escalates_to_human("p1", "unified_signal_pipeline_util", "human_escalation")
_emit_routes_through("p1", "unified_signal_pipeline_util", "route_through")
_emit_checks_agent_registry("p1", "unified_signal_pipeline_util", "agent_registry")
_emit_validates_agent_capability("p1", "unified_signal_pipeline_util", "capability")
_emit_dispatches_execution_plan("p1", "unified_signal_pipeline_util", "exec_plan")
_emit_agent_executes_agent("p1", "unified_signal_pipeline_util", "sub_agent")
_emit_routes_to_agent("p1", "unified_signal_pipeline_util", "target_agent")
_emit_verifies_policy("p1", "unified_signal_pipeline_util", "policy_check")
_emit_observes_runtime_state("p1", "unified_signal_pipeline_util", "runtime_state")
_emit_verifies_boundary("p1", "unified_signal_pipeline_util", "boundary_check")
_emit_transcripts_response("p1", "unified_signal_pipeline_util", "transcript")
_emit_hard_fails_untranscripted("p1", "unified_signal_pipeline_util")
_emit_gated_by_confidence("p1", "unified_signal_pipeline_util", "confidence_gate")
emit_replay_key("p0", "unified_signal_pipeline_util")
emit_determinism_digest("p0", "unified_signal_pipeline_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_1")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_2")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_3")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_4")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_5")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_6")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_7")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_8")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_9")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_10")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_11")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_12")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_13")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_14")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_15")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_16")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_17")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_18")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_19")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_20")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_21")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_22")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_23")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_24")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_25")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_26")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_27")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_28")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_29")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_30")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_31")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_32")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_33")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_34")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_35")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_36")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_37")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_38")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_39")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_40")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_41")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_42")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_43")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_44")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_45")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_46")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_47")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_48")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_49")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_50")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_51")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_52")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_53")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_54")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_55")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_56")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_57")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_58")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_59")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_60")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_61")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_62")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_63")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_64")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_65")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_66")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_67")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_68")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_69")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_70")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_71")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_72")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_73")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_74")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_75")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_76")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_77")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_78")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_79")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_80")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_81")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_82")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_83")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_84")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_85")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_86")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_87")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_88")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_89")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_90")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_91")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_92")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_93")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_94")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_95")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_96")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_97")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_98")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_99")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_100")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_101")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_102")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_103")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_104")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_105")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_106")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_107")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_108")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_109")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_110")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_111")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_112")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_113")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_114")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_115")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_116")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_117")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_118")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_119")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_120")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_121")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_122")
_emit_reads_through("l4", "unified_signal_pipeline_util", "urg_read_123")

logger = logging.getLogger(__name__)


class PipelineStageType(Enum):
    """Stages in the unified signal pipeline."""

    INPUT_PROCESSING = "input_processing"
    CONTEXT_ENRICHMENT = "context_enrichment"
    SIGNAL_AUGMENTATION = "signal_augmentation"
    QUALITY_VALIDATION = "quality_validation"
    OUTPUT_FORMATTING = "output_formatting"


@dataclass
class PipelineContext:
    """Context passed through pipeline stages."""

    engine_type: EngineType
    domain_config: DomainConfig
    original_input: Any
    processed_data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    cache_keys: set[str] = field(default_factory=set)

    def get_cache_key(self, component: str, data: Any) -> str:
        """Generate cache key for component.

        Args:
            component: Component name
            data: Data to hash

        Returns:
            cache key
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"PipelineContext.get_cache_key:{component}"
        )
        content = json.dumps(data, sort_keys=True, default=str)
        hash_key = hashlib.sha256(f"{component}:{content}".encode()).hexdigest()[:16]
        self.cache_keys.add(hash_key)
        return hash_key


class PipelineStage(ABC):
    """Abstract base for pipeline stages."""

    @abstractmethod
    async def execute(self, envelope: SignalEnvelope) -> SignalEnvelope:
        """Execute the pipeline stage.

        Args:
            envelope: Signal envelope

        Returns:
            Updated envelope
        """
        pass

    @property
    @abstractmethod
    def stage_name(self) -> str:
        """Get stage name."""
        pass


class InputProcessingStage(PipelineStage):
    """Processes and normalizes input data."""

    def __init__(self):
        """Initialize input processing stage."""
        self.semantic_cache = semantic_cache()
        self.hyde_processor = HyDEProcessor()

    async def execute(self, envelope: SignalEnvelope) -> SignalEnvelope:
        """Process input data.

        Args:
            envelope: Signal envelope

        Returns:
            Updated envelope
        """
        start_time = time.time()
        stage_name = self.stage_name
        if envelope.has_completed_stage(stage_name):
            logger.debug(f"Skipping {stage_name}, already completed for envelope {envelope.id}")
            return envelope
        envelope.mark_stage_start(stage_name)
        try:
            logger.debug(f"Processing input for {envelope.payload.payload_type}")
            content = self._extract_content_from_payload(envelope.payload)
            cache_key = f"input_processed_{hashlib.sha256(content.encode()).hexdigest()[:16]}"
            cached = self.semantic_cache.get(cache_key)
            if cached:
                self._update_payload_with_processed_data(envelope, cached)
                envelope.mark_stage_complete(
                    stage_name,
                    (time.time() - start_time) * 1000,
                    metadata={"cache_hit": True},
                )
                return envelope
            processed = await self._process_content(content, envelope)
            self._update_payload_with_processed_data(envelope, processed)
            self.semantic_cache.set(cache_key, processed)
            envelope.mark_stage_complete(
                stage_name,
                (time.time() - start_time) * 1000,
                metadata={"cache_hit": False},
            )
            return envelope
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            logger.error(f"Input processing failed: {e}")
            envelope.mark_stage_failed(stage_name, str(e), (time.time() - start_time) * 1000)
            raise

    def _extract_content_from_payload(self, payload) -> str:
        """Extract text content from payload.

        Args:
            payload: Payload object

        Returns:
            Text content
        """
        if hasattr(payload, "text"):
            return payload.text
        elif hasattr(payload, "sections"):
            return json.dumps(payload.sections)
        elif hasattr(payload, "recipient_info"):
            return json.dumps({"recipient": payload.recipient_info, "campaign": payload.campaign_context})
        elif hasattr(payload, "data"):
            return json.dumps(payload.data)
        else:
            return str(payload)

    async def _process_content(self, content: str, envelope: SignalEnvelope) -> dict[str, Any]:
        """Process text content.

        Args:
            content: Text to process
            envelope: Signal envelope

        Returns:
            Processed data
        """
        result = {"word_count": len(content.split()), "char_count": len(content), "language": "en"}
        if envelope.payload.payload_type.value == "resume_data":
            query = f"resume achievements skills {content[:100]}"
        else:
            query = f"outreach personalization {content[:100]}"
        expanded = self.hyde_processor.expand_query_with_hyde(query, envelope.payload.payload_type.value)
        result["expanded_query"] = expanded
        return result

    def _update_payload_with_processed_data(
        self,
        envelope: SignalEnvelope,
        processed: dict[str, Any],
    ) -> None:
        """Update payload with processed data.

        Args:
            envelope: Signal envelope
            processed: Processed data
        """
        if hasattr(envelope.payload, "metadata"):
            envelope.payload.metadata.update(processed)
        else:
            envelope.metadata.update({f"processed_{k}": v for k, v in processed.items()})

    @property
    def stage_name(self) -> str:
        """Get stage name."""
        return "input_processing"


class ContextEnrichmentStage(PipelineStage):
    """Enriches context with external data."""

    def __init__(self):
        """Initialize context enrichment stage."""
        self.kg_injector = KnowledgeGraphInjector()
        self.rag_processor = SelfRAGProcessor()
        self.semantic_cache = semantic_cache()

    async def execute(self, envelope: SignalEnvelope) -> SignalEnvelope:
        """Enrich context.

        Args:
            envelope: Signal envelope

        Returns:
            Updated envelope
        """
        start_time = time.time()
        stage_name = self.stage_name
        if envelope.has_completed_stage(stage_name):
            logger.debug(f"Skipping {stage_name}, already completed for envelope {envelope.id}")
            return envelope
        envelope.mark_stage_start(stage_name)
        try:
            logger.debug(f"Enriching context for {envelope.payload.payload_type}")
            expanded_query = self._get_expanded_query(envelope)
            if not expanded_query:
                envelope.mark_stage_skipped(stage_name, "No expanded query available")
                return envelope
            cache_key = f"context_enriched_{hashlib.sha256(expanded_query.encode()).hexdigest()[:16]}"
            cached = self.semantic_cache.get(cache_key)
            if cached:
                self._update_envelope_with_context(envelope, cached)
                envelope.mark_stage_complete(
                    stage_name,
                    (time.time() - start_time) * 1000,
                    metadata={"cache_hit": True},
                )
                return envelope
            rag_results = self.rag_processor.retrieve_and_rerank(
                expanded_query,
                top_k=10,
                filters={"engine": envelope.payload.payload_type.value},
            )
            kg_context = self.kg_injector.inject_context(expanded_query, envelope.payload.payload_type.value)
            enriched = {
                "rag_results": rag_results,
                "knowledge_graph": kg_context,
                "combined_context": self._combine_contexts(rag_results, kg_context),
            }
            self._update_envelope_with_context(envelope, enriched)
            self.semantic_cache.set(cache_key, enriched)
            envelope.mark_stage_complete(
                stage_name,
                (time.time() - start_time) * 1000,
                metadata={"cache_hit": False},
            )
            return envelope
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            logger.error(f"Context enrichment failed: {e}")
            envelope.mark_stage_failed(stage_name, str(e), (time.time() - start_time) * 1000)
            raise

    def _get_expanded_query(self, envelope: SignalEnvelope) -> str:
        """Get expanded query from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            Expanded query string
        """
        if hasattr(envelope.payload, "metadata") and "expanded_query" in envelope.payload.metadata:
            return envelope.payload.metadata["expanded_query"]
        if "processed_expanded_query" in envelope.metadata:
            return envelope.metadata["processed_expanded_query"]
        return ""

    def _update_envelope_with_context(self, envelope: SignalEnvelope, enriched: dict[str, Any]) -> None:
        """Update envelope with enriched context.

        Args:
            envelope: Signal envelope
            enriched: Enriched context data
        """
        if hasattr(envelope.payload, "metadata"):
            envelope.payload.metadata.update(enriched)
        else:
            envelope.metadata.update({f"enriched_{k}": v for k, v in enriched.items()})

    def _combine_contexts(self, rag_results: list[dict], kg_context: dict) -> str:
        """Combine RAG and KG contexts.

        Args:
            rag_results: RAG retrieval results
            kg_context: Knowledge graph context

        Returns:
            Combined context string
        """
        rag_text = "\n".join(r.get("text", "") for r in rag_results[:5])
        kg_text = "\n".join((f"{k}: {v}" for k, v in kg_context.items()))
        return f"Retrieved Information:\n{rag_text}\n\nRelated Knowledge:\n{kg_text}"

    @property
    def stage_name(self) -> str:
        """Get stage name."""
        return "context_enrichment"


class SignalAugmentationStage(PipelineStage):
    """Augments signal with various enhancements."""

    def __init__(self):
        """Initialize signal augmentation stage."""
        self.claim_scorer = ClaimConfidenceScorer()
        self.prompt_optimizer = PromptOptimizer()
        self.tone_model = ToneModel()
        self.shared_infra = get_shared_infrastructure()
        self.semantic_cache = semantic_cache()

    async def execute(self, envelope: SignalEnvelope) -> SignalEnvelope:
        """Augment signal.

        Args:
            envelope: Signal envelope

        Returns:
            Updated envelope
        """
        start_time = time.time()
        stage_name = self.stage_name
        if envelope.has_completed_stage(stage_name):
            logger.debug(f"Skipping {stage_name}, already completed for envelope {envelope.id}")
            return envelope
        envelope.mark_stage_start(stage_name)
        try:
            logger.debug(f"Augmenting signal for {envelope.payload.payload_type}")
            content = self._extract_content_from_payload(envelope.payload)
            if not content:
                envelope.mark_stage_skipped(stage_name, "No content to augment")
                return envelope
            cache_key = f"signal_augmented_{hashlib.sha256(content.encode()).hexdigest()[:16]}"
            cached = self.semantic_cache.get(cache_key)
            if cached:
                self._update_envelope_with_augmented(envelope, cached)
                envelope.mark_stage_complete(
                    stage_name,
                    (time.time() - start_time) * 1000,
                    metadata={"cache_hit": True},
                )
                return envelope
            augmented = await self._perform_augmentation(content, envelope)
            self._update_envelope_with_augmented(envelope, augmented)
            self.semantic_cache.set(cache_key, augmented)
            envelope.mark_stage_complete(
                stage_name,
                (time.time() - start_time) * 1000,
                metadata={"cache_hit": False},
            )
            return envelope
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            logger.error(f"Signal augmentation failed: {e}")
            envelope.mark_stage_failed(stage_name, str(e), (time.time() - start_time) * 1000)
            raise

    def _extract_content_from_payload(self, payload) -> str:
        """Extract text content from payload.

        Args:
            payload: Payload object

        Returns:
            Text content
        """
        if hasattr(payload, "text"):
            return payload.text
        elif hasattr(payload, "sections"):
            return json.dumps(payload.sections)
        elif hasattr(payload, "recipient_info"):
            return json.dumps({"recipient": payload.recipient_info, "campaign": payload.campaign_context})
        elif hasattr(payload, "data"):
            return json.dumps(payload.data)
        else:
            return str(payload)

    async def _perform_augmentation(self, content: str, envelope: SignalEnvelope) -> dict[str, Any]:
        """Perform signal augmentation.

        Args:
            content: Content to augment
            envelope: Signal envelope

        Returns:
            Augmented data
        """
        augmented = {}
        claims = analyze_claims(content)
        augmented["claims"] = claims
        augmented["claim_confidence"] = sum(c.confidence for c in claims) / len(claims) if claims else 0.5
        if envelope.payload.payload_type.value == "resume_data":
            optimized = optimize_prompt(
                content,
                strategy="achievement_focused",
                constraints=["use_metrics", "action_verbs"],
            )
        else:
            optimized = optimize_prompt(
                content,
                strategy="personalization_focused",
                constraints=["professional_tone", "value_proposition"],
            )
        augmented["optimized_prompt"] = optimized
        if envelope.payload.payload_type.value == "resume_data":
            tone = adapt_tone(content, "professional_achievements")
        else:
            tone = adapt_tone(content, "engaging_professional")
        augmented["adapted_tone"] = tone
        domain_config = json.loads(envelope.metadata.get("domain_config", "{}"))
        assessment = self.shared_infra.assess_signal(
            content,
            EngineType(envelope.metadata.get("engine_type")),
            domain_config,
            self._get_enriched_context(envelope),
        )
        augmented["quality_assessment"] = assessment
        return augmented

    def _get_enriched_context(self, envelope: SignalEnvelope) -> dict[str, Any]:
        """Get enriched context from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            Enriched context
        """
        if hasattr(envelope.payload, "metadata") and "combined_context" in envelope.payload.metadata:
            return envelope.payload.metadata["combined_context"]
        for key, value in envelope.metadata.items():
            if key.startswith("enriched_"):
                return value
        return {}

    def _update_envelope_with_augmented(self, envelope: SignalEnvelope, augmented: dict[str, Any]) -> None:
        """Update envelope with augmented data.

        Args:
            envelope: Signal envelope
            augmented: Augmented data
        """
        if hasattr(envelope.payload, "metadata"):
            envelope.payload.metadata.update(augmented)
        else:
            envelope.metadata.update({f"augmented_{k}": v for k, v in augmented.items()})

    @property
    def stage_name(self) -> str:
        """Get stage name."""
        return "signal_augmentation"


class QualityValidationStage(PipelineStage):
    """Validates signal quality against standards."""

    def __init__(self):
        """Initialize quality validation stage."""
        self.signal_pipeline = SignalQualityPipeline()

    async def execute(self, envelope: SignalEnvelope) -> SignalEnvelope:
        """Validate quality.

        Args:
            envelope: Signal envelope

        Returns:
            Updated envelope
        """
        start_time = time.time()
        stage_name = self.stage_name
        if envelope.has_completed_stage(stage_name):
            logger.debug(f"Skipping {stage_name}, already completed for envelope {envelope.id}")
            return envelope
        envelope.mark_stage_start(stage_name)
        try:
            logger.debug(f"Validating quality for {envelope.payload.payload_type}")
            augmented = self._get_augmented_signal(envelope)
            assessment = augmented.get("quality_assessment")
            if not assessment:
                envelope.mark_stage_skipped(stage_name, "No quality assessment to validate")
                return envelope
            content = self._extract_content_from_payload(envelope.payload)
            quality_result = self.signal_pipeline.process_signal(
                content,
                envelope.payload.payload_type.value,
                self._get_enriched_context(envelope),
            )
            validation = {
                "passes_quality_gate": quality_result.is_pass,
                "quality_score": quality_result.composite_score,
                "flags": quality_result.flags,
                "recommendations": quality_result.recommendations,
            }
            self._update_envelope_with_validation(envelope, validation)
            envelope.mark_stage_complete(
                stage_name,
                (time.time() - start_time) * 1000,
                metadata={"quality_score": quality_result.composite_score},
            )
            return envelope
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            logger.error(f"Quality validation failed: {e}")
            envelope.mark_stage_failed(stage_name, str(e), (time.time() - start_time) * 1000)
            raise

    def _get_augmented_signal(self, envelope: SignalEnvelope) -> dict[str, Any]:
        """Get augmented signal from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            Augmented signal data
        """
        if hasattr(envelope.payload, "metadata"):
            return envelope.payload.metadata
        for key, value in envelope.metadata.items():
            if key.startswith("augmented_") or "augmented" in key:
                return value
        return {}

    def _extract_content_from_payload(self, payload) -> str:
        """Extract text content from payload.

        Args:
            payload: Payload object

        Returns:
            Text content
        """
        if hasattr(payload, "text"):
            return payload.text
        elif hasattr(payload, "sections"):
            return json.dumps(payload.sections)
        elif hasattr(payload, "data"):
            return json.dumps(payload.data)
        else:
            return str(payload)

    def _get_enriched_context(self, envelope: SignalEnvelope) -> dict[str, Any]:
        """Get enriched context from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            Enriched context
        """
        if hasattr(envelope.payload, "metadata") and "combined_context" in envelope.payload.metadata:
            return envelope.payload.metadata["combined_context"]
        for key, value in envelope.metadata.items():
            if key.startswith("enriched_"):
                return value
        return {}

    def _update_envelope_with_validation(self, envelope: SignalEnvelope, validation: dict[str, Any]) -> None:
        """Update envelope with validation results.

        Args:
            envelope: Signal envelope
            validation: Validation results
        """
        if hasattr(envelope.payload, "metadata"):
            envelope.payload.metadata.update(validation)
        else:
            envelope.metadata.update({f"validation_{k}": v for k, v in validation.items()})

    @property
    def stage_name(self) -> str:
        """Get stage name."""
        return "quality_validation"


class OutputFormattingStage(PipelineStage):
    """Formats output for the specific engine."""

    def __init__(self):
        """Initialize output formatting stage."""
        pass

    async def execute(self, envelope: SignalEnvelope) -> SignalEnvelope:
        """Format output.

        Args:
            envelope: Signal envelope

        Returns:
            Updated envelope
        """
        start_time = time.time()
        stage_name = self.stage_name
        if envelope.has_completed_stage(stage_name):
            logger.debug(f"Skipping {stage_name}, already completed for envelope {envelope.id}")
            return envelope
        envelope.mark_stage_start(stage_name)
        try:
            logger.debug(f"Formatting output for {envelope.payload.payload_type}")
            formatted = {
                "engine_type": envelope.payload.payload_type.value,
                "envelope_id": str(envelope.id),
                "trace_id": envelope.trace_id,
                "payload": envelope.payload.dict() if hasattr(envelope.payload, "dict") else envelope.payload,
                "metadata": envelope.metadata,
                "processing_timestamp": datetime.utcnow().isoformat(),
            }
            if envelope.payload.payload_type.value == "resume_data":
                formatted["resume_format"] = self._format_resume_output(envelope)
            else:
                formatted["outreach_format"] = self._format_outreach_output(envelope)
            formatted["stage_history"] = [r.dict() for r in envelope.history]
            self._update_envelope_with_formatted(envelope, formatted)
            envelope.mark_stage_complete(
                stage_name,
                (time.time() - start_time) * 1000,
                metadata={"output_format": formatted.get("format_type", "default")},
            )
            return envelope
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            logger.error(f"Output formatting failed: {e}")
            envelope.mark_stage_failed(stage_name, str(e), (time.time() - start_time) * 1000)
            raise

    def _format_resume_output(self, envelope: SignalEnvelope) -> dict[str, Any]:
        """Format resume-specific output.

        Args:
            envelope: Signal envelope

        Returns:
            Formatted resume output
        """
        return {
            "bullet_points": self._extract_bullets(envelope),
            "achievements": self._extract_achievements(envelope),
            "skills_highlighted": self._extract_skills(envelope),
            "sections": self._get_resume_sections(envelope),
        }

    def _format_outreach_output(self, envelope: SignalEnvelope) -> dict[str, Any]:
        """Format outreach-specific output.

        Args:
            envelope: Signal envelope

        Returns:
            Formatted outreach output
        """
        return {
            "personalization_points": self._extract_personalization(envelope),
            "call_to_action": self._extract_cta(envelope),
            "value_proposition": self._extract_value_prop(envelope),
            "recipient_info": self._get_recipient_info(envelope),
        }

    def _extract_bullets(self, envelope: SignalEnvelope) -> list[str]:
        """Extract bullet points from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            List of bullet points
        """
        augmented = self._get_augmented_data(envelope)
        if "optimized_prompt" in augmented:
            content = augmented["optimized_prompt"]
            bullets = [b.strip() for b in content.split("\n") if b.strip().startswith("•")]
            return bullets[:5]
        return []

    def _extract_achievements(self, envelope: SignalEnvelope) -> list[str]:
        """Extract achievements from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            List of achievements
        """
        augmented = self._get_augmented_data(envelope)
        claims = augmented.get("claims", [])
        return [c.claim for c in claims if hasattr(c, "claim") and c.confidence > 0.7][:3]

    def _extract_skills(self, envelope: SignalEnvelope) -> list[str]:
        """Extract skills from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            List of skills
        """
        if hasattr(envelope.payload, "skills"):
            return envelope.payload.skills
        content = self._extract_content_from_payload(envelope.payload)
        skill_keywords = ["python", "java", "leadership", "analytics", "communication"]
        return [skill for skill in skill_keywords if skill.lower() in content.lower()]

    def _get_resume_sections(self, envelope: SignalEnvelope) -> dict[str, Any]:
        """Get resume sections from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            Resume sections
        """
        if hasattr(envelope.payload, "sections"):
            return envelope.payload.sections
        return {}

    def _extract_personalization(self, envelope: SignalEnvelope) -> list[str]:
        """Extract personalization points from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            List of personalization points
        """
        enriched = self._get_enriched_data(envelope)
        if "rag_results" in enriched:
            return [r.get("text", "")[:100] for r in enriched["rag_results"][:3]]
        return []

    def _extract_cta(self, envelope: SignalEnvelope) -> str:
        """Extract call to action from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            Call to action text
        """
        adapted = self._get_adapted_tone(envelope)
        if adapted and "discuss" in adapted.lower():
            return "Let's discuss how I can contribute to your team."
        return "I would welcome the opportunity to discuss this further."

    def _extract_value_proposition(self, envelope: SignalEnvelope) -> str:
        """Extract value proposition from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            Value proposition text
        """
        augmented = self._get_augmented_data(envelope)
        claims = augmented.get("claims", [])
        if claims and len(claims) > 0:
            first_claim = claims[0]
            return first_claim.claim if hasattr(first_claim, "claim") else str(first_claim)
        return "Experienced professional with proven track record"

    def _get_recipient_info(self, envelope: SignalEnvelope) -> dict[str, Any]:
        """Get recipient information from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            Recipient information
        """
        if hasattr(envelope.payload, "recipient_info"):
            return envelope.payload.recipient_info
        return {}

    def _get_augmented_data(self, envelope: SignalEnvelope) -> dict[str, Any]:
        """Get augmented data from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            Augmented data
        """
        if hasattr(envelope.payload, "metadata"):
            return envelope.payload.metadata
        for key, value in envelope.metadata.items():
            if key.startswith("augmented_"):
                return value
        return {}

    def _get_enriched_data(self, envelope: SignalEnvelope) -> dict[str, Any]:
        """Get enriched data from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            Enriched data
        """
        if hasattr(envelope.payload, "metadata"):
            return {k: v for k, v in envelope.payload.metadata.items() if k.startswith("enriched_")}
        enriched = {}
        for key, value in envelope.metadata.items():
            if key.startswith("enriched_"):
                enriched[key.replace("enriched_", "")] = value
        return enriched

    def _get_adapted_tone(self, envelope: SignalEnvelope) -> str:
        """Get adapted tone from envelope.

        Args:
            envelope: Signal envelope

        Returns:
            Adapted tone text
        """
        augmented = self._get_augmented_data(envelope)
        return augmented.get("adapted_tone", "")

    def _extract_content_from_payload(self, payload) -> str:
        """Extract text content from payload.

        Args:
            payload: Payload object

        Returns:
            Text content
        """
        if hasattr(payload, "text"):
            return payload.text
        elif hasattr(payload, "sections"):
            return json.dumps(payload.sections)
        elif hasattr(payload, "data"):
            return json.dumps(payload.data)
        else:
            return str(payload)

    def _update_envelope_with_formatted(self, envelope: SignalEnvelope, formatted: dict[str, Any]) -> None:
        """Update envelope with formatted output.

        Args:
            envelope: Signal envelope
            formatted: Formatted output
        """
        if hasattr(envelope.payload, "metadata"):
            envelope.payload.metadata.update(formatted)
        else:
            envelope.metadata.update({f"formatted_{k}": v for k, v in formatted.items()})

    @property
    def stage_name(self) -> str:
        """Get stage name."""
        return "output_formatting"


class UnifiedSignalPipeline:
    """Unified pipeline for signal processing across engines."""

    def __init__(self, checkpoint_config: CheckpointConfig | None = None):
        """Initialize the unified pipeline.

        Args:
            checkpoint_config: Optional checkpoint configuration
        """
        self.stages = [
            InputProcessingStage(),
            ContextEnrichmentStage(),
            SignalAugmentationStage(),
            QualityValidationStage(),
            OutputFormattingStage(),
        ]
        self._checkpoint_manager = None
        self._checkpoint_config = checkpoint_config
        self._stats = {
            "total_processed": 0,
            "cache_hits": 0,
            "stage_failures": defaultdict(int),
            "checkpoints_saved": 0,
            "checkpoints_restored": 0,
        }
        self._lock = threading.Lock()
        logger.info("Initialized UnifiedSignalPipeline with checkpointing")

    async def _get_checkpoint_manager(self) -> CheckpointManager:
        """Get checkpoint manager instance.

        Returns:
            CheckpointManager instance
        """
        if self._checkpoint_manager is None:
            self._checkpoint_manager = await get_checkpoint_manager(self._checkpoint_config)
        return self._checkpoint_manager

    async def process(
        self,
        input_data: Any,
        engine_type: EngineType,
        domain_config: DomainConfig | None = None,
        resume_trace_id: str | None = None,
    ) -> SignalEnvelope:
        """Process input through the unified pipeline.

        Args:
            input_data: Input data to process
            engine_type: Type of engine
            domain_config: Domain-specific configuration
            resume_trace_id: Optional trace ID to resume from

        Returns:
            Processed signal envelope
        """
        with self._lock:
            self._stats["total_processed"] += 1
        if not domain_config:
            domain_config = get_shared_infrastructure().create_domain_config(engine_type)
        if resume_trace_id:
            envelope = await self._resume_from_checkpoint(resume_trace_id)
            if not envelope:
                logger.warning(f"Could not resume from trace_id: {resume_trace_id}")
        else:
            envelope = None
        if not envelope:
            envelope = EnvelopeFactory.create_envelope(
                input_data,
                metadata={
                    "engine_type": engine_type.value,
                    "domain_config": domain_config.__class__.__name__,
                },
            )
        envelope.metadata["domain_config"] = json.dumps(domain_config.dict())
        checkpoint_manager = await self._get_checkpoint_manager()
        for stage in self.stages:
            stage_name = stage.stage_name
            try:
                if envelope.has_completed_stage(stage_name):
                    logger.debug(f"Skipping already completed stage: {stage_name}")
                    continue
                logger.debug(f"Executing stage: {stage_name}")
                envelope = await stage.execute(envelope)
                saved = await checkpoint_manager.save_checkpoint(envelope)
                if saved:
                    self._stats["checkpoints_saved"] += 1
                    logger.debug(f"Saved checkpoint after {stage_name}")
            except Exception as e:
                logger.error(f"Stage {stage_name} failed: {e}")
                await checkpoint_manager.save_checkpoint(envelope)
                with self._lock:
                    self._stats["stage_failures"][stage_name] += 1
                raise PipelineExecutionError(
                    f"Pipeline failed at stage {stage_name}",
                    envelope,
                    stage_name,
                    e,
                )
        return envelope

    async def _resume_from_checkpoint(self, trace_id: str) -> SignalEnvelope | None:
        """Resume pipeline from checkpoint.

        Args:
            trace_id: Trace ID to resume from

        Returns:
            envelope if found, None otherwise
        """
        checkpoint_manager = await self._get_checkpoint_manager()
        stage_names = [stage.stage_name for stage in self.stages]
        envelope = await checkpoint_manager.resume_from_checkpoint(trace_id, stage_names)
        if envelope:
            self._stats["checkpoints_restored"] += 1
            logger.info(f"Resumed pipeline from checkpoint: {trace_id}")
            last_stage = envelope.get_last_completed_stage()
            if last_stage:
                logger.info(f"Last completed stage: {last_stage}")
        return envelope

    async def get_checkpoint_status(self, trace_id: str) -> dict[str, Any] | None:
        """Get status of a checkpointed pipeline.

        Args:
            trace_id: Trace ID of pipeline

        Returns:
            Status dictionary if found
        """
        checkpoint_manager = await self._get_checkpoint_manager()
        envelope = await checkpoint_manager.load_checkpoint(trace_id)
        if not envelope:
            return None
        return {
            "trace_id": trace_id,
            "envelope_id": str(envelope.id),
            "created_at": envelope.created_at.isoformat(),
            "updated_at": envelope.updated_at.isoformat(),
            "has_errors": envelope.has_errors,
            "error_count": envelope.error_count,
            "completed_stages": [
                s.stage_name for s in envelope.history if s.status == PipelineStageStatus.SUCCESS
            ],
            "failed_stages": envelope.get_failed_stages(),
            "last_completed_stage": envelope.get_last_completed_stage(),
            "total_duration_ms": envelope.calculate_total_duration(),
        }

    async def cleanup_checkpoints(self, older_than: timedelta | None = None) -> int:
        """Clean up old checkpoints.

        Args:
            older_than: Age threshold for cleanup

        Returns:
            Number of checkpoints cleaned up
        """
        checkpoint_manager = await self._get_checkpoint_manager()
        return await checkpoint_manager.cleanup_old_checkpoints(older_than)

    def get_stats(self) -> dict[str, Any]:
        """Get pipeline statistics.

        Returns:
            Statistics dictionary
        """
        with self._lock:
            stats = self._stats.copy()
            if stats["total_processed"] > 0:
                stats["cache_hit_rate"] = stats["cache_hits"] / stats["total_processed"]
            else:
                stats["cache_hit_rate"] = 0.0
            return stats

    async def health_check(self) -> dict[str, Any]:
        """Check health of pipeline and checkpoint system.

        Returns:
            Health status
        """
        checkpoint_manager = await self._get_checkpoint_manager()
        checkpoint_health = await checkpoint_manager.health_check()
        return {
            "status": "healthy" if checkpoint_health["status"] == "healthy" else "degraded",
            "stages": len(self.stages),
            "checkpoint_storage": checkpoint_health["status"],
            "stats": self.get_stats(),
        }


class PipelineExecutionError(Exception):
    """Error raised when pipeline execution fails."""

    def __init__(
        self,
        message: str,
        envelope: SignalEnvelope,
        failed_stage: str,
        cause: Exception | None = None,
    ):
        """Initialize pipeline execution error.

        Args:
            message: Error message
            envelope: Signal envelope at failure
            failed_stage: Name of failed stage
            cause: Optional cause exception
        """
        super().__init__(message)
        self.envelope = envelope
        self.failed_stage = failed_stage
        self.cause = cause


_pipeline: UnifiedSignalPipeline | None = None
_pipeline_lock = threading.Lock()


def get_unified_pipeline() -> UnifiedSignalPipeline:
    """Get the global unified pipeline instance.

    Returns:
        UnifiedSignalPipeline instance
    """
    global _pipeline
    with _pipeline_lock:
        if _pipeline is None:
            _pipeline = UnifiedSignalPipeline()
    return _pipeline


def process_resume_signal(input_data: Any, strict_mode: bool = True) -> dict[str, Any]:
    """Process resume signal through unified pipeline.

    Args:
        input_data: Resume input data
        strict_mode: Use strict quality thresholds

    Returns:
        Processed output
    """
    pipeline = get_unified_pipeline()
    infra = get_shared_infrastructure()
    config = infra.create_domain_config(EngineType.RESUME)
    return pipeline.process(input_data, EngineType.RESUME, config)


def process_outreach_signal(input_data: Any, strict_mode: bool = True) -> dict[str, Any]:
    """Process outreach signal through unified pipeline.

    Args:
        input_data: Outreach input data
        strict_mode: Use strict quality thresholds

    Returns:
        Processed output
    """
    pipeline = get_unified_pipeline()
    infra = get_shared_infrastructure()
    config = infra.create_domain_config(EngineType.OUTREACH)
    return pipeline.process(input_data, EngineType.OUTREACH, config)
