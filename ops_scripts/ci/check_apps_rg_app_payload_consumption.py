#!/usr/bin/env python3
"""CI gate — apps_rg `app_payload` must remain CONSUMED by L1, L0, C0, PA.

Per plan apps-rg-app-payload-consumption-wiring-b3a449 W6.

The gate fails (exit 1) when any of:
    - L1, L0, C0, or PA imports `AppsRgIngressPayload` (legacy)
    - any of the four bindings reads `envelope.payload` /
      `request_envelope.payload`
    - apps_rg_dispatch passes anything other than `validated_request` to
      C0 or PA at the call site
    - C0 / PA signature does not take ValidatedRequest as its app-payload arg
    - L1 produces an L1PlanContract with empty task_spec / query_spec /
      support_expectation / output_expectation / policy_refs
    - L0 produces a RouteContract with empty route_family /
      cache_eligibility
    - PA produces a CompiledPromptArtifact with empty slot_lineage_map /
      component_hash_map / replay_manifest_ref

Exit 0 — every consumption invariant holds.
Exit 1 — at least one fails.

Constitutional:
    - subprocess-free, deterministic, ≤30s
    - utf-8 stdio, specific exception types only
    - SSOT folder per §31: ops_scripts/ci/check_*.py
"""
from __future__ import annotations

import ast
import inspect
import os
import sys
import traceback
import typing
from pathlib import Path
from typing import Any

REPO_ROOT: Path = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


# ---------------------------------------------------------------------------
# Result accumulator
# ---------------------------------------------------------------------------


class CheckRecorder:
    def __init__(self) -> None:
        self._records: list[tuple[str, bool, str]] = []

    def assert_(self, name: str, condition: bool, detail: str = "") -> None:
        self._records.append((name, bool(condition), detail))

    def fail(self, name: str, detail: str) -> None:
        self._records.append((name, False, detail))

    @property
    def passed(self) -> bool:
        return all(ok for _, ok, _ in self._records)

    def render(self) -> str:
        return "\n".join(
            f"[{'OK' if ok else 'FAIL'}] {name}{(': ' + d) if d and not ok else ''}"
            for name, ok, d in self._records
        )


# ---------------------------------------------------------------------------
# AST gates — no legacy imports / envelope.payload reads in bindings
# ---------------------------------------------------------------------------


_BINDING_FILES: tuple[Path, ...] = (
    REPO_ROOT / "apps_rg" / "runtime" / "bindings" / "l1_binding.py",
    REPO_ROOT / "apps_rg" / "runtime" / "bindings" / "l0_binding.py",
    REPO_ROOT / "apps_rg" / "runtime" / "bindings" / "c0_binding.py",
    REPO_ROOT / "apps_rg" / "runtime" / "bindings" / "pa_binding.py",
)

_DISPATCH_FILE: Path = (
    REPO_ROOT / "agentic_core" / "runtime" / "entry" / "apps_rg_dispatch.py"
)


def check_no_legacy_imports(rec: CheckRecorder) -> None:
    for binding_file in _BINDING_FILES:
        source = binding_file.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            rec.fail(f"{binding_file.name}_parses", str(exc))
            continue
        legacy: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == "AppsRgIngressPayload":
                        legacy.append(f"line {node.lineno}: from {node.module} import AppsRgIngressPayload")
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.endswith("AppsRgIngressPayload"):
                        legacy.append(f"line {node.lineno}: import {alias.name}")
        rec.assert_(
            f"{binding_file.name}_no_legacy_payload_import",
            not legacy,
            "; ".join(legacy),
        )


def check_no_envelope_payload_reads(rec: CheckRecorder) -> None:
    for binding_file in _BINDING_FILES:
        source = binding_file.read_text(encoding="utf-8")
        tree = ast.parse(source)
        violations: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr == "payload":
                obj = node.value
                if isinstance(obj, ast.Name) and obj.id in {"envelope", "request_envelope"}:
                    violations.append(f"line {node.lineno}: {obj.id}.payload")
        rec.assert_(
            f"{binding_file.name}_no_envelope_payload_read",
            not violations,
            "; ".join(violations),
        )


