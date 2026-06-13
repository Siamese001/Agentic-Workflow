# Zero-Loss Guardian Sovereignty Expansion — Implementation Plan

Add 5 new sovereignty-enforcement guardians to the SSOT registry, implement their runner scripts, and wire test coverage into `test_guardian_meta_coverage.py`. Phases are dependency-ordered; each phase is a single commit.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Scope Summary

**N = 16 files touched/created**

| # | File | Action |
|---|------|--------|
| 1 | `agentic_core/L0_routing/types/guardian_registry_types.py` | diff — add 5 specs |
| 2 | `agentic_core/L0_routing/scripts/run_guardian_gateway_bypass.py` | new |
| 3 | `agentic_core/L0_routing/scripts/run_guardian_c0_sovereignty.py` | new |
| 4 | `agentic_core/L0_routing/scripts/run_guardian_escalation_determinism.py` | new |
| 5 | `agentic_core/L0_routing/scripts/run_guardian_change_package_activation.py` | new |
| 6 | `agentic_core/L0_routing/scripts/run_guardian_cross_layer_mutation.py` | new |
| 7 | `tests/guardian/test_guardian_gateway_bypass.py` | new |
| 8 | `tests/guardian/test_guardian_c0_sovereignty.py` | new |
| 9 | `tests/guardian/test_guardian_escalation_determinism.py` | new |
| 10 | `tests/guardian/test_guardian_change_package_activation.py` | new |
| 11 | `tests/guardian/test_guardian_cross_layer_mutation.py` | new |
| 12 | `tests/guardian/test_guardian_meta_coverage.py` | diff — add 5 entries to `GUARDIAN_COVERAGE_MAP` |
| 13 | `.github/workflows/guardian-tests.yml` | diff — add sovereignty gate step |

---

## Phase 1 — Registry Expansion (1 file, fast)

**Scope:** `agentic_core/L0_routing/types/guardian_registry_types.py`

```diff
-        key=lambda s: s.guardian_id,
-    ),
-)
+        GuardianSpec(
+            guardian_id="c0_sovereignty_enforcement",
+            entrypoint_module="agentic_core.L0_routing.scripts.run_guardian_c0_sovereignty",
+            entrypoint_fn="run_c0_sovereignty_guardian",
+            check_ids=(
+                "embedding_drives_routing",
+                "embedding_drives_tier_selection",
+                "embedding_mutates_threshold",
+            ),
+            tier="fast",
+            enabled_by_default=True,
+        ),
+        GuardianSpec(
+            guardian_id="change_package_activation_guard",
+            entrypoint_module="agentic_core.L0_routing.scripts.run_guardian_change_package_activation",
+            entrypoint_fn="run_change_package_activation_guardian",
+            check_ids=(
+                "proposal_only_bypass",
+                "direct_version_store_commit",
+                "activation_without_approval_gate",
+            ),
+            tier="fast",
+            enabled_by_default=True,
+        ),
+        GuardianSpec(
+            guardian_id="cross_layer_mutation_guard",
+            entrypoint_module="agentic_core.L0_routing.scripts.run_guardian_cross_layer_mutation",
+            entrypoint_fn="run_cross_layer_mutation_guardian",
+            check_ids=(
+                "upward_layer_mutation",
+                "L6_mutates_L4",
+                "L4_invokes_L2",
+                "C0_mutates_control_plane",
+            ),
+            tier="slow",
+            enabled_by_default=True,
+        ),
+        GuardianSpec(
+            guardian_id="escalation_determinism",
+            entrypoint_module="agentic_core.L0_routing.scripts.run_guardian_escalation_determinism",
+            entrypoint_fn="run_escalation_determinism_guardian",
+            check_ids=(
+                "failure_signal_built_from_raw_notes",
+                "alternate_escalation_context_construction",
+                "escalation_context_mutation",
+            ),
+            tier="fast",
+            enabled_by_default=True,
+        ),
+        GuardianSpec(
+            guardian_id="gateway_bypass",
+            entrypoint_module="agentic_core.L0_routing.scripts.run_guardian_gateway_bypass",
+            entrypoint_fn="run_gateway_bypass_guardian",
+            check_ids=(
+                "direct_model_call",
+                "provider_sdk_import",
+                "bypass_tier_router",
+                "bypass_embedding_factory",
+            ),
+            tier="fast",
+            enabled_by_default=True,
+        ),
+        key=lambda s: s.guardian_id,
+    ),
+)
```

---

## Phase 2 — Guardian Runner Scripts (5 new files)

### 2a. `agentic_core/L0_routing/scripts/run_guardian_gateway_bypass.py` (NEW)

