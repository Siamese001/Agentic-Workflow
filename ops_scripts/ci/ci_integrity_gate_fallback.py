#!/usr/bin/env python3
"""
CI Integrity Gate (§22) — Standalone script for GitHub Actions.

Extracted from .github/workflows/ci-integrity-gate.yml to enable:
- Linting, testing, and maintainability
- Reuse across different workflows
- Easier debugging
"""

import ast
import json
import re
import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Run CI integrity gate checks."""
    violations = []
    warnings = []

    PLANS_DIR = Path("docs/reports/plans")
    TESTS_DIR = Path("tests")
    REGISTRY_PATH = Path("artifacts/adg/pre_existing_skip_registry.json")

    # ── Condition 2: Evidence files missing FACT_CLASSIFICATION section ──────────
    if PLANS_DIR.exists():
        for f in sorted(PLANS_DIR.rglob("*.md")):
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
            except (OSError, UnicodeDecodeError) as e:
                warnings.append(f"C2-WARN: Could not read {f}: {e}")
                continue
            # Only check files that look like phase evidence (have a ## Scope section)
            if "## Scope" in content and "## FACT_CLASSIFICATION" not in content:
                violations.append(
                    f"C2: {f} has '## Scope' but missing '## FACT_CLASSIFICATION' section (§2.1.1)",
                )
            if "## FACT_CLASSIFICATION" in content:
                # Check for non-empty Unresolved list that isn't deferred
                if "### Unresolved" in content:
                    idx = content.index("### Unresolved")
                    after = content[idx + len("### Unresolved"):idx + 500]
                    lines = [l.strip() for l in after.split("\n") if l.strip()]
                    # If there are bullet items after "### Unresolved" before the next ###
                    unresolved_items = []
                    for line in lines:
                        if line.startswith("###") or line.startswith("##"):
                            break
                        if line.startswith("-") and "deferred to" not in line.lower():
                            unresolved_items.append(line)
                    if unresolved_items:
                        warnings.append(
                            f"C2-WARN: {f} has {len(unresolved_items)} non-deferred UNRESOLVED item(s) "
                            f"— phase cannot be declared complete (§2.1.1)",
                        )

    # ── Condition 3: Broad pytest runs detected in evidence ────────────────────
    BROAD_PYTEST_PATTERNS = [
        r"pytest\s+tests/\s",
        r"pytest\s+tests/unit\s",
        r"pytest\s+tests/unit$",
        r"pytest\s+tests/$",
        r"pytest\s+-[a-zA-Z]+\s+tests/\s",
        r"pytest\s+-[a-zA-Z]+\s+tests/unit",
    ]
    if PLANS_DIR.exists():
        for f in sorted(PLANS_DIR.rglob("*.md")):
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
            except (OSError, UnicodeDecodeError) as e:
                warnings.append(f"C3-WARN: Could not read {f}: {e}")
                continue
            # Only flag in non-final phase evidence (heuristic: no "Phase 7" or "final" in title)
            first_line = content.split("\n")[0].lower()
            is_final = any(k in first_line for k in ["phase 7", "phase7", "final", "full suite", "full-suite"])
            if not is_final:
                for pattern in BROAD_PYTEST_PATTERNS:
                    if re.search(pattern, content):
                        violations.append(
                            f"C3: {f} contains broad pytest run ('{pattern}') in non-final phase evidence (§5.2.1, §7.2)",
                        )
                        break

    # ── Condition 4: Unexpected skips not in registry ─────────────────────────
    if REGISTRY_PATH.exists():
        try:
            registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
            registered_ids = {e["test_id"] for e in registry.get("skips", [])}
        except (json.JSONDecodeError, KeyError) as e:
            warnings.append(f"C4-WARN: Could not parse skip registry at {REGISTRY_PATH}: {e}")
            registered_ids = set()
    else:
        registered_ids = set()

    if TESTS_DIR.exists():
        for f in sorted(TESTS_DIR.rglob("test_*.py")):
            try:
                source = f.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(source, filename=str(f))
            except SyntaxError as e:
                warnings.append(f"C4-WARN: Syntax error in {f}: {e}")
                continue
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if not node.name.startswith("test_"):
                    continue
                for dec in node.decorator_list:
                    is_skip = False
                    if isinstance(dec, ast.Attribute) and dec.attr == "skip":
                        is_skip = True
                    elif isinstance(dec, ast.Call):
                        func = dec.func
                        if isinstance(func, ast.Attribute) and func.attr in ("skip", "skipif"):
                            is_skip = True
                    if is_skip:
                        rel = str(f).replace("\\", "/")
                        node_id = f"{rel}::{node.name}"
                        if node_id not in registered_ids:
                            violations.append(
                                f"C4: Unregistered skip: {node_id} (§17.2, §1.12)",
                            )

    # ── Condition 8: Test strictness weakened (assert True pattern) ───────────
    if TESTS_DIR.exists():
        for f in sorted(TESTS_DIR.rglob("test_*.py")):
            try:
                source = f.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(source, filename=str(f))
            except SyntaxError as e:
                warnings.append(f"C8-WARN: Syntax error in {f}: {e}")
                continue
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if not node.name.startswith("test_"):
                    continue
                for child in ast.walk(node):
                    if isinstance(child, ast.Assert):
                        test_node = child.test
                        # assert True
                        if isinstance(test_node, ast.Constant) and test_node.value is True:
                            violations.append(
                                f"C8: {f}:{child.lineno} — 'assert True' in {node.name} (fake-healthy test, §11.3)",
                            )
                        # assert True as Name (older AST)
                        if isinstance(test_node, ast.Name) and test_node.id == "True":
                            violations.append(
                                f"C8: {f}:{child.lineno} — 'assert True' (Name) in {node.name} (§11.3)",
                            )

    # ── Condition 9: repair_class missing from repair commits ─────────────────
    # Check recent commit messages via git log for commits touching production code
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-20", "--format=%H %s"],
            capture_output=True, text=True, timeout=15, check=False,
        )
        if result.returncode == 0:
            production_dirs = {"agentic_core", "apps_rg", "apps_lic", "apps_shared", "system_learning"}
            for line in result.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split(" ", 1)
                if len(parts) < 2:
                    continue
                sha, msg = parts[0], parts[1]
                # Only check commits that look like repair commits
                repair_keywords = ["fix", "repair", "patch", "resolve", "correct"]
                if any(kw in msg.lower() for kw in repair_keywords):
                    if "repair_class:" not in msg:
                        # Check if commit touches production dirs
                        diff_result = subprocess.run(
                            ["git", "diff-tree", "--no-commit-id", "-r", "--name-only", sha],
                            capture_output=True, text=True, timeout=10, check=False,
                        )
                        if diff_result.returncode == 0:
                            touched = diff_result.stdout.strip().split("\n")
                            touches_production = any(
                                any(t.startswith(d) for d in production_dirs)
                                for t in touched
                            )
                            if touches_production:
                                warnings.append(
                                    f"C9-WARN: Commit {sha[:8]} ('{msg[:60]}') touches production code "
                                    f"but has no 'repair_class:' footer (§14.8, §22.1)",
                                )
    except (subprocess.SubprocessError, OSError) as e:
        warnings.append(f"C9-WARN: Could not check commit messages: {e}")

    # ── Condition 5: FAILURE_CAPTURE section missing from repair phase evidence ─
    if PLANS_DIR.exists():
        for f in sorted(PLANS_DIR.rglob("*.md")):
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
            except (OSError, UnicodeDecodeError) as e:
                warnings.append(f"C5-WARN: Could not read {f}: {e}")
                continue
            first_line = content.split("\n")[0].lower()
            # Only check repair phase evidence (heuristic: phase 3, 4, 5, 6 or "repair" in title)
            is_repair_phase = any(k in first_line for k in ["phase 3", "phase 4", "phase 5", "phase 6", "repair"])
            if is_repair_phase:
                has_failures_section = any(
                    s in content for s in ["## FAILURE_CAPTURE", "## Failures", "## FAILURES"]
                )
                # Only flag if the file also mentions failing tests
                has_failure_mentions = any(
                    kw in content for kw in ["FAILED", "AssertionError", "failures", "failing"]
                )
                if has_failure_mentions and not has_failures_section:
                    warnings.append(
                        f"C5-WARN: {f} is a repair-phase evidence file with failure mentions "
                        f"but no '## FAILURE_CAPTURE' section (§14.6)",
                    )

    # ── Report ─────────────────────────────────────────────────────────────────
    print(f"CI Integrity Gate (§22) — {len(violations)} violation(s), {len(warnings)} warning(s)")

    for w in warnings:
        print(f"  ⚠️  {w}")

    if violations:
        print(f"\n§22 CI INTEGRITY VIOLATIONS ({len(violations)}):")
        for v in violations:
            print(f"  ❌ {v}")
        return 1
    else:
        print("§22 CI integrity gate: PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(main())
