"""M1-M6 ADGGateBase subclasses — wave0 ratchet gates migrated from _adg_ci_gates.py.

These gates read graph_plane_counts (GPC) from the Redis ADG snapshot and evaluate
count-delta and ratio metrics. They no longer use the bespoke _adg_ci_gates.py
baseline; they use ADGGateBase._load_baseline / _save_baseline (per-gate JSON files
in artifacts/adg/ci_ratchets/).

Migration notes (HITL H3):
    - Source logic preserved exactly from _adg_ci_gates.py evaluator functions.
    - Baseline data migrated lazily: if per-gate baseline file is absent, the first
      successful run seeds it from the live GPC snapshot (same as --init).
    - _adg_ci_gates.py is preserved as a shim and deprecated; it will be removed
      after one full wave of parallel operation confirms parity.
    - M7/M8/M9 (edge-count floors) remain in _adg_ci_gates.py shim for now
      (these are min-floor checks, not delta ratchets — low migration priority).
"""

from __future__ import annotations

import sys
from pathlib import Path


def _bootstrap_repo_root() -> Path:
    repo_root = Path(__file__).resolve().parents[3]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    return repo_root


_REPO_ROOT = _bootstrap_repo_root()

import json
from datetime import datetime, timezone
from typing import Any

from ops_scripts.ci.adg_gates.gate_base import ADGGateBase, GateResult, GateViolation
from ops_scripts.ci.adg_gates.gate_policy import ExecutionPolicy

# Thresholds (kept in sync with _adg_ci_gates.py)
GUARDRAIL_COVERAGE_THRESHOLD = 0.10
TRACE_COVERAGE_THRESHOLD = 0.05

import os

_REDIS_HOST = os.getenv("ADG_M_GATES_REDIS_HOST", "localhost")
_REDIS_PORT = int(os.getenv("ADG_M_GATES_REDIS_PORT", "6379"))
_REDIS_DB = int(os.getenv("ADG_M_GATES_REDIS_DB", "0"))
_REDIS_SOCKET_TIMEOUT = float(os.getenv("ADG_M_GATES_REDIS_TIMEOUT", "5"))
_REDIS_CONNECT_TIMEOUT = float(os.getenv("ADG_M_GATES_REDIS_CONNECT_TIMEOUT", "2"))


def _get_gpc() -> dict[str, int]:
    """Fetch graph_plane_counts from Redis ADG snapshot."""
    try:
        import redis  # type: ignore[import]
    except ImportError as exc:
        raise RuntimeError("redis-py not installed; run: pip install redis") from exc

    try:
        r = redis.Redis(
            host=_REDIS_HOST,
            port=_REDIS_PORT,
            db=_REDIS_DB,
            decode_responses=True,
            socket_timeout=_REDIS_SOCKET_TIMEOUT,
            socket_connect_timeout=_REDIS_CONNECT_TIMEOUT,
            health_check_interval=30,
            retry_on_timeout=True,
        )
        r.ping()
        raw = r.get("adg:snapshot")
    except redis.RedisError as exc:
        raise RuntimeError(
            "unable to read Redis ADG snapshot "
            f"(host={_REDIS_HOST}, port={_REDIS_PORT}, db={_REDIS_DB}): {exc}"
        ) from exc
    if not raw:
        raise RuntimeError(
            "adg:snapshot key missing from Redis — run: python tools/adg/adg_redis_ingest.py --force"
        )
    try:
        snap = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("adg:snapshot contains invalid JSON") from exc
    return snap.get("graph_plane_counts", {})


