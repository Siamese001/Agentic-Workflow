"""One-shot script: add strict=True to all xfail decorators lacking it."""

import pathlib
import re
import sys

FILES = [
    "tests/system_learning/test_activation_gate_w4f.py",
    "tests/system_learning/test_policy_recommendation_w4d.py",
    "tests/system_learning/test_retrieval_profile_proposal_w4e.py",
    "tests/system_learning/test_shadow_drift_w4c.py",
    "tests/system_learning/test_shadow_embedder_w4b.py",
    "tests/system_learning/test_w5_replay_engine.py",
]

ROOT = pathlib.Path(__file__).resolve().parents[2]


def fix_xfail(src: str) -> str:
    # Pattern: @pytest.mark.xfail with call args but no strict=True
    def _add_strict(m: re.Match) -> str:
        inner = m.group(1)
        if "strict" in inner:
            return m.group(0)  # already has strict
        if inner.strip():
            return f"@pytest.mark.xfail({inner}, strict=True)"
        return "@pytest.mark.xfail(strict=True)"

    # First handle: @pytest.mark.xfail(...)
    fixed = re.sub(r"@pytest\.mark\.xfail\(([^)]*)\)", _add_strict, src)
    # Then handle bare: @pytest.mark.xfail  (no parens)
    fixed = re.sub(
        r"@pytest\.mark\.xfail\b(?!\s*\()",
        '@pytest.mark.xfail(strict=True, reason="linked_issue: known_defect")',
        fixed,
    )
    return fixed


changed = 0
for rel in FILES:
    p = ROOT / rel
    if not p.exists():
        print(f"MISSING: {rel}")
        continue
    src = p.read_text(encoding="utf-8")
    fixed = fix_xfail(src)
    if fixed != src:
        p.write_text(fixed, encoding="utf-8")
        print(f"Fixed: {rel}")
        changed += 1
    else:
        print(f"No change: {rel}")

print(f"\n{changed} file(s) updated.")
sys.exit(0)
