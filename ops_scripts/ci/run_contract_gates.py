#!/usr/bin/env python3
"""
Contract Gates — Main CI Entrypoint

Runs all contract validation gates in deterministic order.
"""

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


# PRE-WRITE HOOKS INTEGRATION
def validate_pre_write_hooks():
    """Validate all pre-write hook skills."""
    skills_dir = ROOT / ".windsurf" / "skills"
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

    # Gate: AGENTS.md Quick Reference must document every server in mcp_config.json
    returncode, stdout, stderr = run_cmd(
        [sys.executable, str(_script("ops_scripts/ci/check_agents_mcp_coverage.py"))],
        cwd=ROOT,
    )
    if returncode != 0:
        print("❌ AGENTS.md MCP coverage check failed")
        print(stdout or stderr)
        return False
    print("✅ AGENTS.md MCP coverage validated")

    # Gate: every .windsurf/skills/<name>/SKILL.md must conform to Anthropic's
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

    return True


def main():
    """Run all contract gates in deterministic order."""

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

    # Gate: P0 two-pass (preflight + full ADG enforcement)
    print("\n[P0 TWO-PASS GATE]")
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

    # ==================================================================
    # Assurance P1 gate plane (plan assurance-p1-gates-ab4758)
    # Runtime trace, replay digest, and requirements crosswalk.
    # ==================================================================
    print("\n[ASSURANCE-P1 GATE PLANE]")
    assurance_gates = [
        ("§27 windsurf config schema purity", "ops_scripts/ci/check_windsurf_config_schema.py"),
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
        # Three-bucket OTEL view gates (plan: three-bucket-otel-view-5db409, ADR-074).
        # Both are advisory (Tier B) until the runtime store is populated and the
        # GenAI semconv migration completes. Strict mode envvars to flip:
        #   RUNTIME_PROOF_VIEW_STRICT=1
        #   GENAI_SEMCONV_STRICT=1
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
        ("3B6 ADG_CERTIFIED aggregate gate", "ops_scripts/ci/check_adg_certified.py"),
        # W6.P1 (plan apps-eval-harness-deferred-e4a1b7): apps_* eval-harness
        # parity gate. Advisory by default — flip fail-closed via
        # APP_DOMAIN_HARNESS_PARITY_FAIL_CLOSED=1 once calibrated.
        (
            "AEH1 apps_* eval-harness parity (advisory)",
            "ops_scripts/ci/check_app_domain_harness_parity.py",
        ),
        # NP1 — Plans DB mandatory AI Summary gate. Advisory by default;
        # flip fail-closed via NOTION_PLANS_AI_SUMMARY_FAIL_CLOSED=1.
        # Skips when NOTION_API_KEY / NOTION_TOKEN is unset (offline CI).
        # Rule: .windsurf/rules/notion-plans-taxonomy.md > Mandatory AI Summary.
        (
            "NP1 Notion Plans AI Summary (advisory)",
            "ops_scripts/ci/check_notion_plans_ai_summary.py",
        ),
        # NP2 -- Plans DB Status must use canonical option strings.
        # Advisory by default; fail-closed via NOTION_PLANS_STATUS_FAIL_CLOSED=1.
        # Skips when NOTION_API_KEY / NOTION_TOKEN unset (offline CI).
        # Rule: .windsurf/rules/notion-plans-taxonomy.md > CANONICAL Status option strings.
        (
            "NP2 Notion Plans Status drift (advisory)",
            "ops_scripts/ci/check_notion_plans_status_drift.py",
        ),
        # NP3 -- Backlog Items rows must have a Plan relation (true orphans ==0).
        # Advisory by default; fail-closed via BACKLOG_PLAN_LINKAGE_FAIL_CLOSED=1.
        # Orphan count confirmed 0 (2026-05-03, plan backlog-linkage-followup-c2e9f3).
        # Ready to promote: set BACKLOG_PLAN_LINKAGE_FAIL_CLOSED=1 to enforce.
        # Skips when NOTION_API_KEY / NOTION_TOKEN unset (offline CI).
        # Rule: .windsurf/rules/notion-backlog-plan-linkage.md
        (
            "NP3 Notion Backlog plan linkage (advisory)",
            "ops_scripts/ci/check_notion_backlog_plan_linkage.py",
        ),
        # PR1 — Plan–Notion registration freshness (Constitutional §36).
        # Advisory by default; flip fail-closed via
        # PLAN_REGISTRATION_FAIL_CLOSED=1. Offline-safe: SKIPs when no
        # token and no local cache. Rule:
        # .windsurf/rules/plan-registration-enforcement.md.
        (
            "PR1 Plan–Notion Registration (advisory)",
            "ops_scripts/ci/check_plan_registration_freshness.py",
        ),
        # APPS-DOM runtime harness fixture freshness. Fails when
        # artifacts/apps_otel_traces or sibling harness fixture dirs contain
        # a fixture older than APPS_DOM_FIXTURE_FRESHNESS_HOURS (default 168h).
        # Skips when fixture dirs absent (first-run tolerant).
        # Bypass: APPS_DOM_FIXTURE_FRESHNESS_BYPASS=1. Plan:
        # .windsurf/plans/apps-dom-real-evidence-enhancement-c7f4d8.md W4.
        (
            "AD1 APPS-DOM harness fixture freshness",
            "ops_scripts/ci/check_apps_dom_fixture_freshness.py",
        ),
    ]
    for label, script in assurance_gates:
        if not (ROOT / script).is_file():
            # Optional gate not yet shipped — skip without blocking.
            print(f"⚠️  {label}: script missing ({script}) — skipped")
            continue
        returncode, stdout, stderr = run_cmd([sys.executable, str(_script(script))], cwd=ROOT)
        if returncode != 0:
            print(f"❌ {label} failed (exit={returncode})")
            if stdout:
                print(stdout)
            if stderr:
                print(stderr, file=sys.stderr)
            sys.exit(1)
        else:
            print(f"✅ {label} passed")

    # ==================================================================
    # Wiring-CI gate plane (plan adg-wiring-ci-hardening-7a5d84)
    # Exit 1 on any failure. Ratchet gates pass when count <= baseline.
    # ==================================================================
    print("\n[WIRING-CI GATE PLANE]")
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
        # Sibling Windsurf hook: .windsurf/scripts/pre_write_gate.py.
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
            "scripts/verify_control_surface_separation.py",
        ),
    ]
    for label, script in wiring_gates:
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