class _MGateBase(ADGGateBase):
    """Base for M-series gates that read from Redis GPC (not SQLite MV).

    Overrides _find_latest_sqlite and _connect/_close to be no-ops since
    M-gates source their data from Redis, not ADG SQLite materialized views.
    The sqlite_path is still accepted for interface consistency.
    """

    gate_key: str = ""  # unique key for per-gate baseline file

    def _find_latest_sqlite(self) -> Path:
        """M-gates don't require SQLite; return a sentinel path."""
        return Path("/dev/null")

    def _connect(self) -> None:
        """No SQLite connection needed for M-gates."""

    def _close(self) -> None:
        """Nothing to close."""

    def _get_snapshot_id(self) -> str:
        return f"redis_gpc_{self.gate_key}"

    def _get_gpc(self) -> dict[str, int] | None:
        """Fetch GPC; return None on failure (gate degrades to warn)."""
        try:
            return _get_gpc()
        except RuntimeError as exc:
            print(f"[{self.gate_family}] WARNING: Redis unavailable — {exc}", file=sys.stderr)
            return None

    def _load_gpc_baseline(self) -> dict[str, int]:
        """Load per-gate GPC baseline. Returns {} if not yet seeded."""
        data = self._load_baseline(self.gate_key)
        return data.get("snapshot", {})

    def _save_gpc_baseline(self, gpc: dict[str, int]) -> None:
        """Save per-gate GPC baseline."""
        self._save_baseline(self.gate_key, {"snapshot": gpc})

    def _seed_baseline_if_absent(self, gpc: dict[str, int]) -> None:
        """Seed baseline from live GPC on first run (migration from wave0_baseline.json)."""
        existing = self._load_gpc_baseline()
        if not existing:
            print(
                f"[{self.gate_family}] Seeding baseline from live GPC snapshot.",
                file=sys.stderr,
            )
            self._save_gpc_baseline(gpc)

    def _make_passed_result(self, msg: str, gpc: dict[str, int]) -> GateResult:
        return GateResult(
            gate_family=self.gate_family,
            severity=self.severity,
            snapshot_id=self._snapshot_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status="passed",
            violations=[],
            summary={"message": msg, "gpc_sample": dict(list(gpc.items())[:5])},
            policy=getattr(self, "execution_policy", ExecutionPolicy()),
            stage="full",
        )

    def _make_blocked_result(self, msg: str, gpc: dict[str, int]) -> GateResult:
        return GateResult(
            gate_family=self.gate_family,
            severity=self.severity,
            snapshot_id=self._snapshot_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status="blocked",
            violations=[
                GateViolation(
                    violation_id=f"{self.gate_family}_ratchet",
                    source_view="redis_gpc",
                    source_node=None,
                    source_edge=None,
                    file=None,
                    line=None,
                    layer_src=None,
                    layer_dst=None,
                    path_id=None,
                    first_illegal_hop=None,
                    path_criticality=1.0,
                    in_modified_area=False,
                    message=msg,
                )
            ],
            summary={"message": msg, "gpc_sample": dict(list(gpc.items())[:5])},
            policy=getattr(self, "execution_policy", ExecutionPolicy()),
            stage="full",
        )

    def _make_degraded_result(self) -> GateResult:
        """Return warn result when Redis is unavailable."""
        return GateResult(
            gate_family=self.gate_family,
            severity=self.severity,
            snapshot_id=self._snapshot_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status="warn",
            violations=[],
            summary={"message": "Redis unavailable — gate degraded to warn"},
            policy=getattr(self, "execution_policy", ExecutionPolicy()),
            stage="full",
        )


# ---------------------------------------------------------------------------
# M1 — Determinism Gate
# ---------------------------------------------------------------------------


class M1DeterminismGate(_MGateBase):
    """M1: wall_clock delta <= 0, or determinism injection added."""

    gate_family = "m1_determinism"
    severity = "P1"
    source_views = ["redis_gpc"]
    gate_key = "m1_determinism"
    execution_policy = ExecutionPolicy(
        stage="full",
        repairability="suggest_only",
        gate_action="ratchet",
        artifact_policy="full_adg_report",
        signal_source="canonical_policy",
        evidence_tier="truth",
    )

    def _execute_gate_logic(self) -> GateResult:
        gpc = self._get_gpc()
        if gpc is None:
            return self._make_degraded_result()

        self._seed_baseline_if_absent(gpc)
        base = self._load_gpc_baseline()

        wc_base = base.get("uses_wall_clock", 0)
        wc_cur = gpc.get("uses_wall_clock", 0)
        det_base = base.get("emits_determinism_digest", 0)
        det_cur = gpc.get("emits_determinism_digest", 0)
        rng_base = base.get("seeds_rng", 0)
        rng_cur = gpc.get("seeds_rng", 0)
        wc_delta = wc_cur - wc_base
        det_delta = det_cur - det_base
        rng_delta = rng_cur - rng_base

        if wc_delta > 0 and det_delta <= 0 and rng_delta <= 0:
            msg = (
                f"uses_wall_clock +{wc_delta} ({wc_base}->{wc_cur}) with no determinism injection "
                f"(emits_determinism_digest delta={det_delta}, seeds_rng delta={rng_delta})"
            )
            return self._make_blocked_result(msg, gpc)

        msg = f"OK: uses_wall_clock delta={wc_delta}, det_injection delta={det_delta + rng_delta}"
        self._save_gpc_baseline(gpc)
        return self._make_passed_result(msg, gpc)


