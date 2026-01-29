"""Phase 31b Horizontal Boundary Dry Run Report."""

import sys

sys.path.insert(0, ".")
from collections import defaultdict
from pathlib import Path

from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import ArchitectureGovernorAgent

agent = ArchitectureGovernorAgent(project_root=Path("."))
result3 = agent.detect_horizontal_violations(target_layer="L3_orchestration")
if result3["violations"]:
    pairs3 = defaultdict(list)
    for v in result3["violations"]:
        key = f"{v['source_domain']} -> {v['target_domain']}"
        pairs3[key].append(v["file_name"])
    for pair, files in sorted(pairs3.items(), key=lambda x: -len(x[1])):
        for f in files[:3]:
            pass
result5 = agent.detect_horizontal_violations(target_layer="L5_safety")
if result5["violations"]:
    pairs5 = defaultdict(list)
    for v in result5["violations"]:
        key = f"{v['source_domain']} -> {v['target_domain']}"
        pairs5[key].append(v["file_name"])
    for pair, files in sorted(pairs5.items(), key=lambda x: -len(x[1]))[:10]:
        for f in files[:3]:
            pass
        if len(files) > 3:
            pass
