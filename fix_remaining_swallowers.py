import pathlib
import re

ROOT = pathlib.Path(".")

files = [
    "tests/unit/apps_rg/engines/utils/test_rg_healing_orchestrator.py",
    "tests/unit/apps_rg/engines/utils/test_rg_resume_orchestrator.py",
    "tests/unit/apps_rg/engines/utils/test_rg_strategic_planner_agent.py",
    "tests/unit/apps_rg/engines/utils/test_rg_template_optimizer_agent.py",
    "tests/unit/apps_rg/shared/tools/test_dispatch_resume_tools_agent.py",
    "tests/unit/apps_rg/shared/tools/test_gap_closure_architect_agent.py",
]

# Pattern: try:\n<import block>\n            except (...): # guardian: allow-silent-swallower\n                pass
PATTERN = re.compile(
    r"            try:\n"
    r"(                from [^\n]+\n(?:                    [^\n]+\n)*                \)\n)"
    r"            except \(ImportError, NameError, AttributeError\):  # guardian: allow-silent-swallower\n"
    r"                pass\n",
    re.MULTILINE,
)

for fp in files:
    p = ROOT / fp
    if not p.exists():
        print(f"NOT FOUND: {fp}")
        continue
    content = p.read_text(encoding="utf-8")
    new_content = PATTERN.sub(lambda m: m.group(1), content)
    if new_content != content:
        p.write_text(new_content, encoding="utf-8")
        print(f"Fixed: {fp}")
    else:
        print(f"Pattern not matched in {fp}, showing context:")
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if "guardian: allow-silent-swallower" in line:
                for j in range(max(0, i - 5), min(len(lines), i + 3)):
                    print(f"  {j+1}: {lines[j]!r}")