def check_dispatch_passes_validated_request(rec: CheckRecorder) -> None:
    """Both c0_retrieve_apps_rg and pa_compose_apps_rg must be called with
    `validated_request` as the last positional arg."""

    source = _DISPATCH_FILE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    c0_calls: list[ast.Call] = []
    pa_calls: list[ast.Call] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "c0_retrieve_apps_rg":
                c0_calls.append(node)
            elif node.func.id == "pa_compose_apps_rg":
                pa_calls.append(node)

    rec.assert_("dispatch_calls_c0_at_least_once", len(c0_calls) >= 1)
    rec.assert_("dispatch_calls_pa_at_least_once", len(pa_calls) >= 1)

    c0_violations: list[str] = []
    for call in c0_calls:
        last_arg = call.args[-1] if call.args else None
        if not (isinstance(last_arg, ast.Name) and last_arg.id == "validated_request"):
            c0_violations.append(
                f"line {call.lineno}: last arg is {ast.dump(last_arg) if last_arg else 'EMPTY'}"
            )
    rec.assert_(
        "dispatch_c0_call_passes_validated_request",
        not c0_violations,
        "; ".join(c0_violations),
    )

    pa_violations: list[str] = []
    for call in pa_calls:
        last_arg = call.args[-1] if call.args else None
        if not (isinstance(last_arg, ast.Name) and last_arg.id == "validated_request"):
            pa_violations.append(
                f"line {call.lineno}: last arg is {ast.dump(last_arg) if last_arg else 'EMPTY'}"
            )
    rec.assert_(
        "dispatch_pa_call_passes_validated_request",
        not pa_violations,
        "; ".join(pa_violations),
    )


# ---------------------------------------------------------------------------
# Signature gates — C0 + PA take ValidatedRequest, not AppsRgIngressPayload
# ---------------------------------------------------------------------------


def check_c0_pa_signatures(rec: CheckRecorder) -> None:
    from agentic_core.runtime.contracts.apps_rg_ingress_payload import (  # guardian: allow-layer-violation -- CI conformance gate introspects ValidatedRequest SSOT and binding callables; subprocess-free deterministic check per gate charter
        ValidatedRequest,
    )
    from apps_rg.runtime.bindings.c0_binding import (  # guardian: allow-layer-violation -- same CI gate: signature inspection of c0_retrieve_apps_rg
        c0_retrieve_apps_rg,
    )
    from apps_rg.runtime.bindings.pa_binding import (  # guardian: allow-layer-violation -- same CI gate: signature inspection of pa_compose_apps_rg
        pa_compose_apps_rg,
    )

    c0_hints = typing.get_type_hints(c0_retrieve_apps_rg)
    c0_params = [p for p in inspect.signature(c0_retrieve_apps_rg).parameters if p != "return"]
    rec.assert_(
        "c0_signature_takes_validated_request",
        "validated_request" in c0_params
        and c0_hints.get("validated_request") is ValidatedRequest,
        f"params={c0_params}, hints={c0_hints}",
    )

    pa_hints = typing.get_type_hints(pa_compose_apps_rg)
    pa_params = [p for p in inspect.signature(pa_compose_apps_rg).parameters if p != "return"]
    rec.assert_(
        "pa_signature_takes_validated_request",
        len(pa_params) == 4 and pa_hints.get(pa_params[-1]) is ValidatedRequest,
        f"params={pa_params}, hints={pa_hints}",
    )


# ---------------------------------------------------------------------------
# Live-path gates — L1/L0/PA produce non-empty AG-2 fields
# ---------------------------------------------------------------------------


def _live_thin_payload() -> dict[str, Any]:
    return {
        "app_id": "apps_rg",
        "task_class": "resume_generation",
        "target_company": "Acme Corp",
        "target_role": "Senior Director of AI Engineering",
        "target_level": "EXECUTIVE",
        "source_resume_text": "Sample resume content",
        "job_description_text": "Sample JD content",
        "briefing_artifact_ref": "artifact:briefing",
    }


