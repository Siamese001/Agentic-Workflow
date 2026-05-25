"""L6 reorg plan E2E closeout verifier — exit 0 only when all checks pass."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _run(cmd: list[str], env: dict[str, str] | None = None) -> tuple[int, str]:
    merged = {**os.environ, **(env or {})}
    p = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        env=merged,
        timeout=600,
    )
    out = (p.stdout or "") + (p.stderr or "")
    return p.returncode, out.strip()[-2000:]


def main() -> int:
    failures: list[str] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name}" + (f" — {detail}" if detail and not ok else ""))
        if not ok:
            failures.append(f"{name}: {detail}")

    receipts = [
        "docs/reports/cursor/l6_w0_architecture_decision_20260525.md",
        "docs/reports/cursor/l6_w1_gate_receipt_20260525.json",
        "docs/reports/cursor/l6_w2_doc_receipt_20260525.md",
        "docs/reports/cursor/l6_w4_passive_drift_20260525.md",
        "docs/reports/cursor/l6_w5_wave_receipt_20260525.md",
        "docs/reports/cursor/l6_w5_post_rename_cert_20260525.json",
        "docs/reports/cursor/l6_w6_gravity_receipt_20260525.json",
        "config/architectural_exceptions.yaml",
        "docs/architecture/adr/ADR-085-l6-observability-dependency-hygiene.md",
    ]
    for r in receipts:
        check(f"artifact:{r}", (REPO / r).is_file())

    check("no_root_system_learning", not (REPO / "system_learning").exists())
    check("canonical_L6_system_learning", (REPO / "agentic_core/L6_system_learning").is_dir())

    w1 = json.loads((REPO / "docs/reports/cursor/l6_w1_gate_receipt_20260525.json").read_text())
    check("w1_superseded_by_w5_cert", "superseded_by" in w1)

    w5 = json.loads((REPO / "docs/reports/cursor/l6_w5_post_rename_cert_20260525.json").read_text())
    check("w5_post_rename_proof_authority", w5.get("proof_authority") == "final_w1_post_rename")
    check("w5_l6_tag_exit_0", w5.get("l6_tag_exit_code") == 0)
    check("w5_l6_obs_exit_0", w5.get("l6_obs_exit_code") == 0)

    w6 = json.loads((REPO / "docs/reports/cursor/l6_w6_gravity_receipt_20260525.json").read_text())
    check("w6_burndown_documented", w6.get("burndown_status") == "documented_over_threshold")

    legacy: list[str] = []
    skip_parts = ("artifacts/archives", "artifacts\\archives", "tests/", "tests\\", "tools/_oneoff")
    for py in REPO.rglob("*.py"):
        ps = py.as_posix()
        if any(part in ps for part in skip_parts):
            continue
        try:
            for i, line in enumerate(py.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if line.strip().startswith("#"):
                    continue
                if "from system_learning" in line or "import system_learning" in line:
                    legacy.append(f"{ps}:{i}")
        except OSError:
            continue
    check("no_live_legacy_system_learning_imports", not legacy, "; ".join(legacy[:8]))

    code, out = _run(
        [sys.executable, "ops_scripts/ci/check_l6_layer_tag_consistency.py"],
        {"L6_LAYER_TAG_FAIL_CLOSED": "1"},
    )
    check("gate_l6_layer_tag", code == 0, out[-400:])

    code, out = _run(
        [sys.executable, "ops_scripts/ci/check_l6_observer_law.py"],
        {"L6_OBSERVER_LAW_FAIL_CLOSED": "1"},
    )
    check("gate_l6_observer_law", code == 0, out[-400:])

    code, out = _run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/unit/system_learning/test_l6_layer_markers.py",
            "tests/unit/agentic_core/L6_system_learning/",
            "tests/unit/ops_scripts/ci/test_check_l6_layer_tag_consistency.py",
            "tests/unit/ops_scripts/ci/test_check_l6_observer_law.py",
            "-q",
            "-o",
            "addopts=",
        ],
        {"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"},
    )
    check("pytest_l6_suite", code == 0, out[-400:])

    # Import smoke: canonical package subpackages
    code, out = _run(
        [
            sys.executable,
            "-c",
            "import importlib\npkgs=['engines','stores','types','runtime_adg','ports','pipelines']\n"
            "for p in pkgs:\n"
            " importlib.import_module('agentic_core.L6_system_learning.'+p)\n"
            "print('import_smoke_ok', len(pkgs))",
        ],
    )
    check("import_smoke_L6_subpackages", code == 0, out[-400:])

    print("---")
    if failures:
        print(f"E2E_CLOSEOUT: FAIL ({len(failures)} checks)")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("E2E_CLOSEOUT: PASS (all checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
