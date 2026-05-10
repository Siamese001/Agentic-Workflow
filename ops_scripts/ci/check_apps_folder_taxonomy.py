"""ADR-082 apps folder taxonomy CI gate (T7r).

Scans every ``apps_*/`` tree at repo root for:
  1. Forbidden sub-folder names (per ADR-082 §3 / canonical spec §3)
  2. Missing mandatory doc-set files (per spec §4)
  3. Forbidden root-level ``_*.py`` straggler files

Exemptions:
  - Files matching the ADR-082 compat-shim pattern are skipped during the
    2-week sunset window (2026-05-03 → 2026-05-17). A file qualifies as a
    compat shim if it cites ``ADR-082`` AND contains one of:
      * ``sys.modules[__name__]`` (package-redirect pattern)
      * ``DeprecationWarning`` (self-contained shim pattern)
      * the literal string ``Compat shim``

Bypass: set env ``APPS_TAXONOMY_BYPASS=1`` to emit a WARNING and exit 0.

Exit codes:
  0 — no violations
  1 — violations found (stdout = summary; stderr = details)

SSOT: see ``docs/architecture/adr/ADR-082-apps-folder-taxonomy.md`` and
``docs/architecture/apps-folder-taxonomy.md``.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

APPS = [
    "apps_eval",
    "apps_exec",
    "apps_lic",
    "apps_qna",
    "apps_research",
    "apps_rfp",
    "apps_rg",
    "apps_shared",
    "apps_underwriting_ai",
]

# §3 of the canonical spec — forbidden folder names under apps_*/
FORBIDDEN_ROOT_FOLDERS = {
    # ADR-082 §3.3 explicit renames
    "L1_cognition", "L2_execution", "L3_orchestration",
    "L4_state", "L5_policy", "L6_observability", "L0_routing",
    "outreach_engine",
    "persistence",
    "observability",
    "policy",          # code → validators/policy; data → config/policy
    "runtime",         # → services/runtime
    "builder",         # → engines/builder
    "router",          # → engines/router
    "templates",       # → data/templates
    "ingestion",       # → engines/ingestion
    "parsers",         # → engines/parsers
    "examples",        # → docs/examples/
    "adapters",        # → integrations/adapters
    "data_adapters",   # → integrations/data_adapters
    "mixins",          # → utils/mixins
    "orchestration",   # → reasoning/orchestration
    "prompts",         # → data/prompts
    "proof",           # → validators/proof
    "enforcement",     # → validators/enforcement
    "_compat",         # DELETE if empty
    "tests",           # FORBIDDEN: app-local tests/ consolidated into 3-surface canonical layout
                       #   unit      → tests/unit/<app>/
                       #   integration → tests/<app>/
                       #   contract  → tests/_apps_contract/
                       # See plan apps-test-surface-consolidation-11acd9-v2
}

# §4 — mandatory doc-set at app root
MANDATORY_DOCS = {
    "README.md",
    "RUNBOOK.md",
    "SLO.md",
    "SVP_ENGINEERING_REVIEW.md",
    "TECHNICAL_SPEC.md",
    "TEST_STRATEGY.md",
    "spine_manifest.yaml",
}

# Apps that legitimately omit engines/ and outputs/ (library-only)
LIBRARY_ONLY_APPS = {"apps_qna", "apps_shared"}

# Apps that process external/untrusted input → THREAT_MODEL.md required
EXTERNAL_INPUT_APPS = {"apps_lic", "apps_underwriting_ai", "apps_rg", "apps_research"}

# Interview-pack apps → PATHOLOGY_TAXONOMY.md required
INTERVIEW_PACK_APPS = {"apps_qna"}


def _is_adr082_compat_shim(path: Path) -> bool:
    """Return True if file is an ADR-082 compat shim (exempt during sunset window).

    A file qualifies if it cites ``ADR-082`` AND contains any of:
      - ``sys.modules[__name__]`` (package-redirect)
      - ``DeprecationWarning`` (self-contained shim)
      - literal ``Compat shim`` string
    """
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    if "ADR-082" not in src:
        return False
    return (
        "sys.modules[__name__]" in src
        or "DeprecationWarning" in src
        or "Compat shim" in src
        or "compat shim" in src
    )


def check_app(app: str) -> list[str]:
    """Return list of violation strings for the given app (empty = clean)."""
    violations: list[str] = []
    app_path = REPO_ROOT / app
    if not app_path.is_dir():
        violations.append(f"{app}: app root does not exist")
        return violations

    # 1. Forbidden sub-folders (only at app root; nested OK when canonical)
    for child in app_path.iterdir():
        if not child.is_dir():
            continue
        if child.name in FORBIDDEN_ROOT_FOLDERS:
            # Is this folder exempt as ADR-082 compat shim?
            init_py = child / "__init__.py"
            if init_py.is_file() and _is_adr082_compat_shim(init_py):
                continue  # compat shim exemption
            violations.append(
                f"{app}/{child.name}/: forbidden folder name (ADR-082 §3). "
                f"See docs/architecture/apps-folder-taxonomy.md for canonical target."
            )

    # 2. Mandatory doc-set
    for doc in MANDATORY_DOCS:
        if not (app_path / doc).is_file():
            violations.append(f"{app}/{doc}: missing mandatory doc (ADR-082 §4)")

    # 3. Conditional docs
    if app in EXTERNAL_INPUT_APPS and not (app_path / "THREAT_MODEL.md").is_file():
        violations.append(f"{app}/THREAT_MODEL.md: required for external-input apps")
    if app in INTERVIEW_PACK_APPS and not (app_path / "PATHOLOGY_TAXONOMY.md").is_file():
        violations.append(f"{app}/PATHOLOGY_TAXONOMY.md: required for interview-pack apps")

    # 4. Root-level _*.py stragglers
    for child in app_path.iterdir():
        if not child.is_file() or child.suffix != ".py":
            continue
        if child.name.startswith("_") and child.name != "__init__.py" and child.name != "__main__.py":
            if _is_adr082_compat_shim(child):
                continue
            violations.append(
                f"{app}/{child.name}: root-level _*.py straggler forbidden "
                f"(ADR-082 §2.4)"
            )

    return violations


def main() -> int:
    if os.environ.get("APPS_TAXONOMY_BYPASS") == "1":
        print(
            "WARNING: APPS_TAXONOMY_BYPASS=1 — skipping ADR-082 taxonomy check.",
            file=sys.stderr,
        )
        return 0

    all_violations: dict[str, list[str]] = {}
    for app in APPS:
        vios = check_app(app)
        if vios:
            all_violations[app] = vios

    if not all_violations:
        print("ADR-082 taxonomy check: OK (no violations)")
        return 0

    total = sum(len(v) for v in all_violations.values())
    print(
        f"ADR-082 taxonomy check: FAIL — {total} violation(s) across {len(all_violations)} app(s)",
        file=sys.stderr,
    )
    for app, vios in sorted(all_violations.items()):
        print(f"\n[{app}]", file=sys.stderr)
        for v in vios:
            print(f"  - {v}", file=sys.stderr)
    print(
        "\nSee docs/architecture/adr/ADR-082-apps-folder-taxonomy.md for remediation.",
        file=sys.stderr,
    )
    print(
        "Bypass (not recommended): APPS_TAXONOMY_BYPASS=1",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