def check_live_path_consumption(rec: CheckRecorder) -> None:
    from apps_rg.runtime.bindings.l0_binding import (  # guardian: allow-layer-violation -- CI live-path smoke imports shims to assert AG-2 field population; deterministic gate surface
        l0_route_apps_rg,
    )
    from apps_rg.runtime.bindings.l1_binding import (  # guardian: allow-layer-violation -- same CI live-path gate
        l1_plan_apps_rg,
    )
    from apps_rg.runtime.bindings.pa_binding import (  # guardian: allow-layer-violation -- same CI live-path gate
        pa_compose_apps_rg,
    )
    from apps_rg.runtime.bindings.c0_binding import (  # guardian: allow-layer-violation -- same CI live-path gate
        c0_retrieve_apps_rg,
    )
    from apps_rg.runtime.dispatch import apps_rg_parse
    from apps_rg.runtime.bindings.u0_binding import (  # guardian: allow-layer-violation -- same CI live-path gate
        u0_validate_apps_rg,
    )

    envelope = apps_rg_parse(_live_thin_payload())
    if envelope is None:
        rec.fail("live_path_envelope_built", "apps_rg_parse returned None")
        return
    vr = u0_validate_apps_rg(envelope)
    plan = l1_plan_apps_rg(vr)
    route = l0_route_apps_rg(plan)
    old_chroma = os.environ.get("CHROMA_PERSIST_DIR")
    old_mandatory = os.environ.get("APPS_RG_C0_DENSE_SPARSE_MANDATORY")
    os.environ["CHROMA_PERSIST_DIR"] = ""
    os.environ["APPS_RG_C0_DENSE_SPARSE_MANDATORY"] = "0"
    try:
        fec = c0_retrieve_apps_rg(route, vr)
    finally:
        if old_chroma is None:
            os.environ.pop("CHROMA_PERSIST_DIR", None)
        else:
            os.environ["CHROMA_PERSIST_DIR"] = old_chroma
        if old_mandatory is None:
            os.environ.pop("APPS_RG_C0_DENSE_SPARSE_MANDATORY", None)
        else:
            os.environ["APPS_RG_C0_DENSE_SPARSE_MANDATORY"] = old_mandatory
    artifact = pa_compose_apps_rg(route, plan, fec, vr)

    # L1 — five projections populated.
    rec.assert_("l1_task_spec_populated", bool(plan.task_spec))
    rec.assert_("l1_query_spec_populated", bool(plan.query_spec))
    rec.assert_("l1_support_expectation_populated", bool(plan.support_expectation))
    rec.assert_("l1_output_expectation_populated", bool(plan.output_expectation))
    rec.assert_("l1_policy_refs_populated", bool(plan.policy_refs))

    # L0 — route_family / cache_eligibility populated.
    rec.assert_(
        "l0_route_family_populated",
        bool(route.route_family),
        f"route_family={route.route_family!r}",
    )
    rec.assert_(
        "l0_cache_eligibility_populated",
        bool(route.cache_eligibility),
        f"cache_eligibility={route.cache_eligibility!r}",
    )
    rec.assert_(
        "l0_execution_form_populated",
        bool(route.execution_form),
        f"execution_form={route.execution_form!r}",
    )

    # PA — slot_lineage_map / component_hash_map / replay_manifest_ref populated.
    rec.assert_(
        "pa_slot_lineage_map_populated",
        bool(artifact.slot_lineage_map),
    )
    rec.assert_(
        "pa_component_hash_map_populated",
        bool(artifact.component_hash_map)
        and len(artifact.component_hash_map) >= 5,
        f"keys={list(artifact.component_hash_map.keys())}",
    )
    rec.assert_(
        "pa_replay_manifest_ref_populated",
        bool(artifact.replay_manifest_ref),
    )

    # Hard-law guardrail — apps_rg never sets action_required True
    rec.assert_("l0_action_required_false", route.action_required is False)


# ---------------------------------------------------------------------------
# Hard-law gates — no ChromaDB / embedding imports outside the C0 retrieval owner
# ---------------------------------------------------------------------------

#: Top-level module names whose import or runtime usage is forbidden.
#: Raw-string matching is intentionally NOT used here: the AST parser
#: strips comments and isolates only executable nodes, so explanatory
#: comments such as "# no ChromaDB collection" do NOT trigger this gate.
_FORBIDDEN_MODULES = frozenset({"chromadb", "sentence_transformers"})

