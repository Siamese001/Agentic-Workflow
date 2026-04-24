"""Scan actual consumer usage for the 9 W3.3/W4.2/W5 authorized agents."""
from __future__ import annotations

import json
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[2]

# (class_name, module_path, util_path, expected_consumer_files)
AGENTS = [
    ("SubAtomicAgent", "agentic_core.L3_orchestration.reasoning.SubAtomicAgent",
     "agentic_core.L3_orchestration.utils.subatomic_agent_util"),
    ("CodeJanitorAgent", "agentic_core.L5_safety.reasoning.CodeJanitorAgent",
     "agentic_core.L5_safety.utils.code_janitor_util"),
    ("CodeDetectorAgent", "agentic_core.L5_safety.reasoning.CodeDetectorAgent",
     "agentic_core.L5_safety.utils.code_detector_util"),
    ("CodeValidatorAgent", "agentic_core.L5_safety.reasoning.CodeValidatorAgent",
     "agentic_core.L5_safety.utils.code_validator_util"),
    ("CodeEnforcerAgent", "agentic_core.L5_safety.reasoning.CodeEnforcerAgent",
     "agentic_core.L5_safety.utils.code_enforcer_util"),
    ("SSOTFolderCleanupAgent", "agentic_core.L0_routing.reasoning.SSOTFolderCleanupAgent",
     "agentic_core.L0_routing.utils.ssot_folder_cleanup_util"),
    ("RootCustomsAgent", "agentic_core.L0_routing.reasoning.RootCustomsAgent",
     "agentic_core.L0_routing.utils.root_customs_util"),
    ("LocationHealerAgent", "agentic_core.L5_safety.reasoning.LocationHealerAgent",
     "UnifiedAgent"),
    ("GovernanceAgent", "agentic_core.L5_safety.reasoning.GovernanceAgent",
     "direct-path"),
]

EXCLUDE_DIRS = {"archives", ".git", ".venv", "__pycache__"}
EXCLUDE_PATH_PARTS = ("tools/archive", "tools\\archive", "_archived_adg_audits")

out = {}
for class_name, mod_path, util_path in AGENTS:
    agent_file = mod_path.replace(".", "/") + ".py"
    mod_re = re.compile(
        rf"(?:from\s+{re.escape(mod_path)}\s+import|import\s+{re.escape(mod_path)}\b)"
    )
    results = []
    for py in REPO.rglob("*.py"):
        try:
            parts = py.relative_to(REPO).parts
        except ValueError:
            continue
        if parts[0] in EXCLUDE_DIRS:
            continue
        rp = py.relative_to(REPO).as_posix()
        if any(p in rp for p in EXCLUDE_PATH_PARTS):
            continue
        if rp == agent_file:
            continue
        try:
            text = py.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if mod_re.search(text):
            # Capture each line that references the class name
            lines = []
            for i, ln in enumerate(text.splitlines(), start=1):
                if class_name in ln:
                    lines.append((i, ln.rstrip()[:200]))
            results.append({"file": rp, "refs": lines[:20]})
    out[class_name] = {"util": util_path, "consumer_count": len(results), "consumers": results}

outfile = REPO / "artifacts" / "agent_deprecation" / "mw_usage_scan.json"
outfile.write_text(json.dumps(out, indent=2), encoding="utf-8")
print(f"[ok] wrote {outfile}")

for cls, d in out.items():
    print(f'\n=== {cls} ({d["consumer_count"]} consumer files) ===')
    for c in d["consumers"]:
        print(f'  file: {c["file"]}')
        for ln, text in c["refs"][:3]:
            print(f'    L{ln}: {text[:140]}')
