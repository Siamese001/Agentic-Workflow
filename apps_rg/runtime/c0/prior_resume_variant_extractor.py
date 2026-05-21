"""Extract claim-sized atoms from prior résumé variants (not paragraphs as proof)."""

from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from apps_rg.fact_inventory.candidate_fact_ledger import (
    default_ledger_path,
    load_master_candidate_fact_ledger,
)
from apps_rg.runtime.c0.constants import (
    CLAIM_ELIGIBLE,
    CONFIDENCE_HIGH,
    CONFIDENCE_LOW,
    CONFIDENCE_MEDIUM,
    CONFIDENCE_PENDING,
    NOT_PROOF,
    PROOF_ELIGIBLE,
    REPO_ROOT,
    TARGETING_ONLY,
)

_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

_VARIANT_FAMILY_RULES: tuple[tuple[str, str], ...] = (
    ("AI and Data Governance", "AI/Data/Governance"),
    ("Chief AI Officer", "AI/Data/Governance"),
    ("Head of Data", "AI/Data/Governance"),
    ("Data Governance", "AI/Data/Governance"),
    ("Quantitative", "Financial/Quant"),
    ("Strategic Finance", "Financial/Quant"),
    ("VP Finance", "Financial/Quant"),
    ("FSA", "Financial/Quant"),
    ("Chief Technology Officer", "CTO/Platform"),
    ("CTO Resume", "CTO/Platform"),
    ("Field CTO", "CTO/Platform"),
    ("Sales", "GTM/Sales/Industry"),
    ("Strategic Account", "GTM/Sales/Industry"),
    ("Industry Solutions", "GTM/Sales/Industry"),
    ("Partnerships", "Partnerships/Alliances"),
    ("Partner Development", "Partnerships/Alliances"),
    ("Revenue Operations", "RevOps/Customer Success/Finance"),
    ("Head of Customer Success", "RevOps/Customer Success/Finance"),
    ("Customer Success", "RevOps/Customer Success/Finance"),
)

_SKIP_LINE_RE = re.compile(
    r"^(experience|education|skills|summary|profile|certifications|"
    r"professional experience|work history|contact|references)\s*:?\s*$",
    re.I,
)
_BULLET_PREFIX_RE = re.compile(r"^[\u2022\u25cf\u25aa\-\*•]\s*")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")


def _variant_family(name: str) -> str:
    base = Path(name).stem
    for needle, family in _VARIANT_FAMILY_RULES:
        if needle.lower() in base.lower():
            return family
    return "General/Other"


def _read_docx_paragraphs(path: Path) -> list[str]:
    lines: list[str] = []
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml")
    root = ET.fromstring(xml)
    for p in root.findall(".//w:p", _NS):
        parts: list[str] = []
        for t in p.findall(".//w:t", _NS):
            if t.text:
                parts.append(t.text)
        text = "".join(parts).strip()
        if text:
            lines.append(text)
    return lines


def _claim_sized_atoms_from_lines(lines: list[str]) -> list[tuple[str, str]]:
    """Return (source_span_ref, atom_text) — bullets/lines only, not merged paragraphs."""
    out: list[tuple[str, str]] = []
    for idx, raw in enumerate(lines):
        line = _BULLET_PREFIX_RE.sub("", raw).strip()
        if len(line) < 12 or _SKIP_LINE_RE.match(line):
            continue
        if len(line) > 280:
            for j, sent in enumerate(_SENTENCE_SPLIT_RE.split(line)):
                s = sent.strip()
                if len(s) >= 12:
                    out.append((f"line_{idx}:sent_{j}", s[:400]))
            continue
        out.append((f"line_{idx}", line[:400]))
    return out


