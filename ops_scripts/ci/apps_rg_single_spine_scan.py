"""AST/static scan for apps_rg single-spine W1 ratchet (plan apps-rg-spine-only-unification-d8f4a2).

Shared by ``check_apps_rg_single_spine.py`` and ``tests/_apps_contract/test_apps_rg_no_second_pipeline.py``.
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator

REPO_ROOT = Path(__file__).resolve().parents[2]

# Product-path SSOT (W1) — expand only via plan wave approval.
PRODUCT_SCAN_REL_PATHS: tuple[str, ...] = (
    "apps_rg/__main__.py",
    "apps_rg/runtime/orchestration/canonical_dispatch.py",
    "apps_rg/runtime/spine",
    "apps_rg/runtime/sections",
)

FORBIDDEN_IMPORT_MODULE_PREFIXES: tuple[str, ...] = (
    "apps_rg.runtime.section_front_spine_bridge",
    "apps_rg.runtime.section_fec_bridge",
    "apps_rg.runtime.c03_graphrag_bound",
    "apps_rg.runtime.section_exit_spine_receipt",
    "apps_rg.runtime.section_runtime_exhaust_spine_receipt",
    "apps_rg.runtime.proof_pool_lane_integration",
)

# String tokens that must not appear as import targets in product paths.
FORBIDDEN_IMPORT_MODULE_EXACT: frozenset[str] = frozenset(
    {
        "apps_rg.runtime.section_front_spine_bridge",
        "apps_rg.runtime.section_fec_bridge",
        "apps_rg.runtime.c03_graphrag_bound",
        "apps_rg.runtime.section_exit_spine_receipt",
        "apps_rg.runtime.section_runtime_exhaust_spine_receipt",
        "apps_rg.runtime.proof_pool_lane_integration",
    }
)

FORBIDDEN_SOURCE_SUBSTRINGS: tuple[tuple[str, str], ...] = (
    ("wire_section_fec_bridge_for_lane", "FORBIDDEN_BRIDGE_CALL wire_section_fec_bridge_for_lane"),
    ("build_section_fec_bridge", "FORBIDDEN_BRIDGE_CALL build_section_fec_bridge"),
)

LANE_FROM_CLI_PATTERN = re.compile(r"^def _run_.+_lane_from_cli\b", re.MULTILINE)

SPINE_SECTION_CONTRACT_FILENAMES: tuple[str, ...] = (
    "validated_request.json",
    "l1_plan_contract.json",
    "route_contract.json",
    "final_evidence_contract.json",
    "compiled_prompt_artifact.json",
    "sealed_l2_artifact.json",
    "exit_disposition_receipt.json",
)

MIRROR_EXIT_HELPERS: frozenset[str] = frozenset(
    {
        "build_exit_disposition_receipt_for_section",
        "build_exit_review_packet_for_section",
        "build_exit_spine_receipt_for_section",
    }
)

PROOF_POOL_BYPASS_MODULES: frozenset[str] = frozenset(
    {
        "apps_rg.runtime.proof_pool_resolver",
        "apps_rg.runtime.proof_pool_lane_integration",
    }
)

PA_LANE_FILENAME_MARKERS: frozenset[str] = frozenset({"_pa.py"})


@dataclass(frozen=True)
class SingleSpineFinding:
    code: str
    severity: str  # ERROR | WARN
    file: str
    line: int
    message: str
    extra: dict = field(default_factory=dict)


def iter_product_python_files(repo_root: Path | None = None) -> Iterator[Path]:
    root = repo_root or REPO_ROOT
    for rel in PRODUCT_SCAN_REL_PATHS:
        path = root / rel.replace("/", root.anchor and "\\" or "/")
        if not path.exists():
            continue
        if path.is_file() and path.suffix == ".py":
            yield path
            continue
        if path.is_dir():
            for py in sorted(path.rglob("*.py")):
                if "__pycache__" in py.parts:
                    continue
                yield py


def _rel_posix(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def _imports_in_tree(tree: ast.AST) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.append((node.lineno, node.module))
    return out


def _is_forbidden_bridge_import(mod: str) -> bool:
    if mod in FORBIDDEN_IMPORT_MODULE_EXACT:
        return True
    if any(mod.startswith(p) for p in FORBIDDEN_IMPORT_MODULE_PREFIXES):
        return True
    mod_lower = mod.lower()
    bridge_tokens = (
        "section_fec_bridge",
        "section_front_spine_bridge",
        "c03_graphrag_bound",
        "section_exit_spine_receipt",
        "section_runtime_exhaust_spine_receipt",
        "section_c03_graph_binding",
    )
    if any(tok in mod_lower for tok in bridge_tokens):
        return True
    if "_bridge" in mod_lower and "apps_rg.runtime" in mod_lower:
        return True
    if "mirror" in mod_lower and "receipt" in mod_lower:
        return True
    return False


def _scan_forbidden_imports(
    rel: str, imports: list[tuple[int, str]]
) -> list[SingleSpineFinding]:
    findings: list[SingleSpineFinding] = []
    for lineno, mod in imports:
        if not _is_forbidden_bridge_import(mod):
            continue
        code = (
            "FORBIDDEN_BRIDGE_IMPORT"
            if mod in FORBIDDEN_IMPORT_MODULE_EXACT
            or any(mod.startswith(p) for p in FORBIDDEN_IMPORT_MODULE_PREFIXES)
            else "SUSPICIOUS_BRIDGE_IMPORT"
        )
        findings.append(
            SingleSpineFinding(
                code=code,
                severity="ERROR",
                file=rel,
                line=lineno,
                message=f"Product path must not import second-pipeline module {mod!r}",
            )
        )
    return findings


def _scan_source_substrings(rel: str, source: str) -> list[SingleSpineFinding]:
    findings: list[SingleSpineFinding] = []
    for token, msg in FORBIDDEN_SOURCE_SUBSTRINGS:
        if token in source:
            line = source[: source.index(token)].count("\n") + 1
            findings.append(
                SingleSpineFinding(
                    code="FORBIDDEN_BRIDGE_PATTERN",
                    severity="ERROR",
                    file=rel,
                    line=line,
                    message=msg,
                )
            )
    return findings


def _scan_lane_from_cli(rel: str, source: str) -> list[SingleSpineFinding]:
    if rel != "apps_rg/runtime/orchestration/canonical_dispatch.py":
        return []
    findings: list[SingleSpineFinding] = []
    for match in LANE_FROM_CLI_PATTERN.finditer(source):
        line = source[: match.start()].count("\n") + 1
        findings.append(
            SingleSpineFinding(
                code="FORBIDDEN_LANE_FROM_CLI",
                severity="ERROR",
                file=rel,
                line=line,
                message="Second pipeline entry: _run_*_lane_from_cli must be removed (use apps_rg_spine_run)",
                extra={"symbol": match.group(0)},
            )
        )
    return findings


def _scan_x3_without_spine_exit(rel: str, source: str) -> list[SingleSpineFinding]:
    if "x3_disposition.json" not in source:
        return []
    writes_x3 = "x3_disposition.json" in source and (
        "write_json" in source or '"/x3_disposition.json"' in source or "'x3_disposition.json'" in source
    )
    if not writes_x3:
        return []
    has_spine_exit = (
        "ExitEvalPipeline" in source
        or "finalize_section_lane_x3" in source
        or "section_x3_finalize" in source
    )
    has_mirror = any(h in source for h in MIRROR_EXIT_HELPERS) or (
        "section_exit_spine_receipt" in source
    )
    findings: list[SingleSpineFinding] = []
    if not has_spine_exit:
        line = source.find("x3_disposition.json")
        line_no = source[:line].count("\n") + 1 if line >= 0 else 1
        findings.append(
            SingleSpineFinding(
                code="X3_WITHOUT_SPINE_EXIT_RECEIPT",
                severity="ERROR",
                file=rel,
                line=line_no,
                message=(
                    "x3_disposition.json must not be written without ExitEvalPipeline "
                    "emitting exit_disposition_receipt.json (lane aggregate_x3 is not authority)"
                ),
            )
        )
    if has_mirror and not has_spine_exit:
        findings.append(
            SingleSpineFinding(
                code="MIRROR_EXIT_RECEIPT_SUBSTITUTE",
                severity="ERROR",
                file=rel,
                line=1,
                message="Mirror exit receipts are not substitutes for ExitEvalPipeline exit_disposition_receipt.json",
            )
        )
    if "aggregate_x3(" in source and not has_spine_exit and not rel.startswith(
        "apps_rg/runtime/spine/"
    ):
        line = source.find("aggregate_x3(")
        findings.append(
            SingleSpineFinding(
                code="LANE_AGGREGATE_X3_AS_AUTHORITY",
                severity="ERROR",
                file=rel,
                line=source[:line].count("\n") + 1,
                message="aggregate_x3 may be judge math only; spine ExitEvalPipeline must own final X3",
            )
        )
    return findings


def _scan_proof_pool_bypass(rel: str, imports: list[tuple[int, str]], path: Path) -> list[SingleSpineFinding]:
    if not rel.startswith("apps_rg/runtime/sections/"):
        return []
    is_pa = any(marker in path.name for marker in PA_LANE_FILENAME_MARKERS)
    findings: list[SingleSpineFinding] = []
    for lineno, mod in imports:
        if mod in PROOF_POOL_BYPASS_MODULES or mod.startswith("apps_rg.runtime.proof_pool"):
            # proof_pool_resolver only legal inside c0_binding (not in product scan scope here)
            findings.append(
                SingleSpineFinding(
                    code="PROOF_POOL_BYPASS_PA_OR_LANE",
                    severity="ERROR",
                    file=rel,
                    line=lineno,
                    message=(
                        f"proof pool module {mod!r} in product path — "
                        "evidence must enter via c0_retrieve_apps_rg only"
                    ),
                    extra={"is_pa_module": is_pa},
                )
            )
    return findings


def scan_file(path: Path, repo_root: Path | None = None) -> list[SingleSpineFinding]:
    root = repo_root or REPO_ROOT
    rel = _rel_posix(path, root)
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [
            SingleSpineFinding(
                code="SCAN_READ_ERROR",
                severity="ERROR",
                file=rel,
                line=0,
                message=str(exc),
            )
        ]
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return [
            SingleSpineFinding(
                code="SCAN_SYNTAX_ERROR",
                severity="ERROR",
                file=rel,
                line=exc.lineno or 0,
                message=str(exc),
            )
        ]
    imports = _imports_in_tree(tree)
    findings: list[SingleSpineFinding] = []
    findings.extend(_scan_forbidden_imports(rel, imports))
    findings.extend(_scan_source_substrings(rel, source))
    findings.extend(_scan_lane_from_cli(rel, source))
    findings.extend(_scan_x3_without_spine_exit(rel, source))
    findings.extend(_scan_proof_pool_bypass(rel, imports, path))
    return findings


def scan_product_paths(repo_root: Path | None = None) -> list[SingleSpineFinding]:
    root = repo_root or REPO_ROOT
    all_findings: list[SingleSpineFinding] = []
    for path in iter_product_python_files(root):
        all_findings.extend(scan_file(path, root))
    return all_findings


def findings_with_errors(findings: Iterable[SingleSpineFinding]) -> list[SingleSpineFinding]:
    return [f for f in findings if f.severity == "ERROR"]


def summarize_findings(findings: list[SingleSpineFinding]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for f in findings:
        counts[f.code] = counts.get(f.code, 0) + 1
    return counts