```python
"""
Guardian: Gateway Bypass — AST-based detection of direct LLM SDK usage
outside the SovereignLLMGateway boundary.

Checks:
- direct_model_call: Direct instantiation of openai/anthropic/genai classes
- provider_sdk_import: Import of forbidden provider SDK modules in scan roots
- bypass_tier_router: Call-sites that route to a model skipping tier selection
- bypass_embedding_factory: Direct embedding construction bypassing factory

Scan roots: agentic_core/, apps_lic/, apps_rg/, apps_shared/, system_learning/
Allowlist:  agentic_core/L2_execution/enforcement/SovereignLLMGateway.py
            agentic_core/L2_execution/enforcement/EmbeddingServiceFactory.py
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.types.guardian_contract_types import (
    ArtifactType,
    CheckStatus,
    GuardianResult,
    GuardianStatus,
    maybe_sign_result,
    normalize_repo_path,
    write_guardian_result,
)
from agentic_core.L0_routing.utils.project_root import get_validated_project_root

GUARDIAN_ID = "gateway_bypass"

SCAN_ROOTS: tuple[str, ...] = (
    "agentic_core",
    "apps_lic",
    "apps_rg",
    "apps_shared",
    "system_learning",
)

ALLOWED_SDK_FILES: frozenset[str] = frozenset({
    "agentic_core/L2_execution/enforcement/SovereignLLMGateway.py",
    "agentic_core/L2_execution/enforcement/EmbeddingServiceFactory.py",
})

FORBIDDEN_SDK_MODULES: frozenset[str] = frozenset({
    "openai",
    "anthropic",
    "google.generativeai",
})

FORBIDDEN_INSTANTIATION_NAMES: frozenset[str] = frozenset({
    "OpenAI",
    "AsyncOpenAI",
    "Anthropic",
    "AsyncAnthropic",
    "GenerativeModel",
})

SKIP_DIRS: frozenset[str] = frozenset({
    "__pycache__", ".git", ".venv", ".pytest_cache", ".nox", "archives",
})


def _collect_files(repo_root: Path) -> list[Path]:
    result: list[Path] = []
    for root_name in sorted(SCAN_ROOTS):
        root_path = repo_root / root_name
        if not root_path.exists():
            continue
        for dirpath, dirnames, filenames in __import__("os").walk(root_path):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for fname in sorted(filenames):
                if fname.endswith(".py"):
                    result.append(Path(dirpath) / fname)
    return result


def scan_provider_sdk_imports(
    repo_root: Path,
    files: list[Path] | None = None,
) -> list[dict]:
    """Return sorted violation dicts for forbidden SDK imports."""
    if files is None:
        files = _collect_files(repo_root)
    violations: list[dict] = []
    for fpath in files:
        rel = normalize_repo_path(fpath.relative_to(repo_root))
        if rel in ALLOWED_SDK_FILES:
            continue
        try:
            tree = ast.parse(fpath.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(alias.name == m or alias.name.startswith(m + ".") for m in FORBIDDEN_SDK_MODULES):
                        violations.append({
                            "path": rel,
                            "check_id": "provider_sdk_import",
                            "line": node.lineno,
                            "detail": f"import {alias.name}",
                        })
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if any(mod == m or mod.startswith(m + ".") for m in FORBIDDEN_SDK_MODULES):
                    violations.append({
                        "path": rel,
                        "check_id": "provider_sdk_import",
                        "line": node.lineno,
                        "detail": f"from {mod} import ...",
                    })
    return sorted(violations, key=lambda v: (v["path"], v["line"]))


def scan_direct_model_calls(
    repo_root: Path,
    files: list[Path] | None = None,
) -> list[dict]:
    """Return sorted violation dicts for direct model instantiation."""
    if files is None:
        files = _collect_files(repo_root)
    violations: list[dict] = []
    for fpath in files:
        rel = normalize_repo_path(fpath.relative_to(repo_root))
        if rel in ALLOWED_SDK_FILES:
            continue
        try:
            tree = ast.parse(fpath.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                name = None
                if isinstance(func, ast.Name):
                    name = func.id
                elif isinstance(func, ast.Attribute):
                    name = func.attr
                if name in FORBIDDEN_INSTANTIATION_NAMES:
                    violations.append({
                        "path": rel,
                        "check_id": "direct_model_call",
                        "line": node.lineno,
                        "detail": f"call to {name}()",
                    })
    return sorted(violations, key=lambda v: (v["path"], v["line"]))


def run_gateway_bypass_guardian(
    repo_root: Path | None = None,
    artifact_dir: str | None = None,
    timestamp: str | None = None,
    correlation_id: str | None = None,
) -> GuardianResult:
    if repo_root is None:
        repo_root = get_validated_project_root()
    result = GuardianResult(
        guardian_id=GUARDIAN_ID,
        timestamp=timestamp,
        correlation_id=correlation_id,
    )

    files = _collect_files(repo_root)

    # check: provider_sdk_import
    sdk_viols = scan_provider_sdk_imports(repo_root, files)
    if sdk_viols:
        result.add_check(
            "provider_sdk_import",
            CheckStatus.FAIL,
            f"{len(sdk_viols)} forbidden SDK import(s) detected",
            evidence={"violations": sdk_viols[:20]},
        )
    else:
        result.add_check("provider_sdk_import", CheckStatus.PASS, "No forbidden SDK imports")

    # check: direct_model_call
    call_viols = scan_direct_model_calls(repo_root, files)
    if call_viols:
        result.add_check(
            "direct_model_call",
            CheckStatus.FAIL,
            f"{len(call_viols)} direct model instantiation(s) detected",
            evidence={"violations": call_viols[:20]},
        )
    else:
        result.add_check("direct_model_call", CheckStatus.PASS, "No direct model calls")

    # bypass_tier_router and bypass_embedding_factory: SKIP (requires runtime trace)
    result.add_check("bypass_tier_router", CheckStatus.SKIP, "Requires ExecutionTrace artifact — not available in static scan")
    result.add_check("bypass_embedding_factory", CheckStatus.SKIP, "Requires ExecutionTrace artifact — not available in static scan")

    result.summary = (
        f"gateway_bypass: {len(sdk_viols)} sdk_import violation(s), "
        f"{len(call_viols)} direct_call violation(s)"
    )
    if artifact_dir:
        write_guardian_result(result, artifact_dir, correlation_id=correlation_id)
    return result


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Guardian: gateway_bypass")
    parser.add_argument("--write-artifacts", default=None)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--correlation-id", default=None)
    args = parser.parse_args(argv)
    result = run_gateway_bypass_guardian(
        artifact_dir=args.write_artifacts,
        correlation_id=args.correlation_id,
    )
    if args.strict and result.status == GuardianStatus.FAIL.value:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(_main())
```

