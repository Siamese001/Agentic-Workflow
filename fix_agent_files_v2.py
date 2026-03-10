"""
Precisely fix two patterns in agent test files:

1. Fuzzing swallower — remove try/except pass (the try body is just 'pass'):
    try:
        pass  # Would test actual processing
    except (TypeError, ValueError, AttributeError):  # guardian: allow-silent-swallower
        pass  # Expected for invalid inputs
        assert True  # no-exception contract
    ->  (remove the whole try/except, it tests nothing)

2. Import swallower inside with patch block:
    with patch(...):
        try:
            from X import Y  # noqa: F401
        except (ImportError, NameError, AttributeError):  # guardian: allow-silent-swallower
            pass

        assert len(network_calls) == 0, "..."
    ->
    with patch(...):
        from X import Y  # noqa: F401

        assert len(network_calls) == 0, "..."
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
    "tests/unit/test_brand_compliance_agent.py",
    "tests/unit/test_campaign_planner_agent.py",
    "tests/unit/test_content_quality_agent.py",
    "tests/unit/test_content_strategy_agent.py",
    "tests/unit/test_fact_check_agent.py",
    "tests/unit/test_proactive_agent.py",
    "tests/unit/test_rg_reflection_agent.py",
    "tests/unit/test_section_balance_agent.py",
]

# Pattern 1: fuzzing swallower (try body is just pass)
FUZZING_PATTERN = re.compile(
    r"            try:\n"
    r"                pass  # Would test actual processing\n"
    r"            except \(TypeError, ValueError, AttributeError\):  # guardian: allow-silent-swallower\n"
    r"                pass  # Expected for invalid inputs\n"
    r"                assert True  # no-exception contract\n",
    re.MULTILINE,
)

# Pattern 2: import swallower (single-line import)
IMPORT_PATTERN_1LINE = re.compile(
    r"            try:\n"
    r"                (from [^\n]+  # noqa: F401\n)"
    r"            except \(ImportError, NameError, AttributeError\):  # guardian: allow-silent-swallower\n"
    r"                pass\n",
    re.MULTILINE,
)

# Pattern 2b: multi-line import
IMPORT_PATTERN_MULTI = re.compile(
    r"            try:\n"
    r"                (from [^\n]+\n"
    r"                    [^\n]+\n"
    r"                \)  # noqa: F401\n)"
    r"            except \(ImportError, NameError, AttributeError\):  # guardian: allow-silent-swallower\n"
    r"                pass\n",
    re.MULTILINE,
)


total = 0
for fp in FILES:
    p = ROOT / fp
    if not p.exists():
        print(f"NOT FOUND: {fp}")
        continue
    
    content = p.read_text(encoding="utf-8")
    original = content
    
    content = FUZZING_PATTERN.sub("", content)
    content = IMPORT_PATTERN_1LINE.sub(lambda m: f"            {m.group(1)}", content)
    content = IMPORT_PATTERN_MULTI.sub(lambda m: f"            {m.group(1)}", content)
    
    if content != original:
        p.write_text(content, encoding="utf-8")
        total += 1
        print(f"Fixed: {fp}")
    else:
        remaining = [l for l in content.splitlines() if "guardian: allow-silent-swallower" in l]
        if remaining:
            print(f"UNMATCHED in {fp}: {remaining}")

print(f"Total files fixed: {total}")
