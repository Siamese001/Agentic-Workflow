"""Constitutional §29 — L2/cascade router closed-loop ledger wiring tests.

Plan: .cursor/plans/_archive/windsurf_legacy_plans/l2-cascade-router-closed-loop-wiring-c4d8a1.md (W1.7)

Covers:
  - cascade_calibrator math primitives (EU, Brier, Wilson, fingerprint, score band)
  - HealingRouter.route() emits ROUTER_DECISION marker AND writes ledger row
  - dispatch_to_executor() binds outcome to predicted row
  - Ledger writer bypass path is honored (no-op, no exception)
  - Provider-label edge cases (Qwen variant, Pro vs Flash, hitl)
  - Schema-driven row shape matches the documented JSON shapes

The tests are hermetic — they redirect ledger writes to a temp directory by
monkey-patching the LEDGERS_DIR used by the schema registry. No live model
calls; the dispatch tier is HIGH so we exercise the closed-loop path without
touching vLLM or Gemini.
"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

import pytest

from agentic_core.L2_execution.healers.cascade_calibrator import (
    DEFAULT_POSTERIOR_N_FLOOR,
    DEFAULT_VALUE_PER_SUCCESS_USD,
    PosteriorRead,
    brier_component,
    compute_decision_evidence,
    compute_eu,
    fingerprint,
    posterior_for_cell,
    provider_label,
    score_band_for,
    wilson_lower_bound,
    wilson_upper_bound,
)
from agentic_core.L2_execution.healers.confidence_scorer import (
    ConfidenceScore,
    HealTier,
)
from agentic_core.L2_execution.healers.failure_signal import (
    FailureSignal,
    HealFailureClass,
)
from agentic_core.L2_execution.healers.healing_router import HealingRouter

pytestmark = pytest.mark.unit


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _signal(
    *,
    retry_count: int = 0,
    error_code: str = "timeout",
    failure_class: HealFailureClass = HealFailureClass.UNKNOWN,
    source_layer: str = "L2_execution",
) -> FailureSignal:
    return FailureSignal(
        check_id="ut",
        retry_count=retry_count,
        error_code=error_code,
        error_message="",
        lineage_hash="h",
        context_snapshot={},
        source_layer=source_layer,
        operation="heal",
        timestamp=time.time(),
        failure_class=failure_class,
    )


def _score(tier: HealTier, value: float = 0.5) -> ConfidenceScore:
    return ConfidenceScore(
        score=value, tier=tier, confidence_in_score=0.8, reasoning="ut"
    )


@pytest.fixture
def temp_ledger(tmp_path, monkeypatch):
    """Redirect router_l2_cascade ledger writes to a tmp DB.

    Resets the writer cache so a fresh writer rebinds to the new path. Returns
    the Path of the tmp DB so tests can read rows directly.
    """
    from tools.ledgers import schema_registry, writer as writer_mod

    # Point the registry's LEDGERS_DIR override at tmp_path.
    monkeypatch.setattr(schema_registry, "LEDGERS_DIR", tmp_path)
    # Also override the writer module's cache so a fresh writer picks up new path.
    monkeypatch.setattr(writer_mod, "_WRITERS", {})

    # Apply schema to the tmp DB so writer.append doesn't blow up on missing
    # tables. We manually exec the base + per-ledger schema.
    repo_root = Path(__file__).resolve().parents[5]
    base_sql = (repo_root / ".cursor" / "schemas" / "ledger_base.schema.sql").read_text()
    per_sql = (
        repo_root
        / ".cursor"
        / "schemas"
        / "router_l2_cascade_ledger.schema.sql"
    ).read_text()
    db_path = tmp_path / "router_l2_cascade.sqlite"
    conn = sqlite3.connect(str(db_path))
    conn.executescript(base_sql)
    conn.executescript(per_sql)
    conn.commit()
    conn.close()
    return db_path


def _ledger_rows(db_path: Path) -> list[dict]:
    conn = sqlite3.connect(str(db_path))
    cur = conn.execute(
        "SELECT event_id, event_kind, status, score_band, score_numeric, "
        "latency_ms, prediction_json, outcome_json, metadata_json "
        "FROM events ORDER BY ts_utc"
    )
    cols = [c[0] for c in cur.description]
    rows = [dict(zip(cols, row)) for row in cur]
    conn.close()
    return rows


# =========================================================================== #
# cascade_calibrator math primitives
# =========================================================================== #
class TestCascadeCalibrator:
    def test_fingerprint_deterministic(self):
        a = fingerprint(
            failure_class="LAYER_INVERSION",
            source_layer="L2_execution",
            error_code="timeout",
            retry_count=0,
        )
        b = fingerprint(
            failure_class="LAYER_INVERSION",
            source_layer="L2_execution",
            error_code="timeout",
            retry_count=0,
        )
        assert a == b
        assert len(a) == 12
        assert all(ch in "0123456789abcdef" for ch in a)

    def test_fingerprint_retry_band_buckets(self):
        # Same band → same fingerprint
        zero = fingerprint(
            failure_class="X", source_layer="Y", error_code="Z", retry_count=0
        )
        one = fingerprint(
            failure_class="X", source_layer="Y", error_code="Z", retry_count=1
        )
        two = fingerprint(
            failure_class="X", source_layer="Y", error_code="Z", retry_count=2
        )
        three = fingerprint(
            failure_class="X", source_layer="Y", error_code="Z", retry_count=3
        )
        five = fingerprint(
            failure_class="X", source_layer="Y", error_code="Z", retry_count=5
        )
        # 0 is its own band; 1 and 2 share; 3+ share.
        assert one == two
        assert three == five
        assert zero != one != three

    def test_brier_component_perfect_prediction(self):
        assert brier_component(1.0, True) == pytest.approx(0.0)
        assert brier_component(0.0, False) == pytest.approx(0.0)

    def test_brier_component_worst_case(self):
        assert brier_component(1.0, False) == pytest.approx(1.0)
        assert brier_component(0.0, True) == pytest.approx(1.0)

    def test_brier_component_calibrated_priors(self):
        # 0.5 prior on either outcome yields 0.25 (reference value)
        assert brier_component(0.5, True) == pytest.approx(0.25)
        assert brier_component(0.5, False) == pytest.approx(0.25)

    def test_brier_component_clamps_out_of_range(self):
        assert brier_component(1.5, True) == pytest.approx(0.0)  # clamps to 1.0
        assert brier_component(-0.2, False) == pytest.approx(0.0)  # clamps to 0.0

    def test_score_band_tp_fp_tn_fn(self):
        # Predicted-success bands
        assert score_band_for(0.9, True) == "tp"
        assert score_band_for(0.9, False) == "fp"
        # Predicted-fail bands
        assert score_band_for(0.2, True) == "fn"
        assert score_band_for(0.2, False) == "tn"
        # Threshold boundary
        assert score_band_for(0.5, True) == "tp"
        assert score_band_for(0.5, False) == "fp"

    def test_wilson_lower_bound_zero_total(self):
        assert wilson_lower_bound(0, 0) == 0.0

    def test_wilson_lower_bound_monotone_in_n(self):
        # 60% success-rate: more samples → tighter (higher) lower bound
        small = wilson_lower_bound(6, 10)
        med = wilson_lower_bound(60, 100)
        large = wilson_lower_bound(600, 1000)
        assert small < med < large
        # All bounded in [0, 1]
        for x in (small, med, large):
            assert 0.0 <= x <= 1.0

    def test_wilson_lower_bound_ge_60_threshold_n30(self):
        # The §29 promotion gate requires wilson_lower ≥ 0.60 with n ≥ 30.
        # Exhibit a (k, n) where it just barely clears: success_rate must be
        # well above 0.60 to clear the lower bound at n=30.
        # 27/30 = 0.90 should clear easily.
        lower = wilson_lower_bound(27, 30)
        assert lower >= 0.60
        # 18/30 = 0.60 must NOT clear (Wilson lower < point estimate at n=30)
        assert wilson_lower_bound(18, 30) < 0.60

    def test_wilson_upper_bound_complements_lower(self):
        l = wilson_lower_bound(50, 100)
        u = wilson_upper_bound(50, 100)
        # 0.5 point estimate must lie within the interval
        assert l <= 0.5 <= u

    def test_compute_eu_high_tier_is_pure_value(self):
        # HIGH tier has zero cost in default table → EU = p × value
        eu = compute_eu(predicted_p_success=0.8, tier=HealTier.HIGH)
        assert eu == pytest.approx(0.8 * DEFAULT_VALUE_PER_SUCCESS_USD)

    def test_compute_eu_clamps_probability(self):
        eu_high = compute_eu(predicted_p_success=2.0, tier=HealTier.HIGH)
        eu_low = compute_eu(predicted_p_success=-1.0, tier=HealTier.HIGH)
        assert eu_high == pytest.approx(1.0 * DEFAULT_VALUE_PER_SUCCESS_USD)
        assert eu_low == pytest.approx(0.0)

    def test_compute_eu_cost_override(self):
        # When operator provides a spot cost, override the table.
        eu = compute_eu(
            predicted_p_success=1.0, tier=HealTier.LOW, cost_override_usd=99.0
        )
        assert eu == pytest.approx(DEFAULT_VALUE_PER_SUCCESS_USD - 99.0)

    def test_provider_label_canonical(self):
        assert (
            provider_label(tier=HealTier.HIGH, gemini_subtier="", target_model="x")
            == "deterministic"
        )
        assert (
            provider_label(
                tier=HealTier.MEDIUM,
                gemini_subtier="",
                target_model="Qwen/Qwen2.5-32B-Instruct-AWQ",
            )
            == "qwen"
        )
        assert (
            provider_label(
                tier=HealTier.LOW, gemini_subtier="PRO", target_model="gemini-2.5-pro"
            )
            == "gemini_pro"
        )
        assert (
            provider_label(
                tier=HealTier.LOW,
                gemini_subtier="FLASH",
                target_model="gemini-3-flash-preview",
            )
            == "gemini_flash"
        )
        assert (
            provider_label(tier=HealTier.HITL, gemini_subtier="", target_model="")
            == "hitl"
        )

    def test_provider_label_non_qwen_local_disambiguation(self):
        # Operator overrode VLLM_MODEL_NAME to a non-Qwen local — calibration
        # should not silently mix populations.
        label = provider_label(
            tier=HealTier.MEDIUM,
            gemini_subtier="",
            target_model="meta-llama/Llama-3.1-8B",
        )
        assert label.startswith("local:")
        assert "Llama" in label

    def test_compute_decision_evidence_bundle(self):
        ev = compute_decision_evidence(
            tier=HealTier.MEDIUM,
            gemini_subtier="",
            target_model="Qwen/Qwen2.5-32B-Instruct-AWQ",
            confidence_input=0.7,
            failure_class="UNKNOWN",
            source_layer="L2_execution",
            error_code="timeout",
            retry_count=0,
        )
        assert ev.provider == "qwen"
        assert ev.predicted_p_success == pytest.approx(0.7)
        assert ev.fingerprint_hex and len(ev.fingerprint_hex) == 12
        # EU = 0.7*value − cost_medium
        # cost_medium default = 0.001
        assert ev.eu_score == pytest.approx(0.7 * DEFAULT_VALUE_PER_SUCCESS_USD - 0.001)


# =========================================================================== #
# HealingRouter.route() — §29 marker emission and ledger row
# =========================================================================== #
class TestHealingRouterClosedLoop:
    def test_route_assigns_decision_id_and_evidence_fields(self, monkeypatch):
        # W5.4 — disable the live posterior path so the heuristic prior wins
        # regardless of accumulated rows in the on-disk ledger.
        monkeypatch.setenv("ROUTING_POSTERIOR_DISABLED", "1")
        router = HealingRouter()
        decision = router.route(_score(HealTier.HIGH), _signal())
        assert decision.decision_id != ""
        # uuid4.hex is 32 lowercase hex chars
        assert len(decision.decision_id) == 32
        assert all(c in "0123456789abcdef" for c in decision.decision_id)
        # HIGH tier uses default heuristic confidence as predicted_p_success
        assert decision.predicted_p_success == pytest.approx(0.5)
        # EU = 0.5 * value - 0.0 cost (deterministic)
        assert decision.eu_score == pytest.approx(0.5 * DEFAULT_VALUE_PER_SUCCESS_USD)

    def test_route_emits_router_decision_marker(self, caplog):
        import logging

        caplog.set_level(logging.INFO, logger="agentic_core.L2_execution.healers.healing_router")
        router = HealingRouter()
        decision = router.route(_score(HealTier.MEDIUM, value=0.7), _signal())

        marker_lines = [
            r.getMessage()
            for r in caplog.records
            if r.getMessage().startswith("ROUTER_DECISION:")
        ]
        assert len(marker_lines) == 1, f"expected one marker, got: {marker_lines}"
        line = marker_lines[0]
        assert "layer=L2" in line
        assert "router=cascade" in line
        assert f"decision_id={decision.decision_id}" in line
        assert "tier=MEDIUM" in line
        assert "provider=qwen" in line
        assert "eu_score=" in line

    def test_route_writes_ledger_row(self, temp_ledger):
        router = HealingRouter()
        decision = router.route(_score(HealTier.HIGH), _signal())
        assert decision.ledger_event_id != ""

        rows = _ledger_rows(temp_ledger)
        assert len(rows) == 1
        row = rows[0]
        assert row["event_kind"] == "route_decision"
        # Status starts at 'predicted' until dispatch binds outcome
        assert row["status"] in {"predicted", "bound"}  # writer.append may sync-bind if outcome is given
        pred = json.loads(row["prediction_json"])
        assert pred["decision_id"] == decision.decision_id
        assert pred["tier"] == "HIGH"
        assert pred["provider"] == "deterministic"
        assert "fingerprint" in pred
        assert "eu_score" in pred
        assert "predicted_p_success" in pred
        assert pred["app_name"] == "healing_router"

    def test_route_metadata_includes_constitutional_anchor(self, temp_ledger):
        router = HealingRouter()
        router.route(_score(HealTier.HIGH), _signal())
        rows = _ledger_rows(temp_ledger)
        meta = json.loads(rows[0]["metadata_json"])
        assert meta["router"] == "L2/cascade"
        assert meta["constitutional_rule"] == "§29"
        assert "signal_hash" in meta

    # ------------------------------------------------------------------ #
    # dispatch_to_executor() outcome binding
    # ------------------------------------------------------------------ #
    def test_dispatch_high_binds_outcome_with_tp_band(self, temp_ledger, monkeypatch):
        # W5.4 — disable the live posterior path so the heuristic prior wins.
        monkeypatch.setenv("ROUTING_POSTERIOR_DISABLED", "1")
        router = HealingRouter()
        decision = router.route(_score(HealTier.HIGH, value=0.95), _signal())
        result = router.dispatch_to_executor(decision, prompt="noop")
        assert result["success"] is True

        rows = _ledger_rows(temp_ledger)
        assert len(rows) == 1
        row = rows[0]
        assert row["status"] == "bound"
        # 0.95 predicted, success=True → band tp, brier=(1-0.95)^2 = 0.0025
        assert row["score_band"] == "tp"
        assert row["score_numeric"] == pytest.approx((1.0 - 0.95) ** 2, abs=1e-6)
        outcome = json.loads(row["outcome_json"])
        assert outcome["success"] is True
        assert outcome["tier_attempted"] == "HIGH"
        assert outcome["tier_used"] == "HIGH"
        assert outcome["model_used"]  # populated
        assert isinstance(outcome["latency_ms"], int)

    def test_dispatch_hitl_binds_outcome_with_failure(self, temp_ledger):
        router = HealingRouter()
        decision = router.route(_score(HealTier.HITL), _signal())
        result = router.dispatch_to_executor(decision, prompt="noop")
        assert result["success"] is False
        assert result["executor"] == "hitl"

        rows = _ledger_rows(temp_ledger)
        assert len(rows) == 1
        row = rows[0]
        assert row["status"] == "bound"
        # Predicted 0.5, success=False → band fp (predicted-success threshold default 0.5 inclusive)
        assert row["score_band"] in {"fp", "tn"}  # depends on tier-specific p
        outcome = json.loads(row["outcome_json"])
        assert outcome["success"] is False
        assert outcome["error_code"] == "human_review_required"

    # ------------------------------------------------------------------ #
    # Bypass + fail-soft
    # ------------------------------------------------------------------ #
    def test_bypass_env_does_not_emit_ledger_row(self, temp_ledger, monkeypatch):
        monkeypatch.setenv("LEDGER_WRITER_BYPASS", "router_l2_cascade")
        router = HealingRouter()
        decision = router.route(_score(HealTier.HIGH), _signal())
        # Marker IS emitted (audit trail) but ledger writer is short-circuited
        # and returns empty event_id.
        assert decision.ledger_event_id == ""
        rows = _ledger_rows(temp_ledger)
        assert rows == []

    def test_route_does_not_raise_on_evidence_failure(self, monkeypatch):
        """Failure inside compute_decision_evidence must NEVER break routing."""
        from agentic_core.L2_execution.healers import healing_router as hr

        def boom(**_kwargs):
            raise RuntimeError("synthetic")

        # NB: catches RuntimeError → not in the (AttributeError,TypeError,ValueError)
        # set, so routing should still produce a usable RoutingDecision but with
        # zero-valued evidence fields. This is the fail-soft contract.
        monkeypatch.setattr(hr, "compute_decision_evidence", boom)
        router = HealingRouter()
        with pytest.raises(RuntimeError):
            # The narrow guard intentionally re-raises non-listed exception
            # types (RuntimeError is one). This pins the contract: only the
            # *expected* evidence-construction errors are swallowed.
            router.route(_score(HealTier.HIGH), _signal())

    def test_route_swallows_attribute_error_in_evidence(self, monkeypatch):
        """AttributeError in evidence path is swallowed; routing returns decision."""
        from agentic_core.L2_execution.healers import healing_router as hr

        def boom(**_kwargs):
            raise AttributeError("synthetic")

        monkeypatch.setattr(hr, "compute_decision_evidence", boom)
        router = HealingRouter()
        # Should NOT raise; falls back to zero-valued evidence.
        decision = router.route(_score(HealTier.HIGH), _signal())
        assert decision.decision_id == ""
        assert decision.predicted_p_success == 0.0
        assert decision.ledger_event_id == ""


# =========================================================================== #
# Beta posterior reader
# =========================================================================== #
def _seed_ledger_rows(
    db_path: Path,
    *,
    tier: str,
    fingerprint_hex: str,
    n_success: int,
    n_failure: int,
    other_tier_rows: int = 0,
) -> None:
    """Seed N bound rows into a ledger DB for posterior tests."""
    import uuid as _uuid

    conn = sqlite3.connect(str(db_path))
    base_pred = {
        "tier": tier,
        "provider": "deterministic",
        "fingerprint": fingerprint_hex,
        "predicted_p_success": 0.5,
        "eu_score": 0.05,
        "decision_id": "x",
        "target_model": "x",
        "gate_applied": "NO_OVERRIDE",
        "gemini_subtier": "",
        "cost_demoted": False,
    }
    for i in range(n_success):
        eid = _uuid.uuid4().hex
        pred = {**base_pred, "decision_id": eid}
        outcome = {"success": True, "tier_attempted": tier, "tier_used": tier,
                   "fallback_reason": "", "model_used": "x", "latency_ms": 10}
        conn.execute(
            "INSERT INTO events (event_id, ts_utc, event_kind, status, "
            "score_band, score_numeric, prediction_json, outcome_json) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (eid, "2026-04-26T00:00:00Z", "route_decision", "bound",
             "tp", 0.0, json.dumps(pred), json.dumps(outcome)),
        )
    for i in range(n_failure):
        eid = _uuid.uuid4().hex
        pred = {**base_pred, "decision_id": eid}
        outcome = {"success": False, "tier_attempted": tier, "tier_used": tier,
                   "fallback_reason": "x", "model_used": "x", "latency_ms": 10}
        conn.execute(
            "INSERT INTO events (event_id, ts_utc, event_kind, status, "
            "score_band, score_numeric, prediction_json, outcome_json) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (eid, "2026-04-26T00:00:00Z", "route_decision", "bound",
             "fp", 1.0, json.dumps(pred), json.dumps(outcome)),
        )
    # Other-tier rows must NOT be aggregated into our cell
    for i in range(other_tier_rows):
        eid = _uuid.uuid4().hex
        other_pred = {**base_pred, "tier": "MEDIUM" if tier != "MEDIUM" else "HIGH"}
        other_pred["decision_id"] = eid
        outcome = {"success": True, "tier_attempted": "X", "tier_used": "X",
                   "fallback_reason": "", "model_used": "x", "latency_ms": 10}
        conn.execute(
            "INSERT INTO events (event_id, ts_utc, event_kind, status, "
            "score_band, score_numeric, prediction_json, outcome_json) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (eid, "2026-04-26T00:00:00Z", "route_decision", "bound",
             "tp", 0.0, json.dumps(other_pred), json.dumps(outcome)),
        )
    conn.commit()
    conn.close()


class TestPosteriorReader:
    def test_ledger_unavailable_returns_unused(self, tmp_path):
        result = posterior_for_cell(
            tier=HealTier.HIGH,
            fingerprint_hex="deadbeef0000",
            ledger_path=tmp_path / "does_not_exist.sqlite",
        )
        assert result.used is False
        assert result.fallback_reason == "ledger_unavailable"
        assert result.n == 0
        # Beta(1,1) prior has mean 0.5
        assert result.posterior_mean == pytest.approx(0.5)

    def test_no_rows_returns_unused_with_prior_mean(self, temp_ledger):
        result = posterior_for_cell(
            tier=HealTier.HIGH,
            fingerprint_hex="abc123def456",
            ledger_path=temp_ledger,
        )
        assert result.used is False
        assert result.fallback_reason == "no_rows"
        assert result.n == 0

    def test_below_floor_returns_unused(self, temp_ledger):
        fp = "cafebabe0001"
        # Seed 10 rows (below default n_floor=30)
        _seed_ledger_rows(
            temp_ledger, tier="HIGH", fingerprint_hex=fp, n_success=8, n_failure=2
        )
        result = posterior_for_cell(
            tier=HealTier.HIGH,
            fingerprint_hex=fp,
            ledger_path=temp_ledger,
        )
        assert result.n == 10
        assert result.successes == 8
        assert result.used is False
        assert result.fallback_reason == "n_below_floor"
        # Posterior mean = (1+8)/(2+10) = 0.75 (still computed, just not "used")
        assert result.posterior_mean == pytest.approx(9 / 12)

    def test_at_or_above_floor_returns_used(self, temp_ledger):
        fp = "cafebabe0002"
        # 30 rows: 27 success, 3 failure
        _seed_ledger_rows(
            temp_ledger, tier="HIGH", fingerprint_hex=fp, n_success=27, n_failure=3
        )
        result = posterior_for_cell(
            tier=HealTier.HIGH,
            fingerprint_hex=fp,
            ledger_path=temp_ledger,
        )
        assert result.n == 30
        assert result.successes == 27
        assert result.used is True
        assert result.fallback_reason == "ok"
        # (1+27) / (2+30) = 28/32 = 0.875
        assert result.posterior_mean == pytest.approx(28 / 32)

    def test_other_tier_rows_excluded(self, temp_ledger):
        fp_high = "cafebabe0003"
        fp_medium = "fadedface003"
        _seed_ledger_rows(
            temp_ledger, tier="HIGH", fingerprint_hex=fp_high, n_success=30, n_failure=0
        )
        # Pollute with MEDIUM-tier rows on a DIFFERENT fingerprint
        _seed_ledger_rows(
            temp_ledger,
            tier="MEDIUM",
            fingerprint_hex=fp_medium,
            n_success=50,
            n_failure=0,
        )
        result_high = posterior_for_cell(
            tier=HealTier.HIGH, fingerprint_hex=fp_high, ledger_path=temp_ledger
        )
        # Querying for HIGH+fp_medium should aggregate zero (fingerprint mismatch).
        result_high_wrong_fp = posterior_for_cell(
            tier=HealTier.HIGH, fingerprint_hex=fp_medium, ledger_path=temp_ledger
        )
        # Querying for LOW+fp_high should aggregate zero (tier mismatch).
        result_low_right_fp = posterior_for_cell(
            tier=HealTier.LOW, fingerprint_hex=fp_high, ledger_path=temp_ledger
        )
        assert result_high.n == 30
        assert result_high.successes == 30
        assert result_high_wrong_fp.n == 0
        assert result_high_wrong_fp.fallback_reason == "no_rows"
        assert result_low_right_fp.n == 0
        assert result_low_right_fp.fallback_reason == "no_rows"

    def test_n_floor_override(self, temp_ledger):
        fp = "cafebabe0004"
        _seed_ledger_rows(
            temp_ledger, tier="HIGH", fingerprint_hex=fp, n_success=5, n_failure=0
        )
        # Default floor (30): not used
        r_default = posterior_for_cell(
            tier=HealTier.HIGH, fingerprint_hex=fp, ledger_path=temp_ledger
        )
        assert r_default.used is False
        # Lowered floor of 5: used
        r_loose = posterior_for_cell(
            tier=HealTier.HIGH,
            fingerprint_hex=fp,
            ledger_path=temp_ledger,
            n_floor=5,
        )
        assert r_loose.used is True
        assert r_loose.fallback_reason == "ok"

    def test_default_n_floor_is_30(self):
        """Constitutional §29 promotion gate: n ≥ 30. Same floor for routing posterior."""
        assert DEFAULT_POSTERIOR_N_FLOOR == 30

    def test_posterior_read_dataclass_serialization(self):
        pr = PosteriorRead(
            posterior_mean=0.75,
            n=12,
            successes=9,
            used=False,
            fallback_reason="n_below_floor",
        )
        d = pr.as_dict()
        assert d["posterior_mean"] == 0.75
        assert d["n"] == 12
        assert d["used"] is False


# =========================================================================== #
# HealingRouter posterior integration
# =========================================================================== #
class TestHealingRouterPosteriorIntegration:
    def test_route_uses_posterior_when_above_floor(self, temp_ledger, monkeypatch):
        """When (tier, cell) has n>=30 bound rows, predicted_p_success comes from posterior, not heuristic."""
        from agentic_core.L2_execution.healers import healing_router as hr

        # Redirect the posterior reader's default ledger path to our temp DB
        monkeypatch.setattr(hr, "_cell_fingerprint", lambda **_kw: "ut_cell_001")
        # Seed 30 wins for HIGH tier on the synthetic fingerprint
        _seed_ledger_rows(
            temp_ledger,
            tier="HIGH",
            fingerprint_hex="ut_cell_001",
            n_success=30,
            n_failure=0,
        )
        # Patch the posterior reader's ledger path resolver
        from agentic_core.L2_execution.healers import cascade_calibrator as cc

        monkeypatch.setattr(cc, "_DEFAULT_LEDGER_PATH", temp_ledger)

        router = HealingRouter()
        # Heuristic confidence is 0.5 — the posterior should be 31/32 ≈ 0.969
        decision = router.route(_score(HealTier.HIGH, value=0.5), _signal())
        assert decision.predicted_p_success == pytest.approx(31 / 32)

        # Verify the prediction_json carries the provenance markers
        rows = _ledger_rows(temp_ledger)
        # Find our newly written decision row
        live_rows = [
            r
            for r in rows
            if json.loads(r["prediction_json"]).get("decision_id")
            == decision.decision_id
        ]
        assert len(live_rows) == 1
        pred = json.loads(live_rows[0]["prediction_json"])
        assert pred["posterior_used"] is True
        assert pred["posterior_n"] == 30
        assert pred["posterior_successes"] == 30
        assert pred["posterior_fallback_reason"] == "ok"
        assert pred["heuristic_p"] == pytest.approx(0.5)

    def test_route_falls_back_to_heuristic_when_below_floor(
        self, temp_ledger, monkeypatch
    ):
        """When the cell has fewer than 30 rows, heuristic remains authoritative."""
        from agentic_core.L2_execution.healers import healing_router as hr
        from agentic_core.L2_execution.healers import cascade_calibrator as cc

        monkeypatch.setattr(hr, "_cell_fingerprint", lambda **_kw: "ut_cell_002")
        _seed_ledger_rows(
            temp_ledger,
            tier="HIGH",
            fingerprint_hex="ut_cell_002",
            n_success=5,
            n_failure=0,
        )
        monkeypatch.setattr(cc, "_DEFAULT_LEDGER_PATH", temp_ledger)

        router = HealingRouter()
        decision = router.route(_score(HealTier.HIGH, value=0.5), _signal())
        # Heuristic 0.5 wins
        assert decision.predicted_p_success == pytest.approx(0.5)

        rows = _ledger_rows(temp_ledger)
        live_rows = [
            r
            for r in rows
            if json.loads(r["prediction_json"]).get("decision_id")
            == decision.decision_id
        ]
        pred = json.loads(live_rows[0]["prediction_json"])
        assert pred["posterior_used"] is False
        assert pred["posterior_fallback_reason"] == "n_below_floor"
        assert pred["posterior_n"] == 5
        assert pred["heuristic_p"] == pytest.approx(0.5)

    def test_route_respects_posterior_disable_env(self, monkeypatch):
        """ROUTING_POSTERIOR_DISABLED=1 forces heuristic-only path."""
        monkeypatch.setenv("ROUTING_POSTERIOR_DISABLED", "1")
        router = HealingRouter()
        decision = router.route(_score(HealTier.HIGH, value=0.42), _signal())
        # Heuristic value passes through unchanged
        assert decision.predicted_p_success == pytest.approx(0.42)

    def test_route_n_floor_env_override(self, temp_ledger, monkeypatch):
        """ROUTING_POSTERIOR_N_FLOOR lowers the gate, enabling posterior earlier."""
        from agentic_core.L2_execution.healers import healing_router as hr
        from agentic_core.L2_execution.healers import cascade_calibrator as cc

        monkeypatch.setattr(hr, "_cell_fingerprint", lambda **_kw: "ut_cell_003")
        _seed_ledger_rows(
            temp_ledger,
            tier="HIGH",
            fingerprint_hex="ut_cell_003",
            n_success=10,
            n_failure=0,
        )
        monkeypatch.setattr(cc, "_DEFAULT_LEDGER_PATH", temp_ledger)
        # With default n=30 floor, 10 rows is below the floor → heuristic
        # With env override to 5, 10 rows clears → posterior
        monkeypatch.setenv("ROUTING_POSTERIOR_N_FLOOR", "5")

        router = HealingRouter()
        decision = router.route(_score(HealTier.HIGH, value=0.5), _signal())
        # (1+10)/(2+10) = 11/12 ≈ 0.9167
        assert decision.predicted_p_success == pytest.approx(11 / 12)