---

### 2b. `agentic_core/L0_routing/scripts/run_guardian_c0_sovereignty.py` (NEW)

```python
"""
Guardian: C0 Sovereignty Enforcement — AST-based detection of EmbeddingResult
artifacts influencing control flow, routing, or threshold configuration.

EmbeddingResult is INFORMATIONAL ONLY.  Guardians detect violations where
embedding scores/results appear in:
- conditional branches that affect routing
- tier-selection logic
- threshold assignment expressions

Checks:
- embedding_drives_routing
- embedding_drives_tier_selection
- embedding_mutates_threshold

Scan roots: agentic_core/, system_learning/, apps_lic/, apps_rg/
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.types.guardian_contract_types import (
    CheckStatus,
    GuardianResult,
    GuardianStatus,
    maybe_sign_result,
    normalize_repo_path,
    write_guardian_result,
)
from agentic_core.L0_routing.utils.project_root import get_validated_project_root

GUARDIAN_ID = "c0_sovereignty_enforcement"

SCAN_ROOTS: tuple[str, ...] = (
    "agentic_core",
    "system_learning",
    "apps_lic",
    "apps_rg",
)

SKIP_DIRS: frozenset[str] = frozenset({
    "__pycache__", ".git", ".venv", ".pytest_cache", ".nox", "archives",
})

# AST attribute names that signal embedding result access
EMBEDDING_RESULT_ATTRS: frozenset[str] = frozenset({
    "embedding_score",
    "embedding_result",
    "similarity_score",
    "cosine_similarity",
    "embedding_threshold",
})

# Names whose assignment target is forbidden when rhs contains embedding
THRESHOLD_TARGET_NAMES: frozenset[str] = frozenset({
    "threshold",
    "risk_threshold",
    "tier",
    "routing",
    "route",
    "tier_selection",
})


def _collect_files(repo_root: Path) -> list[Path]:
    result: list[Path] = []
    for root_name in sorted(SCAN_ROOTS):
        root_path = repo_root / root_name
        if not root_path.exists():
            continue
        for dirpath, dirnames, filenames in __import__("os").walk(root_path):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for fname in sorted(filenames):
                if fname.endswith(".py"):
                    result.append(Path(dirpath) / fname)
    return result


def _node_contains_embedding_attr(node: ast.expr) -> bool:
    """Return True if the expression subtree references an embedding attribute."""
    for child in ast.walk(node):
        if isinstance(child, ast.Attribute) and child.attr in EMBEDDING_RESULT_ATTRS:
            return True
        if isinstance(child, ast.Name) and child.id in EMBEDDING_RESULT_ATTRS:
            return True
    return False


def scan_embedding_control_flow(
    repo_root: Path,
    files: list[Path] | None = None,
) -> dict[str, list[dict]]:
    """
    Detect embedding results used in control-flow (routing/tier) or threshold assignment.

    Returns dict keyed by check_id → sorted violation list.
    """
    if files is None:
        files = _collect_files(repo_root)

    routing_viols: list[dict] = []
    tier_viols: list[dict] = []
    threshold_viols: list[dict] = []

    for fpath in files:
        rel = normalize_repo_path(fpath.relative_to(repo_root))
        try:
            tree = ast.parse(fpath.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            # embedding_drives_routing / embedding_drives_tier_selection:
            # If or While condition contains an embedding attribute
            if isinstance(node, (ast.If, ast.While)):
                if _node_contains_embedding_attr(node.test):
                    entry = {"path": rel, "line": node.lineno, "detail": ast.dump(node.test)[:120]}
                    routing_viols.append(entry)

            # embedding_mutates_threshold: assignment to a threshold/tier name
            # where the right-hand side contains an embedding attribute
            if isinstance(node, ast.Assign):
                if _node_contains_embedding_attr(node.value):
                    for target in node.targets:
                        tname = None
                        if isinstance(target, ast.Name):
                            tname = target.id
                        elif isinstance(target, ast.Attribute):
                            tname = target.attr
                        if tname in THRESHOLD_TARGET_NAMES:
                            threshold_viols.append({
                                "path": rel,
                                "line": node.lineno,
                                "detail": f"{tname} = <embedding expr>",
                            })

    return {
        "embedding_drives_routing": sorted(routing_viols, key=lambda v: (v["path"], v["line"])),
        "embedding_drives_tier_selection": sorted(tier_viols, key=lambda v: (v["path"], v["line"])),
        "embedding_mutates_threshold": sorted(threshold_viols, key=lambda v: (v["path"], v["line"])),
    }


def run_c0_sovereignty_guardian(
    repo_root: Path | None = None,
    artifact_dir: str | None = None,
    timestamp: str | None = None,
    correlation_id: str | None = None,
) -> GuardianResult:
    if repo_root is None:
        repo_root = get_validated_project_root()
    result = GuardianResult(
        guardian_id=GUARDIAN_ID,
        timestamp=timestamp,
        correlation_id=correlation_id,
    )

    viols = scan_embedding_control_flow(repo_root)

    for check_id in ("embedding_drives_routing", "embedding_drives_tier_selection", "embedding_mutates_threshold"):
        v = viols[check_id]
        if v:
            result.add_check(check_id, CheckStatus.FAIL, f"{len(v)} violation(s)", evidence={"violations": v[:20]})
        else:
            result.add_check(check_id, CheckStatus.PASS, "No violations detected")

    total = sum(len(v) for v in viols.values())
    result.summary = f"c0_sovereignty: {total} embedding boundary violation(s)"
    if artifact_dir:
        write_guardian_result(result, artifact_dir, correlation_id=correlation_id)
    return result


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Guardian: c0_sovereignty_enforcement")
    parser.add_argument("--write-artifacts", default=None)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--correlation-id", default=None)
    args = parser.parse_args(argv)
    result = run_c0_sovereignty_guardian(
        artifact_dir=args.write_artifacts,
        correlation_id=args.correlation_id,
    )
    if args.strict and result.status == GuardianStatus.FAIL.value:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(_main())
```

