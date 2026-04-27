"""
Phase 1 — normative requirement extractor.

Reads each ingested source file line by line, skips fenced code blocks, and
emits a RequirementRecord for every line that contains at least one
normative marker. Every record carries:

    * req_id          : REQ-<source_slug>-<line_start:04d>-<8-hex-sha1>
    * source_folder   : absolute folder path
    * source_path     : absolute file path
    * relative_path   : repo-relative POSIX path
    * line_start/end  : 1-indexed
    * source_text     : raw line
    * requirement_type: from TYPE_RULES classification
    * owning_layer    : derived from folder + filename prefix
    * normalized_requirement : whitespace-collapsed
    * verification_needed    : tuple of evidence categories required
    * status          : always UNMAPPED at extract time
    * matched_markers : tuple of marker tokens that triggered extraction

By design, this extractor over-extracts in ambiguous cases. Refinement to
PROVEN status happens in Phase 2 (implementation mapping) and Phase 3
(coverage matrix), never here.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import List

from agentic_core.runtime.prove_requirements.constants import (
    C0_SUBSTAGES,
    FENCE_RE,
    FOLDER_TO_LAYER,
    L3_FILENAME_PREFIXES,
    NORMATIVE_PATTERNS,
    REPO_ROOT,
    TYPE_RULES,
    verification_needed_for_type,
)
from agentic_core.runtime.prove_requirements.types import RequirementRecord


_SLUG_NORMALIZE_RE = re.compile(r"[^a-z0-9]+")
_WHITESPACE_RE = re.compile(r"\s+")


def _slug_for_path(rel_path: str) -> str:
    base = Path(rel_path).stem.lower()
    slug = _SLUG_NORMALIZE_RE.sub("-", base).strip("-")
    return slug[:48] if len(slug) > 48 else slug


def _stable_hash(text: str) -> str:
    return hashlib.sha1(text.strip().encode("utf-8")).hexdigest()[:8]


def _classify_owning_layer(rel_path: str) -> str:
    parts = Path(rel_path).parts
    # rel_path is e.g. "docs/reference/03A_C0_Context_Engine/C0.5_Final...md"
    folder_name = parts[2] if len(parts) >= 3 else ""
    base_layer = FOLDER_TO_LAYER.get(folder_name, "CrossCutting")
    fname = parts[-1]
    if folder_name == "03A_C0_Context_Engine":
        for sub in C0_SUBSTAGES:
            if fname.startswith(sub + "_") or fname.startswith(sub + "."):
                return sub
        return "C0"
    if folder_name == "03_L0_Route_Decision_and_L3_Orchestration":
        for prefix in L3_FILENAME_PREFIXES:
            if fname.startswith(prefix):
                return "L3"
        if fname.lower().startswith("r1b") or "R3" in fname:
            return "L0"
        return "L0"
    return base_layer


def _classify_requirement_type(line: str) -> str:
    for pat, t in TYPE_RULES:
        if pat.search(line):
            return t
    return "contract"


def _detect_markers(line: str) -> List[str]:
    out: List[str] = []
    for pat, name in NORMATIVE_PATTERNS:
        if pat.search(line):
            out.append(name)
    return out


def _normalize(line: str) -> str:
    # Strip leading markdown bullet/heading markers but keep the substantive
    # text so the hash/normalized form is stable across cosmetic edits.
    stripped = line.strip()
    # Collapse leading list/quote markers like "- ", "* ", "> ", "1. ", "## "
    stripped = re.sub(r"^([-*>+]\s+|\d+\.\s+|#{1,6}\s+|\|\s+)", "", stripped)
    return _WHITESPACE_RE.sub(" ", stripped)


def extract_from_file(repo_root: Path, rel_path: str) -> List[RequirementRecord]:
    """Parse one file and return a list of RequirementRecord."""
    abs_path = (repo_root / rel_path).resolve()
    parts = Path(rel_path).parts
    folder_abs = (
        (repo_root / "/".join(parts[:3])).resolve() if len(parts) >= 3 else repo_root
    )
    slug = _slug_for_path(rel_path)
    layer = _classify_owning_layer(rel_path)

    out: List[RequirementRecord] = []
    in_fence = False

    try:
        text_iter = abs_path.open("r", encoding="utf-8", errors="replace")
    except (OSError, IOError):
        return out

    with text_iter as f:
        for line_no, raw in enumerate(f, start=1):
            line = raw.rstrip("\n").rstrip("\r")
            if FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if len(line.strip()) < 4:
                continue
            markers = _detect_markers(line)
            if not markers:
                continue
            normalized = _normalize(line)
            if len(normalized) < 8:
                continue
            req_type = _classify_requirement_type(line)
            req_id = f"REQ-{slug}-{line_no:04d}-{_stable_hash(normalized)}"
            rec = RequirementRecord(
                req_id=req_id,
                source_folder=str(folder_abs),
                source_path=str(abs_path),
                relative_path=rel_path,
                line_start=line_no,
                line_end=line_no,
                source_text=line,
                requirement_type=req_type,
                owning_layer=layer,
                normalized_requirement=normalized,
                verification_needed=verification_needed_for_type(req_type),
                status="UNMAPPED",
                matched_markers=tuple(markers),
            )
            out.append(rec)
    return out


def extract_from_manifest(
    manifest: dict, repo_root: Path | None = None
) -> List[RequirementRecord]:
    """Apply extract_from_file across every ingested file in the manifest."""
    rr = (repo_root or REPO_ROOT).resolve()
    out: List[RequirementRecord] = []
    for entry in manifest.get("files", []):
        out.extend(extract_from_file(rr, entry["relative_path"]))
    return out
