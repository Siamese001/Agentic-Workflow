#!/usr/bin/env python3
"""
FORENSIC DISCOVERY PREP - V10 GAP ANALYSIS TOOL
===============================================
Generates the authoritative "Environment Under Test" artifact for the
V10 Target State Gap Analysis.

USAGE:
    python forensic_discovery_prep_script.py [--out audit_context.json]

OUTPUT:
    A structured JSON artifact containing:
    1. Validated Agent Manifest (Identity + Path)
    2. Precise MRO Signatures (for Safety Mixin verification)
    3. Ghost/Invalid Agent Report

HARDENED INVARIANTS:
    - Deterministic ordering (stable output across runs)
    - Path traversal defense (validate all candidate paths are within project)
    - Evidence-rich records (file hash, size, parse errors, selection rationale)
    - Strict stub detection (sentinel in header, not substring anywhere)
    - Robust base extraction (no "UnknownBase" silently)
    - Atomic output write support (optional --out)
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import logging
import os
import platform
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

# ==============================================================================
# IMPORT STRATEGY: Inherit strict SSOT paths from production environment
# ==============================================================================
try:
    from agentic_core.L0_maintenance.utils.ssot_discovery_util import (
        load_agent_discovery,
    )
    from agentic_core.L5_safety.config.structure_blueprint.ssot import (
        FORENSIC_DISCOVERY_INTEGRITY_HASH,
        FORENSIC_DISCOVERY_SCRIPT,
    )
    from agentic_core.L5_safety.config.structure_blueprint_config import (  # noqa: F401
        AGENT_DISCOVERY_JSON,
        get_validated_project_root,
        validate_path_within_project,
    )
except ImportError:
    # Fallback for standalone auditing (if outside strict env)
    print("CRITICAL: SSOT imports failed. Ensure PYTHONPATH includes project root.", file=sys.stderr)
    sys.exit(1)

# Configure simplified logging for the tool
logging.basicConfig(level=logging.ERROR, format="%(message)s")
Logger = logging.getLogger("ForensicAudit")

# ==============================================================================
# Forensic Data Structures
# ==============================================================================


@dataclass
class ForensicAgentRecord:
    """The absolute truth for a single agent under audit."""

    agent_name: str
    layer: str
    file_path: str
    class_name: str
    mro_signature: list[str]  # Critical for Point 8.3 (Mixin Order)
    status: str  # ACTIVE | STUB | GHOST | INVALID | SYNTAX_ERROR
    methods_detected: list[str]
    # Evidence (drift-proofing)
    file_sha256: str = ""
    file_size_bytes: int = 0
    # Selection transparency
    selection_reason: str = ""
    selection_candidates: list[str] = field(default_factory=list)
    # Parse/validation diagnostics
    parse_error: str = ""
    # Convenience booleans for audit matrix
    has_heal: bool = False
    is_sovereign: bool = False


OUTPUT_SCHEMA_VERSION = "1.3.0"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_unparse(node: ast.AST) -> str:
    try:
        return ast.unparse(node)  # py>=3.9
    # guardian: allow-silent-swallow
    except Exception:
        return node.__class__.__name__


def extract_precise_mro(node: ast.ClassDef) -> list[str]:
    """
    Extracts base classes in exact declaration order to detect 'Inheritance Traps'.
    Example: class MyAgent(SafetyMixin, BaseAgent) -> ["SafetyMixin", "BaseAgent"]
    """
    bases = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            bases.append(base.id)
        elif isinstance(base, ast.Attribute):
            bases.append(f"{base.value.id}.{base.attr}" if isinstance(base.value, ast.Name) else base.attr)
        else:
            bases.append(safe_unparse(base))
    return bases


def build_class_bases_map(project_root: Path) -> dict[str, list[str]]:
    """Build repo-wide mapping of class_name → direct base class names from AST.

    Scans all .py files under known source roots to enable full MRO resolution.
    On name collision, first-seen definition wins (deterministic via sorted paths).
    Handles starred bases (e.g. ``class Foo(*BASE_CLASSES)``) by resolving
    module-level tuple assignments in the same file.
    """
    class_map: dict[str, list[str]] = {}
    scan_roots = [
        project_root / "agentic_core",
        project_root / "apps_lic",
        project_root / "apps_rg",
        project_root / "apps_shared",
    ]
    for root in scan_roots:
        if not root.exists():
            continue
        for py_file in sorted(root.rglob("*.py")):
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(content)

                # Collect tuple assignments for starred-base resolution
                # (walks full AST to catch assignments inside try/except blocks)
                module_tuples: dict[str, list[str]] = {}
                for stmt in ast.walk(tree):
                    if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
                        tgt = stmt.targets[0]
                        if isinstance(tgt, ast.Name) and isinstance(stmt.value, ast.Tuple):
                            elts = [e.id for e in stmt.value.elts if isinstance(e, ast.Name)]
                            if elts and tgt.id not in module_tuples:
                                module_tuples[tgt.id] = elts

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name not in class_map:
                        raw_bases = extract_precise_mro(node)
                        resolved: list[str] = []
                        for b in raw_bases:
                            if b.startswith("*") and b[1:] in module_tuples:
                                resolved.extend(module_tuples[b[1:]])
                            else:
                                resolved.append(b)
                        class_map[node.name] = resolved
            # guardian: allow-silent-swallow
            except (SyntaxError, Exception):  # noqa: BLE001
                continue
    return class_map


def resolve_full_mro(
    direct_bases: list[str],
    class_map: dict[str, list[str]],
    _seen: set[str] | None = None,
) -> list[str]:
    """Recursively expand direct bases into a full transitive MRO chain.

    Returns a flat list of all ancestor class names (deduplicated, depth-first).
    """
    if _seen is None:
        _seen = set()
    result: list[str] = []
    for base in direct_bases:
        simple = base.rsplit(".", 1)[-1] if "." in base else base
        if simple in _seen:
            continue
        _seen.add(simple)
        result.append(simple)
        if simple in class_map:
            result.extend(resolve_full_mro(class_map[simple], class_map, _seen))
    return result


def stub_sentinel_detected(content: str) -> bool:
    # STRICT: sentinel only in header to avoid accidental substring matches
    head = "\n".join(content.splitlines()[:60])
    return (
        ("STATUS: STUB" in head)
        or ("__AGENT_STATUS__" in head and "STUB" in head)
        or any(line.strip() == "NOT_AN_AGENT" for line in head.splitlines())
    )


def forensic_inspect(name: str, layer: str, file_path: Path) -> ForensicAgentRecord:
    """
    Analyzes a file to build the Forensic Record.
    """
    record = ForensicAgentRecord(
        agent_name=name,
        layer=layer,
        file_path=str(file_path),
        class_name="Unknown",
        mro_signature=[],
        status="INVALID",
        methods_detected=[],
    )

    if not file_path.exists():
        record.status = "GHOST"
        return record

    try:
        record.file_size_bytes = file_path.stat().st_size
        record.file_sha256 = sha256_file(file_path)
        content = file_path.read_text(encoding="utf-8", errors="replace")

        # Fast fail for Stubs
        if stub_sentinel_detected(content):
            record.status = "STUB"
            record.selection_reason = "Stub sentinel detected in file header"
            return record

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            record.status = "SYNTAX_ERROR"
            record.parse_error = f"SyntaxError: {e}"
            return record

        # Collect all classes, then deterministically select best candidate
        classes: list[ast.ClassDef] = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        record.selection_candidates = [c.name for c in classes]

        def score(cls: ast.ClassDef) -> int:
            bases = " ".join(extract_precise_mro(cls))
            s = 0
            # prefer explicit base agents / protocols
            if "SovereignBaseAgent" in bases or "BaseAgent" in bases:
                s += 100
            # prefer class name signals
            if "Agent" in cls.name:
                s += 10
            if "Healer" in cls.name:
                s += 5
            # prefer presence of heal/execute/run methods
            method_names = [i.name for i in cls.body if isinstance(i, ast.FunctionDef | ast.AsyncFunctionDef)]
            if "heal" in method_names:
                s += 20
            if any(m in method_names for m in ("execute", "run", "act")):
                s += 8
            return s

        if classes:
            chosen = sorted(classes, key=lambda c: (score(c), c.name), reverse=True)[0]
            if score(chosen) <= 0:
                record.status = "INVALID"
                record.selection_reason = "No viable agent class candidate (score<=0)"
                return record

            record.class_name = chosen.name
            record.mro_signature = extract_precise_mro(chosen)
            record.status = "ACTIVE"
            record.selection_reason = "Selected highest-scoring ClassDef deterministically"

            for item in chosen.body:
                if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                    record.methods_detected.append(item.name)
            record.has_heal = "heal" in record.methods_detected

    # guardian: allow-silent-swallow
    except Exception as e:
        record.status = f"ERROR: {str(e)}"
        record.parse_error = str(e)

    return record


# ==============================================================================
# Execution
# ==============================================================================


def get_git_commit(root: Path) -> str:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
        )
        return out.decode("utf-8").strip()
    # guardian: allow-silent-swallow
    except Exception:
        return ""


def atomic_write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(data, encoding="utf-8")
    os.replace(tmp, path)


# ==============================================================================
# V5.4 Schema Transformation
# ==============================================================================

V54_SCHEMA_VERSION = "5.4.0"


def _compute_ssot_validation(project_root: Path) -> dict[str, str]:
    """Compute ssot_validation section: self-hash vs SSOT constant."""
    script_path = project_root / FORENSIC_DISCOVERY_SCRIPT
    if script_path.exists():
        computed = hashlib.sha256(script_path.read_bytes()).hexdigest()
    else:
        computed = ""
    return {
        "blueprint_hash": FORENSIC_DISCOVERY_INTEGRITY_HASH,
        "status": "MATCH" if computed == FORENSIC_DISCOVERY_INTEGRITY_HASH else "MISMATCH",
    }


def _derive_mixins(mro_chain: list[str]) -> list[str]:
    """Derive mixins deterministically from MRO chain entries containing 'Mixin'."""
    return [entry for entry in mro_chain if "Mixin" in entry]


def _to_v54_schema(legacy: dict, project_root: Path) -> dict:
    """Transform legacy discovery output to v5.4 strict schema."""
    meta = legacy.get("audit_meta", {})
    v54: dict = {
        "meta": {
            "timestamp": meta.get("generated_at", ""),
            "root_path": meta.get("root", ""),
            "git_hash": meta.get("git_commit", ""),
            "schema_version": V54_SCHEMA_VERSION,
            "python_version": meta.get("python_version", ""),
            "platform": meta.get("platform", ""),
            "total_candidates": meta.get("total_candidates", 0),
        },
        "ssot_validation": _compute_ssot_validation(project_root),
        "agents": [],
    }
    for agent in legacy.get("environment_under_test", []):
        mro_chain = agent.get("mro_signature", [])
        v54["agents"].append(
            {
                "identity": agent.get("agent_name", ""),
                "layer": agent.get("layer", ""),
                "status": agent.get("status", ""),
                "file_path": agent.get("file_path", ""),
                "class_name": agent.get("class_name", ""),
                "mro_chain": mro_chain,
                "mixins": _derive_mixins(mro_chain),
                "detected_methods": agent.get("methods_detected", []),
                "integrity_hash": agent.get("file_sha256", ""),
                "is_sovereign": agent.get("is_sovereign", False),
            },
        )
    return v54


def run_forensic_discovery(out_path: Path | None = None, *, legacy_schema: bool = False) -> int:
    project_root = get_validated_project_root()

    # 0. Build repo-wide class→bases map for full MRO resolution
    class_bases_map = build_class_bases_map(project_root)

    # 1. Load the Candidate List from SSOT
    raw_candidates = load_agent_discovery(project_root, force_reload=True)
    raw_candidates = sorted(
        raw_candidates,
        key=lambda c: (c.get("layer", ""), c.get("class_name", ""), c.get("file", "")),
    )

    manifest = {
        "audit_meta": {
            "root": str(project_root),
            "total_candidates": len(raw_candidates),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "output_schema_version": OUTPUT_SCHEMA_VERSION,
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "git_commit": get_git_commit(project_root),
        },
        "environment_under_test": [],
        "ignored_artifacts": [],
        "counts": {},
    }

    # 2. Inspect every candidate
    for candidate in raw_candidates:
        rel_path = candidate.get("file", "") or candidate.get("path", "")
        name = candidate.get("class_name", "") or candidate.get("name", "Unknown")
        layer = candidate.get("layer", "Unknown")

        if not rel_path:
            record = ForensicAgentRecord(
                agent_name=name,
                layer=layer,
                file_path="",
                class_name="Unknown",
                mro_signature=[],
                status="INVALID",
                methods_detected=[],
                selection_reason="Missing path in SSOT candidate",
            )
            manifest["ignored_artifacts"].append(asdict(record))
            continue

        full_path = project_root / rel_path
        try:
            validate_path_within_project(project_root, full_path)
        # guardian: allow-silent-swallow
        except Exception:
            record = ForensicAgentRecord(
                agent_name=name,
                layer=layer,
                file_path=str(full_path),
                class_name="Unknown",
                mro_signature=[],
                status="INVALID",
                methods_detected=[],
                selection_reason="Path fails validate_path_within_project",
            )
            manifest["ignored_artifacts"].append(asdict(record))
            continue

        record = forensic_inspect(name, layer, full_path)

        # Enrich with full transitive MRO and sovereign classification.
        # Prefer class_bases_map (starred bases already resolved) over raw AST.
        direct_bases = class_bases_map.get(record.class_name, record.mro_signature)
        if direct_bases:
            full_chain = resolve_full_mro(direct_bases, class_bases_map)
            record.mro_signature = full_chain
            record.is_sovereign = "SovereignBaseAgent" in full_chain

        if record.status == "ACTIVE":
            manifest["environment_under_test"].append(asdict(record))
        else:
            manifest["ignored_artifacts"].append(asdict(record))

    # 3. Deterministic ordering and counts
    manifest["environment_under_test"] = sorted(
        manifest["environment_under_test"],
        key=lambda r: (r["agent_name"], r["file_path"]),
    )
    manifest["ignored_artifacts"] = sorted(
        manifest["ignored_artifacts"],
        key=lambda r: (r["agent_name"], r["file_path"]),
    )

    counts: dict[str, int] = {}
    for r in manifest["environment_under_test"] + manifest["ignored_artifacts"]:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    manifest["counts"] = dict(sorted(counts.items(), key=lambda kv: kv[0]))

    if legacy_schema:
        output = manifest
    else:
        output = _to_v54_schema(manifest, project_root)

    payload = json.dumps(output, indent=2)
    if out_path:
        atomic_write(out_path, payload)
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Forensic Discovery Prep (Audit Scope Generator)")
        parser.add_argument("--out", help="Write JSON output to file atomically (recommended)")
        parser.add_argument(
            "--legacy-schema",
            action="store_true",
            default=False,
            help="Emit legacy schema (audit_meta/environment_under_test) instead of v5.4",
        )
        args = parser.parse_args()

        outp = Path(args.out) if args.out else None
        rc = run_forensic_discovery(outp, legacy_schema=args.legacy_schema)
        sys.exit(rc)
    # guardian: allow-silent-swallow
    except Exception as e:
        print(json.dumps({"fatal_error": str(e)}))
        sys.exit(1)