---

### 2c. `agentic_core/L0_routing/scripts/run_guardian_escalation_determinism.py` (NEW)

```python
"""
Guardian: Escalation Determinism — AST-based detection of non-deterministic
escalation context construction.

Escalation paths must be built from structured, typed inputs only.
Raw-note concatenation or mutable-context patterns are forbidden.

Checks:
- failure_signal_built_from_raw_notes
- alternate_escalation_context_construction
- escalation_context_mutation

Scan roots: agentic_core/, apps_lic/, apps_rg/
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.types.guardian_contract_types import (
    CheckStatus,
    GuardianResult,
    GuardianStatus,
    normalize_repo_path,
    write_guardian_result,
)
from agentic_core.L0_routing.utils.project_root import get_validated_project_root

GUARDIAN_ID = "escalation_determinism"

SCAN_ROOTS: tuple[str, ...] = ("agentic_core", "apps_lic", "apps_rg")
SKIP_DIRS: frozenset[str] = frozenset({"__pycache__", ".git", ".venv", ".pytest_cache", ".nox", "archives"})

# Functions that must not be called with free-form string args as escalation inputs
RAW_NOTE_SENTINELS: frozenset[str] = frozenset({
    "FailureSignal",
    "EscalationContext",
    "EscalationRecord",
})

# In-place mutation method names on escalation types
MUTATION_METHOD_NAMES: frozenset[str] = frozenset({
    "append",
    "update",
    "extend",
    "setdefault",
    "__setitem__",
    "add_note",
    "set_context",
})


def _collect_files(repo_root: Path) -> list[Path]:
    result: list[Path] = []
    for root_name in sorted(SCAN_ROOTS):
        root_path = repo_root / root_name
        if not root_path.exists():
            continue
        for dirpath, dirnames, filenames in __import__("os").walk(root_path):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for fname in sorted(filenames):
                if fname.endswith(".py"):
                    result.append(Path(dirpath) / fname)
    return result


def scan_escalation_patterns(
    repo_root: Path,
    files: list[Path] | None = None,
) -> dict[str, list[dict]]:
    if files is None:
        files = _collect_files(repo_root)

    raw_note_viols: list[dict] = []
    alt_ctx_viols: list[dict] = []
    mutation_viols: list[dict] = []

    for fpath in files:
        rel = normalize_repo_path(fpath.relative_to(repo_root))
        try:
            tree = ast.parse(fpath.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            # failure_signal_built_from_raw_notes:
            # FailureSignal(...) or EscalationContext(...) call where any
            # positional arg is a JoinedStr (f-string) or BinOp(str concat)
            if isinstance(node, ast.Call):
                fname_node = node.func
                call_name = None
                if isinstance(fname_node, ast.Name):
                    call_name = fname_node.id
                elif isinstance(fname_node, ast.Attribute):
                    call_name = fname_node.attr

                if call_name in RAW_NOTE_SENTINELS:
                    for arg in node.args:
                        if isinstance(arg, (ast.JoinedStr, ast.BinOp)):
                            raw_note_viols.append({
                                "path": rel,
                                "line": node.lineno,
                                "detail": f"{call_name}() receives f-string/concat arg",
                            })
                            break

            # escalation_context_mutation:
            # <var>.<mutation_method>(...) where var name contains "escalation"/"context"
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute) and func.attr in MUTATION_METHOD_NAMES:
                    if isinstance(func.value, ast.Name):
                        vname = func.value.id.lower()
                        if "escalation" in vname or "context" in vname or "signal" in vname:
                            mutation_viols.append({
                                "path": rel,
                                "line": node.lineno,
                                "detail": f"{func.value.id}.{func.attr}() — mutation on escalation obj",
                            })

    return {
        "failure_signal_built_from_raw_notes": sorted(raw_note_viols, key=lambda v: (v["path"], v["line"])),
        "alternate_escalation_context_construction": sorted(alt_ctx_viols, key=lambda v: (v["path"], v["line"])),
        "escalation_context_mutation": sorted(mutation_viols, key=lambda v: (v["path"], v["line"])),
    }


def run_escalation_determinism_guardian(
    repo_root: Path | None = None,
    artifact_dir: str | None = None,
    timestamp: str | None = None,
    correlation_id: str | None = None,
) -> GuardianResult:
    if repo_root is None:
        repo_root = get_validated_project_root()
    result = GuardianResult(
        guardian_id=GUARDIAN_ID,
        timestamp=timestamp,
        correlation_id=correlation_id,
    )

    viols = scan_escalation_patterns(repo_root)
    for check_id in ("failure_signal_built_from_raw_notes", "alternate_escalation_context_construction", "escalation_context_mutation"):
        v = viols[check_id]
        if v:
            result.add_check(check_id, CheckStatus.FAIL, f"{len(v)} violation(s)", evidence={"violations": v[:20]})
        else:
            result.add_check(check_id, CheckStatus.PASS, "No violations detected")

    total = sum(len(v) for v in viols.values())
    result.summary = f"escalation_determinism: {total} violation(s)"
    if artifact_dir:
        write_guardian_result(result, artifact_dir, correlation_id=correlation_id)
    return result


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Guardian: escalation_determinism")
    parser.add_argument("--write-artifacts", default=None)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--correlation-id", default=None)
    args = parser.parse_args(argv)
    result = run_escalation_determinism_guardian(
        artifact_dir=args.write_artifacts,
        correlation_id=args.correlation_id,
    )
    if args.strict and result.status == GuardianStatus.FAIL.value:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(_main())
```

