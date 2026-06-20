#!/usr/bin/env python3
"""
Contract Gates — Main CI Entrypoint

Runs all contract validation gates in deterministic order.
"""

import os
import subprocess
import sys
from pathlib import Path


def _bootstrap_repo_root() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    return repo_root


ROOT = _bootstrap_repo_root()
DEFAULT_SUBPROCESS_TIMEOUT = 300


def run_cmd(args, cwd=None, timeout: int = DEFAULT_SUBPROCESS_TIMEOUT):
    """Run a command and return result."""
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=timeout,
            check=False,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        return 124, stdout, f"Command timed out after {timeout}s\n{stderr}".strip()
    except (OSError, ValueError) as exc:
        return 2, "", f"{type(exc).__name__}: {exc}"


def _script(rel_path: str) -> Path:
    return ROOT / rel_path


# PFC1 (plan-format-simplification-rca-d4f8e2 W4): forward-only canonical scope.
# Does NOT scan all of .codex/plans — explicit paths only (see W4 CI gate receipt).
_PFC1_CANONICAL_PLAN_PATHS = (
    ".codex/plans/plan-format-simplification-rca-d4f8e2.md",
    ".codex/templates/execution-plan-template.md",
    ".codex/plans/acceptance-gates-master-tracking-b5c3e1.md",
    ".codex/plans/adg-antipattern-hardening-e5a569.md",
    ".codex/plans/agentic-core-signoff-hardening-b8e2c4.md",
)


def _pfc1_gate_cmd() -> list[str]:
    """Argv for check_plan_format_compliance.py with required --paths."""
    mode = (
        "--strict"
        if os.environ.get("PLAN_FORMAT_COMPLIANCE_FAIL_CLOSED") == "1"
        else "--advisory"
    )
    return [
        sys.executable,
        str(_script("ops_scripts/ci/check_plan_format_compliance.py")),
        mode,
        "--paths",
        *_PFC1_CANONICAL_PLAN_PATHS,
        "--artifact",
        "artifacts/ci/plan_format_compliance.json",
    ]


# MCP HEALTH CHECKS
def validate_mcp_health():
    """Validate MCP server health."""
    print("\n[MCP HEALTH CHECK]")

    # Gate: AGENTS.md Quick Reference must document every server in root .mcp.json
    returncode, stdout, stderr = run_cmd(
        [sys.executable, str(_script("ops_scripts/ci/check_agents_mcp_coverage.py"))],
        cwd=ROOT,
    )
    if returncode != 0:
        print("❌ AGENTS.md MCP coverage check failed")
        print(stdout or stderr)
        return False
    print("✅ AGENTS.md MCP coverage validated")

    # cursor-decommission W7: mcp_sync_integrity + mcp_editor_parity validated the
    # deprecated editor mirrors and parity checks. Both mirrors are
    # retired (root .mcp.json is the sole SSOT), so these gates are obsolete and removed.

    # cursor-decommission W7: check_mcp_config_sovereignty enforced a legacy editor-era
    # filesystem-MCP-args lock against root .mcp.json.
    # and intentionally omits the filesystem MCP (native file tools), so the gate's
    # MISSING_FILESYSTEM premise no longer holds. Retired.

    # cursor-decommission W7: check_cursor_config_schema removed (validated deleted
    # deleted legacy editor-era hooks/MCP config; Claude Code uses .codex/hooks.json + root .mcp.json).

    # Gate: every .codex/skills/<name>/SKILL.md must conform to Anthropic's
    # Agent Skills authoring spec (frontmatter, name/description rules, 500-line
    # budget, third person, when-trigger, forward-slash paths).
    returncode, stdout, stderr = run_cmd(
        [sys.executable, str(_script("ops_scripts/ci/check_skill_frontmatter.py"))],
        cwd=ROOT,
    )
    if returncode != 0:
        print("❌ Skill frontmatter check failed (Anthropic spec)")
        print(stdout or stderr)
        return False
    print("✅ Skill frontmatter validated (Anthropic spec)")

    returncode, stdout, stderr = run_cmd(
        [sys.executable, str(_script("ops_scripts/ci/check_skill_description_quality.py"))],
        cwd=ROOT,
    )
    if returncode != 0:
        print("❌ Skill description quality check failed (W4 progressive disclosure)")
        print(stdout or stderr)
        return False
    print("✅ Skill description quality validated (W4)")

    return True


