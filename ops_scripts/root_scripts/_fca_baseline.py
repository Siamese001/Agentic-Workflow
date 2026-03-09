"""PHASE 0 WAVE 0.1: FCA baseline reproduction — save artifact for diffing."""

import json
import logging
import sys
from collections import defaultdict
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, get_validated_project_root

ROOT = get_validated_project_root()
sys.path.insert(0, str(ROOT))

from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
    FileClassificationAgent,
    get_python_files_fast,
)

# Patch missing SERVICE key
fca = FileClassificationAgent(project_root=ROOT, dry_run=True, validate_only=True, verbose=True)
fca.stats["violations"] = defaultdict(int, fca.stats["violations"])


# Capture logger
class Collector(logging.Handler):
    def __init__(self):
        super().__init__()
        self.lines = []

    def emit(self, record):
        self.lines.append(self.format(record))


col = Collector()
col.setFormatter(logging.Formatter("%(message)s"))
logging.getLogger("agentic_core.L5_safety.reasoning.FileClassificationAgent").addHandler(col)
logging.getLogger("agentic_core.L5_safety.reasoning.FileClassificationAgent").setLevel(logging.DEBUG)

# Redirect stdout during audit
real = sys.stdout
sys.stdout = sys.stderr
scan_root = ROOT / AGENTIC_CORE_DIR
exit_code = fca._orchestrate_audit(scan_root)
sys.stdout = real

# Layer alignment scan
all_py = get_python_files_fast(scan_root)
layer_violations = []
for p in all_py:
    try:
        v = fca.validate_layer_alignment(p)
        if v:
            v["file"] = str(Path(v["file"]).relative_to(ROOT)).replace("\\", "/")
            layer_violations.append(v)
    except Exception:
        pass

# Tag parse
findings_by_tag = defaultdict(list)
for line in col.lines:
    for tag in [
        "DETECT",
        "TERRITORY",
        "COMPOUND_SUFFIX",
        "FORBIDDEN",
        "PASSIVE_AGENT_NAMING",
        "COGNITIVE_CONTAMINATION",
        "FAKE_CONFIG",
        "BASE_AGENTS_PURITY",
        "UTILS_PURITY",
        "DOMAIN_ROOT_PURITY",
        "FOLDER_SUFFIX",
        "FOLDER_PURITY",
        "CROSS_DOMAIN",
        "EPHEMERAL",
        "CROSS_LAYER",
        "DUAL-TAG",
        "MISPLACED-TEST",
        "LAYER_PURITY",
        "DUPLICATE",
    ]:
        if f"[{tag}]" in line:
            findings_by_tag[tag].append(line.strip())
            break

violation_counts = defaultdict(int)
for v in layer_violations:
    violation_counts[v.get("violation", "UNKNOWN")] += 1

result = {
    "files_analyzed": fca.stats["analyzed"],
    "compliant": fca.stats["compliant"],
    "audit_findings": sum(len(v) for v in findings_by_tag.values()),
    "layer_violations": len(layer_violations),
    "findings_by_tag": {k: len(v) for k, v in findings_by_tag.items()},
    "layer_violation_counts": dict(violation_counts),
    "violation_type_counts": {k: v for k, v in fca.stats["violations"].items() if v > 0},
}

out_path = ROOT / "artifacts" / "fca_safety_gates" / "baseline_counts.json"
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w") as f:
    json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))