def _ledger_claim_index(repo_root: Path) -> dict[str, str]:
    try:
        ledger = load_master_candidate_fact_ledger(repo_root=repo_root, path=default_ledger_path(repo_root))
    except (OSError, json.JSONDecodeError, KeyError):
        return {}
    index: dict[str, str] = {}
    for row in ledger.get("candidate_facts") or ledger.get("facts") or []:
        if not isinstance(row, dict):
            continue
        fid = str(row.get("candidate_fact_id") or row.get("fact_id") or "").strip()
        claim = str(row.get("claim_text") or "").strip().lower()
        if fid and claim and claim not in index:
            index[claim] = fid
    return index


def _match_fact_id(atom: str, ledger_index: dict[str, str]) -> str | None:
    key = atom.strip().lower()
    if key in ledger_index:
        return ledger_index[key]
    for claim, fid in ledger_index.items():
        if len(claim) >= 20 and (claim in key or key in claim):
            return fid
    return None


def _classify_row(
    *,
    atom: str,
    matched_fact_id: str | None,
) -> dict[str, str]:
    if matched_fact_id:
        return {
            "confidence": CONFIDENCE_HIGH,
            "proof_status": PROOF_ELIGIBLE,
            "requires_trace_audit": "false",
            "embed_allowed": "true",
            "reason": "matched canonical fact ledger row",
        }
    return {
        "confidence": CONFIDENCE_PENDING,
        "proof_status": CLAIM_ELIGIBLE,
        "requires_trace_audit": "true",
        "embed_allowed": "false",
        "reason": "prior variant atom unmatched to ledger — PENDING_TRACE default",
    }


def extract_prior_resume_manifest_rows(
    source_dir: Path,
    *,
    repo_root: Path | None = None,
) -> list[dict[str, Any]]:
    root = repo_root or REPO_ROOT
    ledger_index = _ledger_claim_index(root)
    rows: list[dict[str, Any]] = []
    for docx in sorted(source_dir.glob("*.docx")):
        variant = docx.name
        family = _variant_family(variant)
        try:
            paragraphs = _read_docx_paragraphs(docx)
        except (OSError, zipfile.BadZipFile, ET.ParseError):
            continue
        for span_ref, atom in _claim_sized_atoms_from_lines(paragraphs):
            matched = _match_fact_id(atom, ledger_index)
            cls = _classify_row(atom=atom, matched_fact_id=matched)
            rows.append(
                {
                    "source_resume_variant": variant,
                    "variant_family": family,
                    "candidate_fact_atom": atom,
                    "source_span_ref": f"{variant}::{span_ref}",
                    "matched_existing_fact_id": matched,
                    "confidence": cls["confidence"],
                    "proof_status": cls["proof_status"],
                    "requires_trace_audit": cls["requires_trace_audit"] == "true",
                    "embed_allowed": cls["embed_allowed"] == "true",
                    "reason": cls["reason"],
                }
            )
    return rows


def write_prior_resume_extraction_manifest(
    *,
    repo_root: Path | None = None,
    source_dir: Path | None = None,
    out_path: Path | None = None,
) -> Path:
    root = repo_root or REPO_ROOT
    src = source_dir or (root / "artifacts/apps_rg/c0/_prior_resume_extract_staging")
    dest = out_path or (root / "artifacts/apps_rg/c0/prior_resume_variant_fact_extraction_manifest.json")
    rows = extract_prior_resume_manifest_rows(src, repo_root=root)
    payload = {
        "schema_version": "prior_resume_variant_fact_extraction_manifest_v1",
        "source_archive_policy": (
            "claim-sized atoms only; no whole files, paragraphs, or finished bullets as proof"
        ),
        "row_count": len(rows),
        "embed_allowed_count": sum(1 for r in rows if r.get("embed_allowed")),
        "pending_trace_count": sum(
            1 for r in rows if r.get("confidence") == CONFIDENCE_PENDING
        ),
        "matched_existing_fact_id_count": sum(
            1 for r in rows if r.get("matched_existing_fact_id")
        ),
        "rows": rows,
    }
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return dest


__all__ = [
    "extract_prior_resume_manifest_rows",
    "write_prior_resume_extraction_manifest",
]
