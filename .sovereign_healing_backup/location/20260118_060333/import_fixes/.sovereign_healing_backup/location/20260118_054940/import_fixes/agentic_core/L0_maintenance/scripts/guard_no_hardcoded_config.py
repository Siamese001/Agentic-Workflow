from __future__ import annotations
"""
Sovereign Guardian: No Hardcoded Configuration
Enforces centralized config usage - bans os.getenv outside SSOT.
"""
import re
import sys
from pathlib import Path
from typing import Any, List, Tuple

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.L5_safety.validators.structure_blueprint_1 import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

exempt: Any = ['__init__.py', '__pycache__']
allowed_patterns: Any = ['sovereign_config.py', 'tests/', 'test_']

def check_file(filepath: Path) -> bool:
    """
    Check if file has hardcoded configuration.
    Returns True if compliant, False if violations found.
    """
    if filepath.name in EXEMPT or any((p in str(filepath).replace('\\', '/') for p in ALLOWED_PATTERNS)):
        return True
    try:
        content: Any = filepath.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return True
    violations: Any = []
    if 'os.getenv' in content:
        for match in re.finditer('\\bos\\.getenv\\(', content):
            line_no: Any = content[:match.start()].count('\n') + 1
            violations.append((line_no, 'os.getenv() usage', 'Use config.VARIABLE from sovereign_config'))
    hardcoded_models: Any = ['["\\\']gpt-4["\\\']', '["\\\']gpt-3\\.5-turbo["\\\']', '["\\\']claude-["\\\']', '["\\\']gemini-["\\\']']
    for pattern in hardcoded_models:
        for match in re.finditer(pattern, content):
            line_no: Any = content[:match.start()].count('\n') + 1
            violations.append((line_no, f'Hardcoded model: {match.group()}', 'Use config.PRIMARY_MODEL or config.REASONING_MODEL'))
    hardcoded_paths: Any = ['["\\\']c:/Git/["\\\']', '["\\\']C:\\\\Git\\\\["\\\']', '["\\\']~/["\\\']']
    for pattern in hardcoded_paths:
        for match in re.finditer(pattern, content):
            line_no: Any = content[:match.start()].count('\n') + 1
            violations.append((line_no, f'Hardcoded path: {match.group()}', 'Use config.BASE_GIT_PATH or config.ROOT_DIR'))
    redis_patterns: Any = [('\\bimport\\s+redis\\b', 'Direct redis import'), ('\\bfrom\\s+redis\\s+import\\b', 'Direct redis import'), ('\\bRedis\\s*\\(', 'Direct Redis() instantiation'), ('redis://', 'Direct redis:// connection string')]
    for pattern, desc in redis_patterns:
        for match in re.finditer(pattern, content):
            line_no: Any = content[:match.start()].count('\n') + 1
            violations.append((line_no, desc, 'Use get_redis_client() from agentic_core.L4_state.caching.redis_mcp_client'))
    llm_sdk_patterns: Any = [('\\bimport\\s+openai\\b', 'Direct openai import'), ('\\bfrom\\s+openai\\s+import\\b', 'Direct openai import'), ('\\bimport\\s+anthropic\\b', 'Direct anthropic import'), ('\\bfrom\\s+anthropic\\s+import\\b', 'Direct anthropic import'), ('\\bimport\\s+google\\.generativeai\\b', 'Direct google.generativeai import'), ('\\bgenai\\.GenerativeModel\\b', 'Direct genai.GenerativeModel usage')]
    for pattern, desc in llm_sdk_patterns:
        for match in re.finditer(pattern, content):
            line_no: Any = content[:match.start()].count('\n') + 1
            violations.append((line_no, desc, 'Use get_llm_router_client() from agentic_core.L5_safety.guardrails.llm_router_mcp_client'))
    filesystem_patterns: Any = [('\\bopen\\s*\\(', 'Direct open() call'), ('\\.read_text\\(', 'Direct Path.read_text() call'), ('\\.write_text\\(', 'Direct Path.write_text() call'), ('\\bos\\.remove\\(', 'Direct os.remove() call'), ('\\bos\\.rename\\(', 'Direct os.rename() call'), ('\\bshutil\\.move\\(', 'Direct shutil.move() call'), ('\\bshutil\\.rmtree\\(', 'Direct shutil.rmtree() call')]
    for pattern, desc in filesystem_patterns:
        for match in re.finditer(pattern, content):
            line_no: Any = content[:match.start()].count('\n') + 1
            violations.append((line_no, desc, 'Use get_filesystem_client() from agentic_core.L0_maintenance.P1_core.filesystem_mcp_client'))
    git_patterns: Any = [('subprocess\\.run\\(\\[.*["\\\']git["\\\']', 'Direct git subprocess call'), ('os\\.system\\(["\\\']git', 'Direct git os.system() call'), ('\\bimport\\s+git\\b', 'Direct gitpython import'), ('\\bfrom\\s+git\\s+import\\b', 'Direct gitpython import'), ('\\bimport\\s+pygit2\\b', 'Direct pygit2 import')]
    for pattern, desc in git_patterns:
        for match in re.finditer(pattern, content):
            line_no: Any = content[:match.start()].count('\n') + 1
            violations.append((line_no, desc, 'Use get_git_client() from agentic_core.L0_maintenance.P1_core.gitkraken_mcp_client'))
    pinecone_patterns: Any = [('\\bfrom\\s+pinecone\\s+import\\b', 'Direct pinecone import'), ('\\bPinecone\\s*\\(', 'Direct Pinecone() instantiation'), ('\\.Index\\s*\\(', 'Direct pc.Index() call'), ('["\\\']sovereign-territory-index["\\\']', 'Hardcoded index name')]
    for pattern, desc in pinecone_patterns:
        for match in re.finditer(pattern, content):
            line_no: Any = content[:match.start()].count('\n') + 1
            violations.append((line_no, desc, 'Use get_pinecone_mcp_client() from agentic_core.L4_state.semantic_memory.pinecone_mcp_client'))
    http_patterns: Any = [('\\bimport\\s+requests\\b', 'Direct requests import'), ('\\bimport\\s+httpx\\b', 'Direct httpx import'), ('\\bimport\\s+urllib\\b', 'Direct urllib import'), ('\\brequests\\.(get|post|put|delete|patch)\\s*\\(', 'Direct requests HTTP call'), ('\\bhttpx\\.(get|post|put|delete|patch|AsyncClient)\\s*\\(', 'Direct httpx HTTP call')]
    for pattern, desc in http_patterns:
        for match in re.finditer(pattern, content):
            line_no: Any = content[:match.start()].count('\n') + 1
            violations.append((line_no, desc, 'Use get_fetch_client() from agentic_core.L2_execution.ToolRegistry.fetch_mcp_client'))
    lockdown_patterns: Any = [('\\bsubprocess\\.call\\s*\\(', 'Direct subprocess.call() usage'), ('\\bos\\.popen\\s*\\(', 'Direct os.popen() usage'), ('agentic_core/tools/', "Legacy 'tools/' path usage")]
    for pattern, desc in lockdown_patterns:
        for match in re.finditer(pattern, content):
            line_no: Any = content[:match.start()].count('\n') + 1
            if "Legacy 'tools/' path" in desc:
                violations.append((line_no, desc, "Use 'agentic_core/utils/' or appropriate layer path"))
            else:
                violations.append((line_no, desc, 'Use appropriate MCP client or approved subprocess wrapper'))
    if violations:
        print(f'\n❌ {filepath.name}:')
        for line_no, issue, fix in violations[:5]:
            print(f'  Line {line_no}: {issue}')
            print(f'    → {fix}')
        if len(violations) > 5:
            print(f'  ... and {len(violations) - 5} more violations')
        return False
    return True

def main() -> Any:
    """Scan target directory for hardcoded configuration."""
    if len(sys.argv) < 2:
        print('Usage: python guard_no_hardcoded_config.py <target_dir>')
        sys.exit(1)
    target: Any = Path(sys.argv[1])
    if not target.exists():
        print(f'Error: {target} does not exist')
        sys.exit(1)
    files: Any = [f for f in target.rglob('*.py') if f.is_file()]
    total: Any = len(files)
    violations: Any = 0
    print(f'\n🔍 Scanning {total} Python files in {target}...')
    print('=' * 60)
    for filepath in files:
        if not check_file(filepath):
            violations += 1
    print('\n' + '=' * 60)
    if violations == 0:
        print(f'✅ COMPLIANT: All {total} files use centralized config')
        sys.exit(0)
    else:
        print(f'❌ VIOLATIONS: {violations}/{total} files have hardcoded config')
        print('\nFix by importing: from agentic_core.config.blueprint_sovereign.sovereign_config_1 import config')
        sys.exit(1)
if __name__ == '__main__':
    main()
