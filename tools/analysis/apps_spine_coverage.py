"""Audit apps_* runtime-mode classification + spine coverage.

Classifies each ``apps_*`` package into one of the five canonical
buckets defined in ``docs/reference/APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md``:

    CORE_ONLY_VALID              non-app spine paths (reserved)
    APP_OVERLAY_STATIC_EVIDENCE  app imports the canonical contracts its
                                 declared routes require. STATIC evidence
                                 only -- runtime trace is what proves the
                                 contracts are actually used.
    APP_STANDALONE_FORBIDDEN     app claims a domain runtime but holds
                                 zero contracts and zero spine edges
    PARTIAL_SPINE_STATIC_ONLY    app imports infrastructure (UWG/ledger/
                                 BGE) but not the contracts its routes
                                 require
    UNKNOWN_NEEDS_RUNTIME_TRACE  static evidence is ambiguous; needs
                                 runtime trace

The authority-class contract set is fixed:

    L1PlanContract, RouteContract, FinalEvidenceContract,
    CompiledPromptArtifact, PromptEnvelope, ValidatedRequest,
    SealedArtifact, ExitReviewPacket, CommitRequest,
    RuntimeExhaustBundle, RetrievalPlan, StateDiffCandidate,
    GateVerdict

**Per-route-type contract requirements** (from the executive map, see
``ROUTE_TYPE_CONTRACT_REQUIREMENTS`` below): the scanner only requires
the contracts that the app's *declared routes* need. An app that
declares it supports ``R2_grounded_read`` only needs
``RetrievalPlan`` + ``FinalEvidenceContract`` to qualify -- it does
not need ``CommitRequest`` because it does not claim durable writes.

**Manifest mechanism**: each app may place a ``spine_manifest.yaml``
at its root declaring ``claimed_routes: [...]``. When present, the
scanner uses the manifest to compute the required-contract set. When
absent, the scanner falls back to the legacy any-contract-counts
heuristic so the rollout does not break the workspace.

Importing ``apps_shared`` alone CANNOT make an app valid. Contracts
MUST be imported directly from ``agentic_core``.

The scanner does NOT penalize core-only paths and does NOT require
``apps_*`` for generic core capabilities. It ONLY flags ``apps_*``
packages that claim a domain runtime (have engines / a CLI / a wizard /
a route registry) but provide no authority-handoff evidence.

Usage:
    python -m tools.analysis.apps_spine_coverage [--json] [--app APP]

Output:
    - Markdown table to stdout (default)
    - JSON to stdout (--json)
    - Single-app deep-dive if --app APP given

Reused by:
    - Plan SSOT generation (.windsurf/plans/apps-spine-integration-*.md)
    - Future CI gate for runtime-mode ratchets
    - Tests at tests/unit/tools/analysis/test_apps_spine_coverage.py

Legacy keys preserved on the JSON output for backward-compat with the
spine-coverage-pct metric. New keys: ``runtime_mode``,
``contract_imports``, ``claims_domain_runtime``,
``classification_evidence``, ``manifest_present``,
``manifest_claimed_routes``, ``manifest_required_contracts``,
``manifest_missing_contracts``.

Legacy bucket name ``APP_OVERLAY_VALID`` is still emitted alongside the
canonical ``APP_OVERLAY_STATIC_EVIDENCE`` for one release cycle so
existing CI gates that grep on the old name keep working. New gates
MUST read ``runtime_mode``.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Canonical authority-class contract symbols. Importing any of these from
# ``agentic_core`` is the load-bearing evidence that an app delegates to the
# spine rather than running a shadow runtime. ``apps_shared`` re-exports do
# NOT count -- the import must be from ``agentic_core`` directly so the
# delegation chain is auditable.
#
# Source of truth: docs/reference/APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md.
# When a new spine contract type is added, add it here too.
# ---------------------------------------------------------------------------
CANONICAL_CONTRACTS: frozenset[str] = frozenset({
    "L1PlanContract",
    "RouteContract",
    "FinalEvidenceContract",
    "CompiledPromptArtifact",
    "PromptEnvelope",
    "ValidatedRequest",
    "SealedArtifact",
    "ExitReviewPacket",
    "CommitRequest",
    "RuntimeExhaustBundle",
    "RetrievalPlan",
    "StateDiffCandidate",
    "MutationIntent",
    "GateVerdict",
})

# ---------------------------------------------------------------------------
# Per-route-type contract requirements derived from the executive map
# (``docs/reference/_notes/agentic_system_process_map_exec.md``). Each
# route type a manifest can declare maps to the canonical contracts the
# spine REQUIRES the app to delegate through. An app whose manifest
# declares ``[R3_action]`` must import every contract listed under
# ``R3_action`` to qualify for ``APP_OVERLAY_STATIC_EVIDENCE``.
#
# A route type with an empty requirement set means "no canonical
# contract handoff is required for this route" (e.g., R5_fallback is
# the escape hatch; build_time_compiler is the apps_qna-style
# build-time tool that produces a context pack rather than running a
# live request).
#
# When extending the spine flow, update this table -- not the bucket
# logic. Buckets stay stable; the requirement matrix is the calibration
# surface.
# ---------------------------------------------------------------------------
# Canonical R3 contract chain. The spine's evidence-grounded read path:
# intake -> plan -> route -> retrieval -> evidence -> prompt -> seal -> exit.
_R3_CONTRACT_CHAIN: frozenset[str] = frozenset({
    "ValidatedRequest",
    "L1PlanContract",
    "RouteContract",
    "RetrievalPlan",
    "FinalEvidenceContract",
    "CompiledPromptArtifact",  # PromptEnvelope is an accepted equivalent;
                               # see CONTRACT_EQUIVALENT_GROUPS below.
    "SealedArtifact",
    "ExitReviewPacket",
})

ROUTE_TYPE_CONTRACT_REQUIREMENTS: dict[str, frozenset[str]] = {
    # ===========================================================
    # Canonical taxonomy (W7c rename + W8 expansion)
    # ===========================================================
    # Grounded read with retrieval + sealed answer; no durable side effect.
    # Examples (per docs/reports/apps_runtime_mode_scorecard.md):
    #   apps_research, apps_exec.
    "R3_grounded_read": _R3_CONTRACT_CHAIN,
    # Multi-step / workflow with downstream durable write. Adds
    # ``CommitRequest`` to the R3 chain. Examples: apps_lic, apps_rfp.
    "R3R4_managed_workflow": _R3_CONTRACT_CHAIN | frozenset({"CommitRequest"}),
    # Evaluator surface. Wrapping eval in the generic spine substrate
    # creates a circular evaluation-of-evaluator loop. Empty required-
    # contract set; MUST be paired with an exception record in the
    # manifest to qualify for FORMAL_EXCEPTION_STATIC_EVIDENCE.
    "evaluator_only": frozenset(),
    # Library-style or regulated-domain protocol with its own
    # governance. Generic spine wrapping would be contract theater.
    # Empty required-set; MUST be paired with an exception record to
    # qualify for FORMAL_EXCEPTION_STATIC_EVIDENCE.
    "core_adjacent_utility": frozenset(),
    # Build-time context pack compilers (apps_qna shape). The pack is
    # an output the operator pastes into an external agent; the spine
    # is not in the runtime path of the pasted answer. Empty required
    # set is honored DIRECTLY -- no exception record required, because
    # the build-time tool is not claiming any runtime delegation.
    "build_time_compiler": frozenset(),

    # ===========================================================
    # Legacy / fine-grained route types (back-compat -- kept so any
    # existing manifest references continue to validate). New apps
    # SHOULD use the canonical taxonomy above.
    # ===========================================================
    "R1_cache": frozenset({"ValidatedRequest"}),
    "R2_grounded_read": _R3_CONTRACT_CHAIN,
    "R3_action": frozenset({
        "ValidatedRequest", "L1PlanContract", "RouteContract",
        "CompiledPromptArtifact", "SealedArtifact", "ExitReviewPacket",
        "CommitRequest",
    }),
    "R4_workflow": frozenset({
        "ValidatedRequest", "L1PlanContract", "RouteContract",
        "CompiledPromptArtifact", "SealedArtifact", "ExitReviewPacket",
        "CommitRequest",
    }),
    "R5_fallback": frozenset({"ValidatedRequest"}),
    "domain_synthesis": frozenset({
        "CompiledPromptArtifact", "SealedArtifact", "ExitReviewPacket",
    }),
    "durable_write": frozenset({"CommitRequest"}),
    "learning_writeback": frozenset({"RuntimeExhaustBundle"}),
}

# Contracts that are functionally interchangeable for the purpose of
# satisfying a route's required set. When ANY member of an equivalence
# group is imported, the entire group is considered satisfied. The first
# entry in each tuple is the canonical name (used in error messages).
CONTRACT_EQUIVALENT_GROUPS: tuple[frozenset[str], ...] = (
    # apps_rg uses ``PromptEnvelope`` as its prompt artifact; the
    # canonical name elsewhere is ``CompiledPromptArtifact``. Both
    # represent the L1->L2 prompt handoff contract.
    frozenset({"CompiledPromptArtifact", "PromptEnvelope"}),
)

# Route types that MUST be backed by an exception record (with a
# reason_code AND non-empty compensating_controls in the manifest)
# before they qualify for FORMAL_EXCEPTION_STATIC_EVIDENCE. An app that
# claims one of these route types without the exception fields is
# UNKNOWN_NEEDS_RUNTIME_TRACE -- the formal claim cannot be verified.
_FORMAL_EXCEPTION_ROUTE_TYPES: frozenset[str] = frozenset({
    "evaluator_only",
    "core_adjacent_utility",
})

MANIFEST_FILENAMES: tuple[str, ...] = ("spine_manifest.yaml", "spine_manifest.yml")

# Heuristic markers that an app CLAIMS a domain runtime (i.e., does more
# than passive type definitions). The presence of any of these patterns
# means the app is on the hook for delegation evidence; their absence
# means an app is purely a schema/types package and the scanner classifies
# it ``UNKNOWN_NEEDS_RUNTIME_TRACE`` instead of forbidden.
_DOMAIN_RUNTIME_MARKERS: tuple[tuple[str, str], ...] = (
    ("engines/", "engines directory present"),
    ("integrations/", "integrations directory present"),
    ("router/", "router subpackage present"),
    ("scripts/run_", "CLI runner present"),
    ("scripts/__main__.py", "CLI entrypoint present"),
    ("__main__.py", "package entrypoint present"),
    ("wizard.py", "interactive wizard present"),
    ("control_plane.py", "control-plane module present"),
    ("governed_", "governed_<X>_run.py present"),
)

STDLIB_PREFIXES = {
    "typing", "dataclasses", "pathlib", "json", "os", "sys", "re", "enum",
    "datetime", "collections", "functools", "itertools", "argparse", "logging",
    "contextlib", "copy", "io", "tempfile", "textwrap", "warnings",
    "subprocess", "time", "math", "hashlib", "uuid", "abc", "__future__",
    "shutil", "glob", "asyncio", "concurrent", "threading", "queue", "socket",
    "struct", "pickle", "csv", "string", "operator", "random", "secrets",
    "base64", "binascii", "zipfile", "tarfile", "platform", "errno",
    "traceback", "inspect", "importlib", "types", "weakref", "gc",
    "ast", "dis", "tokenize", "keyword", "parser", "symtable",
    "unittest", "doctest", "pdb", "profile", "cProfile", "trace",
    "fnmatch", "linecache", "atexit", "signal", "selectors",
    "http", "urllib", "email", "html", "xml", "json", "configparser",
}


def _classify(mod: str) -> tuple[str, str]:
    """Return (zone, sub_zone). zone is the headline; sub_zone splits agentic_core layers."""
    if not mod:
        return ("<empty>", "<empty>")
    head = mod.split(".")[0]
    if head in STDLIB_PREFIXES:
        return ("stdlib", "stdlib")
    if mod.startswith("agentic_core."):
        for layer in (
            "L0_routing", "L1_cognition", "L2_execution", "L3_orchestration",
            "L4_storage", "L5_safety", "L6_observability",
        ):
            if mod.startswith(f"agentic_core.{layer}"):
                return ("agentic_core", layer)
        return ("agentic_core", "agentic_core_other")
    if mod.startswith("system_learning"):
        return ("system_learning", "system_learning")
    if mod.startswith("apps_shared"):
        return ("apps_shared", "apps_shared")
    if mod.startswith("apps_"):
        return (f"sibling_apps", head)
    if mod.startswith("infrastructure"):
        return ("infrastructure", "infrastructure")
    if mod.startswith("tools"):
        return ("tools", "tools")
    return ("external", head)


def _is_uwg_token(mod: str) -> bool:
    lower = mod.lower()
    return (
        "uwg" in lower
        or "write_gateway" in lower
        or "durable_write" in lower
        or "writegateway" in lower.replace("_", "")
    )


def _load_manifest(app_dir: Path) -> dict | None:
    """Load ``spine_manifest.yaml`` if present. Returns None when absent.

    The manifest format is documented in
    ``docs/reference/APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md``. Minimal shape::

        schema_version: 1
        app: apps_<name>
        claimed_routes:
          - type: R2_grounded_read
            description: "..."
          - type: build_time_compiler
            description: "..."

    Tolerant of yaml-import failures (returns None) so the scanner stays
    importable in environments without ``pyyaml``.
    """
    for filename in MANIFEST_FILENAMES:
        manifest_path = app_dir / filename
        if not manifest_path.is_file():
            continue
        try:
            import yaml  # type: ignore[import-not-found]
        except ImportError:
            return None
        try:
            data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError):  # type: ignore[attr-defined]
            return None
        if isinstance(data, dict):
            return data
        return None
    return None


def _claimed_route_types_from_manifest(manifest: dict | None) -> list[str]:
    """Extract claimed route-type strings from a parsed manifest dict."""
    if not manifest:
        return []
    raw = manifest.get("claimed_routes") or []
    if not isinstance(raw, list):
        return []
    types: list[str] = []
    for entry in raw:
        if isinstance(entry, dict):
            t = entry.get("type")
            if isinstance(t, str) and t.strip():
                types.append(t.strip())
        elif isinstance(entry, str) and entry.strip():
            types.append(entry.strip())
    return types


def _required_contracts_for_routes(claimed_routes: list[str]) -> set[str]:
    """Union the per-route requirements for the app's declared routes.

    Unknown route-type strings contribute zero contracts. The scanner
    surfaces them via ``manifest_unknown_routes`` so operators can fix
    typos / register new types in ``ROUTE_TYPE_CONTRACT_REQUIREMENTS``.
    """
    required: set[str] = set()
    for route_type in claimed_routes:
        required |= set(ROUTE_TYPE_CONTRACT_REQUIREMENTS.get(route_type, frozenset()))
    return required


def _missing_required_contracts(
    required: set[str], imported: set[str]
) -> list[str]:
    """Return required contracts NOT satisfied by the imported set.

    A required contract is satisfied when EITHER the contract itself OR
    any of its equivalents (per ``CONTRACT_EQUIVALENT_GROUPS``) is in
    the imported set. The canonical name (the missing one) is what gets
    returned, not the equivalent names.
    """
    imported_norm: set[str] = set(imported)
    for group in CONTRACT_EQUIVALENT_GROUPS:
        if group & set(imported):
            imported_norm |= set(group)
    return sorted(required - imported_norm)


def _extract_exception_fields(manifest: dict | None) -> dict[str, object]:
    """Pull formal-exception fields from a manifest, if present.

    Recognized shape (under top-level ``exception`` key)::

        exception:
          reason_code: circular_dependency
          exception_record_class: GovernedEvalException
          exception_record_module: apps_eval.integrations.governed_eval_exception
          blocked_layers: [L0, L1, C0, L2, L5, L6]
          safe_layers: [BUS_T_telemetry, conformance_metadata]
          compensating_controls:
            - "CC-EVAL-01: ..."
            - "CC-EVAL-02: ..."
          review_cadence: annual
          owner: eval-platform team

    Returns a dict with normalized keys; missing fields default to
    empty/falsy values so callers can do ``.get("reason_code")`` safely.
    """
    out: dict[str, object] = {
        "reason_code": "",
        "exception_record_class": "",
        "exception_record_module": "",
        "compensating_controls": [],
        "blocked_layers": [],
        "safe_layers": [],
        "review_cadence": "",
        "owner": "",
    }
    if not manifest:
        return out
    block = manifest.get("exception")
    if not isinstance(block, dict):
        return out
    rc = block.get("reason_code")
    if isinstance(rc, str):
        out["reason_code"] = rc.strip()
    rec_cls = block.get("exception_record_class")
    if isinstance(rec_cls, str):
        out["exception_record_class"] = rec_cls.strip()
    rec_mod = block.get("exception_record_module")
    if isinstance(rec_mod, str):
        out["exception_record_module"] = rec_mod.strip()
    cc = block.get("compensating_controls") or []
    if isinstance(cc, list):
        out["compensating_controls"] = [str(c) for c in cc if c]
    bl = block.get("blocked_layers") or []
    if isinstance(bl, list):
        out["blocked_layers"] = [str(c) for c in bl if c]
    sl = block.get("safe_layers") or []
    if isinstance(sl, list):
        out["safe_layers"] = [str(c) for c in sl if c]
    rev = block.get("review_cadence")
    if isinstance(rev, str):
        out["review_cadence"] = rev.strip()
    own = block.get("owner")
    if isinstance(own, str):
        out["owner"] = own.strip()
    return out


def _has_formal_exception(
    claimed_routes: list[str], exception_fields: dict[str, object]
) -> bool:
    """Decide whether the manifest qualifies for FORMAL_EXCEPTION_STATIC_EVIDENCE.

    Conditions (all required):
      1. At least one declared route is a formal-exception route type
         (``evaluator_only`` or ``core_adjacent_utility``).
      2. ``exception.reason_code`` is non-empty.
      3. ``exception.compensating_controls`` is a non-empty list.
    """
    if not any(rt in _FORMAL_EXCEPTION_ROUTE_TYPES for rt in claimed_routes):
        return False
    reason_code = exception_fields.get("reason_code") or ""
    controls = exception_fields.get("compensating_controls") or []
    return bool(reason_code) and bool(controls)


def _safe_relative_path(py: Path, app_dir: Path) -> str:
    """Return a stable string path for an audited file.

    Prefers ``py.relative_to(REPO_ROOT)`` so callsite paths remain
    reproducible across machines. When the audited app sits outside the
    repo (test fixtures using ``tmp_path``), falls back to a path
    relative to the app's own root prefixed with the app's directory
    name. Final fallback: stringify the absolute path.
    """
    try:
        return str(py.relative_to(REPO_ROOT))
    except ValueError:
        try:
            return f"{app_dir.name}/{py.relative_to(app_dir)}"
        except ValueError:
            return str(py)


def _detect_domain_runtime_claims(app_dir: Path) -> list[str]:
    """Return reasons (human-readable) why an app claims a domain runtime.

    Empty list means the app is a passive types/schemas package and the
    scanner classifies it ``UNKNOWN_NEEDS_RUNTIME_TRACE`` rather than
    forbidden. Non-empty list means the app is on the hook for canonical
    contract delegation evidence.
    """
    reasons: list[str] = []
    for marker, label in _DOMAIN_RUNTIME_MARKERS:
        candidates = list(app_dir.rglob(f"*{marker}*")) if marker.endswith("/") else list(app_dir.rglob(marker))
        # rglob with trailing slash doesn't filter dirs strictly; fall back
        # to a directory-existence test for the directory markers.
        if marker.endswith("/"):
            sub = app_dir / marker.rstrip("/")
            if sub.is_dir() and any(sub.rglob("*.py")):
                reasons.append(label)
        elif candidates:
            # Verify at least one candidate is a real file (rglob can match
            # path stems too).
            for c in candidates:
                if c.is_file() and c.suffix == ".py":
                    reasons.append(label)
                    break
    return reasons


def scan_app(app_dir: Path) -> dict:
    """Return per-app scorecard with delegation-evidence classification.

    Adds the following keys vs the legacy import-edge metric:

    - ``runtime_mode``         one of the five buckets in the module docstring
    - ``contract_imports``     {contract_name: [callsites]}
    - ``claims_domain_runtime`` bool (any _DOMAIN_RUNTIME_MARKERS hit)
    - ``domain_runtime_reasons`` human-readable reason list
    - ``classification_evidence`` short human-readable verdict explanation
    """
    zone_counts: Counter[str] = Counter()
    layer_counts: Counter[str] = Counter()
    uwg_hits: list[tuple[str, int]] = []
    files_scanned = 0
    parse_errors = 0
    contract_imports: dict[str, list[str]] = {}

    for py in app_dir.rglob("*.py"):
        # Skip tests for spine-routing analysis (tests have legitimate
        # reasons to import almost anything for fixturing).
        if any(part in {"tests", "_tests", "test", "fixtures"} for part in py.parts):
            continue
        files_scanned += 1
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            parse_errors += 1
            continue
        rel_path = _safe_relative_path(py, app_dir)
        for node in ast.walk(tree):
            mods: list[str] = []
            symbol_names: list[str] = []
            if isinstance(node, ast.Import):
                mods = [n.name for n in node.names]
            elif isinstance(node, ast.ImportFrom):
                mods = [node.module or ""]
                symbol_names = [n.name for n in node.names]
            for mod in mods:
                zone, sub = _classify(mod)
                zone_counts[zone] += 1
                if zone == "agentic_core":
                    layer_counts[sub] += 1
                if _is_uwg_token(mod):
                    # rel_path was already _safe_relative_path-resolved above.
                    uwg_hits.append((rel_path, getattr(node, "lineno", 0)))
            # Authority-class contract detection: only counts when imported
            # FROM agentic_core (apps_shared re-exports do not qualify per
            # the doc).
            if (
                isinstance(node, ast.ImportFrom)
                and node.module is not None
                and node.module.startswith("agentic_core")
            ):
                for sym in symbol_names:
                    if sym in CANONICAL_CONTRACTS:
                        contract_imports.setdefault(sym, []).append(
                            f"{rel_path}:{getattr(node, 'lineno', 0)}"
                        )

    total_edges = sum(zone_counts.values())
    non_stdlib = total_edges - zone_counts.get("stdlib", 0)
    agentic_edges = zone_counts.get("agentic_core", 0)
    spine_score = (agentic_edges / non_stdlib) if non_stdlib > 0 else 0.0

    layers_touched = sorted(layer_counts.keys())
    has_uwg = len(uwg_hits) > 0
    has_meta_learning = zone_counts.get("system_learning", 0) > 0

    domain_runtime_reasons = _detect_domain_runtime_claims(app_dir)
    claims_domain_runtime = bool(domain_runtime_reasons)

    manifest = _load_manifest(app_dir)
    claimed_routes = _claimed_route_types_from_manifest(manifest)
    required_set = _required_contracts_for_routes(claimed_routes)
    required_contracts = sorted(required_set)
    missing_contracts = _missing_required_contracts(
        required_set, set(contract_imports.keys())
    )
    unknown_routes = sorted(
        rt for rt in claimed_routes if rt not in ROUTE_TYPE_CONTRACT_REQUIREMENTS
    )
    exception_fields = _extract_exception_fields(manifest)
    has_formal_exception = _has_formal_exception(claimed_routes, exception_fields)

    return {
        "app": app_dir.name,
        "files_scanned": files_scanned,
        "parse_errors": parse_errors,
        "total_import_edges": total_edges,
        "non_stdlib_edges": non_stdlib,
        "agentic_core_edges": agentic_edges,
        "spine_coverage_pct": round(spine_score * 100, 1),
        "system_learning_edges": zone_counts.get("system_learning", 0),
        "apps_shared_edges": zone_counts.get("apps_shared", 0),
        "infrastructure_edges": zone_counts.get("infrastructure", 0),
        "tools_edges": zone_counts.get("tools", 0),
        "external_edges": zone_counts.get("external", 0),
        "sibling_apps_edges": zone_counts.get("sibling_apps", 0),
        "layers_touched": layers_touched,
        "layer_counts": dict(layer_counts),
        "has_uwg_usage": has_uwg,
        "uwg_hit_count": len(uwg_hits),
        "uwg_hit_locations": uwg_hits[:5],
        "has_meta_learning_usage": has_meta_learning,
        # NEW (W6): runtime-mode delegation-evidence fields.
        "contract_imports": {
            name: sites for name, sites in sorted(contract_imports.items())
        },
        "contract_count": sum(len(v) for v in contract_imports.values()),
        "distinct_contracts": sorted(contract_imports.keys()),
        "claims_domain_runtime": claims_domain_runtime,
        "domain_runtime_reasons": domain_runtime_reasons,
        # NEW (W7): manifest-aware route-typed classification.
        "manifest_present": manifest is not None,
        "manifest_claimed_routes": claimed_routes,
        "manifest_required_contracts": required_contracts,
        "manifest_missing_contracts": missing_contracts,
        "manifest_unknown_routes": unknown_routes,
        # NEW (W8): formal-exception fields. Populated when manifest
        # carries a top-level ``exception`` block; empty otherwise.
        "manifest_exception_reason_code": exception_fields.get("reason_code", ""),
        "manifest_exception_record_class": exception_fields.get(
            "exception_record_class", ""
        ),
        "manifest_exception_record_module": exception_fields.get(
            "exception_record_module", ""
        ),
        "manifest_compensating_controls": exception_fields.get(
            "compensating_controls", []
        ),
        "manifest_compensating_controls_count": len(
            exception_fields.get("compensating_controls", []) or []
        ),
        "manifest_blocked_layers": exception_fields.get("blocked_layers", []),
        "manifest_safe_layers": exception_fields.get("safe_layers", []),
        "manifest_review_cadence": exception_fields.get("review_cadence", ""),
        "manifest_exception_owner": exception_fields.get("owner", ""),
        "manifest_has_formal_exception": has_formal_exception,
    }


def classify_app(scorecard: dict) -> tuple[str, str]:
    """Return (runtime_mode, evidence) per APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md.

    Six-bucket classification with manifest-aware route-typed evaluation:

    - APP_OVERLAY_STATIC_EVIDENCE: when a manifest is present, app
      imports the FULL set of contracts its declared routes require.
      ``build_time_compiler`` legitimately falls into this bucket with an
      empty required-set because the spine is not in the runtime path of
      its output (apps_qna shape).
    - FORMAL_EXCEPTION_STATIC_EVIDENCE: manifest declares ``evaluator_only``
      or ``core_adjacent_utility`` AND carries a non-empty
      ``exception.reason_code`` AND non-empty
      ``exception.compensating_controls``. The empty required-contract set
      is justified by the recorded exception charter, not by an absent
      runtime path.
    - APP_STANDALONE_FORBIDDEN: app claims a domain runtime AND has zero
      contract imports AND has zero meaningful spine import edges.
    - PARTIAL_SPINE_STATIC_ONLY: app imports infrastructure but does not
      satisfy the route's contract requirements.
    - UNKNOWN_NEEDS_RUNTIME_TRACE: static evidence is ambiguous (e.g., a
      formal-exception route declared without the supporting exception
      record, or an app with no domain-runtime markers).
    - CORE_ONLY_VALID: reserved (not assigned to apps).
    """
    has_contracts = scorecard["contract_count"] > 0
    claims_runtime = scorecard["claims_domain_runtime"]
    has_static_spine = scorecard["agentic_core_edges"] > 0 or scorecard["has_uwg_usage"]
    manifest_present = scorecard.get("manifest_present", False)
    claimed_routes: list[str] = scorecard.get("manifest_claimed_routes", []) or []
    required: list[str] = scorecard.get("manifest_required_contracts", []) or []
    missing: list[str] = scorecard.get("manifest_missing_contracts", []) or []
    has_formal_exception: bool = scorecard.get(
        "manifest_has_formal_exception", False
    )
    reason_code: str = scorecard.get("manifest_exception_reason_code", "") or ""
    cc_count: int = scorecard.get("manifest_compensating_controls_count", 0) or 0
    declares_formal_route = any(
        rt in _FORMAL_EXCEPTION_ROUTE_TYPES for rt in claimed_routes
    )

    # Manifest-aware path runs FIRST. A manifest is the operator's
    # explicit declaration of intent.
    if manifest_present:
        # Branch 1: formal-exception routes. evaluator_only and
        # core_adjacent_utility have empty required-sets, but the
        # operator MUST back the empty-set claim with an exception
        # record + compensating controls. Without those, the manifest
        # is unverified and we refuse to grant any "valid" classification.
        if declares_formal_route:
            if has_formal_exception:
                return (
                    "FORMAL_EXCEPTION_STATIC_EVIDENCE",
                    f"manifest declares formal-exception routes {claimed_routes} "
                    f"with reason_code={reason_code!r} and "
                    f"{cc_count} compensating control(s); recorded charter honored",
                )
            return (
                "UNKNOWN_NEEDS_RUNTIME_TRACE",
                f"manifest declares formal-exception routes {claimed_routes} "
                "but is missing the supporting exception record "
                "(exception.reason_code and/or exception.compensating_controls); "
                "formal exception cannot be verified statically",
            )

        # Branch 2: empty required-set, non-formal route. This is the
        # build_time_compiler shape -- the route legitimately requires
        # no canonical contract handoff and the manifest is
        # self-justifying.
        if not required:
            return (
                "APP_OVERLAY_STATIC_EVIDENCE",
                f"manifest declares routes {claimed_routes} which require no "
                "canonical contract handoff; manifest-honored",
            )
        if not missing:
            return (
                "APP_OVERLAY_STATIC_EVIDENCE",
                f"manifest declares routes {claimed_routes}; "
                f"all required contracts present "
                f"({', '.join(required)})",
            )
        # Manifest present but contracts incomplete. This is
        # PARTIAL_SPINE_STATIC_ONLY when the app has *some* contracts
        # or any spine touch; it's APP_STANDALONE_FORBIDDEN only when
        # contracts AND spine edges are both zero AND it claims runtime.
        if has_contracts or has_static_spine:
            return (
                "PARTIAL_SPINE_STATIC_ONLY",
                f"manifest declares routes {claimed_routes} requiring "
                f"{len(required)} contract(s); imported "
                f"{scorecard['contract_count']} of them; missing: "
                f"{', '.join(missing)}",
            )
        if claims_runtime:
            return (
                "APP_STANDALONE_FORBIDDEN",
                f"manifest declares routes {claimed_routes} requiring "
                f"{len(required)} contract(s); imported zero contracts "
                "AND zero spine edges; shadow runtime",
            )
        return (
            "UNKNOWN_NEEDS_RUNTIME_TRACE",
            f"manifest declares routes {claimed_routes} but no domain-runtime "
            "markers and no spine imports; runtime trace required",
        )

    # Legacy (no-manifest) path. Lenient any-contract-counts fallback
    # so existing apps don't regress at rollout. Apps SHOULD declare a
    # manifest; until they do, the classification is approximate.
    if scorecard["non_stdlib_edges"] == 0:
        return (
            "UNKNOWN_NEEDS_RUNTIME_TRACE",
            "empty package: no non-stdlib imports and no manifest; "
            "static analysis cannot classify; runtime trace required",
        )

    if has_contracts:
        return (
            "APP_OVERLAY_STATIC_EVIDENCE",
            f"no spine_manifest.yaml; imports {scorecard['contract_count']} "
            f"canonical contract(s) ({', '.join(scorecard['distinct_contracts'])}); "
            "declare a manifest to enable route-typed validation",
        )

    if not claims_runtime:
        return (
            "UNKNOWN_NEEDS_RUNTIME_TRACE",
            "no domain-runtime markers (engines/integrations/router/CLI); "
            "static analysis cannot decide; runtime trace required",
        )

    if has_static_spine:
        return (
            "PARTIAL_SPINE_STATIC_ONLY",
            "claims domain runtime AND imports spine infrastructure (UWG/ledger/BGE), "
            "BUT zero canonical contract imports; static-only spine touch, "
            "runtime authority is local to the app -- not valid as overlay",
        )

    return (
        "APP_STANDALONE_FORBIDDEN",
        "claims domain runtime ("
        + ", ".join(scorecard["domain_runtime_reasons"])
        + ") AND zero canonical contracts AND zero spine import edges; "
        + "shadow runtime; constitutional violation",
    )


def _legacy_status_for(scorecard: dict) -> str:
    """Compute the legacy ON_SPINE / PARTIAL_SPINE / ... bucket.

    Preserved for downstream consumers that grep on the old strings;
    new consumers should read ``runtime_mode`` instead.
    """
    if scorecard["non_stdlib_edges"] == 0:
        return "EMPTY"
    if scorecard["agentic_core_edges"] == 0:
        return "OFF_SPINE"
    if scorecard["spine_coverage_pct"] < 5:
        return "BARELY_ON_SPINE"
    if scorecard["spine_coverage_pct"] < 20:
        return "PARTIAL_SPINE"
    return "ON_SPINE"


def scan_all() -> list[dict]:
    apps = sorted(
        d for d in REPO_ROOT.iterdir()
        if d.is_dir() and d.name.startswith("apps_")
    )
    results = []
    for app_dir in apps:
        sc = scan_app(app_dir)
        runtime_mode, evidence = classify_app(sc)
        sc["runtime_mode"] = runtime_mode
        sc["classification_evidence"] = evidence
        sc["status"] = _legacy_status_for(sc)  # backward-compat
        results.append(sc)
    return results


_RUNTIME_MODE_EMOJI: dict[str, str] = {
    "APP_OVERLAY_STATIC_EVIDENCE": "✅",
    # Legacy alias for one release cycle; same emoji.
    "APP_OVERLAY_VALID": "✅",
    # W8: formal-exception bucket -- structurally valid via recorded
    # charter rather than via canonical-contract delegation.
    "FORMAL_EXCEPTION_STATIC_EVIDENCE": "📜",
    "APP_STANDALONE_FORBIDDEN": "🔴",
    "PARTIAL_SPINE_STATIC_ONLY": "🟠",
    "UNKNOWN_NEEDS_RUNTIME_TRACE": "❔",
    "CORE_ONLY_VALID": "🔵",
}


def render_markdown(results: list[dict]) -> str:
    lines = []
    lines.append("# apps_* runtime-mode scorecard")
    lines.append("")
    lines.append(
        "**Methodology**: AST scan of every `apps_*/` package (excluding "
        "tests/fixtures). Detects (a) imports of canonical authority-class "
        "contracts FROM `agentic_core`, (b) domain-runtime markers "
        "(engines/integrations/router/CLI/wizard), and (c) infrastructure "
        "imports (UWG/ledger/BGE). Classifies per the five-bucket taxonomy "
        "in `docs/reference/APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md`."
    )
    lines.append("")
    lines.append(
        "**Authority-class contracts**: " + ", ".join(
            f"`{c}`" for c in sorted(CANONICAL_CONTRACTS)
        )
    )
    lines.append("")
    lines.append(
        "| App | Files | Spine % (legacy) | Contracts | Distinct contracts | Claims runtime | Runtime Mode |"
    )
    lines.append(
        "|---|---:|---:|---:|---|:---:|---|"
    )
    for r in results:
        rm = r.get("runtime_mode", "UNKNOWN_NEEDS_RUNTIME_TRACE")
        emoji = _RUNTIME_MODE_EMOJI.get(rm, "?")
        contract_summary = (
            ", ".join(f"`{c}`" for c in r["distinct_contracts"])
            if r["distinct_contracts"]
            else "—"
        )
        claims = "✓" if r["claims_domain_runtime"] else "—"
        lines.append(
            f"| `{r['app']}` | {r['files_scanned']} | {r['spine_coverage_pct']}% | "
            f"{r['contract_count']} | {contract_summary} | {claims} | {emoji} {rm} |"
        )
    lines.append("")
    lines.append("## Runtime-mode legend")
    lines.append("")
    lines.append(
        "- ✅ **APP_OVERLAY_VALID** — imports ≥1 canonical authority "
        "contract from `agentic_core`. Delegates to the spine."
    )
    lines.append(
        "- � **APP_STANDALONE_FORBIDDEN** — claims a domain runtime "
        "(engines/integrations/router/CLI) AND imports zero canonical "
        "contracts AND zero spine edges. Shadow runtime."
    )
    lines.append(
        "- 🟠 **PARTIAL_SPINE_STATIC_ONLY** — claims domain runtime AND "
        "imports spine infrastructure (UWG/ledger/BGE), BUT no "
        "authority-class contracts. Static-only spine touch."
    )
    lines.append(
        "- ❔ **UNKNOWN_NEEDS_RUNTIME_TRACE** — does not claim a domain "
        "runtime; static analysis cannot decide. Runtime trace required."
    )
    lines.append(
        "- � **CORE_ONLY_VALID** — reserved for non-`apps_*` paths."
    )
    lines.append("")
    lines.append("## Per-app classification evidence")
    lines.append("")
    for r in results:
        rm = r.get("runtime_mode", "UNKNOWN_NEEDS_RUNTIME_TRACE")
        ev = r.get("classification_evidence", "")
        emoji = _RUNTIME_MODE_EMOJI.get(rm, "?")
        lines.append(f"- {emoji} **`{r['app']}`** → {rm}")
        lines.append(f"  - {ev}")
        if r["distinct_contracts"]:
            lines.append(f"  - contracts: {', '.join(r['distinct_contracts'])}")
        if r["domain_runtime_reasons"]:
            lines.append(
                f"  - claims runtime via: {', '.join(r['domain_runtime_reasons'])}"
            )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of markdown")
    parser.add_argument("--app", default=None, help="Deep-dive a single app (e.g. apps_qna)")
    args = parser.parse_args(argv)

    if args.app:
        app_dir = REPO_ROOT / args.app
        if not app_dir.is_dir():
            print(f"App not found: {args.app}", file=sys.stderr)
            return 1
        sc = scan_app(app_dir)
        runtime_mode, evidence = classify_app(sc)
        sc["runtime_mode"] = runtime_mode
        sc["classification_evidence"] = evidence
        sc["status"] = _legacy_status_for(sc)
        # JSON in either branch — single-app deep-dive is always
        # machine-readable since the markdown render is built for the
        # multi-app comparison view.
        print(json.dumps(sc, indent=2, default=str))
        return 0

    results = scan_all()
    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        print(render_markdown(results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
