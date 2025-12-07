import logging
#!/usr/bin/env python3
"""
PHASE 3H — CANONICAL STUB HYDRATION (ZERO-LOSS, DETERMINISTIC, FULL OVERWRITE)

Purpose:
    Hydrate canonical stubs identified by Phase 3A by copying the single best
    real implementation from:
        • Archive trees (resume/outreach archives)
        • Phase 0.5 global semantic lineage
        • Deterministic semantic similarity scoring (token overlap)

    Never mutate archives.
    Never guess when ambiguity is >1 donor.
    Never hydrate outside canonical domains.

Output:
    06_data/semantic_cache/meta/phase03_hydration_report.json
"""

from __future__ import annotations

import json
import sys
import hashlib
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ======================================================================
# ROOT PATHS — MUST MATCH PIPELINE
# ======================================================================

PROJECT_ROOT = Path(r"C:/Git/Agentic-Workflow").resolve()
CACHE_ROOT = PROJECT_ROOT / "06_data" / "semantic_cache"
META_ROOT = CACHE_ROOT / "meta"

STUB_AUDIT_PATH = META_ROOT / "phase03_stub_audit.json"
HYDRATION_REPORT_PATH = META_ROOT / "phase03_hydration_report.json"

# Global components file — autodetect newest global_* file
def detect_global_components_file() -> Optional[Path]:
    candidates = list(META_ROOT.glob("global_*"))
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)

GLOBAL_COMPONENTS_INDEX = detect_global_components_file()

# Component graph (optional)
COMPONENT_GRAPH = CACHE_ROOT / "graphs" / "component_graph.json"

# Archive roots
ARCHIVE_ROOTS: List[Path] = [
    PROJECT_ROOT / "06_data" / "resume_engine_archive",
    PROJECT_ROOT / "06_data" / "outreach_engine_archive",
]


# ======================================================================
# DATA STRUCTURES
# ======================================================================

@dataclass
class Stub:
    relative_path: str
    reason: str
    domain: Optional[str] = None

@dataclass
class HydrationAction:
    stub_path: str
    donor_path: str
    strategy: str
    confidence: float


# ======================================================================
# LOADERS
# ======================================================================

def load_stub_audit() -> List[Stub]:
    if not STUB_AUDIT_PATH.exists():
        logging.debug("[FATAL] Stub audit missing – run Phase 3A first", file=sys.stderr)
        sys.exit(1)

    raw = json.loads(STUB_AUDIT_PATH.read_text(encoding="utf-8"))
    stubs = []
    for s in raw.get("stub_files", []):
        # Extract only the fields the Stub dataclass expects
        stubs.append(Stub(
            relative_path=s.get("relative_path", ""),
            reason="; ".join(s.get("stub_reasons", [])) if isinstance(s.get("stub_reasons"), list) else s.get("reason", "unknown"),
            domain=s.get("domain"),
        ))
    return stubs


def load_global_components() -> Dict[str, dict]:
    if GLOBAL_COMPONENTS_INDEX and GLOBAL_COMPONENTS_INDEX.exists():
        return json.loads(GLOBAL_COMPONENTS_INDEX.read_text(encoding="utf-8"))
    return {}


# ======================================================================
# CANDIDATE SEARCH STRATEGIES
# ======================================================================

def candidates_by_filename(basename: str) -> List[Path]:
    results: List[Path] = []
    for root in ARCHIVE_ROOTS:
        if not root.exists():
            continue
        for p in root.rglob(basename):
            if p.is_file():
                results.append(p)
    return results


def normalize_key(s: str) -> str:
    return (
        s.lower()
        .replace(".py", "")
        .replace("_", "")
        .replace("-", "")
        .replace("/", "")
    )


def candidate_by_component_id(normalized_stub: str, components: dict) -> Optional[Path]:
    for cid, info in components.items():
        cid_norm = normalize_key(cid)
        if normalized_stub in cid_norm or cid_norm in normalized_stub:
            src = info.get("source_path")
            if src:
                donor = PROJECT_ROOT / src
                if donor.exists():
                    return donor
    return None


def semantic_candidates(basename: str) -> List[Tuple[float, Path]]:
    """Token-overlap similarity. Deterministic, no ML."""
    tokens = set(basename.replace(".py", "").split("_"))
    scored: List[Tuple[float, Path]] = []

    if not tokens:
        return scored

    for root in ARCHIVE_ROOTS:
        if not root.exists():
            continue
        for p in root.rglob("*.py"):
            cand_tokens = set(p.stem.split("_"))
            if not cand_tokens:
                continue

            score = len(tokens & cand_tokens) / len(tokens | cand_tokens)
            if score >= 0.40:  # deterministic threshold
                scored.append((score, p))

    return sorted(scored, reverse=True, key=lambda x: x[0])


