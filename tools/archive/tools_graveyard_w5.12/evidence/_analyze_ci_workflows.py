"""Analyse all .github/workflows/*.yml files for conflicts, redundancies, and stray CIs."""

import re
from pathlib import Path

WF_DIR = Path(r"c:\Git\Agentic-Workflow\.github\workflows")

workflows = {}
for f in sorted(WF_DIR.glob("*.yml")):
    workflows[f.name] = f.read_text(encoding="utf-8")

print("=" * 80)
print(f"TOTAL WORKFLOWS: {len(workflows)}")
print("=" * 80)

rows = []
for fname, content in workflows.items():
    name_m = re.search(r"^name:\s*(.+)", content, re.M)
    wf_name = name_m.group(1).strip() if name_m else "?"

    # triggers
    triggers = set(re.findall(r"^\s{2}(push|pull_request|schedule|workflow_dispatch)", content, re.M))

    # branches targeted
    branch_lists = re.findall(r"branches:\s*\[([^\]]+)\]", content)
    branch_items = re.findall(r"branches:\s*\n((?:\s+-\s+\S+\n)+)", content)
    all_branches = set()
    for bl in branch_lists:
        for b in bl.split(","):
            all_branches.add(b.strip().strip('"').strip("'"))
    for bi in branch_items:
        for b in re.findall(r"-\s+(\S+)", bi):
            all_branches.add(b.strip('"').strip("'"))
    # paths filters
    has_paths_filter = bool(re.search(r"^\s+paths:", content, re.M))

    # Python versions
    py_versions = set(re.findall(r"python-version[:\s]+[\"']([\d.]+)[\"']", content))

    # actions versions
    checkout_v = set(re.findall(r"actions/checkout@(v\d+)", content))
    setup_py_v = set(re.findall(r"actions/setup-python@(v\d+)", content))

    # what does it run?
    pytest_calls = bool(re.search(r"pytest", content))
    pip_install = bool(re.search(r"pip install", content))
    ops_scripts = re.findall(r"ops_scripts/ci/(\S+\.py)", content)
    guardian_calls = bool(re.search(r"guardian", content, re.I))

    rows.append(
        {
            "file": fname,
            "name": wf_name,
            "triggers": triggers,
            "branches": all_branches,
            "paths_filter": has_paths_filter,
            "py_versions": py_versions,
            "checkout_v": checkout_v,
            "setup_py_v": setup_py_v,
            "pytest": pytest_calls,
            "ops_scripts": ops_scripts,
            "guardian": guardian_calls,
        },
    )

# ── Print summary table ──────────────────────────────────────────────────────
print(f"\n{'FILE':<46} {'TRIGGERS':<25} {'BRANCHES':<35} {'PY':<8} {'PATH_FILTER'}")
print("-" * 130)
for r in rows:
    print(
        f"{r['file']:<46} "
        f"{str(r['triggers']):<25} "
        f"{str(sorted(r['branches'])):<35} "
        f"{str(sorted(r['py_versions'])):<8} "
        f"{'YES' if r['paths_filter'] else 'no'}",
    )

# ── Detect: old actions versions ────────────────────────────────────────────
print("\n\n=== STALE ACTION VERSIONS ===")
for r in rows:
    issues = []
    if "v3" in r["checkout_v"]:
        issues.append("checkout@v3 (should be v4)")
    if "v4" in r["setup_py_v"]:
        issues.append("setup-python@v4 (should be v5)")
    if "v3" in r["setup_py_v"]:
        issues.append("setup-python@v3 (should be v5)")
    if "3.11" in r["py_versions"] and "3.12" not in r["py_versions"]:
        issues.append("Python 3.11 only (repo uses 3.12)")
    if issues:
        print(f"  {r['file']}: {', '.join(issues)}")

# ── Detect: branch scope mismatches ─────────────────────────────────────────
print("\n\n=== BRANCH SCOPE ISSUES (not targeting ADG_v7 / ** ) ===")
for r in rows:
    branches = r["branches"]
    # Workflows targeting only main/develop are stale if ADG_v7 is the active branch
    if branches and not any(b in ("**", "ADG_v7") for b in branches):
        print(f"  {r['file']}: targets {sorted(branches)} — misses ADG_v7")

# ── Detect: redundant SSOT checks ───────────────────────────────────────────
ssot_wfs = [r for r in rows if "ssot" in r["file"].lower() or "ssot" in r["name"].lower()]
print(f"\n\n=== SSOT WORKFLOWS ({len(ssot_wfs)}) — potential redundancy ===")
for r in ssot_wfs:
    print(f"  {r['file']}: {r['name']}")
    print(f"    triggers={r['triggers']} branches={sorted(r['branches'])} paths={r['paths_filter']}")

# ── Detect: sovereignty/layer overlap ───────────────────────────────────────
sov_wfs = [
    r
    for r in rows
    if any(
        k in r["file"].lower() or k in r["name"].lower()
        for k in ("sovereignty", "layer", "scope", "structure")
    )
]
print(f"\n\n=== SOVEREIGNTY/LAYER WORKFLOWS ({len(sov_wfs)}) — potential overlap ===")
for r in sov_wfs:
    print(f"  {r['file']}: {r['name']}")
    print(f"    triggers={r['triggers']} branches={sorted(r['branches'])} paths={r['paths_filter']}")

# ── Detect: workflows running on ALL branches (**) with no path filter ───────
print("\n\n=== BROAD TRIGGER (all branches, no path filter) — noise risk ===")
for r in rows:
    if "**" in r["branches"] and not r["paths_filter"]:
        print(f"  {r['file']}: {r['name']}")

# ── Ops scripts overlap ──────────────────────────────────────────────────────
print("\n\n=== OPS SCRIPTS CALLED ===")
all_ops = {}
for r in rows:
    for s in r["ops_scripts"]:
        all_ops.setdefault(s, []).append(r["file"])
for script, callers in sorted(all_ops.items()):
    marker = " <-- CALLED BY MULTIPLE" if len(callers) > 1 else ""
    print(f"  {script}: {callers}{marker}")

print("\nDone.")