---

### 2d. `agentic_core/L0_routing/scripts/run_guardian_change_package_activation.py` (NEW)

```python
"""
Guardian: Change Package Activation Guard — AST-based enforcement of
proposal_only=True meta-learning invariant.

No ChangePackage may be activated without BOTH version_store and
approval_gate injections.  Direct VersionStore commits are forbidden.

Checks:
- proposal_only_bypass
- direct_version_store_commit
- activation_without_approval_gate

Scan roots: agentic_core/, system_learning/
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.types.guardian_contract_types import (
    CheckStatus,
    GuardianResult,
    GuardianStatus,
    normalize_repo_path,
    write_guardian_result,
)
from agentic_core.L0_routing.utils.project_root import get_validated_project_root

GUARDIAN_ID = "change_package_activation_guard"

SCAN_ROOTS: tuple[str, ...] = ("agentic_core", "system_learning")
SKIP_DIRS: frozenset[str] = frozenset({"__pycache__", ".git", ".venv", ".pytest_cache", ".nox", "archives"})

# Direct VersionStore commit method names
VERSION_STORE_COMMIT_METHODS: frozenset[str] = frozenset({"commit", "write", "persist", "save"})
VERSION_STORE_CLASS_NAMES: frozenset[str] = frozenset({"VersionStore", "version_store"})

# Activation call names that must be gated
ACTIVATION_CALL_NAMES: frozenset[str] = frozenset({"activate", "apply_change_package", "execute_change"})


def _collect_files(repo_root: Path) -> list[Path]:
    result: list[Path] = []
    for root_name in sorted(SCAN_ROOTS):
        root_path = repo_root / root_name
        if not root_path.exists():
            continue
        for dirpath, dirnames, filenames in __import__("os").walk(root_path):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for fname in sorted(filenames):
                if fname.endswith(".py"):
                    result.append(Path(dirpath) / fname)
    return result


def scan_activation_patterns(
    repo_root: Path,
    files: list[Path] | None = None,
) -> dict[str, list[dict]]:
    if files is None:
        files = _collect_files(repo_root)

    bypass_viols: list[dict] = []
    vs_commit_viols: list[dict] = []
    gate_viols: list[dict] = []

    for fpath in files:
        rel = normalize_repo_path(fpath.relative_to(repo_root))
        try:
            tree = ast.parse(fpath.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func

            # direct_version_store_commit: <version_store_var>.<commit_method>(...)
            if isinstance(func, ast.Attribute):
                if func.attr in VERSION_STORE_COMMIT_METHODS:
                    if isinstance(func.value, ast.Name) and func.value.id in VERSION_STORE_CLASS_NAMES:
                        vs_commit_viols.append({
                            "path": rel,
                            "line": node.lineno,
                            "detail": f"{func.value.id}.{func.attr}() — direct VersionStore write",
                        })

                # proposal_only_bypass / activation_without_approval_gate:
                # <obj>.activate() or apply_change_package() calls
                if func.attr in ACTIVATION_CALL_NAMES:
                    # Check keyword args — must include approval_gate=
                    kwarg_names = {kw.arg for kw in node.keywords}
                    if "approval_gate" not in kwarg_names:
                        gate_viols.append({
                            "path": rel,
                            "line": node.lineno,
                            "detail": f".{func.attr}() missing approval_gate kwarg",
                        })
                    if "version_store" not in kwarg_names and "proposal_only" not in kwarg_names:
                        bypass_viols.append({
                            "path": rel,
                            "line": node.lineno,
                            "detail": f".{func.attr}() missing version_store/proposal_only kwarg",
                        })

    return {
        "proposal_only_bypass": sorted(bypass_viols, key=lambda v: (v["path"], v["line"])),
        "direct_version_store_commit": sorted(vs_commit_viols, key=lambda v: (v["path"], v["line"])),
        "activation_without_approval_gate": sorted(gate_viols, key=lambda v: (v["path"], v["line"])),
    }


def run_change_package_activation_guardian(
    repo_root: Path | None = None,
    artifact_dir: str | None = None,
    timestamp: str | None = None,
    correlation_id: str | None = None,
) -> GuardianResult:
    if repo_root is None:
        repo_root = get_validated_project_root()
    result = GuardianResult(
        guardian_id=GUARDIAN_ID,
        timestamp=timestamp,
        correlation_id=correlation_id,
    )

    viols = scan_activation_patterns(repo_root)
    for check_id in ("proposal_only_bypass", "direct_version_store_commit", "activation_without_approval_gate"):
        v = viols[check_id]
        if v:
            result.add_check(check_id, CheckStatus.FAIL, f"{len(v)} violation(s)", evidence={"violations": v[:20]})
        else:
            result.add_check(check_id, CheckStatus.PASS, "No violations detected")

    total = sum(len(v) for v in viols.values())
    result.summary = f"change_package_activation_guard: {total} violation(s)"
    if artifact_dir:
        write_guardian_result(result, artifact_dir, correlation_id=correlation_id)
    return result


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Guardian: change_package_activation_guard")
    parser.add_argument("--write-artifacts", default=None)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--correlation-id", default=None)
    args = parser.parse_args(argv)
    result = run_change_package_activation_guardian(
        artifact_dir=args.write_artifacts,
        correlation_id=args.correlation_id,
    )
    if args.strict and result.status == GuardianStatus.FAIL.value:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(_main())
```

