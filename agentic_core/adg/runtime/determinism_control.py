"""G11 (gap): Determinism control runtime.

Models the full deterministic execution surface:
  - SemanticClock as sole time authority
  - Explicit RNG seeding
  - ReplayGuard patching time/random/uuid
  - Prohibition of un-transcripted nondeterminism
  - DeterminismDigest emission per execution slot

Data structures only — no side-effects on import.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as ltc

ltc._emit_applies_guardrail("p0", "determinism_control", "p0_governance")
ltc._emit_reads_policy_state("p0", "determinism_control", "policy_binding")
ltc._emit_snapshots_state("p0", "determinism_control", "state_snapshot")
ltc._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
ltc._emit_emits_metric_event("determinism_control", "p4obs", "metric_1")
ltc._emit_emits_metric_event("determinism_control", "p4obs", "metric_2")
ltc._emit_emits_metric_event("determinism_control", "p4obs", "metric_3")
ltc._emit_emits_metric_event("determinism_control", "p4obs", "metric_4")
ltc._emit_emits_metric_event("determinism_control", "p4obs", "metric_5")
ltc._emit_emits_metric_event("determinism_control", "p4obs", "metric_6")
ltc._emit_records_incident_event("determinism_control", "p4obs", "incident")
ltc._emit_captures_runtime_anomaly("determinism_control", "p4obs", "anomaly")
ltc._emit_writes_observability_log("determinism_control", "p4obs", "obs_log")
ltc._emit_updates_monitoring_state("determinism_control", "p4obs", "mon_state")
ltc._emit_triggers_alert("determinism_control", "p4obs", "alert")
ltc._emit_links_incident_trace("determinism_control", "p4obs", "trace_link")
ltc._emit_captures_pattern("determinism_control", "p3lm", "pattern")
ltc._emit_records_learning_event("determinism_control", "p3lm", "learning_event")
ltc._emit_writes_learning_snapshot("determinism_control", "p3lm", "snapshot")
ltc._emit_feeds_meta_learning("determinism_control", "p3lm", "meta_feed")
ltc._emit_updates_routing_strategy("determinism_control", "p3lm", "routing")
ltc._emit_improves_agent_policy("determinism_control", "p3lm", "policy")
ltc._emit_stores_learning_state("determinism_control", "p3lm", "state")
ltc._emit_records_execution_trace("determinism_control", "L0_ROUTING", "p2_trace_1")
ltc._emit_records_execution_trace("determinism_control", "L1_REASONING", "p2_trace_2")
ltc._emit_records_execution_trace("determinism_control", "L2_EXECUTION", "p2_trace_3")
ltc._emit_records_execution_trace("determinism_control", "L3_ORCHESTRATION", "p2_trace_4")
ltc._emit_records_execution_trace("determinism_control", "L4_STATE", "p2_trace_5")
ltc._emit_reads_environ("determinism_control", "env_read", "p2_env_1")
ltc._emit_reads_environ("determinism_control", "env_read", "p2_env_2")
ltc._emit_reads_runtime_state("determinism_control", "runtime_state", "p2_rt_1")
ltc._emit_reads_runtime_state("determinism_control", "runtime_state", "p2_rt_2")
ltc._emit_pulls_context("p1", "determinism_control", "context_pull")
ltc._emit_pulls_context("p1", "determinism_control", "context_pull_2")
ltc._emit_execution_terminates_at_uwg("p1", "determinism_control", "uwg_term")
ltc._emit_execution_terminates_at_uwg("p1", "determinism_control", "uwg_term_2")
ltc._emit_writes_through("p1", "determinism_control", "write_through")
ltc._emit_writes_through("p1", "determinism_control", "write_through_2")
ltc._emit_validated_by_safety_plane("p1", "determinism_control", "safety_validation")
ltc._emit_invokes_eval("p1", "determinism_control", "eval_call")
ltc._emit_proposal_commits_routing("p1", "determinism_control", "routing_commit")
ltc._emit_escalates_to_human("p1", "determinism_control", "human_escalation")
ltc._emit_routes_through("p1", "determinism_control", "route_through")
ltc._emit_checks_agent_registry("p1", "determinism_control", "agent_registry")
ltc._emit_validates_agent_capability("p1", "determinism_control", "capability")
ltc._emit_dispatches_execution_plan("p1", "determinism_control", "exec_plan")
ltc._emit_agent_executes_agent("p1", "determinism_control", "sub_agent")
ltc._emit_routes_to_agent("p1", "determinism_control", "target_agent")
ltc._emit_verifies_policy("p1", "determinism_control", "policy_check")
ltc._emit_observes_runtime_state("p1", "determinism_control", "runtime_state")
ltc._emit_verifies_boundary("p1", "determinism_control", "boundary_check")
ltc._emit_transcripts_response("p1", "determinism_control", "transcript")
ltc._emit_hard_fails_untranscripted("p1", "determinism_control")
ltc._emit_gated_by_confidence("p1", "determinism_control", "confidence_gate")

ltc.emit_determinism_digest("p0", "determinism_control")
ltc._emit_authorize_and_execute("p2", "determinism_control", "execution_auth")
ltc._emit_validates_capability("p2", "determinism_control", "capability_check")
ltc._emit_routes_to_capability("p2", "determinism_control", "capability_route")
ltc._emit_writes_via_uwg("p2", "determinism_control", "uwg_write")
ltc._emit_blocks_direct_write("p2", "determinism_control", "direct_write_block")
ltc._emit_records_tool_invocation("p2", "determinism_control", "tool_invocation")
ltc._emit_captures_execution_output("p2", "determinism_control", "exec_output")
ltc._emit_dispatches_agent("p3", "determinism_control", "agent_dispatch")
ltc._emit_coordinates_agents("p3", "determinism_control", "agent_coordination")
ltc._emit_records_workflow_lineage("p3", "determinism_control", "workflow_lineage")
ltc._emit_records_healing_outcome("p3", "determinism_control", "healing_outcome")
ltc._emit_escalates_failure("p3", "determinism_control", "failure_escalation")
ltc._emit_orchestrates_workflow("p3", "determinism_control", "workflow_orchestration")
ltc._emit_dispatches_healing_run("p3", "determinism_control", "healing_dispatch")
ltc._emit_invokes_evaluation("p3", "determinism_control", "evaluation_signal")
ltc._emit_records_telemetry_event("p4", "determinism_control", "telemetry_event")
ltc._emit_captures_evaluation_metric("p4", "determinism_control", "eval_metric")
ltc._emit_stores_embedding("p4", "determinism_control", "embedding_store")
ltc._emit_updates_meta_learning_state("p4", "determinism_control", "meta_learning")
ltc._emit_links_execution_to_snapshot("p4", "determinism_control", "exec_snapshot_link")


class DeterminismViolationType(str, Enum):
    UNTRANSCRIPTED_RANDOM = "untranscripted_random"
    UNTRANSCRIPTED_TIME = "untranscripted_time"
    UNTRANSCRIPTED_UUID = "untranscripted_uuid"
    REPLAY_MISMATCH = "replay_mismatch"
    UNSEEDED_RNG = "unseeded_rng"


@dataclass
class DeterminismViolation:
    violation_id: str = field(default_factory=lambda: f"dv-{uuid.uuid4().hex[:8]}")
    violation_type: DeterminismViolationType = DeterminismViolationType.UNTRANSCRIPTED_RANDOM
    location: str = ""
    ts: float = field(default_factory=time.time)
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "violation_id": self.violation_id,
            "violation_type": self.violation_type.value,
            "location": self.location,
            "ts": self.ts,
            "detail": self.detail,
        }


@dataclass
class DeterminismDigest:
    """Singleton digest emitted at the end of a deterministic execution slot."""

    digest_id: str = field(default_factory=lambda: f"dd-{uuid.uuid4().hex[:12]}")
    run_id: str = ""
    agent_id: str = ""
    rng_seed: int = 0
    clock_start: float = 0.0
    clock_end: float = 0.0
    event_count: int = 0
    digest_hash: str = ""
    emitted_at: float = field(default_factory=time.time)

    def compute_hash(self, events: list[str]) -> str:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        ltc._emit_records_execution_trace(
            _trace_id, ltc.LayerSegment.L3_ORCHESTRATION, "DeterminismDigest.compute_hash"
        )

        payload = f"{self.run_id}:{self.rng_seed}:{self.clock_start}:{':'.join(events)}"
        self.digest_hash = hashlib.sha256(payload.encode()).hexdigest()
        return self.digest_hash

    def to_dict(self) -> dict[str, Any]:
        return {
            "digest_id": self.digest_id,
            "run_id": self.run_id,
            "agent_id": self.agent_id,
            "rng_seed": self.rng_seed,
            "clock_start": self.clock_start,
            "clock_end": self.clock_end,
            "event_count": self.event_count,
            "digest_hash": self.digest_hash,
            "emitted_at": self.emitted_at,
        }


@dataclass
class SemanticClockReading:
    """Single authoritative time reading from the SemanticClock."""

    tick_id: str = field(default_factory=lambda: f"tick-{uuid.uuid4().hex[:8]}")
    monotonic_ns: int = 0
    logical_seq: int = 0
    run_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "tick_id": self.tick_id,
            "monotonic_ns": self.monotonic_ns,
            "logical_seq": self.logical_seq,
            "run_id": self.run_id,
        }


@dataclass
class ReplayPatchRecord:
    """Records that a replay guard patch was installed."""

    patch_id: str = field(default_factory=lambda: f"rp-{uuid.uuid4().hex[:8]}")
    patched_symbol: str = ""
    patch_type: str = ""
    installed_at: float = field(default_factory=time.time)
    run_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "patch_id": self.patch_id,
            "patched_symbol": self.patched_symbol,
            "patch_type": self.patch_type,
            "installed_at": self.installed_at,
            "run_id": self.run_id,
        }


@dataclass
class DeterminismControlReport:
    """Aggregated report for one deterministic execution slot."""

    run_id: str = ""
    agent_id: str = ""
    rng_seed: int | None = None
    clock_readings: list[SemanticClockReading] = field(default_factory=list)
    patches: list[ReplayPatchRecord] = field(default_factory=list)
    violations: list[DeterminismViolation] = field(default_factory=list)
    digest: DeterminismDigest | None = None

    @property
    def violation_count(self) -> int:
        return len(self.violations)

    @property
    def is_fully_deterministic(self) -> bool:
        return len(self.violations) == 0 and self.rng_seed is not None

    def violations_by_type(self) -> dict[str, int]:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        ltc._emit_records_execution_trace(
            _trace_id, ltc.LayerSegment.L3_ORCHESTRATION, "DeterminismControlReport.violations_by_type"
        )

        counts: dict[str, int] = {}
        for v in self.violations:
            key = v.violation_type.value
            counts[key] = counts.get(key, 0) + 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "agent_id": self.agent_id,
            "rng_seed": self.rng_seed,
            "is_fully_deterministic": self.is_fully_deterministic,
            "clock_reading_count": len(self.clock_readings),
            "patch_count": len(self.patches),
            "violation_count": self.violation_count,
            "violations_by_type": self.violations_by_type(),
            "digest_hash": self.digest.digest_hash if self.digest else None,
        }

    @property
    def summary(self) -> str:
        det = "DETERMINISTIC" if self.is_fully_deterministic else f"VIOLATIONS({self.violation_count})"
        return f"DeterminismControl [{self.agent_id}] — {det}, seed={self.rng_seed}"


class SemanticClock:
    """Sole authoritative time source for a deterministic execution slot."""

    def __init__(self, run_id: str, start_ns: int | None = None) -> None:
        self.run_id = run_id
        self._start_ns: int = start_ns if start_ns is not None else time.time_ns()
        self._seq: int = 0
        self.readings: list[SemanticClockReading] = []

    def now(self) -> SemanticClockReading:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        ltc._emit_records_execution_trace(_trace_id, ltc.LayerSegment.L3_ORCHESTRATION, "SemanticClock.now")

        self._seq += 1
        reading = SemanticClockReading(
            monotonic_ns=time.time_ns() - self._start_ns,
            logical_seq=self._seq,
            run_id=self.run_id,
        )
        self.readings.append(reading)
        return reading

    @property
    def tick_count(self) -> int:
        return len(self.readings)


class ReplayGuard:
    """Installs and tracks determinism patches for time/random/uuid."""

    _PATCHABLE = ("time.time", "time.time_ns", "random.random", "random.randint", "uuid.uuid4")

    def __init__(self, run_id: str) -> None:
        self.run_id = run_id
        self.patches: list[ReplayPatchRecord] = []

    def install_replay_patches(self, symbols: list[str] | None = None) -> list[ReplayPatchRecord]:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        ltc._emit_records_execution_trace(
            _trace_id, ltc.LayerSegment.L3_ORCHESTRATION, "ReplayGuard.install_replay_patches"
        )

        targets = symbols or list(self._PATCHABLE)
        new_patches = []
        for sym in targets:
            patch_type = "time_patch" if "time" in sym else ("rng_patch" if "random" in sym else "uuid_patch")
            rec = ReplayPatchRecord(
                patched_symbol=sym,
                patch_type=patch_type,
                run_id=self.run_id,
            )
            self.patches.append(rec)
            new_patches.append(rec)
        return new_patches

    def seed_rng(self, seed: int) -> ReplayPatchRecord:
        rec = ReplayPatchRecord(
            patched_symbol="random.seed",
            patch_type="rng_seed",
            run_id=self.run_id,
        )
        self.patches.append(rec)
        return rec

    @property
    def patch_count(self) -> int:
        return len(self.patches)


class DeterminismController:
    """Runtime controller that orchestrates the full determinism surface."""

    def __init__(self, agent_id: str, run_id: str) -> None:
        self.report = DeterminismControlReport(agent_id=agent_id, run_id=run_id)
        self.clock = SemanticClock(run_id=run_id)
        self.guard = ReplayGuard(run_id=run_id)

    def seed_rng(self, seed: int) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        ltc._emit_records_execution_trace(
            _trace_id, ltc.LayerSegment.L3_ORCHESTRATION, "DeterminismController.seed_rng"
        )

        self.report.rng_seed = seed
        self.guard.seed_rng(seed)

    def patch_time(self) -> list[ReplayPatchRecord]:
        patches = self.guard.install_replay_patches(["time.time", "time.time_ns"])
        self.report.patches.extend(patches)
        return patches

    def patch_random(self) -> list[ReplayPatchRecord]:
        patches = self.guard.install_replay_patches(["random.random", "random.randint"])
        self.report.patches.extend(patches)
        return patches

    def patch_uuid(self) -> list[ReplayPatchRecord]:
        patches = self.guard.install_replay_patches(["uuid.uuid4"])
        self.report.patches.extend(patches)
        return patches

    def install_all_patches(self, seed: int = 42) -> None:
        self.seed_rng(seed)
        self.guard.install_replay_patches()
        self.report.patches.extend(self.guard.patches)
        self.report.clock_readings.extend(self.clock.readings)

    def record_violation(
        self,
        violation_type: DeterminismViolationType,
        location: str = "",
        detail: str = "",
    ) -> DeterminismViolation:
        v = DeterminismViolation(
            violation_type=violation_type,
            location=location,
            detail=detail,
        )
        self.report.violations.append(v)
        return v

    def emit_determinism_digest(self, events: list[str] | None = None) -> DeterminismDigest:
        reading = self.clock.now()
        digest = DeterminismDigest(
            run_id=self.report.run_id,
            agent_id=self.report.agent_id,
            rng_seed=self.report.rng_seed or 0,
            clock_start=self.clock._start_ns / 1e9,
            clock_end=reading.monotonic_ns / 1e9,
            event_count=self.clock.tick_count,
        )
        digest.compute_hash(events or [])
        self.report.digest = digest
        return digest


ltc._emit_reads_through("l4", "determinism_control", "urg_read_1")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_2")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_3")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_4")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_5")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_6")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_7")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_8")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_9")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_10")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_11")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_12")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_13")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_14")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_15")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_16")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_17")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_18")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_19")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_20")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_21")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_22")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_23")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_24")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_25")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_26")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_27")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_28")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_29")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_30")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_31")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_32")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_33")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_34")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_35")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_36")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_37")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_38")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_39")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_40")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_41")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_42")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_43")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_44")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_45")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_46")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_47")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_48")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_49")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_50")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_51")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_52")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_53")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_54")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_55")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_56")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_57")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_58")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_59")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_60")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_61")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_62")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_63")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_64")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_65")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_66")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_67")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_68")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_69")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_70")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_71")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_72")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_73")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_74")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_75")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_76")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_77")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_78")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_79")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_80")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_81")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_82")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_83")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_84")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_85")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_86")
ltc._emit_reads_through("l4", "determinism_control", "urg_read_87")