# ======================================================================
# SAFETY BOUNDARY: ONLY HYDRATE CANONICAL PATHS
# ======================================================================

def is_allowed_stub_path(p: Path) -> bool:
    canonical_roots = [
        PROJECT_ROOT / "01_agentic_core",
        PROJECT_ROOT / "02_schemas",
        PROJECT_ROOT / "03_runtime",
        PROJECT_ROOT / "04_prompt_governance",
        PROJECT_ROOT / "05_config",
        PROJECT_ROOT / "07_observability",
        PROJECT_ROOT / "08_scripts",
        PROJECT_ROOT / "09_apps",
    ]

    p = p.resolve()
    return any(str(p).startswith(str(root.resolve())) for root in canonical_roots)


# ======================================================================
# HYDRATION ENGINE
# ======================================================================

def copy_with_header(target: Path, donor: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    code = donor.read_text(encoding="utf-8")

    header = (
        "# ==============================================================\n"
        "# AUTO-HYDRATED BY PHASE 3H\n"
        f"# Donor: {donor.as_posix()}\n"
        "# Review and refactor as needed. Archive copy preserved.\n"
        "# ==============================================================\n\n"
    )

    target.write_text(header + code, encoding="utf-8")


def hydrate_stub(stub: Stub, components_index: dict) -> Optional[HydrationAction]:
    stub_path = (PROJECT_ROOT / stub.relative_path).resolve()
    basename = stub_path.name
    stub_norm = normalize_key(basename)

    # Safety boundary
    if not is_allowed_stub_path(stub_path):
        logging.debug(f"[SKIP] Non-canonical stub location: {stub.relative_path}", file=sys.stderr)
        return None

    # -------------------------------------------------------------
    # 1. Exact filename match (highest confidence)
    # -------------------------------------------------------------
    filename_matches = candidates_by_filename(basename)
    if len(filename_matches) == 1:
        donor = filename_matches[0]
        copy_with_header(stub_path, donor)
        return HydrationAction(
            stub_path=stub.relative_path,
            donor_path=str(donor.relative_to(PROJECT_ROOT)),
            strategy="filename_exact",
            confidence=1.0,
        )
    if len(filename_matches) > 1:
        logging.debug(f"[AMBIGUOUS] {stub.relative_path} → {len(filename_matches)} filename matches")
        return None

    # -------------------------------------------------------------
    # 2. Component-ID heuristic (Phase 0.5 lineage)
    # -------------------------------------------------------------
    donor = candidate_by_component_id(stub_norm, components_index)
    if donor:
        copy_with_header(stub_path, donor)
        return HydrationAction(
            stub_path=stub.relative_path,
            donor_path=str(donor.relative_to(PROJECT_ROOT)),
            strategy="component_id",
            confidence=0.9,
        )

    # -------------------------------------------------------------
    # 3. Semantic fallback (token overlap)
    # -------------------------------------------------------------
    semantic = semantic_candidates(basename)
    if semantic:
        score, donor = semantic[0]
        if score >= 0.50:  # strong enough to be deterministic
            copy_with_header(stub_path, donor)
            return HydrationAction(
                stub_path=stub.relative_path,
                donor_path=str(donor.relative_to(PROJECT_ROOT)),
                strategy="semantic",
                confidence=score,
            )

    logging.debug(f"[NO DONOR] {stub.relative_path} – no usable source found")
    return None


# ======================================================================
# MAIN
# ======================================================================

def main() -> int:
    logging.debug("=== PHASE 3H — STUB HYDRATION ===")
    stubs = load_stub_audit()

    if not stubs:
        logging.debug("No canonical stubs found.")
        return 0

    components_index = load_global_components()
    logging.debug(f"[INFO] Loaded global-components index: {GLOBAL_COMPONENTS_INDEX}")

    actions: List[HydrationAction] = []

    for stub in stubs:
        action = hydrate_stub(stub, components_index)
        if action:
            actions.append(action)
            logging.debug(f"[HYDRATED] {action.stub_path} ← {action.donor_path} [{action.strategy}]")

    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_stubs": len(stubs),
        "hydrated": [asdict(a) for a in actions],
        "remaining": len(stubs) - len(actions),
    }

    HYDRATION_REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    logging.debug(f"\nHydrated {len(actions)} / {len(stubs)} stubs")
    logging.debug(f"Report → {HYDRATION_REPORT_PATH.as_posix()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
