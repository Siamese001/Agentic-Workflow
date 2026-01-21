#!/usr/bin/env python3
"""
Test Suite: Google GenAI Migration

Verifies that the codebase has been migrated from deprecated google-generativeai
to the new google.genai package.

CONSTRAINT: 100% PASSING MANDATORY.
"""
import ast
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

PASSED = 0
FAILED = 0

def test_pass(test_id: str, msg: str):
    global PASSED
    PASSED += 1
    print(f"  ✅ {test_id}: {msg}")

def test_fail(test_id: str, msg: str):
    global FAILED
    FAILED += 1
    print(f"  ❌ {test_id}: {msg}")


def test_no_deprecated_imports():
    """Verify no deprecated google.generativeai imports in agentic_core."""
    print("\n" + "=" * 70)
    print("Test 1: No Deprecated google.generativeai Imports")
    print("=" * 70)

    agentic_core = PROJECT_ROOT / "agentic_core"
    deprecated_pattern = re.compile(r'import\s+google\.generativeai|from\s+google\.generativeai')

    violations = []
    for py_file in agentic_core.rglob("*.py"):
        try:
            content = py_file.read_text(encoding='utf-8')
            matches = deprecated_pattern.findall(content)
            if matches:
                rel_path = py_file.relative_to(PROJECT_ROOT)
                violations.append(f"{rel_path}: {matches}")
        except Exception:
            pass

    if violations:
        for v in violations:
            test_fail("DEPRECATED_IMPORT", v)
    else:
        test_pass("DEPRECATED_IMPORT", "No deprecated google.generativeai imports found")


def test_new_genai_imports():
    """Verify files use new google.genai import pattern."""
    print("\n" + "=" * 70)
    print("Test 2: New google.genai Import Pattern")
    print("=" * 70)

    # Files that should use google.genai
    target_files = [
        "agentic_core/semantic_memory/embeddings/gemini_embedder.py",
        "agentic_core/L5_safety/guardrails/subatomic_engine.py",
        "agentic_core/L2_execution/mcp/inference_engine.py",
        "agentic_core/L2_execution/ToolRegistry/L2ExecutionBaseAgent.py",
    ]

    new_pattern = re.compile(r'from\s+google\s+import\s+genai')

    for rel_path in target_files:
        full_path = PROJECT_ROOT / rel_path
        if not full_path.exists():
            test_fail(f"FILE_EXISTS-{Path(rel_path).stem}", f"File not found: {rel_path}")
            continue

        content = full_path.read_text(encoding='utf-8')
        if new_pattern.search(content):
            test_pass(f"NEW_IMPORT-{Path(rel_path).stem}", f"Uses google.genai")
        else:
            test_fail(f"NEW_IMPORT-{Path(rel_path).stem}", f"Missing 'from google import genai'")


def test_genai_client_usage():
    """Verify files use genai.Client() instead of genai.configure()."""
    print("\n" + "=" * 70)
    print("Test 3: genai.Client() Usage (Not genai.configure)")
    print("=" * 70)

    agentic_core = PROJECT_ROOT / "agentic_core"
    deprecated_configure = re.compile(r'genai\.configure\s*\(')

    violations = []
    for py_file in agentic_core.rglob("*.py"):
        try:
            content = py_file.read_text(encoding='utf-8')
            if deprecated_configure.search(content):
                rel_path = py_file.relative_to(PROJECT_ROOT)
                violations.append(str(rel_path))
        except Exception:
            pass

    if violations:
        for v in violations:
            test_fail("DEPRECATED_CONFIGURE", f"Uses genai.configure(): {v}")
    else:
        test_pass("DEPRECATED_CONFIGURE", "No genai.configure() usage found")


def test_pyproject_dependency():
    """Verify pyproject.toml has google-genai dependency."""
    print("\n" + "=" * 70)
    print("Test 4: pyproject.toml Dependency")
    print("=" * 70)

    pyproject = PROJECT_ROOT / "pyproject.toml"
    if not pyproject.exists():
        test_fail("PYPROJECT_EXISTS", "pyproject.toml not found")
        return

    content = pyproject.read_text(encoding='utf-8')

    if "google-genai" in content:
        test_pass("PYPROJECT_NEW_DEP", "google-genai dependency present")
    else:
        test_fail("PYPROJECT_NEW_DEP", "google-genai dependency missing")

    if "google-generativeai" in content:
        test_fail("PYPROJECT_OLD_DEP", "Deprecated google-generativeai still in dependencies")
    else:
        test_pass("PYPROJECT_OLD_DEP", "No deprecated google-generativeai dependency")


