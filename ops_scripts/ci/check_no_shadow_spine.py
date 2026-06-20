"""W5 CI gate — one-spine enforcement (advisory).

Scans all apps_* production Python for shadow-spine violations:
  PB-1..PB-5   profile_builder.py module rules
  BM-1..BM-6   bindings/*.py module rules
  SS-1..SS-6   general app-code rules
  NC-1..NC-5   negative controls (must hold)

ADVISORY by default. Fail-closed: NO_SHADOW_SPINE_FAIL_CLOSED=1
Bypass: NO_SHADOW_SPINE_BYPASS=1

DEFERRED apps (DEFER_WITH_REASON disposition — excluded from pass/fail assertions):
  apps_qna  — W1+W3 DONE (2026-05-14); SS-4 exemption added for provider_dispatch.py
              (DispatchResult is defined and owned there — not a shadow import).
              Removed from DEFERRED_APPS in W3.
  
W1 corrective patch (2026-05-14):
  apps_qna.scripts.run_qna::_run_build amended from MUST_ROUTE to EXEMPT_DOCUMENTED.
  Rationale: build-time compiler path operating on assembled Interview typed object,
  not a slug-keyed RequestEnvelope. Product/live runtime paths route through
  AppIngressRunner unconditionally via __main__.py. Structural tests in
  tests/_apps_contract/test_w1_qna_spine_migration.py::TestRunBuildExemptDocumented.

These apps must not cause this gate to fail. They will be included in W3 when
their DEFERRED_APPS removal is confirmed with zero-error scan.

Plan: .codex/plans/kill-shadow-pipelines-a7f3c2.md (W5)
      .codex/plans/one-spine-qna-rfp-migration-d2e8f1.md (W1 corrective patch)
"""
from __future__ import annotations

import ast
import json
import os
import re
import sys
from pathlib import Path
from typing import NamedTuple

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

OUTPUT_PATH = REPO_ROOT / "artifacts" / "ci" / "no_shadow_spine_gate.json"

DEFERRED_APPS: set[str] = set()  # W3 (2026-05-14): apps_qna migrations complete

_STAGE_PREFIXES = (
    "u0_validate_",
    "l1_plan_",
    "l0_route_",
    "c0_retrieve_",
    "pa_compose_",
    "l2_execute_",
    "exit_emit_",
)

_STAGE_RE = re.compile(
    r"\b(u0_validate_|l1_plan_|l0_route_|c0_retrieve_|pa_compose_|l2_execute_|exit_emit_)\w+"
)

_DISPATCH_IMPORT_RE = re.compile(
    r"from\s+apps_[a-z_]+\.runtime\.(entry|dispatch)\.dispatch\s+import"
)
_DISPATCH_RESULT_RE = re.compile(r"\bDispatchResult\b")
_CORE_APP_IMPORT_RE = re.compile(r"from\s+apps_[a-z_]+\s+import")
_APP_NAME_LITERAL_RE = re.compile(r"\b(apps_rg|apps_lic|apps_qna|apps_research|apps_underwriting_ai)\b")


class Finding(NamedTuple):
    severity: str
    rule_id: str
    file: str
    line: int
    message: str


def _is_deferred(path: Path) -> bool:
    parts = path.parts
    for app in DEFERRED_APPS:
        if app in parts:
            return True
    return False


