#!/usr/bin/env python3
"""
Agentic-L5 Windsurf Validator (Final, L5-Ready)

- Reads policy from:      scripts/validation_config.yaml
- Writes results to:      windsurf_rules/windsurf_validation_keys.json
- Writes summary to:      VALIDATION_KEYS_SUMMARY.md

Implements:
- External YAML config with documented rationale
- L1–L5 layer purity via config-driven rules and AST
- Engine isolation (no cross-engine imports unless allowed by config)
- Prompt governance: schema-first + inline prompt detection
- Circular import detection with configurable early-exit
- Hardened subprocess execution (ruff, mypy, pytest) with circuit breaker
- Zero-loss DAG execution check (config-driven)
- Severity taxonomy: PASS/WARN/FAIL/CRITICAL/UNVALIDATED
- Atomic JSON writing
- Structured logging (JSON) with run_id + phase + duration
- Observability config used to enforce validator-phase timing/logging behavior
- Honest UNVALIDATED for unimplemented categories
"""

from __future__ import annotations

import ast
import dataclasses
import enum
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
import uuid
from collections import defaultdict
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

import yaml


# =============================================================================
# PATHS
# =============================================================================

PROJECT_ROOT = Path(".").resolve()
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
CONFIG_PATH = SCRIPTS_DIR / "validation_config.yaml"
RULES_PATH = PROJECT_ROOT / "windsurf_rules" / "windsurf_validation_keys.json"
SUMMARY_PATH = PROJECT_ROOT / "VALIDATION_KEYS_SUMMARY.md"


# =============================================================================
# LOGGING (Structured, per-phase)
# =============================================================================