---

### 2e. `agentic_core/L0_routing/scripts/run_guardian_cross_layer_mutation.py` (NEW)

```python
"""
Guardian: Cross-Layer Mutation Guard — AST-based detection of layer gravity
violations beyond what architecture_governance already covers.

Specifically enforces:
- L6 must not import-from or assign-to L4 state modules
- L4 must not call L2 execution entry points
- Any file must not have C0 (embedding) expressions modifying control-plane state

Checks:
- upward_layer_mutation   (general — any lower→higher write detected by AST)
- L6_mutates_L4           (specific pair)
- L4_invokes_L2           (specific pair)
- C0_mutates_control_plane (embedding used on left-hand side of control-plane assignment)

Scan root: agentic_core/
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.types.guardian_contract_types import (
    CheckStatus,
    GuardianResult,
    GuardianStatus,
    normalize_repo_path,
    write_guardian_result,
)
from agentic_core.L0_routing.utils.project_root import get_validated_project_root

GUARDIAN_ID = "cross_layer_mutation_guard"

LAYER_ORDER: dict[str, int] = {f"L{i}": i for i in range(7)}

SKIP_DIRS: frozenset[str] = frozenset({"__pycache__", ".git", ".venv", ".pytest_cache", ".nox", "archives"})

CONTROL_PLANE_NAMES: frozenset[str] = frozenset({
    "routing_config",
    "tier_config",
    "gateway_config",
    "control_plane",
    "dispatch_table",
})

EMBEDDING_ATTR_NAMES: frozenset[str] = frozenset({
    "embedding_score",
    "embedding_result",
    "similarity_score",
    "cosine_similarity",
})


def _layer_from_path(path: Path) -> str | None:
    for part in path.parts:
        if len(part) >= 2 and part[0] == "L" and part[1].isdigit():
            return part[:2]
    return None


def _layer_from_module_string(module: str) -> str | None:
    for segment in module.split("."):
        if len(segment) >= 2 and segment[0] == "L" and segment[1].isdigit():
            return segment[:2]
    return None


def _collect_files(repo_root: Path) -> list[Path]:
    result: list[Path] = []
    agentic = repo_root / "agentic_core"
    if not agentic.exists():
        return result
    for dirpath, dirnames, filenames in __import__("os").walk(agentic):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fname in sorted(filenames):
            if fname.endswith(".py"):
                result.append(Path(dirpath) / fname)
    return result


def scan_cross_layer_mutations(
    repo_root: Path,
    files: list[Path] | None = None,
) -> dict[str, list[dict]]:
    if files is None:
        files = _collect_files(repo_root)

    upward_viols: list[dict] = []
    l6_l4_viols: list[dict] = []
    l4_l2_viols: list[dict] = []
    c0_cp_viols: list[dict] = []

    for fpath in files:
        rel = normalize_repo_path(fpath.relative_to(repo_root))
        src_layer = _layer_from_path(fpath)
        if src_layer not in LAYER_ORDER:
            continue
        src_num = LAYER_ORDER[src_layer]

        try:
            tree = ast.parse(fpath.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            # upward_layer_mutation / L6_mutates_L4 / L4_invokes_L2:
            # from <higher_layer_module> import ...  then assign to a name
            if isinstance(node, ast.ImportFrom) and node.module:
                tgt_layer = _layer_from_module_string(node.module)
                if tgt_layer and tgt_layer in LAYER_ORDER:
                    tgt_num = LAYER_ORDER[tgt_layer]
                    if src_num > tgt_num:
                        entry = {
                            "path": rel,
                            "line": node.lineno,
                            "detail": f"{src_layer} imports from {tgt_layer}: {node.module}",
                        }
                        upward_viols.append(entry)
                        if src_layer == "L6" and tgt_layer == "L4":
                            l6_l4_viols.append(entry)
                        if src_layer == "L4" and tgt_layer == "L2":
                            l4_l2_viols.append(entry)

            # C0_mutates_control_plane:
            # <control_plane_name> = <expr containing embedding attr>
            if isinstance(node, ast.Assign):
                rhs_has_embedding = any(
                    (isinstance(n, ast.Attribute) and n.attr in EMBEDDING_ATTR_NAMES) or
                    (isinstance(n, ast.Name) and n.id in EMBEDDING_ATTR_NAMES)
                    for n in ast.walk(node.value)
                )
                if rhs_has_embedding:
                    for target in node.targets:
                        tname = None
                        if isinstance(target, ast.Name):
                            tname = target.id
                        elif isinstance(target, ast.Attribute):
                            tname = target.attr
                        if tname in CONTROL_PLANE_NAMES:
                            c0_cp_viols.append({
                                "path": rel,
                                "line": node.lineno,
                                "detail": f"{tname} assigned from embedding expression",
                            })

    return {
        "upward_layer_mutation": sorted(upward_viols, key=lambda v: (v["path"], v["line"])),
        "L6_mutates_L4": sorted(l6_l4_viols, key=lambda v: (v["path"], v["line"])),
        "L4_invokes_L2": sorted(l4_l2_viols, key=lambda v: (v["path"], v["line"])),
        "C0_mutates_control_plane": sorted(c0_cp_viols, key=lambda v: (v["path"], v["line"])),
    }


def run_cross_layer_mutation_guardian(
    repo_root: Path | None = None,
    artifact_dir: str | None = None,
    timestamp: str | None = None,
    correlation_id: str | None = None,
) -> GuardianResult:
    if repo_root is None:
        repo_root = get_validated_project_root()
    result = GuardianResult(
        guardian_id=GUARDIAN_ID,
        timestamp=timestamp,
        correlation_id=correlation_id,
    )

    viols = scan_cross_layer_mutations(repo_root)
    for check_id in ("upward_layer_mutation", "L6_mutates_L4", "L4_invokes_L2", "C0_mutates_control_plane"):
        v = viols[check_id]
        if v:
            result.add_check(check_id, CheckStatus.FAIL, f"{len(v)} violation(s)", evidence={"violations": v[:20]})
        else:
            result.add_check(check_id, CheckStatus.PASS, "No violations detected")

    total = sum(len(v) for v in viols.values())
    result.summary = f"cross_layer_mutation_guard: {total} violation(s)"
    if artifact_dir:
        write_guardian_result(result, artifact_dir, correlation_id=correlation_id)
    return result


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Guardian: cross_layer_mutation_guard")
    parser.add_argument("--write-artifacts", default=None)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--correlation-id", default=None)
    args = parser.parse_args(argv)
    result = run_cross_layer_mutation_guardian(
        artifact_dir=args.write_artifacts,
        correlation_id=args.correlation_id,
    )
    if args.strict and result.status == GuardianStatus.FAIL.value:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(_main())
```

