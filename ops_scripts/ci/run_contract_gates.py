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
# Does NOT scan all of .claude/plans — explicit paths only (see W4 CI gate receipt).
_PFC1_CANONICAL_PLAN_PATHS = (
    ".claude/plans/plan-format-simplification-rca-d4f8e2.md",
    ".claude/templates/execution-plan-template.md",
    ".claude/plans/acceptance-gates-master-tracking-b5c3e1.md",
    ".claude/plans/adg-antipattern-hardening-e5a569.md",
    ".claude/plans/agentic-core-signoff-hardening-b8e2c4.md",
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


# PRE-WRITE HOOKS INTEGRATION
def validate_pre_write_hooks():
    """Validate all pre-write hook skills."""
    skills_dir = ROOT / ".claude" / "skills"
    failed_skills: list[str] = []
    if not skills_dir.is_dir():
        print(f"❌ Skills directory missing: {skills_dir}")
        return False

    skill_dirs = sorted((d for d in skills_dir.iterdir() if d.is_dir()), key=lambda p: p.name)
    for idx, skill_dir in enumerate(skill_dirs, 1):  # progress_bar: skill health checks
        print(f"  [{idx}/{len(skill_dirs)}] checking skill: {skill_dir.name}")
        main_script = skill_dir / "main.py"
        if main_script.exists():
            try:
                result = subprocess.run(
                    [sys.executable, str(main_script), "--health-check"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=False,
                    cwd=ROOT,
                )
                if result.returncode != 0:
                    failed_skills.append(f"{skill_dir.name} (rc={result.returncode})")
            except (subprocess.TimeoutExpired, OSError) as exc:
                failed_skills.append(f"{skill_dir.name} ({type(exc).__name__})")

    if failed_skills:
        print(f"❌ Failed skills: {', '.join(failed_skills)}")
        return False

    print("✅ All pre-write hooks validated")
    return True


# MCP HEALTH CHECKS
def validate_mcp_health():
    """Validate MCP server health."""
    print("\n[MCP HEALTH CHECK]")

    # Gate: AGENTS.md Quick Reference must document every server in .cursor/mcp.json
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
    # .cursor/mcp.json mirror + Cursor-vs-Windsurf editor parity. Both mirrors are
    # retired (root .mcp.json is the sole SSOT), so these gates are obsolete and removed.

    # cursor-decommission W7: check_mcp_config_sovereignty enforced a Cursor-era
    # filesystem-MCP-args lock against .cursor/mcp.json. Root .mcp.json is the SSOT
    # and intentionally omits the filesystem MCP (native file tools), so the gate's
    # MISSING_FILESYSTEM premise no longer holds. Retired.

    # cursor-decommission W7: check_cursor_config_schema removed (validated deleted
    # .cursor/hooks.json + .cursor/mcp.json; Claude Code uses .claude/settings.json + root .mcp.json).

    # Gate: every .claude/skills/<name>/SKILL.md must conform to Anthropic's
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

    # Validate pre-write hooks
    if not validate_pre_write_hooks():
        sys.exit(1)

    # Gate: Infrastructure wiring scan (Rule: no raw infra in forbidden layers)
    print("🔍 Running infrastructure wiring scan...")
    returncode, stdout, stderr = run_cmd(
        [sys.executable, str(_script("ops_scripts/ci/infra_wiring_scan.py"))], cwd=ROOT
    )
    if returncode != 0:
        print(stdout)
        print(stderr)
        sys.exit(1)
    print("✅ Infrastructure wiring scan passed")

    # Gate: Executor theater (no fake parallelism in production code)
    print("🔍 Running executor theater gate...")
    returncode, stdout, stderr = run_cmd(
        [sys.executable, str(_script("ops_scripts/ci/executor_theater_gate.py"))], cwd=ROOT
    )
    if returncode != 0:
        print(stdout)
        print(stderr)
        sys.exit(1)
    print("✅ Executor theater gate passed")

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

    # Gate: ADG snapshot graph-layer completeness (Constitutional §22 — artifact side)
    # Symmetric to check_graph_layer_evidence.py (plan side). Protects the
    # adg-pipeline-e2e-5287a1 W1 ordering fix from silent regression.
    print("🔍 Running snapshot graph-layer completeness gate (artifact side)...")
    returncode, stdout, stderr = run_cmd(
        [sys.executable, str(_script("ops_scripts/ci/check_snapshot_has_mvs.py"))],
        cwd=ROOT,
    )
    if returncode != 0:
        print(stdout)
        print(stderr)
        sys.exit(1)
    print("✅ Snapshot graph-layer completeness gate passed")

    # Gate: ADG pipeline skip ledger (Constitutional §22 — observability)
    # Symmetric to the snapshot gate. Plan adg-pipeline-e2e-5287a1 W4.
    print("🔍 Running pipeline skip ledger gate (observability)...")
    returncode, stdout, stderr = run_cmd(
        [sys.executable, str(_script("ops_scripts/ci/check_pipeline_skips.py"))],
        cwd=ROOT,
    )
    if returncode != 0:
        print(stdout)
        print(stderr)
        sys.exit(1)
    print("✅ Pipeline skip ledger gate passed")

    # Gate: Severity<->Band SSOT (Constitutional §22/§23 — no hardcoded mappings)
    print("🔍 Running severity<->band SSOT gate...")
    returncode, stdout, stderr = run_cmd(
        [sys.executable, str(_script("ops_scripts/ci/check_severity_band_ssot.py"))],
        cwd=ROOT,
    )
    if returncode != 0:
        print(stdout)
        print(stderr)
        sys.exit(1)
    print("✅ Severity<->band SSOT gate passed")

    # Gate: ADG exclusion-list sync (was config-sync-gates.yml — folded 2026-05-06)
    # Verifies tools/generate/check_exclusion_sync.py — ensures ADG exclusion
    # lists stay in sync across config sources. Sole unique check from the
    # retired config-sync-gates.yml workflow.
    print("🔍 Running ADG exclusion-sync gate...")
    returncode, stdout, stderr = run_cmd(
        [sys.executable, str(_script("tools/generate/check_exclusion_sync.py"))],
        cwd=ROOT,
    )
    if returncode != 0:
        print(stdout)
        print(stderr)
        sys.exit(1)
    print("✅ ADG exclusion-sync gate passed")

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

    # Gate: Reference doctrine orphans (prevent '*.pre-reqid-rewrite.bak' and
    # '* exec.md' predecessors from leaking back into docs/reference/ outside
    # docs/reference/_archive/). RCA 2026-04-27: external bundler + bulk-WIP
    # sync commits re-add orphans silently; this gate is the durable defense.
    print("🔍 Running reference doctrine orphans gate...")
    returncode, stdout, stderr = run_cmd(
        [sys.executable, str(_script("ops_scripts/ci/check_reference_orphans.py"))],
        cwd=ROOT,
    )
    if returncode != 0:
        print(stdout)
        print(stderr)
        sys.exit(1)
    print("✅ Reference doctrine orphans gate passed")

    # Gate: LLM-as-Judge calibration (LJH4.3) — non-blocking while gold set
    # is bootstrapping. Gate exits 2 when gold set is too small to enforce
    # kappa and we treat that as a warning so plain-main CI stays green.
    print("\n[LLM-AS-JUDGE CALIBRATION]")
    returncode, stdout, stderr = run_cmd(
        [
            sys.executable,
            str(_script("ops_scripts/ci/check_judge_calibration.py")),
            "--allow-empty",
            "--allow-missing-judge-outputs",
        ],
        cwd=ROOT,
    )
    if returncode == 1:
        print("❌ Judge calibration gate failed (kappa < threshold)")
        print(stdout or stderr)
        sys.exit(1)
    if returncode == 2:
        print("⚠️  Judge calibration gate SKIPPED (gold set below min_items)")
    else:
        print("✅ Judge calibration gate passed")

    # Gate: Author-gate (harness HITL) — ledger schema + outcome coverage (W2)
    print("\n[AUTHOR-GATE HARNESS HITL]")
    returncode, stdout, stderr = run_cmd(
        [sys.executable, str(_script("ops_scripts/ci/author_gate/check_ledger_schema.py"))],
        cwd=ROOT,
    )
    if returncode != 0:
        print("❌ Author-gate ledger schema check failed")
        print(stdout or stderr)
        sys.exit(1)
    print("✅ Author-gate ledger schema validated")

    returncode, stdout, stderr = run_cmd(
        [sys.executable, str(_script("ops_scripts/ci/check_refactor_decision_ledger_ssot.py"))],
        cwd=ROOT,
    )
    if returncode != 0:
        print("❌ Refactor decision ledger SSOT check failed")
        print(stdout or stderr)
        sys.exit(1)
    print("✅ Refactor decision ledger SSOT validated")

    returncode, stdout, stderr = run_cmd(
        [sys.executable, str(_script("ops_scripts/ci/author_gate/check_outcome_coverage.py"))],
        cwd=ROOT,
    )
    if returncode != 0:
        print("❌ Author-gate outcome coverage check failed")
        print(stdout or stderr)
        sys.exit(1)
    print("✅ Author-gate outcome coverage validated")

    # Gate: Author-gate ledger hash-chain integrity (W5)
    returncode, stdout, stderr = run_cmd(
        [sys.executable, str(_script("ops_scripts/ci/author_gate/check_ledger_integrity.py"))],
        cwd=ROOT,
    )
    if returncode != 0:
        print("❌ Author-gate ledger integrity check failed")
        print(stdout or stderr)
        sys.exit(1)

    # Gate: ask_user_question packet vacuum-closure freshness
    # (plan author-gate-four-req-enforcement-c4d2a8 W2.P1).
    # Watches artifacts/cursor/ask_user_question_packet_violations.jsonl
    # produced by post_agent_ask_user_question_packet_audit.py.
    # Bypass: ASK_PACKET_AUDIT_FRESHNESS_BYPASS=1.
    returncode, stdout, stderr = run_cmd(
        [
            sys.executable,
            str(
                _script(
                    "ops_scripts/ci/author_gate/check_ask_user_question_packet_freshness.py"
                )
            ),
        ],
        cwd=ROOT,
    )
    if returncode != 0:
        print("❌ Author-gate ask_user_question packet freshness check failed")
        print(stdout or stderr)
        sys.exit(1)
    print("✅ Author-gate ask_user_question packet freshness validated")

    # Gate: AGP1 — Author-Gate pipeline completion freshness
    # (plan author-gate-ui-renderer-hardening-a7f3c2 W3.P3.2).
    # Watches artifacts/cursor/author_gate_pipeline_violations.jsonl
    # produced by post_agent_author_gate_pipeline_audit.py.
    # Fail-closed by default; AG_PIPELINE_ADVISORY=1 downgrades to warning-only.
    # Bypass: AG_PIPELINE_FRESHNESS_BYPASS=1.
    returncode, stdout, stderr = run_cmd(
        [
            sys.executable,
            str(
                _script(
                    "ops_scripts/ci/check_author_gate_pipeline_freshness.py"
                )
            ),
        ],
        cwd=ROOT,
    )
    if returncode != 0:
        print("❌ AGP1 Author-Gate pipeline completion freshness check failed")
        print(stdout or stderr)
        sys.exit(1)
    print("✅ AGP1 Author-Gate pipeline completion freshness validated")

    # Gate: Author-Gate v2/W4 completeness (plan 1f4c8a W5) — advisory by
    # default; emits warnings without blocking. Set AUTHOR_GATE_V2_STRICT=1
    # to fail closed once the ledger is clean for one full 7-day window.
    returncode, stdout, stderr = run_cmd(
        [sys.executable, str(_script("ops_scripts/ci/check_author_gate_v2_completeness.py"))],
        cwd=ROOT,
    )
    if returncode != 0:
        print("❌ Author-gate v2 completeness check failed (strict mode)")
        print(stdout or stderr)
        sys.exit(1)
    print("✅ Author-gate v2 completeness check ran")
    print("✅ Author-gate ledger integrity validated")

    # W4.1 — Author-Gate ledger anomaly heuristics (advisory by default).
    # AUTHOR_GATE_ANOMALY_FAIL_CLOSED=1 fails on high-severity findings.
    # AUTHOR_GATE_ANOMALY_BYPASS=1 skips.
    returncode, stdout, stderr = run_cmd(
        [
            sys.executable,
            str(_script("ops_scripts/ci/author_gate/detect_author_gate_ledger_anomalies.py")),
        ],
        cwd=ROOT,
    )
    if returncode != 0:
        print("❌ Author-gate ledger anomaly detector failed (fail-closed mode?)")
        print(stdout or stderr)
        sys.exit(1)
    print("✅ Author-gate ledger anomaly detector ran")

    # W4.2 — governance bypass JSONL rollup (advisory; always exit 0 from script).
    returncode, stdout, stderr = run_cmd(
        [
            sys.executable,
            str(_script("ops_scripts/ci/author_gate/rollup_governance_bypass_logs.py")),
        ],
        cwd=ROOT,
    )
    if returncode != 0:
        print("❌ Governance bypass rollup failed")
        print(stdout or stderr)
        sys.exit(1)
    print("✅ Governance bypass rollup refreshed")

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
        # NOTE: check_windsurf_config_schema.py is canonical in wiring_gates (§26 label).
        # Removed from assurance_gates 2026-05-05 to eliminate true CI-plane duplication.
        # See: ops_scripts/ci/run_contract_gates.py wiring_gates entry "§26 Windsurf config schema purity".
        ("W1 runtime trace contract", "ops_scripts/ci/check_runtime_trace_contract.py"),
        ("W3 replay determinism proof", "ops_scripts/ci/check_replay_proof.py"),
        ("W4 requirements ↔ ADG crosswalk", "ops_scripts/ci/check_requirements_adg_crosswalk.py"),
        ("W4a 10C ledger ↔ matrix consistency", "ops_scripts/ci/check_10c_ledger_consistency.py"),
        ("W4b requirements universe inventory", "ops_scripts/ci/check_requirements_universe_inventory.py"),
        ("W4c AGEN registry schema", "ops_scripts/ci/check_agen_registry_schema.py"),
        ("W4d 10C proof-ledger validation", "tools/requirements/validate_10c_proof_ledger.py"),
        ("W4d-3 10C cross-file consistency", "ops_scripts/ci/check_10c_cross_file_consistency.py"),
        ("W4d-4 10C pilot proof-evidence", "ops_scripts/ci/check_10c_pilot_proof_evidence.py"),
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
        # NP1 — Plans DB mandatory AI Summary gate. Advisory by default;
        # flip fail-closed via NOTION_PLANS_AI_SUMMARY_FAIL_CLOSED=1.
        # Skips when NOTION_API_KEY / NOTION_TOKEN is unset (offline CI).
        # Rule: .claude/rules/notion-plans-taxonomy.md > Mandatory AI Summary.
        (
            "NP1 Notion Plans AI Summary (advisory)",
            "ops_scripts/ci/check_notion_plans_ai_summary.py",
        ),
        # NP2 -- Plans DB Status must use canonical option strings.
        # Advisory by default; fail-closed via NOTION_PLANS_STATUS_FAIL_CLOSED=1.
        # Skips when NOTION_API_KEY / NOTION_TOKEN unset (offline CI).
        # Rule: .claude/rules/notion-plans-taxonomy.md > CANONICAL Status option strings.
        (
            "NP2 Notion Plans Status drift (advisory)",
            "ops_scripts/ci/check_notion_plans_status_drift.py",
        ),
        # NP3 -- Backlog Items rows must have a Plan relation (true orphans ==0).
        # Advisory by default; fail-closed via BACKLOG_PLAN_LINKAGE_FAIL_CLOSED=1.
        # Orphan count confirmed 0 (2026-05-03, plan backlog-linkage-followup-c2e9f3).
        # Ready to promote: set BACKLOG_PLAN_LINKAGE_FAIL_CLOSED=1 to enforce.
        # Skips when NOTION_API_KEY / NOTION_TOKEN unset (offline CI).
        # Rule: .claude/rules/notion-backlog-plan-linkage.md
        (
            "NP3 Notion Backlog plan linkage (advisory)",
            "ops_scripts/ci/check_notion_backlog_plan_linkage.py",
        ),
        # NP4 -- Plans DB freshness vs on-disk plan files. Backstop for the
        # wave-lifecycle auto-sync chain (plan notion-wave-lifecycle-autosync-f4a2b8).
        # Advisory by default; fail-closed via NOTION_PLANS_WAVE_FAIL_CLOSED=1.
        # Bypass: NOTION_PLANS_WAVE_BYPASS=1.
        # Skips when NOTION_API_KEY / NOTION_TOKEN unset (offline CI).
        # Rule: .claude/rules/notion-plan-wave-deferral.md (sanctioned non-MCP path).
        (
            "NP4 Notion Plans wave freshness (advisory)",
            "ops_scripts/ci/check_plan_notion_wave_freshness.py",
        ),
        # NP5 -- Plans DB duplicate-slug dedup gate. Uses local cache snapshot
        # (offline safe) or --live mode against the Notion API. Fails when any
        # slug has ≥2 active rows. Advisory by default; fail-closed via
        # NOTION_PLANS_DUP_BYPASS=1 to bypass.
        # Plan: notion-plans-status-rca-followups-b8e3f2 (W1.P2d).
        (
            "NP5 Notion Plans no duplicate slugs (advisory)",
            "ops_scripts/ci/check_notion_plans_no_duplicates.py",
        ),
        # NP6 -- Backlog Items DB duplicate-title dedup gate (DS-6).
        # Advisory by default; fail-closed via BACKLOG_DUP_FAIL_CLOSED=1.
        # Bypass: BACKLOG_DUP_BYPASS=1. Skips when token absent (offline CI).
        # Plan: notion-plans-db-hygiene-deferred-scope-d4f7c1 DS-6.
        (
            "NP6 Notion Backlog no duplicate titles (advisory)",
            "ops_scripts/ci/check_notion_backlog_no_duplicates.py",
        ),
        # NP7 -- Plans-DB write telemetry log size gate (DS-4).
        # Fails when artifacts/cursor/plans_db_writes.jsonl exceeds 10 MB
        # without rotation. Advisory by default; fail-closed via
        # NOTION_TELEMETRY_LOG_SIZE_FAIL_CLOSED=1.
        # Plan: notion-plans-db-hygiene-deferred-scope-d4f7c1 DS-4.
        (
            "NP7 Notion telemetry log size (advisory)",
            "ops_scripts/ci/check_notion_telemetry_log_size.py",
        ),
        # NP8 -- Plans DB status anomaly detection. Detects suspicious status
        # changes (quick flips, identity mismatches, etc.). Advisory by default;
        # fail-closed via NOTION_PLAN_STATUS_ANOMALIES_FAIL_CLOSED=1.
        # Skips when NOTION_API_KEY / NOTION_TOKEN unset (offline CI).
        # Rule: .claude/rules/notion-plan-identity-verification.md
        (
            "NP8 Notion plan status anomalies (advisory)",
            "ops_scripts/ci/check_notion_plan_status_anomalies.py",
        ),
        # RULE-XREF -- Rule cross-reference validation. Ensures all rule-to-rule
        # links are intact and targets exist. Advisory by default;
        # fail-closed via RULE_CROSS_REF_FAIL_CLOSED=1.
        # Bypass: RULE_CROSS_REF_BYPASS=1.
        (
            "RULE-XREF Rule cross-references (advisory)",
            "ops_scripts/ci/check_rule_cross_references.py",
        ),
        # NP9 -- New plans must use "Not Started" status, not "Lower Priority" or "Waiting".
        # 24h detection window. Advisory by default; fail-closed via
        # NOTION_PLANS_NEW_STATUS_FAIL_CLOSED=1. Bypass: NOTION_PLANS_NEW_STATUS_BYPASS=1.
        # Plan: notion-plans-new-status-enforcement-c9f2a3.
        (
            "NP9 Notion Plans new-plan status (advisory)",
            "ops_scripts/ci/check_notion_plans_new_status.py",
        ),
        # NP10 -- Waiting-status plans must have non-blank Waiting For.
        # Queries Notion API for all Waiting-status rows and reports ERROR
        # for any with empty Waiting For property. Advisory by default;
        # fail-closed via NOTION_PLANS_WAITING_FOR_FAIL_CLOSED=1.
        # Bypass: NOTION_PLANS_WAITING_FOR_BYPASS=1.
        # Skips when NOTION_API_KEY / NOTION_TOKEN unset (offline CI).
        # Rule: .claude/rules/notion-plans-taxonomy.md > Field Requirements.
        (
            "NP10 Notion Plans Waiting-For completeness (advisory)",
            "ops_scripts/ci/check_notion_plans_waiting_for.py",
        ),
        # NP11 -- Backlog Items DB Waiting-status rows must have non-blank
        # Waiting For (DS-3 parity with NP10). Advisory by default;
        # fail-closed via NOTION_BACKLOG_WAITING_FOR_FAIL_CLOSED=1.
        # Bypass: NOTION_BACKLOG_WAITING_FOR_BYPASS=1.
        # Skips when NOTION_API_KEY / NOTION_TOKEN unset (offline CI).
        # Rule: .claude/rules/notion-plans-taxonomy.md > Field Requirements.
        (
            "NP11 Notion Backlog Waiting-For completeness (advisory)",
            "ops_scripts/ci/check_notion_backlog_waiting_for.py",
        ),
        # NP13 -- Plans DB rows stuck In Progress for >7d with no
        # PLAN_COMPLETE marker in wave_lifecycle_capture.jsonl.
        # Advisory by default; fail-closed via
        # NOTION_PLAN_COMPLETE_FAIL_CLOSED=1.
        # Bypass: NOTION_PLAN_COMPLETE_BYPASS=1.
        # Skips when NOTION_API_KEY / NOTION_TOKEN unset (offline CI).
        # Rule: .claude/rules/notion-plan-wave-deferral.md.
        # Plan: plan-complete-marker-enforcement-d2e9f1 W2.
        (
            "NP13 Notion Plans PLAN_COMPLETE marker freshness (advisory)",
            "ops_scripts/ci/check_plan_complete_marker_freshness.py",
        ),
        # NP14 — Plans DB status at creation time. Detects plans created with
        # wrong initial status (not "Not Started" or "Completed").
        # Advisory by default; fail-closed via NOTION_PLAN_STATUS_INITIAL_FAIL_CLOSED=1.
        # Bypass: NOTION_PLAN_STATUS_INITIAL_BYPASS=1.
        # Skips when NOTION_API_KEY / NOTION_TOKEN unset (offline CI).
        # Rule: .claude/rules/notion-plans-taxonomy.md > Status Creation Invariant.
        # Plan: holistic-plan-status-discipline-d4e8a1 (W3).
        (
            "NP14 Notion Plans status initial (advisory)",
            "ops_scripts/ci/check_notion_plan_status_initial.py",
        ),
        # NP12 — Schema preflight validation. Validates that Notion write
        # operations target existing properties before API calls are made.
        # Advisory by default; fail-closed via NOTION_SCHEMA_PREFLIGHT_FAIL_CLOSED=1.
        # Bypass: NOTION_SCHEMA_PREFLIGHT_BYPASS=1.
        # Rule: .claude/rules/notion-sync-enforcement.md > Schema Validation.
        # Plan: notion-sync-enforcement-hardening-f5a2c1 W1.P2.
        (
            "NP12 Notion Schema Pre-flight (advisory)",
            "ops_scripts/ci/check_notion_schema_preflight.py",
        ),
        # NP15 — Wave/Phase Convergence DB ↔ disk plan-file drift. Checks that
        # open Backlog rows whose Plan File field is set resolve to an on-disk
        # .claude/plans/ file. Orphan rows are reported.
        # Advisory by default; fail-closed via STRICT_DRIFT=1.
        # Bypass: PLAN_FILE_DRIFT_BYPASS=1.
        # Plan: notion-integration-consistency-audit-b2c4d8 W3.
        (
            "NP15 Notion plan file drift (advisory)",
            "ops_scripts/ci/check_notion_plan_file_drift.py",
        ),
        # NP16 — Author-Gate decision signals. SQLite ledger under
        # ``.claude/state/refactor_decisions/`` is SSOT; Notion Author-Gate ledger
        # archived 2026-05-02. Gate logs legacy Notion post traffic; fail-closed
        # only when NOTION_DECISION_PARITY_FAIL_CLOSED=1 and legacy posts > 0.
        # Bypass: NOTION_DECISION_PARITY_BYPASS=1.
        # Plan: notion-enforcement-ssot-hardening-e4f8a2.
        (
            "NP16 Notion decision parity (advisory)",
            "ops_scripts/ci/check_notion_decision_parity.py",
        ),
        # NP17 — Wave/Phase Convergence MECE v2 schema gate. Verifies that known
        # Notion writer scripts do not write retired fields and do write Evidence.
        # Fail policy: exit 1 on any violation (always enforced).
        # Plan: notion-integration-consistency-audit-b2c4d8 W3.
        (
            "NP17 Notion Wave/Phase MECE v2 schema (enforced)",
            "ops_scripts/ci/check_notion_schema_mece.py",
        ),
        # NP18 — Plans DB canonical status + discipline gate. Validates status
        # option strings are canonical (not stale emoji variants) and flags
        # In Progress plans with stale deferred items lacking Waiting For.
        # Advisory by default; fail-closed via --fail-closed arg.
        # Bypass: NOTION_PLANS_STATUS_CANONICAL_BYPASS=1 (env, advisory only).
        # Plan: notion-integration-consistency-audit-b2c4d8 W3.
        (
            "NP18 Notion Plans status canonical (advisory)",
            "ops_scripts/ci/check_notion_plans_status_canonical.py",
        ),
        # NP-DONE -- Plans whose on-disk Wave Structure table shows all waves
        # ✅ DONE but Notion status ≠ "Completed". Belt-and-suspenders backstop
        # for the wave_execution_state.py + PLAN_COMPLETE: hook chain.
        # Advisory by default; fail-closed via NP_PLAN_DONE_STATUS_FAIL_CLOSED=1.
        # Bypass: NP_PLAN_DONE_STATUS_BYPASS=1.
        # Skips when NOTION_TOKEN / NOTION_API_KEY unset (offline CI).
        # RCA: plan apps-lic-quarantine-u0-coverage-review-d9f4a2 stayed Archived.
        # Plan: plan-complete-notion-status-enforcement-a7e2d1 (W2.P1).
        (
            "NP-DONE Plans all-waves-done disk-vs-Notion (advisory)",
            "ops_scripts/ci/check_plan_done_notion_status.py",
        ),
        # WAVE-MARKER — Plans with mixed wave state (some DONE, some TODO) but
        # no WAVE_COMPLETE / PLAN_COMPLETE entry in wave_lifecycle_capture.jsonl.
        # Detects the failure mode from RCA rca-wave-marker-emission-gap-c7d3f1
        # where Cursor Agent executed waves without emitting required markers.
        # Advisory by default; fail-closed via WAVE_MARKER_GATE_FAIL_CLOSED=1.
        # Bypass: WAVE_MARKER_EMISSION_BYPASS=1.
        # Report: artifacts/ci/wave_marker_emission_gate.json.
        (
            "WAVE-MARKER Wave marker emission completeness (advisory)",
            "ops_scripts/ci/check_wave_marker_emission.py",
        ),
        # RG-W3 — Retired warm_r1b_cache shadow runner must stay absent.
        # Canonical cache proof is via python -m apps_rg + contract tests only.
        # Advisory by default; flip fail-closed via R1B_WARMUP_SMOKE_FAIL_CLOSED=1.
        # Plan: apps-rg-cache-followon-deferred-c7d3a1 W1.
        (
            "RG-W3 R1B warmup smoke (advisory)",
            "ops_scripts/ci/check_r1b_warmup_smoke.py",
        ),
        # PR1 — Plan–Notion registration freshness (Constitutional §36).
        # Advisory by default; flip fail-closed via
        # PLAN_REGISTRATION_FAIL_CLOSED=1. Offline-safe: SKIPs when no
        # token and no local cache. Rule:
        # .claude/rules/plan-registration-enforcement.md.
        (
            "PR1 Plan–Notion Registration (advisory)",
            "ops_scripts/ci/check_plan_registration_freshness.py",
        ),
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
        # .claude/plans/apps-dom-real-evidence-enhancement-c7f4d8.md W4.
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
        # -- Cursor Agent violation log freshness backstops (2026-05-05) ---------------
        # Windsurf post_agent_* hooks write persistent violation logs. These
        # gates ensure CI surfaces stale unresolved violations — same pattern
        # as check_ask_user_question_packet_freshness.py. Advisory by default.
        #
        # ADG-first violations: post_agent_adg_audit.py writes
        # artifacts/cursor/adg_first_violations.jsonl (see gate script).
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
        # EC-UI — Enriched Choice UI invariants gate.
        # Validates ask_user_question calls use enriched format (confidence prefix,
        # trade-off segment, star marker) per consolidated plan a1e3f7.
        # Advisory by default; fail-closed via ENRICHED_CHOICE_UI_FAIL_CLOSED=1.
        # Bypass: ENRICHED_CHOICE_UI_BYPASS=1.
        (
            "EC-UI Enriched Choice UI invariants (advisory)",
            "ops_scripts/ci/check_enriched_choice_ui_invariants.py",
        ),
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
        # MCP-SCHEMA — .cursor/mcp.json + .cursor/mcp.json validation.
        # Verifies required servers present, valid keys per constitutional §27,
        # and proper server configuration (command/args for local, url for remote).
        # Advisory by default; fail-closed via MCP_CONFIG_SCHEMA_FAIL_CLOSED=1.
        # Bypass: MCP_CONFIG_SCHEMA_BYPASS=1.
        (
            "MCP-SCHEMA Cursor+Windsurf MCP config validation (advisory)",
            "ops_scripts/ci/check_mcp_config_schema.py --profile all",
        ),
        # NO-CURSOR-REFS — .cursor decommission anti-regression (W7): no tracked
        # .cursor/ files + no active .cursor/ path construction in live code.
        (
            "NO-CURSOR-REFS .cursor decommission anti-regression",
            "ops_scripts/ci/check_no_cursor_refs.py",
        ),
        # MCP-PARITY — canonical fleet parity across editor configs.
        (
            "MCP-PARITY Cursor vs Windsurf MCP editor parity",
            "ops_scripts/ci/check_mcp_editor_parity.py",
        ),
        # MCP-SCOPE0 — filesystem MCP locked to repo root (Constitutional Rule #0).
        # Bypass: MCP_CONFIG_SOVEREIGNTY_BYPASS=1
        (
            "MCP-SCOPE0 filesystem scope sovereignty (Rule #0)",
            "ops_scripts/ci/check_mcp_config_sovereignty.py",
        ),
        # DEFER — Deferred scope marker compliance (CI mode).
        # Scans all .claude/plans/*.md for prose indicating deferred work
        # without DEFERRED_SCOPE: marker. Baseline: 12 violations (advisory).
        # Advisory by default; fail-closed via DEFERRED_SCOPE_GATE_FAIL_CLOSED=1.
        # Bypass: DEFERRED_SCOPE_GATE_BYPASS=1.
        (
            "DEFER Deferred scope marker compliance (advisory baseline)",
            "ops_scripts/ci/check_deferred_scope_markers.py",
        ),
        # RULE-FMT — Rule frontmatter schema validation.
        # Validates .claude/rules/*.md YAML frontmatter against canonical schema.
        # Baseline: many rules lack proper frontmatter (advisory).
        # Advisory by default; fail-closed via RULE_FRONTMATTER_FAIL_CLOSED=1.
        # Bypass: RULE_FRONTMATTER_BYPASS=1.
        (
            "RULE-FMT Rule frontmatter schema (advisory baseline)",
            "ops_scripts/ci/check_rule_frontmatter_schema.py",
        ),
        # RULES1 — Rules filesystem integrity check.
        # Validates .claude/rules/*.md files for: frontmatter presence,
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
        # hook count thresholds, lifecycle stage thresholds, post_cascade growth,
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
            "MIRROR-H Cursor docs/archive/windsurf/legacy-tree mirror health (advisory)",
            "ops_scripts/ci/check_cursor_governance_mirror_health.py",
        ),
        (
            "WIND-DEL docs/archive/windsurf/legacy-tree deletion readiness report (advisory)",
            "ops_scripts/ci/check_windsurf_deletion_readiness.py",
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
        # CHECK-RG-FACT-VECTORS — apps_rg C0 dense lane (fact_vectors, BGE-M3 / 1024).
        # Preceded by SEED-RG-FV so contract_gates succeeds on fresh clones when chromadb
        # + sentence-transformers are installed. Bypass seed: APPS_RG_SEED_FACT_VECTORS_BYPASS=1.
        # Advisory by default; fail-closed via APPS_RG_FACT_VECTORS_FAIL_CLOSED=1.
        # Bypass: APPS_RG_FACT_VECTORS_BYPASS=1.
        (
            "SEED-RG-FV apps_rg fact_vectors Chroma seed (if missing)",
            "ops_scripts/ci/seed_apps_rg_fact_vectors_chroma.py",
            "SEED-RG-FV",
        ),
        (
            "CHECK-RG-FACT-VECTORS apps_rg fact_vectors readiness (advisory)",
            "ops_scripts/ci/check_apps_rg_fact_vectors_readiness.py",
            "CHECK-RG-FACT-VECTORS",
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
        # apps_qna and apps_rfp are EXCLUDED from pass/fail (DEFER_WITH_REASON disposition).
        # Advisory by default; fail-closed: NO_SHADOW_SPINE_FAIL_CLOSED=1.
        # Bypass: NO_SHADOW_SPINE_BYPASS=1.
        # Report: artifacts/ci/no_shadow_spine_gate.json.
        (
            "W5 no-shadow-spine one-spine enforcement (advisory)",
            "ops_scripts/ci/check_no_shadow_spine.py",
        ),
    ]

    # Isolated ``--gate`` filter matching CHECK-RG-FACT-VECTORS must still run SEED-RG-FV first,
    # otherwise RG-FV-1 fails on an empty canonical Chroma path.
    _g = getattr(args, "gate", None)
    if _g and "CHECK-RG-FACT-VECTORS" in str(_g) and "SEED-RG-FV" not in str(_g):
        print(
            "🔍 Running: SEED-RG-FV apps_rg fact_vectors Chroma seed (if missing) "
            "[prerequisite for filtered CHECK-RG-FACT-VECTORS] ...",
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
            "§26 Windsurf config schema purity",
            "ops_scripts/ci/check_windsurf_config_schema.py",
        ),
        # §31 — SSOT folder routing for NEW Python files. Pre-commit covers
        # commit-time staged-file checks; this aggregator entry ensures CI
        # workflows that stage files (e.g., during release branches or merge
        # queues) also see the gate. Pass-through when no staged additions.
        # Sibling Windsurf hook: .claude/governance/scripts/pre_write_gate.py.
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
        # the block to Cursor Agent at every turn. Advisory by default;
        # fail-closed via DEFERRED_PLAN_GUARD_FAIL_CLOSED=1.
        # RCA: 2026-05-10 notion-test-hardening-deferred-scope-a7b4c9.
        # Bypass: DEFERRED_PLAN_GUARD_BYPASS=1.
        ("AG-DEFER Deferred-scope plan guard marker parity (advisory)", "ops_scripts/ci/check_deferred_plan_guard_markers.py"),
        # NP-GUARD — Notion plan lifecycle Completed guard presence check.
        # Validates that wave_execution_state.py and _wave_lifecycle_helpers.py
        # contain the belt-and-suspenders guards preventing a Completed plan from
        # being flipped back to In Progress by a spurious wave_start marker.
        # Advisory by default; fail-closed via NP_LIFECYCLE_GUARD_FAIL_CLOSED=1.
        # Bypass: NP_LIFECYCLE_GUARD_BYPASS=1.
        # Plan: notion-plan-status-hardening-e5f3a1 (W3.P1).
        ("NP-GUARD Notion plan lifecycle Completed guard (advisory)", "ops_scripts/ci/check_notion_plan_lifecycle_guard.py"),
        # RG-JD0 — apps_rg JD resolution / default JD SSOT must not appear under agentic_core/.
        ("RG-JD0 agentic_core JD SSOT boundary", "ops_scripts/ci/check_agentic_core_no_apps_rg_jd_ssot.py"),
        # RG-RESUME0 — apps_rg resume resolution / default resume SSOT must not appear under agentic_core/.
        ("RG-RESUME0 agentic_core resume SSOT boundary", "ops_scripts/ci/check_agentic_core_no_apps_rg_resume_ssot.py"),
        # HEAL-SSOT — L2 heal-confidence band bounds must resolve via routing_thresholds_ssot;
        # forbid legacy HEALING_CONFIDENCE_X/Y path_constants imports in prod code (tests exempt);
        # docs + .env.example must not advertise SOVEREIGN_*_CONFIDENCE; env_key_consumer_map
        # cites HEALING_CONFIDENCE_HIGH/MEDIUM. Bypass: HEAL_ROUTING_SSOT_BYPASS=1.
        ("HEAL-SSOT heal confidence routing thresholds (fail-closed)", "ops_scripts/ci/check_heal_routing_threshold_ssot.py"),
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
