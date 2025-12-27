"""
Sovereign Guardian: No Hardcoded Configuration
Enforces centralized config usage - bans os.getenv outside SSOT.
"""
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Files exempt from this check
EXEMPT = ["__init__.py", "__pycache__"]

# Allow os.getenv only in sovereign_config.py and tests
ALLOWED_PATTERNS = ["sovereign_config.py", "tests/", "test_"]

def check_file(filepath: Path) -> bool:
    """
    Check if file has hardcoded configuration.
    Returns True if compliant, False if violations found.
    """
    # Skip allowed files
    if filepath.name in EXEMPT or any(p in str(filepath).replace("\\", "/") for p in ALLOWED_PATTERNS):
        return True
    
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return True  # Skip files that can't be read
    
    violations = []
    
    # Check 1: Explicit os.getenv calls
    if "os.getenv" in content:
        for match in re.finditer(r'\bos\.getenv\(', content):
            line_no = content[:match.start()].count('\n') + 1
            violations.append((line_no, "os.getenv() usage", "Use config.VARIABLE from sovereign_config"))
    
    # Check 2: Hardcoded model names (common patterns)
    hardcoded_models = [
        r'["\']gpt-4["\']',
        r'["\']gpt-3\.5-turbo["\']',
        r'["\']claude-["\']',
        r'["\']gemini-["\']',
    ]
    for pattern in hardcoded_models:
        for match in re.finditer(pattern, content):
            line_no = content[:match.start()].count('\n') + 1
            violations.append((line_no, f"Hardcoded model: {match.group()}", "Use config.PRIMARY_MODEL or config.REASONING_MODEL"))
    
    # Check 3: Hardcoded paths (common patterns)
    hardcoded_paths = [
        r'["\']c:/Git/["\']',
        r'["\']C:\\Git\\["\']',
        r'["\']~/["\']',
    ]
    for pattern in hardcoded_paths:
        for match in re.finditer(pattern, content):
            line_no = content[:match.start()].count('\n') + 1
            violations.append((line_no, f"Hardcoded path: {match.group()}", "Use config.BASE_GIT_PATH or config.ROOT_DIR"))
    
    # Check 4: Phase 16A - Block direct Redis usage
    redis_patterns = [
        (r'\bimport\s+redis\b', "Direct redis import"),
        (r'\bfrom\s+redis\s+import\b', "Direct redis import"),
        (r'\bRedis\s*\(', "Direct Redis() instantiation"),
        (r'redis://', "Direct redis:// connection string"),
    ]
    for pattern, desc in redis_patterns:
        for match in re.finditer(pattern, content):
            line_no = content[:match.start()].count('\n') + 1
            violations.append((line_no, desc, "Use get_redis_client() from agentic_core.L4_state.caching.redis_mcp_client"))
    
    # Check 5: Phase 16B - Block direct LLM SDK usage
    llm_sdk_patterns = [
        (r'\bimport\s+openai\b', "Direct openai import"),
        (r'\bfrom\s+openai\s+import\b', "Direct openai import"),
        (r'\bimport\s+anthropic\b', "Direct anthropic import"),
        (r'\bfrom\s+anthropic\s+import\b', "Direct anthropic import"),
        (r'\bimport\s+google\.generativeai\b', "Direct google.generativeai import"),
        (r'\bgenai\.GenerativeModel\b', "Direct genai.GenerativeModel usage"),
    ]
    for pattern, desc in llm_sdk_patterns:
        for match in re.finditer(pattern, content):
            line_no = content[:match.start()].count('\n') + 1
            violations.append((line_no, desc, "Use get_llm_router_client() from agentic_core.L5_safety.guardrails.llm_router_mcp_client"))
    
    # Check 6: Phase 16C - Block direct filesystem I/O
    filesystem_patterns = [
        (r'\bopen\s*\(', "Direct open() call"),
        (r'\.read_text\(', "Direct Path.read_text() call"),
        (r'\.write_text\(', "Direct Path.write_text() call"),
        (r'\bos\.remove\(', "Direct os.remove() call"),
        (r'\bos\.rename\(', "Direct os.rename() call"),
        (r'\bshutil\.move\(', "Direct shutil.move() call"),
        (r'\bshutil\.rmtree\(', "Direct shutil.rmtree() call"),
    ]
    for pattern, desc in filesystem_patterns:
        for match in re.finditer(pattern, content):
            line_no = content[:match.start()].count('\n') + 1
            violations.append((line_no, desc, "Use get_filesystem_client() from agentic_core.L0_maintenance.filesystem_mcp_client"))
    
    if violations:
        print(f"\n❌ {filepath.name}:")
        for line_no, issue, fix in violations[:5]:  # Limit to first 5
            print(f"  Line {line_no}: {issue}")
            print(f"    → {fix}")
        if len(violations) > 5:
            print(f"  ... and {len(violations) - 5} more violations")
        return False
    
    return True

def main():
    """Scan target directory for hardcoded configuration."""
    if len(sys.argv) < 2:
        print("Usage: python guard_no_hardcoded_config.py <target_dir>")
        sys.exit(1)
    
    target = Path(sys.argv[1])
    if not target.exists():
        print(f"Error: {target} does not exist")
        sys.exit(1)
    
    files = [f for f in target.rglob("*.py") if f.is_file()]
    total = len(files)
    violations = 0
    
    print(f"\n🔍 Scanning {total} Python files in {target}...")
    print("=" * 60)
    
    for filepath in files:
        if not check_file(filepath):
            violations += 1
    
    print("\n" + "=" * 60)
    if violations == 0:
        print(f"✅ COMPLIANT: All {total} files use centralized config")
        sys.exit(0)
    else:
        print(f"❌ VIOLATIONS: {violations}/{total} files have hardcoded config")
        print("\nFix by importing: from agentic_core.config.blueprint_sovereign.environments.sovereign_config import config")
        sys.exit(1)

if __name__ == "__main__":
    main()