logging.basicConfig(
    format='{"time":"%(asctime)s","level":"%(levelname)s",'
           '"phase":"%(phase)s","run_id":"%(run_id)s","msg":"%(message)s"}',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# =============================================================================
# SEVERITY & RESULT TYPES
# =============================================================================

class Severity(enum.Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    CRITICAL = "CRITICAL"
    UNVALIDATED = "UNVALIDATED"


@dataclasses.dataclass
class ValidationResult:
    severity: Severity
    message: str = ""
    error: Optional[str] = None

    def as_bool(self) -> bool:
        """
        Boolean representation for Windsurf JSON:
        Only PASS is True; all other severities are False.
        """
        return self.severity == Severity.PASS


# =============================================================================
# CONFIG
# =============================================================================

def load_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise RuntimeError(f"Missing config file: {CONFIG_PATH}")
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


CONFIG: Dict[str, Any] = load_config()


# =============================================================================
# UTILS
# =============================================================================

def atomic_write_json(path: Path, content: Dict[str, Any]) -> None:
    """Atomically write JSON to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = tempfile.NamedTemporaryFile("w", delete=False, dir=str(path.parent))
    try:
        json.dump(content, tmp, indent=2)
        tmp.flush()
        os.fsync(tmp.fileno())
    finally:
        tmp.close()
    shutil.move(tmp.name, path)


def safe_read_file(path: Path) -> Tuple[bool, Optional[str], Optional[str]]:
    """Safely read a file with size guards and full traceback on error."""
    try:
        size = path.stat().st_size
        max_size = CONFIG["structure"]["max_file_size_bytes"]
        if size > max_size:
            return False, None, f"File too large: {size} bytes > {max_size}"
        with path.open("r", encoding="utf-8", errors="replace") as f:
            return True, f.read(), None
    except Exception as e:  # noqa: BLE001
        return False, None, f"{type(e).__name__}: {e}\n{traceback.format_exc()}"


def ast_parse_file(path: Path) -> Tuple[Optional[ast.AST], Optional[str]]:
    ok, content, err = safe_read_file(path)
    if not ok or content is None:
        return None, err
    try:
        return ast.parse(content), None
    except SyntaxError as e:
        return None, f"SyntaxError in {path}: {e}"


def run_subprocess(cmd: List[str], *, label: str, timeout: int) -> Tuple[Severity, str]:
    """Hardened subprocess with timeouts, output limits, no shell."""
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(PROJECT_ROOT),
            shell=False,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
    except subprocess.TimeoutExpired:
        return Severity.CRITICAL, f"{label} timed out after {timeout}s"
    except Exception as e:  # noqa: BLE001
        return Severity.CRITICAL, f"{label} failed to start: {e}"

    out = (proc.stdout or "") + (proc.stderr or "")
    if len(out.encode("utf-8")) > CONFIG["security"]["max_subprocess_output_bytes"]:
        return Severity.CRITICAL, f"{label} output exceeded max size limit"

    if proc.returncode != 0:
        return Severity.FAIL, f"{label} exited {proc.returncode}: {proc.stderr.strip()}"

    return Severity.PASS, ""


@contextmanager
def validation_phase(name: str, run_id: str):
    """
    Wrap a validation phase:
      - Injects phase + run_id into structured logs
      - Tracks duration and compares with observability.max_phase_duration_ms
    """
    start = time.monotonic()
    old_factory = logging.getLogRecordFactory()
    max_ms = CONFIG.get("observability", {}).get("max_phase_duration_ms", 5000)

    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.phase = name
        record.run_id = run_id
        return record

    logging.setLogRecordFactory(record_factory)
    logger.info("phase_start")
    try:
        yield
    finally:
        duration_ms = (time.monotonic() - start) * 1000.0
        if duration_ms > max_ms:
            logger.warning(
                f"phase_duration_exceeded threshold_ms={max_ms} actual_ms={duration_ms:.1f}"
            )
        else:
            logger.info(
                f"phase_duration_ok threshold_ms={max_ms} actual_ms={duration_ms:.1f}"
            )
        logging.setLogRecordFactory(old_factory)


# =============================================================================
# STRUCTURE & HYGIENE
# =============================================================================

def validate_structure() -> Dict[str, ValidationResult]:
    results: Dict[str, ValidationResult] = {}

    max_allowed = CONFIG["structure"]["max_depth"]
    max_depth = 0
    empty_dirs = 0

    for root, dirs, files in os.walk(PROJECT_ROOT):
        if ".git" in root:
            continue
        depth = len(Path(root).relative_to(PROJECT_ROOT).parts)
        max_depth = max(max_depth, depth)
        if not dirs and not files:
            empty_dirs += 1

    if max_depth > max_allowed:
        results["max_depth_respected"] = ValidationResult(
            Severity.FAIL,
            f"Max depth {max_depth} > allowed {max_allowed}",
        )
    else:
        results["max_depth_respected"] = ValidationResult(Severity.PASS)

    if empty_dirs > CONFIG["structure"]["max_empty_dirs"]:
        results["no_empty_directories"] = ValidationResult(
            Severity.FAIL,
            f"{empty_dirs} empty directories found",
        )
    else:
        results["no_empty_directories"] = ValidationResult(Severity.PASS)

    return results


# =============================================================================
# LAYER PURITY (L1–L5) VIA AST
# =============================================================================

def _violations_for_layer(layer_dir: Path, rules: Dict[str, Any]) -> List[str]:
    violations: List[str] = []
    forbidden_imports: List[str] = rules.get("forbidden_imports", [])
    forbidden_calls: List[str] = rules.get("forbidden_calls", [])

    for py in layer_dir.rglob("*.py"):
        tree, err = ast_parse_file(py)
        if err:
            violations.append(f"{py}: {err}")
            continue

        # Imports
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                mod = node.module
                for fimp in forbidden_imports:
                    if fimp in mod:
                        violations.append(f"{py}: forbidden import '{mod}' (rule={fimp})")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name
                    for fimp in forbidden_imports:
                        if fimp in name:
                            violations.append(f"{py}: forbidden import '{name}' (rule={fimp})")

        # Calls
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = None
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr

                if func_name and func_name in forbidden_calls:
                    violations.append(f"{py}: forbidden call '{func_name}'")

    return violations


def validate_layer_purity() -> Dict[str, ValidationResult]:
    results: Dict[str, ValidationResult] = {}
    layer_hierarchy = CONFIG.get("layer_rules", {}).get("hierarchy", {})

    for layer_name, rules in layer_hierarchy.items():
        layer_dir = PROJECT_ROOT / "agentic_core" / layer_name
        if not layer_dir.exists():
            results[f"{layer_name}_exists"] = ValidationResult(
                Severity.WARN,
                f"{layer_name} directory missing",
            )
            continue

        violations = _violations_for_layer(layer_dir, rules)
        if violations:
            results[f"{layer_name}_purity"] = ValidationResult(
                Severity.FAIL,
                f"{len(violations)} violations",
                "\n".join(violations[:10]),
            )
        else:
            results[f"{layer_name}_purity"] = ValidationResult(Severity.PASS)

    return results


# =============================================================================
# ENGINE ISOLATION
# =============================================================================

def validate_engine_isolation() -> Dict[str, ValidationResult]:
    results: Dict[str, ValidationResult] = {}
    engines_cfg = CONFIG.get("engines", {})
    root_rel = engines_cfg.get("root", "agentic_core/l2_execution/engines")
    engines_root = PROJECT_ROOT / root_rel

    if not engines_root.exists():
        results["engines_root_exists"] = ValidationResult(
            Severity.WARN,
            f"Engines root missing: {engines_root}",
        )
        return results

    engine_names = [d.name for d in engines_root.iterdir() if d.is_dir()]
    cross_allowed = engines_cfg.get("cross_engine_sharing_allowed", False)

    violations: List[str] = []

    for engine in engine_names:
        for py in (engines_root / engine).rglob("*.py"):
            tree, err = ast_parse_file(py)
            if err:
                violations.append(f"{py}: {err}")
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    for other in engine_names:
                        if other == engine:
                            continue
                        if f".engines.{other}" in node.module:
                            violations.append(
                                f"{py}: engine '{engine}' imports '{other}' via {node.module}"
                            )

    if cross_allowed:
        if violations:
            results["no_cross_engine_imports"] = ValidationResult(
                Severity.WARN,
                "Cross-engine imports present (allowed but tracked)",
                "\n".join(violations[:10]),
            )
        else:
            results["no_cross_engine_imports"] = ValidationResult(Severity.PASS)
    else:
        if violations:
            results["no_cross_engine_imports"] = ValidationResult(
                Severity.FAIL,
                f"{len(violations)} cross-engine imports",
                "\n".join(violations[:10]),
            )
        else:
            results["no_cross_engine_imports"] = ValidationResult(Severity.PASS)

    return results


# =============================================================================
# PROMPT GOVERNANCE
# =============================================================================

def validate_prompt_governance() -> Dict[str, ValidationResult]:
    results: Dict[str, ValidationResult] = {}
    prompts_cfg = CONFIG.get("prompts", {})
    max_len = prompts_cfg.get("max_inline_prompt_length", 200)
    indicators = prompts_cfg.get("inline_prompt_indicators", [])
    schema_dir_rel = prompts_cfg.get("required_schema_directory", "prompt_governance/schemas")

    # Schema presence
    schema_dir = PROJECT_ROOT / schema_dir_rel
    if not schema_dir.exists() or not any(schema_dir.glob("*.json")):
        results["prompts_have_schemas"] = ValidationResult(
            Severity.FAIL,
            f"No prompt schemas found in {schema_dir}",
        )
    else:
        results["prompts_have_schemas"] = ValidationResult(Severity.PASS)

    # Inline prompts (anti-pattern) in agentic_core/**
    inline_violations: List[str] = []
    agentic_core = PROJECT_ROOT / "agentic_core"
    if agentic_core.exists():
        for py in agentic_core.rglob("*.py"):
            tree, err = ast_parse_file(py)
            if err:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    s = node.value
                    if len(s) >= max_len:
                        lower = s.lower()
                        if any(ind.lower() in lower for ind in indicators):
                            inline_violations.append(f"{py}:{node.lineno}")

    if inline_violations:
        results["no_inline_prompts"] = ValidationResult(
            Severity.FAIL,
            f"{len(inline_violations)} inline prompts found",
            "\n".join(inline_violations[:10]),
        )
    else:
        results["no_inline_prompts"] = ValidationResult(Severity.PASS)

    return results


# =============================================================================
# SUBPROCESS VALIDATION (ruff, mypy, pytest) with CIRCUIT BREAKER
# =============================================================================

def validate_tooling() -> Dict[str, ValidationResult]:
    results: Dict[str, ValidationResult] = {}
    timeout = CONFIG["security"]["subprocess_timeout_seconds"]
    python_exec = CONFIG["security"]["python_executable"]

    tools = [
        ("ruff", [python_exec, "-m", "ruff", "check", "--quiet"]),
        ("mypy", [python_exec, "-m", "mypy", "."]),
        ("pytest", [python_exec, "-m", "pytest", "-x", "--tb=short"]),
    ]

    critical_failure = False
    for tool, cmd in tools:
        key = f"{tool}_zero_errors"
        if critical_failure:
            results[key] = ValidationResult(
                Severity.UNVALIDATED,
                "Skipped due to prior critical failure",
            )
            continue

        sev, msg = run_subprocess(cmd, label=tool, timeout=timeout)
        results[key] = ValidationResult(sev, msg)
        if sev == Severity.CRITICAL:
            critical_failure = True

    return results


# =============================================================================
# CIRCULAR IMPORT DETECTION
# =============================================================================

def _build_import_graph() -> Dict[str, Set[str]]:
    graph: Dict[str, Set[str]] = defaultdict(set)
    agentic_core = PROJECT_ROOT / "agentic_core"
    if not agentic_core.exists():
        return graph

    for py in agentic_core.rglob("*.py"):
        module_name = (
            str(py.relative_to(PROJECT_ROOT))
            .replace(os.sep, ".")
            .replace(".py", "")
        )
        tree, err = ast_parse_file(py)
        if err:
            continue
        imports: Set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module.startswith("agentic_core"):
                    imports.add(node.module)
        graph[module_name] |= imports

    return graph


def _find_cycles(graph: Dict[str, Set[str]], max_cycles: int) -> List[List[str]]:
    visited: Set[str] = set()
    visiting: Set[str] = set()
    stack: List[str] = []
    cycles: List[List[str]] = []

    def dfs(node: str):
        if node in visited or len(cycles) >= max_cycles:
            return
        visiting.add(node)
        stack.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in graph:
                continue
            if neighbor in visiting:
                try:
                    idx = stack.index(neighbor)
                    cycle = stack[idx:] + [neighbor]
                    cycles.append(cycle)
                    if len(cycles) >= max_cycles:
                        return
                except ValueError:
                    pass
            elif neighbor not in visited:
                dfs(neighbor)
                if len(cycles) >= max_cycles:
                    return
        visiting.remove(node)
        visited.add(node)
        stack.pop()

    for node in graph:
        if node not in visited and len(cycles) < max_cycles:
            dfs(node)
            if len(cycles) >= max_cycles:
                break

    return cycles


def validate_circular_imports() -> Dict[str, ValidationResult]:
    results: Dict[str, ValidationResult] = {}
    cfg = CONFIG.get("circular_imports", {})
    if not cfg.get("enabled", True):
        results["no_circular_imports"] = ValidationResult(
            Severity.UNVALIDATED,
            "Circular import detection disabled in config",
        )
        return results

    max_cycles_to_find = cfg.get("max_cycles_to_find", 20)
    graph = _build_import_graph()
    cycles = _find_cycles(graph, max_cycles=max_cycles_to_find)
    max_display = cfg.get("max_cycles_displayed", 5)

    if cycles:
        pretty = [" -> ".join(cycle) for cycle in cycles[:max_display]]
        results["no_circular_imports"] = ValidationResult(
            Severity.CRITICAL,
            f"{len(cycles)} circular import cycles detected (max {max_cycles_to_find} checked)",
            "\n".join(pretty),
        )
    else:
        results["no_circular_imports"] = ValidationResult(Severity.PASS)

    return results


# =============================================================================
# ZERO-LOSS DAG EXECUTION
# =============================================================================

def validate_zero_loss() -> Dict[str, ValidationResult]:
    results: Dict[str, ValidationResult] = {}
    zcfg = CONFIG.get("zeroloss", {})

    require_exec = zcfg.get("require_dag_execution", True)
    if not require_exec:
        results["dag_execution_completes"] = ValidationResult(
            Severity.UNVALIDATED,
            "DAG execution not required by config",
        )
        return results

    try:
        framework = __import__("agentic_core.l3_orchestration.framework", fromlist=["*"])
        create_dag = getattr(framework, "create_dag", None)
        validate_dag = getattr(framework, "validate_dag", None)
        execute_dag = getattr(framework, "execute_dag", None)
        if not create_dag or not validate_dag or not execute_dag:
            results["dag_execution_completes"] = ValidationResult(
                Severity.UNVALIDATED,
                "framework.create_dag/validate_dag/execute_dag missing",
            )
            return results

        dag = create_dag("zero-loss-test")
        is_valid = bool(validate_dag(dag))
        result = execute_dag(dag)
        status = getattr(getattr(result, "status", None), "value", None)
        ok = is_valid and status == "COMPLETED"

        if ok:
            results["dag_execution_completes"] = ValidationResult(Severity.PASS)
        else:
            results["dag_execution_completes"] = ValidationResult(
                Severity.FAIL,
                f"DAG execution failed: valid={is_valid}, status={status}",
            )
    except Exception as e:  # noqa: BLE001
        results["dag_execution_completes"] = ValidationResult(
            Severity.CRITICAL,
            "DAG execution raised exception",
            f"{type(e).__name__}: {e}\n{traceback.format_exc()}",
        )

    # capability matrix, merge preservation etc. remain UNVALIDATED unless required
    if zcfg.get("require_capability_matrix", False):
        results["capability_matrix_equivalence"] = ValidationResult(
            Severity.UNVALIDATED,
            "Capability matrix validation not implemented",
        )
    if zcfg.get("require_merge_preservation", False):
        results["merge_preservation"] = ValidationResult(
            Severity.UNVALIDATED,
            "Merge preservation validation not implemented",
        )

    return results


# =============================================================================
# UNIMPLEMENTED CATEGORIES (HONESTLY UNVALIDATED)
# =============================================================================

def validate_unimplemented() -> Dict[str, ValidationResult]:
    keys = [
        "mcp_used_for_external_calls",
        "mcp_tools_define_input_output_schemas",
        "mcp_access_respects_acls",
        "rag_calls_are_deterministic",
        "kg_lookups_are_deterministic",
        "temporal_validity_enforced_on_events",
        "safety_runs_on_all_outbound_content",
        "safety_runs_on_all_mutating_actions",
        "pii_filter_active",
        "hallucination_detector_active",
        "injection_detector_active",
        "cost_tracking_enabled",
        "latency_tracking_enabled",
        "error_taxonomy_applied",
        "reliability_scores_updated",
        "golden_datasets_loaded",
        "llm_as_judge_runs_successfully",
        "regression_tests_all_pass",
        "toolpath_evaluation_passed",
        "environment_separation_valid",
        "rest_endpoints_secure",
        "authn_authz_enforced",
        "model_versions_pinned",
    ]
    msg = "Not implemented in validator; requires separate infra/test harness"
    return {k: ValidationResult(Severity.UNVALIDATED, msg) for k in keys}


# =============================================================================
# MAIN DRIVER
# =============================================================================

def main() -> None:
    run_id = uuid.uuid4().hex[:8]
    all_results: Dict[str, Dict[str, ValidationResult]] = {}

    with validation_phase("structure", run_id):
        all_results["structure"] = validate_structure()

    with validation_phase("layer_purity", run_id):
        all_results["layer_purity"] = validate_layer_purity()

    with validation_phase("engine_isolation", run_id):
        all_results["engine_isolation"] = validate_engine_isolation()

    with validation_phase("prompt_governance", run_id):
        all_results["prompt_governance"] = validate_prompt_governance()

    with validation_phase("tooling", run_id):
        all_results["tooling"] = validate_tooling()

    with validation_phase("circular_imports", run_id):
        all_results["circular_imports"] = validate_circular_imports()

    with validation_phase("zero_loss", run_id):
        all_results["zero_loss"] = validate_zero_loss()

    with validation_phase("unimplemented", run_id):
        all_results["unimplemented"] = validate_unimplemented()

    # Convert to JSON format for Windsurf
    json_out = {
        "validation_keys": {
            category: {k: v.as_bool() for k, v in results.items()}
            for category, results in all_results.items()
        }
    }
    atomic_write_json(RULES_PATH, json_out)

    # Summary with severity counts
    total = 0
    counts = {s: 0 for s in Severity}
    for _, results in all_results.items():
        for res in results.values():
            total += 1
            counts[res.severity] += 1

    with SUMMARY_PATH.open("w", encoding="utf-8") as f:
        f.write("# Agentic L5 Validation Summary\n\n")
        f.write(f"- Run ID: `{run_id}`\n")
        f.write(f"- Total checks: {total}\n")
        for sev in Severity:
            f.write(f"- {sev.value}: {counts[sev]}\n")
        f.write("\n---\n\n")

        for category, results in all_results.items():
            f.write(f"## {category}\n\n")
            for key, res in results.items():
                f.write(f"- **{key}** → {res.severity.value}")
                if res.message:
                    f.write(f" — {res.message}")
                if res.error:
                    f.write(f"\n  - error:\n    {res.error}")
                f.write("\n")
            f.write("\n")

    logger.info("validation_complete")


if __name__ == "__main__":
    main()