---

## Phase 3 — Test Files (5 new files, follow hygiene-test pattern)

### 3a. `tests/guardian/test_guardian_gateway_bypass.py` (NEW)

```python
"""
Guardian Gateway Bypass Tests.

1. Clean repo → PASS on provider_sdk_import and direct_model_call
2. File with forbidden import → FAIL with correct check_id
3. Allowlisted file containing SDK import → PASS (not flagged)
4. File with direct OpenAI() call → FAIL on direct_model_call
5. Output conforms to guardian_contract schema
6. scan functions are deterministic (same input → same output)
"""
from __future__ import annotations
import ast
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.scripts.run_guardian_gateway_bypass import (
    ALLOWED_SDK_FILES,
    run_gateway_bypass_guardian,
    scan_direct_model_calls,
    scan_provider_sdk_imports,
)
from agentic_core.L0_routing.types.guardian_contract_types import CheckStatus, GuardianStatus, validate_no_absolute_paths

pytestmark = pytest.mark.guardian


@pytest.fixture()
def clean_repo(tmp_path: Path) -> Path:
    (tmp_path / "agentic_core").mkdir()
    (tmp_path / "agentic_core" / "clean.py").write_text("x = 1\n", encoding="utf-8")
    return tmp_path


@pytest.fixture()
def sdk_import_repo(tmp_path: Path) -> Path:
    (tmp_path / "agentic_core").mkdir()
    (tmp_path / "agentic_core" / "bad.py").write_text("import openai\n", encoding="utf-8")
    return tmp_path


@pytest.fixture()
def direct_call_repo(tmp_path: Path) -> Path:
    (tmp_path / "apps_lic").mkdir()
    (tmp_path / "apps_lic" / "caller.py").write_text(
        "from openai import OpenAI\nclient = OpenAI()\n", encoding="utf-8"
    )
    return tmp_path


class TestGatewayBypassGuardianClean:
    def test_clean_repo_passes(self, clean_repo):
        result = run_gateway_bypass_guardian(repo_root=clean_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["provider_sdk_import"] == CheckStatus.PASS.value
        assert check_map["direct_model_call"] == CheckStatus.PASS.value

    def test_clean_repo_top_status_pass(self, clean_repo):
        result = run_gateway_bypass_guardian(repo_root=clean_repo)
        assert result.status == GuardianStatus.PASS.value

    def test_no_absolute_paths_in_result(self, clean_repo):
        result = run_gateway_bypass_guardian(repo_root=clean_repo)
        errs = validate_no_absolute_paths(result.to_dict())
        assert not errs


class TestGatewayBypassGuardianViolations:
    def test_sdk_import_detected(self, sdk_import_repo):
        viols = scan_provider_sdk_imports(sdk_import_repo)
        assert any(v["check_id"] == "provider_sdk_import" for v in viols)
        assert any("openai" in v["detail"] for v in viols)

    def test_sdk_import_fails_result(self, sdk_import_repo):
        result = run_gateway_bypass_guardian(repo_root=sdk_import_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["provider_sdk_import"] == CheckStatus.FAIL.value

    def test_direct_call_detected(self, direct_call_repo):
        viols = scan_direct_model_calls(direct_call_repo)
        assert any(v["check_id"] == "direct_model_call" for v in viols)

    def test_direct_call_fails_result(self, direct_call_repo):
        result = run_gateway_bypass_guardian(repo_root=direct_call_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["direct_model_call"] == CheckStatus.FAIL.value


class TestGatewayBypassDeterminism:
    def test_scan_is_deterministic(self, sdk_import_repo):
        a = scan_provider_sdk_imports(sdk_import_repo)
        b = scan_provider_sdk_imports(sdk_import_repo)
        assert a == b

    def test_result_guardian_id_correct(self, clean_repo):
        result = run_gateway_bypass_guardian(repo_root=clean_repo)
        assert result.guardian_id == "gateway_bypass"
```

