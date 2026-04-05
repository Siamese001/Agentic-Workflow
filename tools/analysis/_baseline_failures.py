"""Capture pre-change and post-change failure lists to confirm zero regressions."""

import subprocess
import sys

TEST_PATHS = [
    "tests/unit/agentic_core/L2_execution/healers/",
    "tests/unit_min_deps/test_dispatcher_emits_proposal_only.py",
    "tests/unit_min_deps/test_heal_bug_regressions.py",
]


def get_failures(label: str) -> list[str]:
    r = subprocess.run(
        [sys.executable, "-m", "pytest"] + TEST_PATHS + ["-q", "--tb=no", "--no-header"],
        capture_output=True,
        text=True,
        cwd=r"C:\Git\Agentic-Workflow",
    )
    fails = [l for l in r.stdout.splitlines() if l.startswith("FAILED")]
    print(f"\n{label}: {len(fails)} failures")
    for f in sorted(fails):
        print(f"  {f}")
    return sorted(fails)


# --- baseline (pre-change: stash already applied above) ---
pre = get_failures("PRE-CHANGE")

# --- restore changes ---
r = subprocess.run(
    ["git", "stash", "pop"],
    capture_output=True,
    text=True,
    cwd=r"C:\Git\Agentic-Workflow",
)
print("\ngit stash pop:", r.stdout.strip()[:120])

# --- post-change ---
post = get_failures("POST-CHANGE")

# --- diff ---
new_failures = set(post) - set(pre)
fixed = set(pre) - set(post)

print("\n=== REGRESSION ANALYSIS ===")
print(f"  Pre:  {len(pre)} failures")
print(f"  Post: {len(post)} failures")
if new_failures:
    print(f"  NEW REGRESSIONS ({len(new_failures)}):")
    for f in sorted(new_failures):
        print(f"    *** {f}")
else:
    print("  NEW REGRESSIONS: 0  ✓")
if fixed:
    print(f"  FIXED ({len(fixed)}):")
    for f in sorted(fixed):
        print(f"    +++ {f}")