# ---------------------------------------------------------------------------
# M2 — Dispatch Visibility Gate
# ---------------------------------------------------------------------------


class M2DispatchVisibilityGate(_MGateBase):
    """M2: getattr_dynamic delta <= 0, or typed dispatch added."""

    gate_family = "m2_dispatch_visibility"
    severity = "P1"
    source_views = ["redis_gpc"]
    gate_key = "m2_dispatch_visibility"
    execution_policy = ExecutionPolicy(
        stage="full",
        repairability="suggest_only",
        gate_action="ratchet",
        artifact_policy="full_adg_report",
        signal_source="canonical_policy",
        evidence_tier="truth",
    )

    def _execute_gate_logic(self) -> GateResult:
        gpc = self._get_gpc()
        if gpc is None:
            return self._make_degraded_result()

        self._seed_baseline_if_absent(gpc)
        base = self._load_gpc_baseline()

        gad_base = base.get("invokes_getattr_dynamic", 0)
        gad_cur = gpc.get("invokes_getattr_dynamic", 0)
        aea_base = base.get("agent_executes_agent", 0)
        aea_cur = gpc.get("agent_executes_agent", 0)
        gad_delta = gad_cur - gad_base
        aea_delta = aea_cur - aea_base

        if gad_delta > 0 and aea_delta <= 0:
            msg = (
                f"invokes_getattr_dynamic +{gad_delta} ({gad_base}->{gad_cur}) with no typed "
                f"dispatch added (agent_executes_agent delta={aea_delta})"
            )
            return self._make_blocked_result(msg, gpc)

        msg = f"OK: getattr_dynamic delta={gad_delta}, typed_dispatch delta={aea_delta}"
        self._save_gpc_baseline(gpc)
        return self._make_passed_result(msg, gpc)


# ---------------------------------------------------------------------------
# M3 — Mutation Sovereignty Gate
# ---------------------------------------------------------------------------


class M3MutationSovereigntyGate(_MGateBase):
    """M3: writes_to delta <= 0, or writes_through added."""

    gate_family = "m3_mutation_sovereignty"
    severity = "P1"
    source_views = ["redis_gpc"]
    gate_key = "m3_mutation_sovereignty"
    execution_policy = ExecutionPolicy(
        stage="full",
        repairability="manual_only",
        gate_action="ratchet",
        artifact_policy="full_adg_report",
        signal_source="canonical_policy",
        evidence_tier="truth",
    )

    def _execute_gate_logic(self) -> GateResult:
        gpc = self._get_gpc()
        if gpc is None:
            return self._make_degraded_result()

        self._seed_baseline_if_absent(gpc)
        base = self._load_gpc_baseline()

        wt_base = base.get("writes_to", 0)
        wt_cur = gpc.get("writes_to", 0)
        wth_base = base.get("writes_through", 0)
        wth_cur = gpc.get("writes_through", 0)
        wt_delta = wt_cur - wt_base
        wth_delta = wth_cur - wth_base

        if wt_delta > 0 and wth_delta <= 0:
            msg = (
                f"writes_to +{wt_delta} ({wt_base}->{wt_cur}) with no UWG writes added "
                f"(writes_through delta={wth_delta})"
            )
            return self._make_blocked_result(msg, gpc)

        msg = f"OK: writes_to delta={wt_delta}, writes_through delta={wth_delta}"
        self._save_gpc_baseline(gpc)
        return self._make_passed_result(msg, gpc)


