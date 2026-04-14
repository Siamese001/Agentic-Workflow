"""
AST-based archive recovery auditor for apps_rg migration planning.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import logging
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path

from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
LOGGER = logging.getLogger(__name__)
DEFAULT_ARCHIVE_RELATIVE_PATHS = [
    Path("archives") / "Reachout Engine Archive",
    Path("archives") / "resume_gen_json",
]
DEFAULT_TARGET_ROOT = Path("apps_rg")
DEFAULT_OUTPUT_NAME = "RG_ARCHIVE_RECOVERY_PLAN.json"


def _resolve_repo_root(explicit_root: str | None = None) -> Path:
    if explicit_root:
        return Path(explicit_root).expanduser().resolve()
    env_root = os.getenv("AGENTIC_WORKFLOW_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists():
            return candidate
    return Path.cwd().resolve()


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.replace(path)


@dataclass
class LogicSignature:
    name: str
    type: str
    content_hash: str
    line_count: int
    is_stateful: bool = False
    docstring: str = ""


@dataclass
class FileAudit:
    path: str
    signatures: list[LogicSignature] = field(default_factory=list)
    classification: str = "unknown"
    redundancy_score: float = 0.0
    target_destination: str | None = None
    refactor_notes: list[str] = field(default_factory=list)


class LogicHasher(ast.NodeVisitor):
    def __init__(self) -> None:
        self.signatures: list[LogicSignature] = []

    @staticmethod
    def _normalize_and_hash(node: ast.AST) -> str:
        content_to_hash = ast.dump(node, include_attributes=False)
        return hashlib.sha256(content_to_hash.encode("utf-8")).hexdigest()

    @staticmethod
    def _line_count(node: ast.AST) -> int:
        start = getattr(node, "lineno", 0)
        end = getattr(node, "end_lineno", start)
        return max(1, end - start + 1)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        is_stateful = any(
            child.name in {"__init__", "execute", "run", "process", "act"}
            for child in node.body
            if isinstance(child, ast.FunctionDef)
        )
        bases = [base.id for base in node.bases if isinstance(base, ast.Name)]
        is_type = any(base in {"Enum", "BaseModel", "TypedDict"} for base in bases)
        sig_type = "type" if is_type else "class"
        self.signatures.append(
            LogicSignature(
                name=node.name,
                type=sig_type,
                content_hash=self._normalize_and_hash(node),
                line_count=self._line_count(node),
                is_stateful=is_stateful,
                docstring=ast.get_docstring(node) or "",
            )
        )
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.signatures.append(
            LogicSignature(
                name=node.name,
                type="function",
                content_hash=self._normalize_and_hash(node),
                line_count=self._line_count(node),
                docstring=ast.get_docstring(node) or "",
            )
        )
        self.generic_visit(node)


def scan_file(filepath: Path) -> FileAudit | None:
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
        if not content.strip():
            return None
        tree = ast.parse(content, filename=str(filepath))
    except (OSError, SyntaxError, UnicodeDecodeError, ValueError) as exc:
        LOGGER.warning("Skipping %s: %s", filepath.name, exc)
        return None

    hasher = LogicHasher()
    hasher.visit(tree)
    if not hasher.signatures:
        return None

    classification = "unknown"
    signatures = hasher.signatures
    if any(signature.type == "type" for signature in signatures):
        classification = "Type"
    elif any(signature.type == "class" and signature.is_stateful for signature in signatures):
        classification = "Engine"
    elif any(signature.type in {"class", "function"} for signature in signatures):
        classification = "Tool"

    return FileAudit(path=str(filepath), signatures=signatures, classification=classification)


def build_recovery_plan(repo_root: Path, archive_roots: list[Path], target_root: Path) -> list[dict]:
    LOGGER.info("Building logic fingerprint for %s (baseline)...", target_root)
    target_signatures: set[str] = set()

    if target_root.exists():
        for py_file in target_root.rglob("*.py"):
            audit = scan_file(py_file)
            if not audit:
                continue
            for signature in audit.signatures:
                target_signatures.add(signature.content_hash)

    LOGGER.info("Indexed %d unique logic blocks in %s.", len(target_signatures), target_root.name)
    recovery_plan: list[dict] = []

    for archive_root in archive_roots:
        if not archive_root.exists():
            LOGGER.warning("Archive path not found: %s", archive_root)
            continue

        LOGGER.info("Scanning archive: %s", archive_root.name)
        for py_file in tqdm(sorted(archive_root.rglob("*.py")), desc="Processing", unit="file"):
            audit = scan_file(py_file)
            if not audit:
                continue

            matches = sum(1 for signature in audit.signatures if signature.content_hash in target_signatures)
            total = len(audit.signatures)
            audit.redundancy_score = matches / total if total else 0.0

            if audit.redundancy_score == 1.0:
                audit.target_destination = "REJECT_DUPLICATE"
            elif audit.classification == "Engine":
                audit.target_destination = f"apps_rg/engines/{py_file.name}"
                audit.refactor_notes.append("Must inherit RGAgentBase")
            elif audit.classification == "Tool":
                audit.target_destination = f"apps_rg/shared/tools/{py_file.name}"
            elif audit.classification == "Type":
                new_name = py_file.stem.replace("Agent", "") + "_types.py"
                audit.target_destination = f"apps_rg/domain/types/{new_name}"

            recovery_plan.append(asdict(audit))

    return recovery_plan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build an archive recovery plan for apps_rg.")
    parser.add_argument("--repo-root", help="Override automatic repository root detection.")
    parser.add_argument(
        "--output",
        help="Output JSON path. Defaults to apps_rg/RG_ARCHIVE_RECOVERY_PLAN.json under the detected repo root.",
    )
    args = parser.parse_args(argv)

    repo_root = _resolve_repo_root(args.repo_root)
    archive_roots = [repo_root / rel_path for rel_path in DEFAULT_ARCHIVE_RELATIVE_PATHS]
    target_root = repo_root / DEFAULT_TARGET_ROOT
    output_path = (
        Path(args.output).expanduser().resolve() if args.output else target_root / DEFAULT_OUTPUT_NAME
    )

    recovery_plan = build_recovery_plan(repo_root, archive_roots, target_root)
    _atomic_write(output_path, json.dumps(recovery_plan, indent=2) + "\n")
    LOGGER.info("Audit complete. Report saved to %s", output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