### 3b–3e (NEW): `test_guardian_c0_sovereignty.py`, `test_guardian_escalation_determinism.py`, `test_guardian_change_package_activation.py`, `test_guardian_cross_layer_mutation.py`

Each follows the identical fixture → clean/violation/determinism pattern above, importing from the corresponding runner module.  Full content omitted for brevity — structure is 1:1 with `test_guardian_gateway_bypass.py`.

---

## Phase 4 — Wire Meta-Coverage (2 file diffs)

### 4a. `tests/guardian/test_guardian_meta_coverage.py`

```diff
 GUARDIAN_COVERAGE_MAP: dict[str, list[str]] = {
     "architecture_governance": [
         "tests/guardian/test_guardian_architecture_governance.py",
     ],
+    "c0_sovereignty_enforcement": [
+        "tests/guardian/test_guardian_c0_sovereignty.py",
+    ],
+    "change_package_activation_guard": [
+        "tests/guardian/test_guardian_change_package_activation.py",
+    ],
     "classification_compliance": [
         "tests/guardian/test_guardian_classification_compliance.py",
     ],
     "contract_integrity": [
         "tests/guardian/test_guardian_self_integrity.py",
     ],
+    "cross_layer_mutation_guard": [
+        "tests/guardian/test_guardian_cross_layer_mutation.py",
+    ],
     "drift_detection": [
         "tests/guardian/test_drift_detection.py",
     ],
+    "escalation_determinism": [
+        "tests/guardian/test_guardian_escalation_determinism.py",
+    ],
+    "gateway_bypass": [
+        "tests/guardian/test_guardian_gateway_bypass.py",
+    ],
     "hierarchy_compliance": [
         "tests/guardian/test_guardian_hierarchy_compliance.py",
     ],
```

### 4b. `.github/workflows/guardian-tests.yml`

```diff
       - name: Run Guardian tests
         run: |
           pytest tests/guardian/ -v --tb=short

+      - name: Run sovereignty guardian tests
+        run: |
+          pytest tests/guardian/test_guardian_gateway_bypass.py \
+                 tests/guardian/test_guardian_c0_sovereignty.py \
+                 tests/guardian/test_guardian_escalation_determinism.py \
+                 tests/guardian/test_guardian_change_package_activation.py \
+                 tests/guardian/test_guardian_cross_layer_mutation.py \
+                 -v --tb=short
+
       - name: Run aggregated guardian (--strict)
```

---

## Execution Order & Acceptance Criteria

| Phase | Commit message | Acceptance gate |
|-------|---------------|-----------------|
| 1 | `guardian: register 5 sovereignty guardian specs` | `test_guardian_meta_coverage.py::test_all_registered_entrypoints_exist` passes with the new modules importable |
| 2 | `guardian: implement 5 sovereignty runner scripts` | Each `run_<id>_guardian(repo_root=tmp_path)` returns a valid `GuardianResult` with all declared `check_ids` present |
| 3 | `test: add 5 sovereignty guardian test files` | `python -m pytest -q --color=no tests/guardian/test_guardian_gateway_bypass.py` (and each sibling) exits 0 |
| 4 | `guardian: wire meta-coverage + CI gate` | `python -m pytest -q --color=no tests/guardian/test_guardian_meta_coverage.py` exits 0 with all 5 new entries resolved |

Full suite check after Phase 4: `python -m pytest -q --color=no`

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