def main():
    """Run all contract gates in deterministic order."""

    # Piped invocations (e.g. ``python ... | Tee-Object`` on Windows) default to
    # block-buffered stdout/stderr, so multi-minute gate subprocesses appear hung.
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(line_buffering=True)
            sys.stderr.reconfigure(line_buffering=True)
        except OSError:
            pass

    # Validate MCP health (critical for Redis/ADG)
    if not validate_mcp_health():
        sys.exit(1)

    # [contract-gates-deband 2026-06-15] Removed legacy editor-era band-aids from the runner:
    # 0b skill-health loop, 1.1 infra_wiring_scan (ADG v_p0_* views are the canonical
    # structural check), 1.2 executor_theater. (memory: contract-gates-debanding-triage)
    # Gate: ADG graph-layer evidence in refactoring plans (Constitutional §22)
    print("🔍 Running graph-layer evidence gate (refactoring plans)...")
    returncode, stdout, stderr = run_cmd(
        [sys.executable, str(_script("ops_scripts/ci/check_graph_layer_evidence.py"))],
        cwd=ROOT,
    )
    if returncode != 0:
        print(stdout)
        print(stderr)
        sys.exit(1)
    print("✅ Graph-layer evidence gate passed")

    # [contract-gates-deband 2026-06-15] Removed legacy editor-era ADG-pipeline band-aids from the
    # runner: 1.4 snapshot_has_mvs, 1.5 pipeline_skips, 1.6 severity_band_ssot, 1.7 exclusion_sync.
    # (memory: contract-gates-debanding-triage)
    # Gate: Repository structure policy (config/structure_blueprint/structure_policy.yaml)
    print("🔍 Running structure policy gate...")
    returncode, stdout, stderr = run_cmd(
        [sys.executable, str(_script("ops_scripts/ci/check_structure_policy.py"))],
        cwd=ROOT,
    )
    if returncode != 0:
        print(stdout)
        print(stderr)
        sys.exit(1)
    print("✅ Structure policy gate passed")

    # [contract-gates-deband 2026-06-15] Removed from the runner: 1.9 reference_orphans,
    # 1.10 judge_calibration (legacy editor-era). (memory: contract-gates-debanding-triage)
    # [W1 claude-native-supersession-9d3f7a] Author-Gate harness-HITL CI gates RETIRED.
    # The 9 gates here (ledger schema/SSOT/outcome-coverage/integrity, ask_user_question
    # packet freshness, AGP1 pipeline freshness, v2 completeness, anomaly detector,
    # bypass rollup) enforced a bespoke packet -> render -> marker -> queue -> SQLite-ledger
    # pipeline that emulated a structured-choice tool. Native AskUserQuestion supersedes
    # it. Gate scripts under ops_scripts/ci/decision_ledger/ are dormant (uncalled); the
    # governance hook scripts + 2 skills are dormant in place. Invariant (stop & ask before
    # ambiguous edits) preserved in AGENTS.md + constitutional s6.
    # ADR: docs/architecture/adr/ADR-093-author-gate-native-ask-user-question.md

    # Gate: P0 two-pass (preflight + full ADG enforcement)
    # Bypass: P0_TWO_PASS_BYPASS=1 — skips this gate (log warning only).
    # Use only when pre-existing P0 violations are tracked and a targeted
    # single-gate run (e.g. --gate CHECK-RG-CHROMA) is being executed.
    print("\n[P0 TWO-PASS GATE]")
    if os.environ.get("P0_TWO_PASS_BYPASS") == "1":
        print("⚠️  P0 two-pass gate BYPASSED (P0_TWO_PASS_BYPASS=1)")
    else:
        try:
            from ops_scripts.ci.adg_gates.p0_runner import run_p0_two_pass

            p0_rc = run_p0_two_pass(emit_artifacts=True)
            if p0_rc == 1:
                print("❌ P0 two-pass gate BLOCKED — commit rejected")
                sys.exit(1)
            elif p0_rc == 2:
                print("⚠️  P0 two-pass gate ERROR — runner-level failure (see stderr)")
                sys.exit(1)
            else:
                print("✅ P0 two-pass gate passed")
        except ImportError as exc:
            print(f"❌ P0 runner import failed: {exc}")
            sys.exit(1)

    # Gate: P3 trend tracking (watch-only, never blocks)
    print("\n[P3 TREND RUNNER]")
    try:
        from ops_scripts.ci.adg_gates.p3_trend_runner import run_p3_trend

        p3_rc = run_p3_trend(emit_artifacts=True)
        if p3_rc == 2:
            print("⚠️  P3 trend runner ERROR — see stderr (non-blocking)")
        else:
            print("✅ P3 trend runner completed")
    except ImportError as exc:
        print(f"⚠️  P3 runner import failed — {exc} (non-blocking)")

    # Parse args for --gate flag
    import argparse
    parser = argparse.ArgumentParser(description="Contract Gates — Main CI Entrypoint")
    parser.add_argument("--gate", type=str, default=None, help="Run single gate by ID (e.g., AG-PURITY)")
    args, _ = parser.parse_known_args()

    # ==================================================================
    # Assurance P1 gate plane (plan assurance-p1-gates-ab4758)
    # Runtime trace, replay digest, and requirements crosswalk.
    # ==================================================================
    print("\n[ASSURANCE-P1 GATE PLANE]", flush=True)
    assurance_gates = [
        # AG-PURITY — Agentic Core Purity gate (plan adg-ci-agentic-core-purity-a7c3e9).
        # Validates agentic_core remains app-agnostic; apps_* enter via U0 runtime_customization_package.
        # Advisory by default; fail-closed via AG_PURITY_FAIL_CLOSED=1. Bypass: AG_PURITY_BYPASS=1.
        # W4: CI registration, synthetic tests, baseline artifact, promotion criteria doc.
        (
            "AG-PURITY agentic_core purity (advisory)",
            "ops_scripts/ci/adg_gates/gate_agentic_core_purity.py",
            "AG-PURITY",
        ),
        # NOTE: check_legacy_tree_config_schema.py is canonical in wiring_gates (§26 label).
        # Removed from assurance_gates 2026-05-05 to eliminate true CI-plane duplication.
        # See: ops_scripts/ci/run_contract_gates.py wiring_gates entry "§26 legacy editor config schema purity".
        ("W1 runtime trace contract", "ops_scripts/ci/check_runtime_trace_contract.py"),
        ("W3 replay determinism proof", "ops_scripts/ci/check_replay_proof.py"),
        ("W4 requirements ↔ ADG crosswalk", "ops_scripts/ci/check_requirements_adg_crosswalk.py"),
        ("W4a 10C ledger ↔ matrix consistency", "ops_scripts/ci/check_10c_ledger_consistency.py"),
        ("W4b requirements universe inventory", "ops_scripts/ci/check_requirements_universe_inventory.py"),
        ("W4c AGEN registry schema", "ops_scripts/ci/check_agen_registry_schema.py"),
        ("W4d 10C proof-ledger validation", "tools/requirements/validate_10c_proof_ledger.py"),
        ("W4d-3 10C cross-file consistency", "ops_scripts/ci/check_10c_cross_file_consistency.py"),
        ("W4d-4 10C pilot proof-evidence", "ops_scripts/ci/check_10c_pilot_proof_evidence.py"),
        # [notion-wave-enforcement-removal] PLAN-SUPERSEDE (Notion predecessor-retire backstop) REMOVED.
        # Runtime-evidence stack (plan: runtime-evidence-foundation-54ad39).
        # All three close the static-only-proof gap that the OTEL emission RCA
        # surfaced. Pact-style contract verifier is the master gate; the orphan
        # report is informational; the lifecycle gate enforces OTel-style
        # experimental→stable governance for closure claims.
        ("RE1 REQ coverage contracts (Pact-style)", "ops_scripts/ci/check_req_coverage_contracts.py"),
        ("RE2 orphan observability nodes", "ops_scripts/ci/check_orphan_observability_nodes.py"),
        ("RE3 closure lifecycle (experimental→stable)", "ops_scripts/ci/check_closure_lifecycle.py"),
        # ADR-081 plane-2 manifest (quick strict on latest snapshot after Redis ingest).
        (
            "3B0 ADG three-graph manifest quick (strict)",
            "ops_scripts/ci/run_adg_three_graph_quick_gate.py",
        ),
        # Three-bucket OTEL view gates — thin wrappers; same scripts as
        # ops_scripts/ci/adg_gate_manifest.yaml (3B* kept for contract visibility).
        # Strict mode envvars: RUNTIME_PROOF_VIEW_STRICT=1, GENAI_SEMCONV_STRICT=1
        ("3B1 runtime proof view well-formed", "ops_scripts/ci/check_runtime_proof_view_well_formed.py"),
        ("3B2 OTel GenAI semconv coverage", "ops_scripts/ci/check_otel_genai_semconv_coverage.py"),
        # W5 of three-bucket-gap-remediation-069806: per-class threshold gate
        # over the gap report. Bypass: THREE_BUCKET_GAP_BYPASS=1.
        ("3B3 three-bucket gap thresholds", "ops_scripts/ci/check_three_bucket_gap_thresholds.py"),
        # ADR-078 / W3 P3.2 + W5 P5.1 of adg-three-bucket-unified-c4f8e2:
        # every apps_*/ top-level package MUST import the agentic_core spine
        # (L0/L1/L2). Default: STRICT (W5 P5.1 flip, 2026-04-30). Rollback:
        # APPS_SPINE_DELEGATION_GATE_MODE=advisory. Bypass:
        # APPS_SPINE_DELEGATION_GATE_BYPASS=1. Baseline allowlisted via
        # config/apps_spine_delegation_allowlist.yaml (expires 2026-05-31).
        ("3B7 apps_* spine delegation (ADR-078)", "ops_scripts/ci/check_apps_spine_delegation.py"),
        # W6 of three-bucket-gap-remediation-069806: in-toto/SLSA signing of
        # the snapshot. Verifies Ed25519 signature + file SHA-256 +
        # three-bucket content digest. Bypass: ADG_SIGNATURE_BYPASS=1.
        ("3B4 ADG snapshot signed (in-toto/SLSA)", "ops_scripts/ci/check_adg_snapshot_signed.py"),
        # W7 of three-bucket-gap-remediation-069806: schema-graduation
        # readiness — advisory by default, reports remaining NULL counts on
        # closed-enum columns. Flip via SCHEMA_GRADUATION_READINESS_STRICT=1
        # once a 4-week green window of 3B1..3B4 closes cleanly.
        ("3B5 schema graduation readiness (advisory)", "ops_scripts/ci/check_schema_graduation_readiness.py"),
        # Aggregate three-bucket certification gate (plan three-bucket-otel-view-5db409 W7).
        # Advisory by default; flip via ADG_CERTIFIED_STRICT=1 once the consumer-mode
        # gate is permanently strict-mode and runtime evidence is consistently flowing.
        (
            "3B6 ADG_CERTIFIED aggregate gate (rollup strict)",
            "ops_scripts/ci/check_adg_certified.py --rollup --strict --write-verdict",
        ),
        # W6.P1 (plan apps-eval-harness-deferred-e4a1b7): apps_* eval-harness
        # parity gate. Advisory by default — flip fail-closed via
        # APP_DOMAIN_HARNESS_PARITY_FAIL_CLOSED=1 once calibrated.
        (
            "AEH1 apps_* eval-harness parity (advisory)",
            "ops_scripts/ci/check_app_domain_harness_parity.py",
        ),
        # TSP1 — apps_* test surface parity gate.
        # Verifies every apps_<x> has tests/unit/<app>/ + tests/<app>/ with
        # __init__.py, and flags forbidden tests/integration/apps_<x>/ dirs.
        # Advisory by default; fail-closed via APPS_TEST_SURFACE_FAIL_CLOSED=1.
        # Plan: apps-test-surface-consolidation-11acd9-v2 W6.
        (
            "TSP1 apps_* test surface parity (advisory)",
            "ops_scripts/ci/check_apps_test_surface_parity.py",
        ),
        # EPE1 — Embedding provenance enforcement (ADR-055 W3.1).
        # Verifies EmbeddingProvenanceMismatchError is importable and
        # SovereignChromaClient references the hard-fail block.
        # Plan: bge-m3-gap-closure-c8f3a2 W3.1.
        (
            "EPE1 embedding provenance enforcement (advisory)",
            "ops_scripts/ci/check_embedding_provenance_enforcement.py",
        ),
        # RJC1 — RationaleQualityJudge Spearman calibration gate.
        # Verifies global Spearman >= 0.80 and per-dim >= 0.70 against the
        # holdout dataset.  FAIL-CLOSED (DS-R5 flip 2026-05-06): heuristic v2
        # judge confirmed at global Spearman=0.812 >= 0.80.  Override via
        # RATIONALE_JUDGE_CALIB_FAIL_CLOSED=0 to revert to advisory.
        # Plan: apps-underwriting-ai-rationale-judge-deferred-d4e7a2 W4.P4.1.
        (
            "RJC1 rationale judge calibration (fail-closed)",
            "ops_scripts/ci/check_rationale_judge_calibration.py",
        ),
        # RJC2 — RationaleQualityJudge holdout/dev split integrity.
        # Detects holdout decision_id values that also appear in dev fixtures.
        # FAIL-CLOSED (DS-R3 flip 2026-05-06): no dev-fixture overlap confirmed.
        # Override via EVAL_HOLDOUT_SPLIT_FAIL_CLOSED=0 to revert to advisory.
        # Plan: apps-underwriting-ai-rationale-judge-deferred-d4e7a2 W3.P3.1.
        (
            "RJC2 rationale judge holdout split (fail-closed)",
            "ops_scripts/ci/check_eval_holdout_split.py",
        ),
        # AEH2 — AgentSpec completeness across all apps_* domains.
        # Advisory by default; fail-closed via
        # AGENT_SPEC_COMPLETENESS_FAIL_CLOSED=1.
        # Plan: apps-core-contract-rectification-a8f3c2 Phase 2.3.
        (
            "AEH2 AgentSpec completeness (advisory)",
            "ops_scripts/ci/check_agent_spec_completeness.py",
        ),
        # AG8 — apps_lic golden path runtime proof (plan: apps-lic-ag8-golden-template-adoption-f3c2e1).
        # Verifies full spine wiring: U0->L1->L0->L3->C0->PA->L2->Exit->X1/X3.
        # Advisory by default; fail-closed via APPS_LIC_GOLDEN_PATH_FAIL_CLOSED=1.
        (
            "AG8 apps_lic golden path runtime (advisory)",
            "ops_scripts/ci/check_apps_lic_golden_path_runtime.py",
        ),
        # AEH3 — Grounded RAG dim activation gate.
        # Checks that dims removed from intentional_failopen_dims have
        # weight>0 and fail_closed_if_unknown=true (i.e. C0 fully wired).
        # Advisory by default; fail-closed via
        # GROUNDED_RAG_ACTIVE_FAIL_CLOSED=1.
        # Plan: apps-core-contract-rectification-a8f3c2 Phase 5.3.
        (
            "AEH3 grounded RAG dim activation (advisory)",
            "ops_scripts/ci/check_grounded_rag_active.py",
        ),
        # [notion-wave-enforcement-removal] NP1–NP8 Notion Plans/Backlog status gates REMOVED
        # (AI-summary, status-drift, backlog-linkage, wave-freshness, dedup x2, telemetry-size,
        # status-anomalies). The windsurf/cursor-era Notion plan-status enforcement is retired.
        # RULE-XREF -- Rule cross-reference validation. Ensures all rule-to-rule
        # links are intact and targets exist. Advisory by default;
        # fail-closed via RULE_CROSS_REF_FAIL_CLOSED=1.
        # Bypass: RULE_CROSS_REF_BYPASS=1.
        (
            "RULE-XREF Rule cross-references (advisory)",
            "ops_scripts/ci/check_rule_cross_references.py",
        ),
        # [notion-wave-enforcement-removal] NP9–NP18 Notion Plans/Backlog status gates REMOVED
        # (new-plan-status, waiting-for x2, PLAN_COMPLETE-freshness, status-initial, schema-preflight,
        # plan-file-drift, decision-parity, MECE-v2, status-canonical). Retired plan-status enforcement.
        # [notion-wave-enforcement-removal] NP-IDSSOT (check_notion_id_ssot_parity) + AUDIT-3
        # (check_external_service_literal_ssot) Notion-ID enforcement gates REMOVED. _notion_constants
        # + config/notion_databases.yaml are KEPT (load-bearing for sync_mcp_config / check_agents_md_sync
        # / recover_deferred_scope_pendings / agentic_core notion_approval_adapter) but no longer policed.
        # [notion-wave-enforcement-removal] NP-DONE (all-waves-done disk-vs-Notion) and
        # WAVE-MARKER (WAVE_COMPLETE/PLAN_COMPLETE marker emission) gates REMOVED — retired
        # Notion plan-status + wave-marker enforcement.
        # RG-W3 — Retired warm_r1b_cache shadow runner must stay absent.
        # Canonical cache proof is via python -m apps_rg + contract tests only.
        # Advisory by default; flip fail-closed via R1B_WARMUP_SMOKE_FAIL_CLOSED=1.
        # Plan: apps-rg-cache-followon-deferred-c7d3a1 W1.
        (
            "RG-W3 R1B warmup smoke (advisory)",
            "ops_scripts/ci/check_r1b_warmup_smoke.py",
        ),
        # [notion-wave-enforcement-removal] PR1 Plan–Notion registration freshness (§36) REMOVED —
        # retired plan-registration enforcement.
        # L6-OBS — L6 observer-law (system_learning/ MUST NOT import writers
        # from L0..L5 runtime layers). Advisory; flip fail-closed via
        # L6_OBSERVER_LAW_FAIL_CLOSED=1 once baseline is clean.
        # Plan: l6-doctrinal-alignment-noninvasive-b9d3f5 W4.
        (
            "L6-OBS L6 observer-law (advisory)",
            "ops_scripts/ci/check_l6_observer_law.py",
        ),
        # L6-TAG — L6 ADG layer-tag consistency (every system_learning/*.py
        # MUST resolve to layer=L6 in latest ADG snapshot). Advisory;
        # SKIPs when snapshot missing or stale. Plan: same W5.
        (
            "L6-TAG L6 layer-tag consistency (advisory)",
            "ops_scripts/ci/check_l6_layer_tag_consistency.py",
        ),
        # L6-W1 — no direct semantic cache import outside UWG/cache surfaces.
        # Advisory; fail-closed: DIRECT_CACHE_WRITE_FAIL_CLOSED=1.
        # Bypass: DIRECT_CACHE_WRITE_BYPASS=1. Plan: p4.2 apps-rg L6 hardening.
        (
            "L6-W1 no direct semantic cache write imports (advisory)",
            "ops_scripts/ci/check_no_direct_semantic_cache_write.py",
        ),
        (
            "L6-W2 no duplicate apps_rg L6 engine module (advisory)",
            "ops_scripts/ci/check_no_apps_rg_runtime_l6_engine.py",
        ),
        (
            "L6-W2a no fake L6 span labels (advisory)",
            "ops_scripts/ci/check_no_fake_l6_span_label.py",
        ),
        (
            "L6-W2b package-driven L6 binding only (advisory)",
            "ops_scripts/ci/check_package_driven_l6_only.py",
        ),
        (
            "L6-W2c apps_rg L6 profile-only imports (advisory)",
            "ops_scripts/ci/check_apps_rg_l6_profile_only.py",
        ),
        (
            "L6-W4a G29 learning firewall (advisory)",
            "ops_scripts/ci/check_g29_firewall.py",
        ),
        (
            "L6-W4b no L6 X3Disposition coupling (advisory)",
            "ops_scripts/ci/check_no_l6_current_run_mutation.py",
        ),
        (
            "L6-W4c no L6 X3 emit surface (advisory)",
            "ops_scripts/ci/check_no_l6_x3_emit.py",
        ),
        (
            "L6-W4d no L6 direct UWG/L4 writer imports (advisory)",
            "ops_scripts/ci/check_no_l6_direct_l4_write.py",
        ),
        # APPS-DOM runtime harness fixture freshness. Fails when
        # artifacts/apps_otel_traces or sibling harness fixture dirs contain
        # a fixture older than APPS_DOM_FIXTURE_FRESHNESS_HOURS (default 168h).
        # Skips when fixture dirs absent (first-run tolerant).
        # Advisory by default (exit 0 with stderr report); fail-closed via
        # APPS_DOM_FIXTURE_FRESHNESS_FAIL_CLOSED=1.
        # Bypass: APPS_DOM_FIXTURE_FRESHNESS_BYPASS=1. Plan:
        # .codex/plans/apps-dom-real-evidence-enhancement-c7f4d8.md W4.
        (
            "AD1 APPS-DOM harness fixture freshness (advisory)",
            "ops_scripts/ci/check_apps_dom_fixture_freshness.py",
        ),
        # AR1 — apps_research FEC v1.1 wiring gate. Checks that
        # produce_fec() emits schema_version="1.1" + all 10 v1.1 field keys,
        # GovernedE2ERunRecord has research_depth_profile + fec_run_context,
        # and company_brief_engine re-exports catalog shim symbols.
        # Advisory by default; fail-closed via
        # APPS_RESEARCH_FEC_V11_FAIL_CLOSED=1.
        # Plan: apps-research-spine-deferred-followup-9c3e1a P4.2.
        (
            "AR1 apps_research FEC v1.1 wiring (advisory)",
            "ops_scripts/ci/check_apps_research_fec_v11.py",
        ),
        # -- Promoted from manual stage 2026-05-05 (hardening dedup pass) -------
        # These gates were `stages: [manual]` in .pre-commit-config.yaml.
        # They are stable (0 violations at promotion date), safety-critical,
        # and cheap enough to run in CI. Pre-commit manual stage is retained
        # for on-demand local runs; CI is now the authoritative sweep.
        #
        # OT1 — OTEL coverage (advisory by default; drift logged).
        # Every engines/integrations/outputs module should emit ≥1 OTEL signal.
        # Fail-closed: APPS_OTEL_COVERAGE_FAIL_CLOSED=1.
        (
            "OT1 apps_* OTEL coverage (advisory; fail-closed via env)",
            "ops_scripts/ci/check_apps_otel_coverage.py",
        ),
        # OT2 — Required spans manifest (advisory by default; drift logged).
        # Fail-closed: REQUIRED_SPANS_FAIL_CLOSED=1.
        (
            "OT2 required spans manifest (advisory; fail-closed via env)",
            "ops_scripts/ci/check_required_spans_coverage.py",
        ),
        # SP1 — apps_shared purity: no domain-app imports from apps_shared/.
        # ADG SQLite query; 0 violations; lock boundary at zero.
        # Fail-closed: APPS_SHARED_PURITY_FAIL_CLOSED=1.
        (
            "SP1 apps_shared purity (no domain-app imports)",
            "ops_scripts/ci/check_apps_shared_purity.py",
        ),
        # SP2 — PII in telemetry sinks. Blocks PII-shaped variable names from
        # leaking through OTEL/logging emit sites. 0 violations (3 explicit
        # waivers for env-var-name-only logs). Fail-closed: PII_TELEMETRY_FAIL_CLOSED=1.
        (
            "SP2 PII in telemetry sinks",
            "ops_scripts/ci/check_pii_in_telemetry.py",
        ),
        # -- Codex violation log freshness backstops (2026-05-05) ---------------
        # legacy editor post_agent_* hooks write persistent violation logs. These
        # gates ensure CI surfaces stale unresolved violations — same pattern
        # as check_ask_user_question_packet_freshness.py. Advisory by default.
        #
        # ADG-first violations: post_agent_adg_audit.py writes
        # artifacts/governance/adg_first_violations.jsonl (see gate script).
        # Advisory by default; fail-closed: ADG_FIRST_VIOLATIONS_FRESHNESS_FAIL_CLOSED=1.
        # Bypass: ADG_FIRST_VIOLATIONS_FRESHNESS_BYPASS=1.
        (
            "CF1 ADG-first violations freshness (advisory; fail-closed via env)",
            "ops_scripts/ci/check_adg_first_violations_freshness.py",
        ),
        # RG-W8 — apps_rg runtime gate hardening wave completion (advisory by default).
        # Catalog vs tests can drift; fail-closed: APPS_RG_W8_GATE_FAIL_CLOSED=1.
        # Validates all W0-W7 gates implemented, exported, tested per plan.
        # 206 tests across 8 waves; zero tolerance for missing gates.
        # Plan: apps-rg-runtime-gate-catalog-c4d7e1.md W8.
        (
            "RG-W8 apps_rg runtime gate hardening (advisory; fail-closed via env)",
            "ops_scripts/ci/check_apps_rg_runtime_gate_hardening.py",
        ),
        # PA-RG1 — apps_rg + agentic_core/prompt_governance PA boundary anti-bypass scanner.
        # Baseline (ADR-083 D3, W4 2026-05-09): ERROR=0 after allowlisting HardenedanthropicexecutorStrategy
        # (both copies) and CONDITIONAL_V1_BASELINE for hops/_llm_client.py.
        # Flip fail-closed: APPS_RG_PA_BOUNDARY_FAIL_CLOSED=1. Bypass: APPS_RG_PA_BOUNDARY_BYPASS=1.
        # Plans: apps-rg-spine-hardening-7e3b9c W6 + apps-rg-spine-hardening-deferred-wave-2f8b1d W4.
        (
            "PA-RG1 apps_rg PA boundary anti-bypass (advisory — baseline clean 2026-05-09)",
            "ops_scripts/ci/check_apps_rg_pa_boundary.py",
        ),
        (
            "PA-SSOT prompt assembly E0 examples hydration (advisory)",
            "ops_scripts/ci/check_prompt_assembly_ssot.py",
        ),
        # L5CR1 — emit-contract l5_certification_ref field presence scan.
        # AST-based; checks all 18 (file, class) pairs from plan §7.
        # Advisory by default; fail-closed via L5_CERT_REF_GATE_FAIL_CLOSED=1.
        # Bypass: L5_CERT_REF_GATE_BYPASS=1.
        # Plan: l5-cert-ref-emit-chain-threading-c4e7f1 W4 / P4.2.
        (
            "L5CR1 emit-contract l5_certification_ref field scan (advisory)",
            "ops_scripts/ci/check_l5_cert_ref_on_emit_contracts.py",
        ),
        # APPS-RG-L5-CREFS — apps_rg binding-layer APPS_RG_*_CERT_REF scan (GAP-009).
        # Advisory by default; fail-closed APPS_RG_L5_CERT_REFS_FAIL_CLOSED=1.
        # Bypass: APPS_RG_L5_CERT_REFS_BYPASS=1.
        (
            "APPS-RG-L5-CREFS apps_rg binding l5_certification_ref constants (advisory)",
            "ops_scripts/ci/check_apps_rg_l5_cert_refs.py",
        ),
        # APPS-IMPORT, APPS-DRYRUN, PLAN-DOD — Definition-of-Done discipline gates.
        # Plan: apps-rg-runtime-wiring-completion-d4e8a1 W6.
        # Closes the c8b3e1 failure mode (plan marked Completed while
        # `python -m apps_rg` raised ImportError).
        # APPS-IMPORT: advisory; fail-closed APPS_RG_IMPORT_GATE_FAIL_CLOSED=1; bypass APPS_RG_IMPORT_GATE_BYPASS=1.
        # APPS-DRYRUN: advisory; fail-closed APPS_RG_DRYRUN_GATE_FAIL_CLOSED=1; bypass APPS_RG_DRYRUN_GATE_BYPASS=1.
        # PLAN-DOD: advisory; fail-closed PLAN_DOD_GATE_FAIL_CLOSED=1; bypass PLAN_DOD_GATE_BYPASS=1.
        (
            "APPS-IMPORT apps_rg --help importable (advisory)",
            "ops_scripts/ci/check_apps_rg_import.py",
        ),
        # APPS-RG-SINGLE-SPINE — W1 ratchet: no second pipeline in product paths (d8f4a2).
        # Fail-closed by default. Bypass: APPS_RG_SINGLE_SPINE_GATE_BYPASS=1.
        # Advisory: APPS_RG_SINGLE_SPINE_GATE_ADVISORY=1.
        (
            "APPS-RG-SINGLE-SPINE apps_rg one spine product-path ratchet (fail-closed)",
            "ops_scripts/ci/check_apps_rg_single_spine.py",
        ),
        # APPS-RG-SPINE-CONVERGENCE — W8 ratchet: governed W5–W7 seams + span checklist + gap audit.
        # Fail-closed by default. Bypass: APPS_RG_SPINE_CONVERGENCE_BYPASS=1.
        (
            "APPS-RG-SPINE-CONVERGENCE apps_rg spine convergence W8 (fail-closed)",
            "ops_scripts/ci/check_apps_rg_spine_convergence_w8.py",
        ),
        # APPS-RG-MODEL-SSOT - generator model IDs resolve through provider_profiles.yaml.
        # Fail-closed by default. Bypass: APPS_RG_MODEL_SSOT_GATE_BYPASS=1.
        (
            "APPS-RG-MODEL-SSOT apps_rg generator model SSOT (fail-closed)",
            "ops_scripts/ci/check_apps_rg_model_ssot.py",
        ),
        (
            "MODEL-LITERAL-SSOT provider model literal SSOT (fail-closed)",
            "ops_scripts/ci/check_model_literal_ssot.py",
        ),
        (
            "APPS-DRYRUN apps_rg --dry-run smoke (advisory)",
            "ops_scripts/ci/check_apps_rg_dryrun.py",
        ),
        # APPS-E2E-SMOKE, APPS-TYPE-VALID, APPS-EXIT-PATH — Runtime contract validation gates.
        # Plan: apps-rg-ci-runtime-enforcement-0be75b W1-W4.
        # Catches the 8 runtime bugs that escaped APPS-DRYRUN and AEH1.
        # APPS-E2E-SMOKE: advisory; fail-closed APPS_RG_E2E_SMOKE_FAIL_CLOSED=1; bypass APPS_RG_E2E_SMOKE_BYPASS=1.
        # APPS-TYPE-VALID: advisory; fail-closed APPS_RG_TYPE_VALID_FAIL_CLOSED=1; bypass APPS_RG_TYPE_VALID_BYPASS=1.
        # APPS-EXIT-PATH: advisory; fail-closed APPS_RG_EXIT_PATH_FAIL_CLOSED=1; bypass APPS_RG_EXIT_PATH_BYPASS=1.
        (
            "APPS-E2E-SMOKE apps_rg runtime smoke test (advisory)",
            "ops_scripts/ci/check_apps_rg_e2e_smoke.py",
        ),
        # RG-SMOKE-BUNDLE — pinned smoke dirs carry RUN_BUNDLE_INDEX (+ RUN_LINKS on integrated).
        # apps-rg-run-evidence-consolidation-d2c8e4 DoD-4. Advisory when roots absent on fresh clones.
        # Bypass: APPS_RG_SMOKE_BUNDLE_INDEX_BYPASS=1.
        # Strict (require dirs exist): APPS_RG_SMOKE_BUNDLE_INDEX_FAIL_CLOSED=1.
        (
            "RG-SMOKE-BUNDLE apps_rg smoke RUN_BUNDLE_INDEX + RUN_LINKS (advisory)",
            "ops_scripts/ci/check_apps_rg_smoke_bundle_indexes.py",
        ),
        (
            "APPS-TYPE-VALID apps_rg type contract validation (advisory)",
            "ops_scripts/ci/check_apps_rg_type_validation.py",
        ),
        (
            "APPS-EXIT-PATH apps_rg exit path construction (advisory)",
            "ops_scripts/ci/check_apps_rg_exit_path_construction.py",
        ),
        # SECTION-X2-X1D — all GENERATED_LANES: SSOT vs run_*_x2_gates vs X1D rubrics (+ exec synthesis/judge packet).
        # Fail-closed by default; advisory SECTION_X2_X1D_DRIFT_ADVISORY=1; bypass SECTION_X2_X1D_DRIFT_BYPASS=1.
        (
            "SECTION-X2-X1D generated-lane X2/X1D contract drift (fail-closed)",
            "ops_scripts/ci/check_section_x2_x1d_drift.py",
        ),
        # APPS-RG-PROMPT-JUDGE-SYNC — focused pytest contract suite for the
        # three-file prompt/judge update contract: product-shape SSOT,
        # executable prompt source, and X1D rubric/alignment matrix.
        # Fail-closed by default; bypass APPS_RG_PROMPT_JUDGE_SYNC_BYPASS=1.
        (
            "APPS-RG-PROMPT-JUDGE-SYNC apps_rg prompt/product-shape/X2/X1D sync (fail-closed)",
            "ops_scripts/ci/check_apps_rg_prompt_judge_sync.py",
            "APPS-RG-PROMPT-JUDGE-SYNC",
        ),
        # APPS-RG-REGISTRY-COVERAGE — non-numeric registry SSOT drift gate.
        # Fail-closed by default; advisory APPS_RG_REGISTRY_COVERAGE_ADVISORY=1;
        # bypass APPS_RG_REGISTRY_COVERAGE_BYPASS=1.
        (
            "APPS-RG-REGISTRY-COVERAGE apps_rg registry SSOT coverage (fail-closed)",
            "ops_scripts/ci/check_apps_rg_registry_coverage.py",
        ),
        (
            "EXEC-SUMMARY-L2-X1D-MANIFEST executive_summary L2/X1D input parity manifest",
            "ops_scripts/ci/check_exec_summary_l2_x1d_manifest_drift.py",
        ),
        # APPS-RG-L2-V4-ENVELOPE — apps_rg L2 v4 envelope feature flag bridge validation.
        # Validates W7B feature flag integration: _use_v4_l2_envelope helper,
        # feature flag bridge delegation, legacy path preservation, boundary checks,
        # provider governance, and mutation law invariants.
        # Plan: apps-rg-l2-v4-envelope-adoption-e9f2b1 W8.
        (
            "APPS-RG-L2-V4-ENVELOPE apps_rg L2 v4 envelope bridge (advisory; fail-closed via env)",
            "ops_scripts/ci/check_apps_rg_l2_v4_envelope.py",
        ),
        # APPS-AUTH — apps_rg live authority leak detection (advisory).
        # Scans apps_rg/tools/ + apps_rg/config/ for non-quarantined files
        # containing provider imports, core contract emissions, or runner
        # execution patterns. Quarantine stubs and INERT_CONFIG files are exempt.
        # Plan: apps-rg-quarantine-gap-remediation-8f405c W2.
        # Fail-closed: APPS_RG_LIVE_AUTHORITY_FAIL_CLOSED=1. Bypass: APPS_RG_LIVE_AUTHORITY_BYPASS=1.
        (
            "APPS-AUTH apps_rg live authority leak detection (advisory)",
            "ops_scripts/ci/check_apps_rg_live_authority.py",
        ),
        (
            "PLAN-DOD plan files have ## Definition of Done (advisory baseline)",
            "ops_scripts/ci/check_plan_definition_of_done.py",
        ),
        # PLAN-WAVE-TOP — consolidated wave summary at top (Status Tables → Wave Progress).
        # Advisory by default; fail-closed PLAN_WAVE_SUMMARY_TOP_FAIL_CLOSED=1.
        # Bypass: PLAN_WAVE_SUMMARY_TOP_BYPASS=1.
        (
            "PLAN-WAVE-TOP consolidated wave summary at plan top (advisory)",
            "ops_scripts/ci/check_plan_wave_summary_top.py",
        ),
        # GAP-001 — Exit L4 Boundary Hardening gate.
        # Blocks direct filesystem durable writes in apps_rg Exit binding.
        # Verifies Exit only produces inert CommitRequest candidates.
        # Advisory by default; fail-closed via APPS_RG_EXIT_NO_DIRECT_WRITES_FAIL_CLOSED=1.
        # Bypass: APPS_RG_EXIT_NO_DIRECT_WRITES_BYPASS=1.
        (
            "GAP001-EXIT apps_rg Exit no direct writes (advisory)",
            "ops_scripts/ci/check_gap001_exit_no_direct_writes.py",
        ),
        # EC-UI Enriched Choice UI invariants gate — RETIRED (Author-Gate W1 teardown,
        # ADR-093). It scanned callsites for the retired enriched-choice/AUTHOR_GATE_PACKET
        # wrapper; the live native-tool convention (numeric confidence + (Recommended)) is
        # enforced by the PreToolUse gate pre_ask_user_question_recommendation_gate.py. Gate
        # archived under archives/claude_native_supersession_2026-06-07/.
        # W6ECE1 — W6 Emit-Contract Enrichment 9-concern gate (ADR-084).
        # Structural field scan across all 11 emit contracts (AST-level).
        # Verifies: C1 identity quad, C2 l5_cert_ref, C3 gate_verdict_refs,
        # C4 replay fields, C5 observability refs, C7 posture, C9 signature,
        # C10 write-firewall, RuntimePosture sentinels.
        # Advisory by default; fail-closed via W6_EMIT_CONTRACT_GATE_FAIL_CLOSED=1.
        # Bypass: W6_EMIT_CONTRACT_GATE_BYPASS=1.
        # Plan: w6-emit-contract-enrichment-d8b2a4 W9.
        (
            "W6ECE1 emit-contract enrichment 9-concern gate (advisory)",
            "ops_scripts/ci/check_w6_emit_contract_enrichment.py",
        ),
        # MCP-SCHEMA — root .mcp.json validation.
        # Verifies required servers present, valid keys per constitutional §27,
        # and proper server configuration (command/args for local, url for remote).
        # Advisory by default; fail-closed via MCP_CONFIG_SCHEMA_FAIL_CLOSED=1.
        # Bypass: MCP_CONFIG_SCHEMA_BYPASS=1.
        (
            "MCP-SCHEMA legacy editor+legacy editor MCP config validation (advisory)",
            "ops_scripts/ci/check_mcp_config_schema.py --profile all",
        ),
        # NO-CURSOR-REFS — .cursor decommission anti-regression (W7): no tracked
        # .cursor/ files + no active .cursor/ path construction in live code.
        (
            "NO-CURSOR-REFS .cursor decommission anti-regression",
            "ops_scripts/ci/check_no_legacy_ide_refs.py",
        ),
        # NO-ARCHIVES-IMPORTS — constitutional §12: archived/superseded code is
        # reference-only and MUST NOT be imported back into production
        # (agentic_core/ + apps_*/). Fail-closed ratchet (baseline: 0 hits).
        # Bypass: CHECK_NO_ARCHIVES_IMPORTS_BYPASS=1.
        (
            "NO-ARCHIVES-IMPORTS no production imports from archive namespaces (§12)",
            "ops_scripts/ci/check_no_archives_imports.py",
        ),
        # MCP-PARITY — canonical fleet parity across editor configs.
        (
            "MCP-PARITY legacy editor vs legacy editor MCP editor parity",
            "ops_scripts/ci/check_mcp_editor_parity.py",
        ),
        # [W4 claude-native-supersession-9d3f7a] DEFER deferred-scope-marker gate RETIRED;
        # out-of-scope work now surfaces via native spawn_task chips (ADR-096).
        # RULE-FMT — Rule frontmatter schema validation.
        # Validates .codex/rules/*.md YAML frontmatter against canonical schema.
        # Baseline: many rules lack proper frontmatter (advisory).
        # Advisory by default; fail-closed via RULE_FRONTMATTER_FAIL_CLOSED=1.
        # Bypass: RULE_FRONTMATTER_BYPASS=1.
        (
            "RULE-FMT Rule frontmatter schema (advisory baseline)",
            "ops_scripts/ci/check_rule_frontmatter_schema.py",
        ),
        # RULES1 — Rules filesystem integrity check.
        # Validates .codex/rules/*.md files for: frontmatter presence,
        # duplicate titles, kebab-case filenames, and broken internal refs.
        # Advisory by default; fail-closed via RULES_INTEGRITY_FAIL_CLOSED=1.
        # Bypass: RULES_INTEGRITY_BYPASS=1.
        # Plan: fix-rules-notion-drift-c4e7b2 (Phase 1.3).
        (
            "RULES1 Rules filesystem integrity (advisory)",
            "ops_scripts/ci/check_rules_filesystem_integrity.py",
        ),
        # HK-CONS — Hook consolidation and growth monitoring gate (W5.P3).
        # Parses hooks.json to report hook statistics and detect growth risks:
        # hook count thresholds, lifecycle stage thresholds, post-agent growth,
        # missing v2 metadata, duplicate hook_ids, invalid replacement references.
        # Advisory by default (59 hooks, 10 stages, 22 replacement mappings baseline);
        # fail-closed via HOOK_CONSOLIDATION_FAIL_CLOSED=1.
        # Bypass: HOOK_CONSOLIDATION_BYPASS=1.
        # Plan: windsurf-governance-consolidation-a7c3e9 W5.P3.
        (
            "HK-CONS Hook consolidation growth check (advisory)",
            "ops_scripts/ci/check_hook_consolidation.py",
        ),
        (
            "MIRROR-H legacy editor docs/archive/windsurf/legacy-tree mirror health (advisory)",
            "ops_scripts/ci/check_cursor_governance_mirror_health.py",
        ),
        (
            "WIND-DEL docs/archive/windsurf/legacy-tree deletion readiness report (advisory)",
            "ops_scripts/ci/check_legacy_tree_deletion_readiness.py",
        ),
        # GOV-1..GOV-4 — Agentic Core governance enforcement gates
        # Plan: agentic-core-governance-remediation-c4e8a2 W1.
        # Advisory by default (sunset 2026-06-15); strict post-sunset.
        # Bypass: GOV_LITERALS_BYPASS=1, GOV_BOUNDARY_BYPASS=1, etc.
        (
            "GOV-1 No app-specific literals in core (advisory)",
            "ops_scripts/ci/check_no_app_specific_literals_in_core.py",
        ),
        (
            "GOV-2 Agentic core static boundary (advisory)",
            "ops_scripts/ci/check_agentic_core_static_boundary.py",
        ),
        (
            "GOV-JPH Judge panel harness boundary (strict)",
            "ops_scripts/ci/check_judge_panel_harness_boundary.py",
        ),
        (
            "GOV-3 Core Addition Author-Gate (fail-closed)",
            "ops_scripts/ci/check_agentic_core_addition.py",
        ),
        (
            "GOV-5 Apps runtime package contracts (advisory)",
            "ops_scripts/ci/check_apps_runtime_package_contracts.py",
        ),
        (
            "GOV-6 Governance receipts valid (advisory)",
            "ops_scripts/ci/check_governance_receipts.py",
        ),
        # PFC1 — Plan Format Compliance gate (W4 of plan-format-simplification-rca-d4f8e2).
        # Validates simplified-plan-format-v1 compliance for new and actively touched plans.
        # Does NOT scan archived/completed historical plans by default.
        # Modes: --advisory (exit 0) or --strict (exit non-zero on FAIL/ERROR/unclassified WARN).
        # Advisory by default; fail-closed via PLAN_FORMAT_COMPLIANCE_FAIL_CLOSED=1.
        # Bypass: PLAN_FORMAT_COMPLIANCE_BYPASS=1.
        (
            "PFC1 Plan format compliance (advisory)",
            "ops_scripts/ci/check_plan_format_compliance.py",
        ),
        # CHECK-RG-CHROMA — apps_rg ChromaDB readiness gate.
        # Verifies process_docs has app=apps_rg records, all 7 source_class counts
        # match expected stable values, all 8 metadata fields present, citation_anchor
        # populated for normative corpora, prior_outputs excluded from normative
        # source classes, and UNKNOWN not treated as PASS in support_status logic.
        # Advisory by default; fail-closed via APPS_RG_CHROMA_FAIL_CLOSED=1.
        # Bypass: APPS_RG_CHROMA_BYPASS=1.
        # Plan: apps-rg-chroma-ingestion-wiring-c7f2d9 W5.3.
        (
            "CHECK-RG-CHROMA apps_rg ChromaDB readiness (advisory)",
            "ops_scripts/ci/check_apps_rg_chroma_readiness.py",
        ),
        # CHECK-RG-FACT-VECTORS — apps_rg C0.2 dense+sparse lane
        # (fact_vectors, BGE-M3 / 1024 + data/cache/sparse/fact_vectors.db).
        # Preceded by SEED-RG-FV so contract_gates succeeds on fresh clones when
        # chromadb + sentence-transformers are installed. Bypass seed:
        # APPS_RG_SEED_FACT_VECTORS_BYPASS=1.
        # Advisory by default; fail-closed via APPS_RG_FACT_VECTORS_FAIL_CLOSED=1.
        # Bypass: APPS_RG_FACT_VECTORS_BYPASS=1.
        (
            "SEED-RG-FV apps_rg fact_vectors dense+sparse bootstrap (if missing)",
            "ops_scripts/ci/seed_apps_rg_fact_vectors_chroma.py",
            "SEED-RG-FV",
        ),
        (
            "CHECK-RG-FACT-VECTORS apps_rg fact_vectors readiness (advisory)",
            "ops_scripts/ci/check_apps_rg_fact_vectors_readiness.py",
            "CHECK-RG-FACT-VECTORS",
        ),
        # CHECK-RG-FV-PARITY / SCHEMA — governance visibility gates for the
        # c0-grounded-fact-writeback-spine W5 closeout. Parity checks the live
        # dense Chroma lane against data/cache/sparse/fact_vectors.db; schema
        # checks sampled metadata against apps_rg fact_vectors_schema.yaml.
        # Advisory by default; fail-closed via APPS_RG_FACT_VECTORS_PARITY_FAIL_CLOSED=1
        # and APPS_RG_FACT_VECTORS_SCHEMA_FAIL_CLOSED=1.
        (
            "CHECK-RG-FV-PARITY apps_rg fact_vectors dense/sparse parity (advisory)",
            "ops_scripts/ci/check_fact_vectors_lane_parity.py",
            "CHECK-RG-FV-PARITY",
        ),
        (
            "CHECK-RG-FV-SCHEMA apps_rg fact_vectors schema conformance (advisory)",
            "ops_scripts/ci/check_fact_vectors_schema_conformance.py",
            "CHECK-RG-FV-SCHEMA",
        ),
        # L4-FS-WRITE — apps_rg direct filesystem durable write gate.
        # Scans runtime/cache/providers for forbidden write_text/write_bytes/json.dump/open-w calls.
        # Advisory by default; fail-closed via APPS_RG_FS_WRITE_GATE_FAIL_CLOSED=1.
        # Bypass: APPS_RG_FS_WRITE_GATE_BYPASS=1.
        # Plan: apps-rg-l4-boundary-hardening-c8f2a1 W5.1.
        (
            "L4-FS-WRITE apps_rg no durable filesystem writes (advisory)",
            "ops_scripts/ci/check_no_direct_filesystem_durable_writes.py",
        ),
        # L4-CHROMA-RO — apps_rg Chroma read-only runtime gate.
        # Scans runtime/cache/tools/providers for Chroma mutation calls (add/upsert/delete/etc).
        # Advisory by default; fail-closed via APPS_RG_CHROMA_RO_GATE_FAIL_CLOSED=1.
        # Bypass: APPS_RG_CHROMA_RO_GATE_BYPASS=1.
        # Plan: apps-rg-l4-boundary-hardening-c8f2a1 W5.3.
        (
            "L4-CHROMA-RO apps_rg Chroma read-only enforcement (advisory)",
            "ops_scripts/ci/check_c0_chroma_readonly_runtime.py",
        ),
        # L4-IMPORT — apps_rg no direct L4 writer imports gate.
        # Scans apps_rg/ for forbidden imports from core L4 write modules.
        # Advisory by default; fail-closed via APPS_RG_L4_IMPORT_GATE_FAIL_CLOSED=1.
        # Bypass: APPS_RG_L4_IMPORT_GATE_BYPASS=1.
        # Plan: apps-rg-l4-boundary-hardening-c8f2a1 W5.4.
        (
            "L4-IMPORT apps_rg no direct L4 writer imports (advisory)",
            "ops_scripts/ci/check_no_direct_l4_writer_imports.py",
        ),
        # L4-MANIFEST — apps_rg L4 namespace manifest present and valid gate.
        # Verifies apps_rg/config/l4_namespace_manifest.yaml exists with >= 10 surfaces.
        # Advisory by default; fail-closed via APPS_RG_L4_MANIFEST_GATE_FAIL_CLOSED=1.
        # Bypass: APPS_RG_L4_MANIFEST_GATE_BYPASS=1.
        # Plan: apps-rg-l4-boundary-hardening-c8f2a1 W5.5.
        (
            "L4-MANIFEST apps_rg namespace manifest valid (advisory)",
            "ops_scripts/ci/check_l4_namespace_manifest_present.py",
        ),
        # W5 — One-spine enforcement (kill-shadow-pipelines-a7f3c2 W5).
        # Scans all apps_* for shadow-spine violations: profile_builder, binding,
        # and general app-code rules (PB-1..5, BM-1..6, SS-1..6, NC-1..5).
        # apps_qna are EXCLUDED from pass/fail (DEFER_WITH_REASON disposition).
        # Advisory by default; fail-closed: NO_SHADOW_SPINE_FAIL_CLOSED=1.
        # Bypass: NO_SHADOW_SPINE_BYPASS=1.
        # Report: artifacts/ci/no_shadow_spine_gate.json.
        (
            "W5 no-shadow-spine one-spine enforcement (advisory)",
            "ops_scripts/ci/check_no_shadow_spine.py",
        ),
    ]

    # Isolated ``--gate`` filters matching fact_vectors checks must still run SEED-RG-FV first,
    # otherwise fresh checkouts have no canonical Chroma/sparse lane to inspect.
    _g = getattr(args, "gate", None)
    if (
        _g
        and any(
            gate_id in str(_g)
            for gate_id in (
                "CHECK-RG-FACT-VECTORS",
                "CHECK-RG-FV-PARITY",
                "CHECK-RG-FV-SCHEMA",
            )
        )
        and "SEED-RG-FV" not in str(_g)
    ):
        print(
            "🔍 Running: SEED-RG-FV apps_rg fact_vectors dense+sparse bootstrap (if missing) "
            "[prerequisite for filtered fact_vectors gate] ...",
            flush=True,
        )
        _seed_cmd = [
            sys.executable,
            str(_script("ops_scripts/ci/seed_apps_rg_fact_vectors_chroma.py")),
        ]
        _rc, _out, _err = run_cmd(_seed_cmd, cwd=ROOT, timeout=900)
        if _rc != 0:
            print(f"❌ SEED-RG-FV prerequisite failed (exit={_rc})")
            if _out:
                print(_out)
            if _err:
                print(_err, file=sys.stderr)
            sys.exit(1)
        print("✅ SEED-RG-FV prerequisite passed")

    for gate_tuple in assurance_gates:
        # Handle both 2-tuple (label, script) and 3-tuple (label, script, gate_id)
        if len(gate_tuple) == 3:
            label, script, gate_id = gate_tuple
        else:
            label, script = gate_tuple
            gate_id = None

        # If --gate specified, skip gates that don't match
        if args.gate:
            # Check for exact match on gate_id or substring match on label
            gate_id_match = gate_id and args.gate == gate_id
            label_match = args.gate in label
            if not (gate_id_match or label_match):
                continue  # Skip this gate when filtering

        print(f"🔍 Running: {label} ...", flush=True)
        script_parts = script.split()
        script_rel = script_parts[0].replace("\\", "/")
        if script_rel.endswith("ops_scripts/ci/check_plan_format_compliance.py"):
            if os.environ.get("PLAN_FORMAT_COMPLIANCE_BYPASS") == "1":
                print("⚠️  PFC1 BYPASSED (PLAN_FORMAT_COMPLIANCE_BYPASS=1)")
                print(f"✅ {label} passed (bypassed)")
                continue
            cmd = _pfc1_gate_cmd()
        else:
            cmd = [sys.executable, str(_script(script_parts[0]))]
            cmd.extend(script_parts[1:])
        gate_timeout = DEFAULT_SUBPROCESS_TIMEOUT
        if script_rel.endswith("ops_scripts/ci/seed_apps_rg_fact_vectors_chroma.py"):
            gate_timeout = 900
        if script_rel.endswith("ops_scripts/ci/check_10c_pilot_proof_evidence.py"):
            cmd.append("--skip-pytest")
        returncode, stdout, stderr = run_cmd(cmd, cwd=ROOT, timeout=gate_timeout)
        if returncode != 0:
            print(f"❌ {label} failed (exit={returncode})")
            if stdout:
                print(stdout)
            if stderr:
                print(stderr, file=sys.stderr)
            sys.exit(1)
        else:
            print(f"✅ {label} passed")

    # If --gate was specified and a gate ran, exit early (don't run wiring_gates)
    if args.gate:
        # Check if any gate matched
        matched = False
        for gate_tuple in assurance_gates:
            if len(gate_tuple) == 3:
                label, script, gate_id = gate_tuple
            else:
                label, script = gate_tuple
                gate_id = None
            if gate_id == args.gate or args.gate in label:
                matched = True
                break
        if not matched:
            print(f"⚠️ Gate '{args.gate}' not found in assurance_gates")
            sys.exit(1)
        # Successfully ran the specified gate, exit
        return 0

    # ==================================================================
    # Wiring-CI gate plane (plan adg-wiring-ci-hardening-7a5d84)
    # Exit 1 on any failure. Ratchet gates pass when count <= baseline.
    # ==================================================================
    print("\n[WIRING-CI GATE PLANE]", flush=True)
    wiring_gates = [
        ("J1 canonical pipeline wiring", "ops_scripts/ci/check_canonical_pipeline_wiring.py"),
        ("A1 orphan module ratchet", "ops_scripts/ci/check_orphan_module_ratchet.py"),
        ("A3 dead-symbol ratchet", "ops_scripts/ci/check_dead_symbols_ratchet.py"),
        ("G4 graph-reach archival ratchet", "ops_scripts/ci/check_graph_reach_archival.py"),
        ("D7 dead-folder detector ratchet", "ops_scripts/ci/check_dead_folder_detector.py"),
        ("A6 import cycle", "ops_scripts/ci/check_import_cycles.py"),
        ("E1 trace-stub ratchet", "ops_scripts/ci/check_trace_stub_modules.py"),
        ("G2 seam-test export coherence", "ops_scripts/ci/check_seam_test_export_coherence.py"),
        ("L1 layer gravity ratchet", "ops_scripts/ci/check_layer_gravity.py"),
        ("L2 L_PG drift ratchet", "ops_scripts/ci/check_lpg_drift_ratchet.py"),
        ("M1 module LOC ratchet", "ops_scripts/ci/check_module_loc_ratchet.py"),
        ("D1 layer doc binding (warn)", "ops_scripts/ci/check_layer_doc_binding.py"),
        ("S1 global state mutation ratchet", "ops_scripts/ci/check_global_state_mutation_ratchet.py"),
        ("S2 UWG bypass ratchet", "ops_scripts/ci/check_uwg_bypass_ratchet.py"),
        (
            "00A L5 cross-child consistency (parent-pack alias)",
            "ops_scripts/ci/verify_l5_cross_child_consistency_validator.py",
        ),
        (
            "00A L5 no-write (parent-pack alias)",
            "ops_scripts/ci/verify_l5_no_write_validator.py",
        ),
        (
            "00B UWG sole admission (parent-pack alias)",
            "ops_scripts/ci/verify_uwg_sole_admission_validator.py",
        ),
        (
            "00B UWG receipt parent fields",
            "ops_scripts/ci/verify_uwg_receipt_parent_fields.py",
        ),
        ("S3 exception swallow ratchet", "ops_scripts/ci/check_exception_swallow_ratchet.py"),
        ("S4 unused imports ratchet", "ops_scripts/ci/check_unused_imports_ratchet.py"),
        ("W5 waiver expiry", "ops_scripts/ci/check_waiver_expiry.py"),
        (
            "§26 legacy editor config schema purity",
            "ops_scripts/ci/check_legacy_tree_config_schema.py",
        ),
        # §31 — SSOT folder routing for NEW Python files. Pre-commit covers
        # commit-time staged-file checks; this aggregator entry ensures CI
        # workflows that stage files (e.g., during release branches or merge
        # queues) also see the gate. Pass-through when no staged additions.
        # Sibling legacy editor hook: .codex/governance/scripts/pre_write_gate.py.
        ("§31 SSOT folder routing", "ops_scripts/ci/check_ssot_folder_routing.py"),
        # T8r — Phase E.1 advisory runtime-certification gate (ADR-080 §11).
        # Reads per-app Phase D cert-decision ledgers, compares latest
        # verdict against the TOML baseline at
        # docs/reference/runtime_certification/cert_baseline.toml. Advisory
        # today (exit 0 + warnings); `--strict` with a non-advisory baseline
        # flips to fail-closed after calibration. Non-promoting: every app
        # stays `runtime_certification_status = NOT_CERTIFIED`.
        # Plan family: runtime-cert-e1-*.md. Sibling pre-commit hook id
        # `runtime-certification`.
        ("T8r Runtime Cert Advisory Gate (Phase E.1)", "ops_scripts/ci/check_runtime_certification.py"),
        # Control-surface separation — verifies that the healing surface
        # and the RTC-REQ-056 LLM-as-judge surface remain disjoint on
        # disk. Read-only; reports `artifacts/certification/
        # control_surface_separation_report.json`.
        # Operator directive 2026-05-01.
        (
            "Control-surface separation (healing vs llm_as_judge)",
            "ops_scripts/ci/verify_control_surface_separation.py",
        ),
        # DS-R5 — fail-closed Spearman promotion gate for LLM-judge calibration.
        # Advisory by default; JUDGE_SPEARMAN_FAIL_CLOSED=1 activates blocking.
        # Plan: apps-underwriting-ai-d3-rationale-judge-f2c8d5 DS-R5.
        ("DS-R5 Judge Spearman calibration gate (advisory)", "ops_scripts/ci/check_judge_spearman_gate.py"),
        # AG-WIRE — Author-Gate hook wiring invariant.
        # Enforces AG-WIRE-1..4: pre_user_prompt reminder hook present+visible,
        # and all 3 AG audit hooks in post_agent_response have show_output=true.
        # Advisory by default; AG_HOOK_WIRING_FAIL_CLOSED=1 activates blocking.
        # Plan: author-gate-deferred-scope-b8c1d4 W3.
        # AG-DEFER — Deferred-scope plan guard marker parity.
        # Every plan with "do not implement without" prose MUST have a
        # DO_NOT_IMPLEMENT_GUARD: marker so the pre_user_prompt hook can surface
        # the block to Codex at every turn. Advisory by default;
        # fail-closed via DEFERRED_PLAN_GUARD_FAIL_CLOSED=1.
        # RCA: 2026-05-10 notion-test-hardening-deferred-scope-a7b4c9.
        # Bypass: DEFERRED_PLAN_GUARD_BYPASS=1.
        ("AG-DEFER Deferred-scope plan guard marker parity (advisory)", "ops_scripts/ci/check_deferred_plan_guard_markers.py"),
        # [notion-wave-enforcement-removal] NP-GUARD (Notion plan-lifecycle Completed guard) REMOVED.
        # RG-JD0 — apps_rg JD resolution / default JD SSOT must not appear under agentic_core/.
        ("RG-JD0 agentic_core JD SSOT boundary", "ops_scripts/ci/check_agentic_core_no_apps_rg_jd_ssot.py"),
        # RG-RESUME0 — apps_rg resume resolution / default resume SSOT must not appear under agentic_core/.
        ("RG-RESUME0 agentic_core resume SSOT boundary", "ops_scripts/ci/check_agentic_core_no_apps_rg_resume_ssot.py"),
        # HEAL-DEPRECATION — keep L2 E4 same-authority repair, but reject
        # retired confidence-router env/config surfaces in apps and env files.
        # Bypass: HEAL_ROUTING_DEPRECATION_BYPASS=1.
        ("HEAL-DEPRECATION retired confidence routing guard", "ops_scripts/ci/check_heal_routing_threshold_ssot.py"),
        # WG1 — ADG wiring gap detector (4 modes: registry-gaps,
        # instantiation-orphans, port-adapter-gaps, dead-imports).
        # Advisory by default (--gate flag not passed); activates blocking via
        # ADG_WIRING_GAP_GATE=1 env var, which adds --gate to the invocation.
        # Plan: adg-distilled-followups-c8e4a1 W2 / P3-P4.
        ("WG1 ADG wiring gap check (advisory)", "tools/adg/adg_wiring_gap_check.py"),
    ]
    for label, script in wiring_gates:
        print(f"🔍 Running: {label} ...", flush=True)
        returncode, stdout, stderr = run_cmd([sys.executable, str(_script(script))], cwd=ROOT)
        if returncode != 0:
            print(f"❌ {label} failed")
            print(stdout)
            print(stderr)
            sys.exit(1)
        print(f"✅ {label} passed")

    # Continue with existing logic...
    return 0


if __name__ == "__main__":
    sys.exit(main())