def test_provider_modules():
    """Verify provider module references use google.genai."""
    print("\n" + "=" * 70)
    print("Test 5: Provider Module References")
    print("=" * 70)

    archive_providers = PROJECT_ROOT / "agentic_core/L2_execution/mcp/archive_providers.py"
    if not archive_providers.exists():
        test_fail("ARCHIVE_PROVIDERS", "archive_providers.py not found")
        return

    content = archive_providers.read_text(encoding='utf-8')

    if '"google": "google.genai"' in content:
        test_pass("PROVIDER_MODULE", "Google provider uses google.genai")
    elif '"google": "google.generativeai"' in content:
        test_fail("PROVIDER_MODULE", "Google provider still uses deprecated google.generativeai")
    else:
        test_pass("PROVIDER_MODULE", "Google provider module reference OK")


def test_syntax_validation():
    """Verify all modified files have valid Python syntax."""
    print("\n" + "=" * 70)
    print("Test 6: Syntax Validation")
    print("=" * 70)

    files_to_check = [
        "agentic_core/semantic_memory/embeddings/gemini_embedder.py",
        "agentic_core/L2_execution/mcp/runtime_shared_multi_provider_clients.py",
        "agentic_core/L5_safety/guardrails/subatomic_engine.py",
        "agentic_core/L2_execution/mcp/archive_providers.py",
        "agentic_core/L0_maintenance/scripts/guard_no_hardcoded_config.py",
    ]

    for rel_path in files_to_check:
        full_path = PROJECT_ROOT / rel_path
        if not full_path.exists():
            test_fail(f"SYNTAX-{Path(rel_path).stem}", f"File not found: {rel_path}")
            continue

        try:
            content = full_path.read_text(encoding='utf-8')
            ast.parse(content)
            test_pass(f"SYNTAX-{Path(rel_path).stem}", "Valid Python syntax")
        except SyntaxError as e:
            test_fail(f"SYNTAX-{Path(rel_path).stem}", f"Syntax error: {e}")


def test_gemini_embedder_class():
    """Verify GeminiEmbedder class uses new API."""
    print("\n" + "=" * 70)
    print("Test 7: GeminiEmbedder Class Implementation")
    print("=" * 70)

    embedder_file = PROJECT_ROOT / "agentic_core/semantic_memory/embeddings/gemini_embedder.py"
    if not embedder_file.exists():
        test_fail("EMBEDDER_EXISTS", "gemini_embedder.py not found")
        return

    content = embedder_file.read_text(encoding='utf-8')

    # Check for new Client usage
    if "genai.Client(" in content:
        test_pass("EMBEDDER_CLIENT", "Uses genai.Client()")
    else:
        test_fail("EMBEDDER_CLIENT", "Missing genai.Client() usage")

    # Check for GENAI_AVAILABLE flag
    if "GENAI_AVAILABLE" in content:
        test_pass("EMBEDDER_FLAG", "Has GENAI_AVAILABLE flag")
    else:
        test_fail("EMBEDDER_FLAG", "Missing GENAI_AVAILABLE flag")

    # Check for new embed_content method
    if "client.models.embed_content" in content or "self.client.models.embed_content" in content:
        test_pass("EMBEDDER_METHOD", "Uses new embed_content API")
    else:
        test_fail("EMBEDDER_METHOD", "Missing new embed_content API")


def test_guard_deprecation_check():
    """Verify guard script checks for deprecated imports."""
    print("\n" + "=" * 70)
    print("Test 8: Guard Script Deprecation Check")
    print("=" * 70)

    guard_file = PROJECT_ROOT / "agentic_core/L0_maintenance/scripts/guard_no_hardcoded_config.py"
    if not guard_file.exists():
        test_fail("GUARD_EXISTS", "guard_no_hardcoded_config.py not found")
        return

    content = guard_file.read_text(encoding='utf-8')

    if "Deprecated google.generativeai" in content or "use google.genai" in content:
        test_pass("GUARD_DEPRECATION", "Guard checks for deprecated imports")
    else:
        test_fail("GUARD_DEPRECATION", "Guard doesn't check for deprecated imports")


def main():
    print("\n" + "=" * 70)
    print("GOOGLE GENAI MIGRATION TEST SUITE")
    print("=" * 70)
    print("Verifying migration from google-generativeai to google.genai")

    test_no_deprecated_imports()
    test_new_genai_imports()
    test_genai_client_usage()
    test_pyproject_dependency()
    test_provider_modules()
    test_syntax_validation()
    test_gemini_embedder_class()
    test_guard_deprecation_check()

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    total = PASSED + FAILED
    print(f"  Total Tests: {total}")
    print(f"  Passed: {PASSED}")
    print(f"  Failed: {FAILED}")
    print(f"  Pass Rate: {100 * PASSED / total:.1f}%")

    if FAILED == 0:
        print("\n  ✅ ALL TESTS PASSED - GENAI MIGRATION COMPLETE")
        return 0
    else:
        print(f"\n  ❌ {FAILED} TESTS FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(main())