# ---------------------------------------------------------------------------
# M4 — Guardrail Coverage Gate
# ---------------------------------------------------------------------------


class M4GuardrailCoverageGate(_MGateBase):
    """M4: applies_guardrail / calls >= 0.10."""

    gate_family = "m4_guardrail_coverage"
    severity = "P1"
    source_views = ["redis_gpc"]
    gate_key = "m4_guardrail_coverage"
    execution_policy = ExecutionPolicy(
        stage="full",
        repairability="suggest_only",
        gate_action="ratchet",
        artifact_policy="full_adg_report",
        signal_source="canonical_policy",
        evidence_tier="truth",
    )

    def _execute_gate_logic(self) -> GateResult:
        gpc = self._get_gpc()
        if gpc is None:
            return self._make_degraded_result()

        ag = gpc.get("applies_guardrail", 0)
        calls = gpc.get("calls", 1)
        ratio = ag / calls if calls > 0 else 0.0
        threshold = GUARDRAIL_COVERAGE_THRESHOLD

        if ratio < threshold:
            msg = f"applies_guardrail/calls = {ag}/{calls} = {ratio:.4f} < {threshold} required"
            return self._make_blocked_result(msg, gpc)

        msg = f"OK: guardrail ratio = {ratio:.4f} ({ag}/{calls})"
        return self._make_passed_result(msg, gpc)


# ---------------------------------------------------------------------------
# M5 — Trace Coverage Gate
# ---------------------------------------------------------------------------


class M5TraceCoverageGate(_MGateBase):
    """M5: records_execution_trace / (calls + invokes_eval) >= 0.05."""

    gate_family = "m5_trace_coverage"
    severity = "P1"
    source_views = ["redis_gpc"]
    gate_key = "m5_trace_coverage"
    execution_policy = ExecutionPolicy(
        stage="full",
        repairability="suggest_only",
        gate_action="ratchet",
        artifact_policy="full_adg_report",
        signal_source="canonical_policy",
        evidence_tier="truth",
    )

    def _execute_gate_logic(self) -> GateResult:
        gpc = self._get_gpc()
        if gpc is None:
            return self._make_degraded_result()

        ret = gpc.get("records_execution_trace", 0)
        calls = gpc.get("calls", 0)
        inv_eval = gpc.get("invokes_eval", 0)
        denom = calls + inv_eval
        ratio = ret / denom if denom > 0 else 0.0
        threshold = TRACE_COVERAGE_THRESHOLD

        if ratio < threshold:
            msg = f"trace_coverage = {ret}/{denom} = {ratio:.4f} < {threshold} required"
            return self._make_blocked_result(msg, gpc)

        msg = f"OK: trace coverage = {ratio:.4f} ({ret}/{denom})"
        return self._make_passed_result(msg, gpc)


# ---------------------------------------------------------------------------
# M6 — Replay Key Gate
# ---------------------------------------------------------------------------


class M6ReplayKeyGate(_MGateBase):
    """M6: emits_replay_key must not decrease."""

    gate_family = "m6_replay_key"
    severity = "P1"
    source_views = ["redis_gpc"]
    gate_key = "m6_replay_key"
    execution_policy = ExecutionPolicy(
        stage="full",
        repairability="manual_only",
        gate_action="ratchet",
        artifact_policy="full_adg_report",
        signal_source="canonical_policy",
        evidence_tier="truth",
    )

    def _execute_gate_logic(self) -> GateResult:
        gpc = self._get_gpc()
        if gpc is None:
            return self._make_degraded_result()

        self._seed_baseline_if_absent(gpc)
        base = self._load_gpc_baseline()

        erk_base = base.get("emits_replay_key", 0)
        erk_cur = gpc.get("emits_replay_key", 0)
        delta = erk_cur - erk_base

        if delta < 0:
            msg = f"emits_replay_key regressed: {erk_base}->{erk_cur} (delta={delta})"
            return self._make_blocked_result(msg, gpc)

        msg = f"OK: emits_replay_key {erk_base}->{erk_cur} (delta={delta})"
        self._save_gpc_baseline(gpc)
        return self._make_passed_result(msg, gpc)