def _is_tombstone(path: Path) -> bool:
    """Return True when the file is a quarantine/retirement stub.

    Accepts either pattern:
      - ``raise ImportError(...)``  — standard tombstone pattern
      - ``raise RuntimeError(...)`` — W0A quarantine pattern used in
        apps_rg/runtime/entry/dispatch.py and similar files
    Both patterns must appear together with a QUARANTINE or retired marker.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        has_raise = "raise ImportError" in text or "raise RuntimeError" in text
        has_marker = (
            "retired" in text.lower()
            or "tombstone" in text.lower()
            or "Bundle" in text
            or "QUARANTINE" in text
            or "QUARANTINED" in text
        )
        return has_raise and has_marker
    except OSError:
        return False


def _is_cert_wrapper(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        return '_CERT_PATH_ROLE = "RECEIPT_ONLY_WRAPPER"' in text
    except OSError:
        return False


def _collect_app_py_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for app_dir in repo_root.glob("apps_*/"):
        if not app_dir.is_dir():
            continue
        for py in app_dir.rglob("*.py"):
            rel = py.relative_to(repo_root)
            parts_str = str(rel)
            if any(x in parts_str for x in ("tests/", "_archive/", "artifacts/", "_quarantine/")):
                continue
            if _is_tombstone(py) or _is_cert_wrapper(py):
                continue
            files.append(py)
    return files


def _parse_safe(path: Path) -> ast.Module | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    except SyntaxError:
        return None


def _is_stage_call_name(name: str) -> bool:
    return any(name.startswith(p) for p in _STAGE_PREFIXES)


def _core_imported_names(tree: ast.Module) -> frozenset[str]:
    """Return the set of names imported from agentic_core.* at module level.

    SS-2 must only fire when the chained callees are core stage executors, not
    when the calling file uses app-owned helpers whose names happen to share a
    stage-prefix (e.g. ``pa_compose_apps_rg`` imported from
    ``apps_rg.runtime.bindings.pa_binding``).
    """
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("agentic_core"):
                for alias in node.names:
                    names.add(alias.asname if alias.asname else alias.name)
    return frozenset(names)


def _find_stage_calls_in_func(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[ast.Call]:
    hits = []
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and _is_stage_call_name(node.func.id):
                hits.append(node)
            elif isinstance(node.func, ast.Attribute) and _is_stage_call_name(node.func.attr):
                hits.append(node)
    return hits


def _scan_profile_builder(path: Path, deferred: bool) -> list[Finding]:
    findings: list[Finding] = []
    if deferred:
        return findings
    tree = _parse_safe(path)
    if tree is None:
        return findings
    rel = str(path.relative_to(REPO_ROOT))

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        fname = node.name

        if fname == "build_app_runtime_contract":
            stage_calls = _find_stage_calls_in_func(node)
            for call in stage_calls:
                findings.append(Finding("ERROR", "PB-1", rel, call.lineno,
                    f"Stage callable invoked inside build_app_runtime_contract"))

            for subnode in ast.walk(node):
                if isinstance(subnode, ast.Call):
                    if isinstance(subnode.func, ast.Name) and subnode.func.id == "AppIngressRunner":
                        findings.append(Finding("ERROR", "PB-2", rel, subnode.lineno,
                            "AppIngressRunner instantiated in build_app_runtime_contract"))
                    if isinstance(subnode.func, ast.Attribute) and subnode.func.attr == "run":
                        if isinstance(subnode.func.value, ast.Name) and "runner" in subnode.func.value.id.lower():
                            findings.append(Finding("ERROR", "PB-2", rel, subnode.lineno,
                                "AppIngressRunner.run() called in build_app_runtime_contract"))

            for subnode in ast.walk(node):
                if isinstance(subnode, ast.Return) and subnode.value is not None:
                    if isinstance(subnode.value, ast.Call):
                        if isinstance(subnode.value.func, ast.Name):
                            if subnode.value.func.id in ("X3Disposition", "DispatchResult"):
                                findings.append(Finding("ERROR", "PB-3", rel, subnode.lineno,
                                    f"build_app_runtime_contract returns {subnode.value.func.id} directly"))

            for subnode in ast.walk(node):
                if isinstance(subnode, ast.For):
                    findings.append(Finding("WARN", "PB-4", rel, subnode.lineno,
                        "Loop in build_app_runtime_contract may indicate stage sequencing via iteration"))

        if fname == "parse_payload":
            for subnode in ast.walk(node):
                if isinstance(subnode, ast.Return) and subnode.value is not None:
                    if isinstance(subnode.value, ast.Call):
                        if isinstance(subnode.value.func, ast.Name):
                            if "Profile" in subnode.value.func.id or "Contract" in subnode.value.func.id:
                                findings.append(Finding("ERROR", "PB-5", rel, subnode.lineno,
                                    f"parse_payload returns {subnode.value.func.id} — must return RequestEnvelope|None only"))

        for subnode in ast.walk(node):
            if isinstance(subnode, ast.Call):
                if isinstance(subnode.func, ast.Name) and subnode.func.id == "AppIngressRunner":
                    findings.append(Finding("ERROR", "PB-2", rel, subnode.lineno,
                        f"AppIngressRunner instantiated in {fname}"))

    return findings


def _scan_binding_module(path: Path, deferred: bool) -> list[Finding]:
    findings: list[Finding] = []
    if deferred:
        return findings
    tree = _parse_safe(path)
    if tree is None:
        return findings
    rel = str(path.relative_to(REPO_ROOT))

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        body = node.body
        if (len(body) == 1 and isinstance(body[0], ast.Return)
                and isinstance(body[0].value, ast.Call)):
            callee = body[0].value.func
            name = (callee.id if isinstance(callee, ast.Name)
                    else callee.attr if isinstance(callee, ast.Attribute) else "")
            if _is_stage_call_name(name) or name.startswith("core_"):
                findings.append(Finding("ERROR", "BM-1", rel, node.lineno,
                    f"{node.name}: single-statement body is return core_stage(...) — fake wrapper"))

        stage_calls = _find_stage_calls_in_func(node)
        if len(stage_calls) >= 2:
            findings.append(Finding("ERROR", "BM-4", rel, node.lineno,
                f"{node.name}: sequences {len(stage_calls)} stage calls — orchestration in binding"))

        for subnode in ast.walk(node):
            if isinstance(subnode, ast.Call):
                if isinstance(subnode.func, ast.Name) and subnode.func.id == "AppIngressRunner":
                    findings.append(Finding("ERROR", "BM-5", rel, subnode.lineno,
                        f"{node.name}: instantiates AppIngressRunner"))
                if isinstance(subnode.func, ast.Name) and subnode.func.id in ("X3Disposition",):
                    # BM-6 exemption: exit_binding.py is the canonical final-disposition
                    # producer. Returning X3Disposition is the intended contract for an
                    # Exit binding — flagging it is a rule defect, not a violation.
                    if path.name == "exit_binding.py":
                        findings.append(Finding("WARN", "BM-6", rel, subnode.lineno,
                            f"{node.name}: returns X3Disposition (EXEMPT — exit_binding.py is canonical disposition producer)"))
                    else:
                        findings.append(Finding("ERROR", "BM-6", rel, subnode.lineno,
                            f"{node.name}: returns X3Disposition directly"))

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            mod = ""
            if isinstance(node, ast.ImportFrom) and node.module:
                mod = node.module
            if "executor" in mod and "agentic_core" in mod:
                findings.append(Finding("WARN", "BM-2", rel, node.lineno,
                    f"Binding imports core executor module: {mod}"))

    return findings


def _scan_general(path: Path, deferred: bool) -> list[Finding]:
    findings: list[Finding] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return findings
    rel = str(path.relative_to(REPO_ROOT))

    # SS-4 file-level exemptions (surgical — only the two files that define/re-export
    # apps_qna's internal DispatchResult class; all other modules still warn).
    _SS4_GOVERNED_FILES = (
        "apps_qna" + os.sep + "engines" + os.sep + "dispatch" + os.sep + "provider_dispatch.py",
        "apps_qna" + os.sep + "engines" + os.sep + "dispatch" + os.sep + "__init__.py",
        "apps_qna/engines/dispatch/provider_dispatch.py",
        "apps_qna/engines/dispatch/__init__.py",
    )
    _ss4_exempt_file = any(rel.endswith(g) for g in _SS4_GOVERNED_FILES)

    for i, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if _DISPATCH_IMPORT_RE.search(line):
            if "# tombstone" not in line.lower() and "raise ImportError" not in line:
                findings.append(Finding("ERROR", "SS-3", rel, i,
                    f"Deprecated dispatch namespace import: {line.strip()}"))
        if _DISPATCH_RESULT_RE.search(line):
            if (
                "tombstone" not in line.lower()
                and not stripped.startswith("#")
                and not _ss4_exempt_file
            ):
                findings.append(Finding("WARN", "SS-4", rel, i,
                    f"DispatchResult reference in production: {line.strip()}"))

    tree = _parse_safe(path)
    if tree is None:
        return findings

    core_names = _core_imported_names(tree)

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        stage_calls = _find_stage_calls_in_func(node)
        if len(stage_calls) >= 2:
            if "profile_builder" not in rel and "/bindings/" not in rel:
                # SS-2 refinement: only flag when at least one callee is a name
                # imported from agentic_core.*  App-owned helpers whose names
                # happen to carry a stage prefix (e.g. pa_compose_apps_rg,
                # l2_execute_apps_rg from apps_rg.runtime.bindings.*) are NOT
                # shadow-spine violations — the rule intent is to catch files
                # that directly sequence core executor symbols, bypassing
                # AppIngressRunner.
                core_stage_callees = [
                    c for c in stage_calls
                    if (
                        isinstance(c.func, ast.Name) and c.func.id in core_names
                    ) or (
                        isinstance(c.func, ast.Attribute) and c.func.attr in core_names
                    )
                ]
                if core_stage_callees:
                    findings.append(Finding("ERROR", "SS-2", rel, node.lineno,
                        f"{node.name}: app-owned function chains {len(stage_calls)} stage calls outside bindings/ "
                        f"({len(core_stage_callees)} from agentic_core)"))

        for subnode in ast.walk(node):
            if isinstance(subnode, ast.Call):
                if isinstance(subnode.func, ast.Name) and subnode.func.id == "AppIngressRunner":
                    if "/runtime/" in rel and "__main__" not in rel:
                        findings.append(Finding("ERROR", "SS-6", rel, subnode.lineno,
                            f"AppIngressRunner instantiated in app runtime/ sub-module (not __main__.py)"))

    with_nodes = [n for n in ast.walk(tree) if isinstance(n, ast.With)]
    for wnode in with_nodes:
        for item in wnode.items:
            ctx = item.context_expr
            if isinstance(ctx, ast.Call) and isinstance(ctx.func, ast.Name) and ctx.func.id == "governed_run":
                for body_node in ast.walk(wnode):
                    if isinstance(body_node, ast.Call):
                        if isinstance(body_node.func, ast.Name) and _is_stage_call_name(body_node.func.id):
                            findings.append(Finding("ERROR", "SS-1", rel, body_node.lineno,
                                f"Stage executor called inside governed_run block: {body_node.func.id}"))
                        if isinstance(body_node.func, ast.Name) and body_node.func.id == "AppIngressRunner":
                            findings.append(Finding("ERROR", "SS-5", rel, body_node.lineno,
                                "AppIngressRunner invoked inside governed_run block"))

    return findings


def _run_negative_controls() -> list[Finding]:
    findings: list[Finding] = []

    def _try_import(module: str) -> bool:
        import importlib
        try:
            importlib.import_module(module)
            return True
        except (ImportError, ModuleNotFoundError, RuntimeError):
            return False
        except Exception:
            return False

    checks = [
        ("NC-1", "apps_rg.runtime.entry.dispatch",
         "apps_rg.runtime.entry.dispatch should be retired (raise ImportError tombstone)"),
        ("NC-2", "agentic_core.runtime.entrypoints.apps_rg_integrated_pipeline",
         "apps_rg integrated pipeline should no longer be importable"),
        ("NC-3", "apps_underwriting_ai.runtime.dispatch.underwriting_dispatch",
         "underwriting_dispatch should be retired"),
        ("NC-4", "apps_research.runtime.entry.dispatch",
         "apps_research.runtime.entry.dispatch should be tombstoned"),
    ]
    for rule_id, mod, msg in checks:
        if _try_import(mod):
            findings.append(Finding("ERROR", rule_id, mod, 0,
                f"NEGATIVE CONTROL FAILED — {msg}"))

    pb_findings: list[Finding] = []
    for pattern in (
        "apps_*/runtime/profile_builder.py",
        "apps_*/runtime/profile_builder_adapter.py",
    ):
        for pb in REPO_ROOT.glob(pattern):
            if _is_deferred(pb):
                continue
            for f in _scan_profile_builder(pb, deferred=False):
                if f.rule_id == "PB-1":
                    pb_findings.append(f)
    if pb_findings:
        findings.append(Finding("ERROR", "NC-5", "profile_builder.py scan", 0,
            f"NC-5 FAILED: {len(pb_findings)} profile_builder(s) have stage-symbol calls in build_app_runtime_contract"))

    return findings


def main() -> int:
    bypass = os.environ.get("NO_SHADOW_SPINE_BYPASS", "0") == "1"
    fail_closed = os.environ.get("NO_SHADOW_SPINE_FAIL_CLOSED", "0") == "1"

    if bypass:
        print("WARNING: NO_SHADOW_SPINE_BYPASS=1 — gate skipped")
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(json.dumps({"status": "bypassed"}, indent=2), encoding="utf-8")
        return 0

    all_findings: list[Finding] = []
    files = _collect_app_py_files(REPO_ROOT)

    for path in files:
        deferred = _is_deferred(path)
        rel = str(path.relative_to(REPO_ROOT))
        is_profile_builder = path.name in (
            "profile_builder.py",
            "profile_builder_adapter.py",
        )
        is_binding = "/bindings/" in rel or "\\bindings\\" in rel

        if is_profile_builder:
            all_findings.extend(_scan_profile_builder(path, deferred))
        if is_binding:
            all_findings.extend(_scan_binding_module(path, deferred))
        all_findings.extend(_scan_general(path, deferred))

    all_findings.extend(_run_negative_controls())

    errors = [f for f in all_findings if f.severity == "ERROR"]
    warnings = [f for f in all_findings if f.severity == "WARN"]

    report = {
        "gate": "NO_SHADOW_SPINE",
        "advisory": not fail_closed,
        "deferred_apps": sorted(DEFERRED_APPS),
        "files_scanned": len(files),
        "errors": len(errors),
        "warnings": len(warnings),
        "findings": [f._asdict() for f in all_findings],
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"NO_SHADOW_SPINE: scanned {len(files)} files — {len(errors)} errors, {len(warnings)} warnings")
    print(f"  Deferred (excluded from pass/fail): {sorted(DEFERRED_APPS)}")
    if errors:
        print(f"  ERRORS:")
        for f in errors:
            print(f"    [{f.rule_id}] {f.file}:{f.line} — {f.message}")
    if warnings:
        print(f"  WARNINGS:")
        for f in warnings[:10]:
            print(f"    [{f.rule_id}] {f.file}:{f.line} — {f.message}")
        if len(warnings) > 10:
            print(f"    ... and {len(warnings) - 10} more")

    if fail_closed and errors:
        print("FAIL: NO_SHADOW_SPINE_FAIL_CLOSED=1 and errors found")
        return 1

    if errors:
        print("WARN: advisory mode — errors found but not blocking")
    elif DEFERRED_APPS:
        print(
            f"OK (advisory pass while deferred): no shadow-spine violations in "
            f"non-deferred apps — {sorted(DEFERRED_APPS)} excluded from pass/fail; "
            f"deferred apps are NOT claimed fully clean"
        )
    else:
        print("OK: no shadow-spine violations detected — all apps scoped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
