"""
Safely fix the no-network-calls test pattern in agent test files.

Original pattern (try/except ImportError swallower inside with patch):
    with patch("requests.get", ...), patch("requests.post", ...):
        try:
            from apps_rg.X import Y  # noqa: F401
        except (ImportError, NameError, AttributeError):  # guardian: allow-silent-swallower
            pass

        assert len(network_calls) == 0, ...

Fix: remove the try/except, leave direct import.
The import error will now surface as a real test failure.

Also fix assert True # no-exception contract ONLY when it's not the sole
statement in a block (i.e., when there's a real preceding statement too).
"""
import pathlib
import re

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

ROOT = pathlib.Path(".")

FILES = [
    "tests/unit/apps_rg/engines/utils/test_brand_compliance_agent.py",
    "tests/unit/apps_rg/engines/utils/test_campaign_planner_agent.py",
    "tests/unit/apps_rg/engines/utils/test_content_quality_agent.py",
    "tests/unit/apps_rg/engines/utils/test_content_strategy_agent.py",
    "tests/unit/apps_rg/engines/utils/test_fact_check_agent.py",
    "tests/unit/apps_rg/engines/utils/test_proactive_agent.py",
    "tests/unit/apps_rg/engines/utils/test_rg_healing_orchestrator.py",
    "tests/unit/apps_rg/engines/utils/test_rg_reflection_agent.py",
    "tests/unit/apps_rg/engines/utils/test_rg_resume_orchestrator.py",
    "tests/unit/apps_rg/engines/utils/test_rg_strategic_planner_agent.py",
    "tests/unit/apps_rg/engines/utils/test_rg_template_optimizer_agent.py",
    "tests/unit/apps_rg/engines/utils/test_section_balance_agent.py",
    "tests/unit/apps_rg/shared/tools/test_dispatch_resume_tools_agent.py",
    "tests/unit/apps_rg/shared/tools/test_gap_closure_architect_agent.py",
    # Mirror copies in tests/unit/
    "tests/unit/test_brand_compliance_agent.py",
    "tests/unit/test_campaign_planner_agent.py",
    "tests/unit/test_content_quality_agent.py",
    "tests/unit/test_content_strategy_agent.py",
    "tests/unit/test_fact_check_agent.py",
    "tests/unit/test_proactive_agent.py",
    "tests/unit/test_rg_reflection_agent.py",
    "tests/unit/test_section_balance_agent.py",
]

# Pattern: try:\n                from X import (\n                    Y,\n                )\n            except (...): ... pass
IMPORT_SWALLOWER = re.compile(
    r"            try:\n"
    r"(                from [^\n]+\n                    [^\n]+\n                \)\n)"
    r"            except \(ImportError, NameError, AttributeError\):  # guardian: allow-silent-swallower\n"
    r"                pass\n",
    re.MULTILINE,
)

# Also handle single-line imports
IMPORT_SWALLOWER2 = re.compile(
    r"            try:\n"
    r"(                from [^\n]+\n)"
    r"            except \(ImportError, NameError, AttributeError\):  # guardian: allow-silent-swallower\n"
    r"                pass\n",
    re.MULTILINE,
)

# assert True # no-exception contract — ONLY remove when preceded by non-empty line that is NOT a block opener
# We'll do this carefully line by line
def remove_safe_assert_true(content: str) -> str:
    lines = content.splitlines(keepends=True)
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        if re.match(r"assert True\s*(?:#.*)?$", stripped):
            # Check if this is the SOLE statement in a block
            # Look back for the most recent non-empty, non-comment line
            prev_code = ""
            prev_indent = 0
            for j in range(i - 1, max(i - 15, -1), -1):
                ps = lines[j].rstrip()
                if ps.strip() and not ps.strip().startswith("#"):
                    prev_code = ps.strip()
                    prev_indent = len(ps) - len(ps.lstrip())
                    break
            
            curr_indent = len(line) - len(line.lstrip())
            
            # If previous line ends with ":" (block opener) and same indentation delta,
            # this assert True is the sole statement — DON'T remove (would break syntax)
            if prev_code.endswith(":") and curr_indent > prev_indent:
                # SOLE statement in block — keep as pass instead
                new_lines.append(line.replace("assert True", "pass").rstrip() + "\n")
                i += 1
                continue
            else:
                # Not sole statement — safe to remove
                i += 1
                continue
        
        new_lines.append(line)
        i += 1
    
    return "".join(new_lines)


total_fixed = 0
for fp in FILES:
    p = ROOT / fp
    if not p.exists():
        print(f"NOT FOUND: {fp}")
        continue
    
    content = p.read_text(encoding="utf-8")
    original = content
    
    # Remove import swallowers
    content = IMPORT_SWALLOWER.sub(lambda m: m.group(1), content)
    content = IMPORT_SWALLOWER2.sub(lambda m: m.group(1), content)
    
    # Remove safe assert True
    content = remove_safe_assert_true(content)
    
    if content != original:
        p.write_text(content, encoding="utf-8")
        total_fixed += 1
        print(f"Fixed: {fp}")
    else:
        # Check if any guardian swallower remains
        if "guardian: allow-silent-swallower" in content:
            print(f"UNMATCHED SWALLOWER in: {fp}")

print(f"Total files fixed: {total_fixed}")