#: Attribute / function names that indicate embedding-generation usage.
_FORBIDDEN_SYMBOLS = frozenset({"embed_text", "embed", "get_embeddings"})


def _ast_chromadb_violations(source: str, filename: str) -> list[str]:
    """Return violation strings for any ChromaDB / embedding AST nodes.

    Checks (all AST-level — comments are invisible):
    1. ``import chromadb`` / ``import sentence_transformers``
    2. ``from chromadb import ...`` / ``from sentence_transformers import ...``
    3. Any ``Name`` node whose id is a forbidden module root
       (e.g. bare ``chromadb`` usage after ``import chromadb as chromadb``).
    4. ``importlib.import_module("chromadb")`` dynamic import pattern.
    5. Forbidden symbol names (``embed_text``, ``embed``, ``get_embeddings``)
       used as ``Name`` or ``Attribute`` nodes in non-docstring positions.
    """
    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as exc:
        return [f"SyntaxError: {exc}"]

    violations: list[str] = []

    for node in ast.walk(tree):
        # 1 & 2 — import statements
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in _FORBIDDEN_MODULES:
                    violations.append(
                        f"line {node.lineno}: import {alias.name}"
                    )
        elif isinstance(node, ast.ImportFrom):
            mod_root = (node.module or "").split(".")[0]
            if mod_root in _FORBIDDEN_MODULES:
                names = ", ".join(a.name for a in node.names)
                violations.append(
                    f"line {node.lineno}: from {node.module} import {names}"
                )

        # 3 — bare Name referencing a forbidden module (after import-as)
        elif isinstance(node, ast.Name):
            if node.id in _FORBIDDEN_MODULES:
                violations.append(
                    f"line {node.lineno}: Name reference '{node.id}'"
                )
            if node.id in _FORBIDDEN_SYMBOLS:
                violations.append(
                    f"line {node.lineno}: symbol '{node.id}'"
                )

        # 4 — importlib.import_module("chromadb") dynamic import
        elif isinstance(node, ast.Call):
            func = node.func
            is_import_module = (
                isinstance(func, ast.Attribute)
                and func.attr == "import_module"
            ) or (
                isinstance(func, ast.Name)
                and func.id == "import_module"
            )
            if is_import_module and node.args:
                first_arg = node.args[0]
                if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
                    root = first_arg.value.split(".")[0]
                    if root in _FORBIDDEN_MODULES:
                        violations.append(
                            f"line {node.lineno}: importlib.import_module({first_arg.value!r})"
                        )

        # 5 — Attribute node whose attr is a forbidden symbol
        elif isinstance(node, ast.Attribute):
            if node.attr in _FORBIDDEN_SYMBOLS:
                violations.append(
                    f"line {node.lineno}: attribute '.{node.attr}'"
                )

    return violations


def check_no_chromadb_or_embeddings(rec: CheckRecorder) -> None:
    """AST-aware gate: fail on actual imports/usage outside C0 retrieval."""
    binding_files = tuple(
        p for p in _BINDING_FILES if p.name != "c0_binding.py"
    )
    for binding_file in binding_files:
        source = binding_file.read_text(encoding="utf-8")
        violations = _ast_chromadb_violations(source, binding_file.name)
        rec.assert_(
            f"{binding_file.name}_no_ChromaDB_or_embeddings",
            not violations,
            "; ".join(violations),
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    rec = CheckRecorder()
    try:
        check_no_legacy_imports(rec)
        check_no_envelope_payload_reads(rec)
        check_dispatch_passes_validated_request(rec)
        check_c0_pa_signatures(rec)
        check_live_path_consumption(rec)
        check_no_chromadb_or_embeddings(rec)
    except Exception as exc:  # guardian: allow-broad -- top-level CI safety net
        traceback.print_exc()
        print(f"FATAL: AG-2 consumption check raised unexpectedly: {exc}", file=sys.stderr)
        return 1

    print(rec.render())
    if rec.passed:
        print()
        print("apps_rg AG-2 app_payload consumption: ALL CHECKS PASSED.")
        return 0
    print()
    print(
        "apps_rg AG-2 app_payload consumption FAILED — see plan "
        "apps-rg-app-payload-consumption-wiring-b3a449.md for the consumption invariants.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
