"""RG-SPEARMAN-L6-PLACEMENT: protect layer and write sovereignty."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci._apps_rg_spearman_gate_common import finish  # noqa: E402

L6_ENGINE = REPO_ROOT / "agentic_core/L6_observability/shadow_eval/spearman_calibration.py"
PIPELINE = REPO_ROOT / "agentic_core/L6_observability/shadow_eval/pipeline.py"


def _imports_and_calls(path: Path) -> tuple[set[str], set[str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: set[str] = set()
    calls: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module or "")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.add(node.func.attr)
    return imports, calls


def validate_placement() -> list[str]:
    errors: list[str] = []
    if not L6_ENGINE.is_file():
        return ["Spearman engine is not under L6 shadow evaluation"]
    imports, _ = _imports_and_calls(L6_ENGINE)
    if any("L4_state" in name or ".uwg" in name for name in imports):
        errors.append("L6 Spearman engine imports an L4/UWG write surface")

    forbidden_calls = {"compute_spearman_calibration", "spearmanr", "_load_rows"}
    for path in (REPO_ROOT / "apps_rg/runtime").rglob("*.py"):
        runtime_imports, calls = _imports_and_calls(path)
        if any(name == "scipy" or name.startswith("scipy.") for name in runtime_imports):
            errors.append(f"Exit/runtime imports scipy in {path.relative_to(REPO_ROOT)}")
        if any("spearman_calibration" in name for name in runtime_imports):
            errors.append(f"Exit/runtime imports L6 calibration in {path.relative_to(REPO_ROOT)}")
        overlap = sorted(calls & forbidden_calls)
        if overlap:
            errors.append(
                f"Exit/runtime performs calibration calls in {path.relative_to(REPO_ROOT)}: "
                f"{','.join(overlap)}"
            )

    pipeline_text = PIPELINE.read_text(encoding="utf-8")
    g29_pos = pipeline_text.find("state.g29")
    commit_pos = pipeline_text.find("uwg_receipt_id, l4_digest = uwg_commit")
    if g29_pos < 0 or commit_pos < 0 or g29_pos > commit_pos:
        errors.append("G29 calibration check does not precede UWG promotion")
    if "agentic_core.L4_state" in pipeline_text:
        errors.append("L6 pipeline imports L4 directly")

    for root in (REPO_ROOT / "apps_rg/runtime", REPO_ROOT / "ops_scripts/calibration"):
        for path in root.rglob("*.py"):
            if "apps_rg.engines.judges" in path.read_text(encoding="utf-8"):
                errors.append(f"obsolete app-local judge import in {path.relative_to(REPO_ROOT)}")
    return errors


def main() -> int:
    return finish(
        "RG-SPEARMAN-L6-PLACEMENT",
        validate_placement(),
        fail_closed_env="APPS_RG_SPEARMAN_L6_PLACEMENT_FAIL_CLOSED",
    )


if __name__ == "__main__":
    raise SystemExit(main())
