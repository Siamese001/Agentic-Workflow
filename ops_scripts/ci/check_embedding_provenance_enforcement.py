"""CI gate — embedding provenance enforcement (ADR-055 W3.1).

Checks:
1. PROVENANCE_ENFORCED_COLLECTIONS contains at least 'apps_qna_interview_cards'.
2. EmbeddingProvenanceMismatchError is importable from the canonical location.
3. SovereignChromaClient.add_documents references the enforcement block
   (static check: the exception class name appears in the client source).

Exit codes:
    0 — all checks pass
    1 — one or more checks fail
    2 — unexpected import error

Plan: .codex/plans/bge-m3-gap-closure-c8f3a2.md W3.1
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

_ERRORS: list[str] = []
_WARNINGS: list[str] = []


def _check_exception_importable() -> None:
    try:
        from agentic_core.embeddings.exceptions import (  # noqa: F401
            EmbeddingProvenanceMismatchError,
            PROVENANCE_ENFORCED_COLLECTIONS,
        )
    except ImportError as exc:
        _ERRORS.append(f"Cannot import EmbeddingProvenanceMismatchError: {exc}")
        return

    from agentic_core.embeddings.exceptions import PROVENANCE_ENFORCED_COLLECTIONS

    if "apps_qna_interview_cards" not in PROVENANCE_ENFORCED_COLLECTIONS:
        _ERRORS.append(
            "PROVENANCE_ENFORCED_COLLECTIONS does not contain 'apps_qna_interview_cards'. "
            "ADR-055 W3.1 requires this collection to be hard-enforced."
        )
    else:
        print("[OK] PROVENANCE_ENFORCED_COLLECTIONS contains apps_qna_interview_cards")


def _check_client_references_enforcement() -> None:
    client_path = (
        REPO_ROOT
        / "agentic_core"
        / "L4_state"
        / "utils"
        / "client"
        / "chroma_client.py"
    )
    if not client_path.exists():
        _ERRORS.append(f"chroma_client.py not found at {client_path}")
        return

    source = client_path.read_text(encoding="utf-8")
    if "EmbeddingProvenanceMismatchError" not in source:
        _ERRORS.append(
            "chroma_client.py does not reference EmbeddingProvenanceMismatchError. "
            "W3.1 hard-fail block may be missing."
        )
    else:
        print("[OK] chroma_client.py references EmbeddingProvenanceMismatchError")

    if "PROVENANCE_ENFORCED_COLLECTIONS" not in source:
        _ERRORS.append(
            "chroma_client.py does not reference PROVENANCE_ENFORCED_COLLECTIONS. "
            "W3.1 enforcement block may be missing."
        )
    else:
        print("[OK] chroma_client.py references PROVENANCE_ENFORCED_COLLECTIONS")


def _check_exceptions_file_exists() -> None:
    exceptions_path = REPO_ROOT / "agentic_core" / "embeddings" / "exceptions.py"
    if not exceptions_path.exists():
        _ERRORS.append(f"agentic_core/embeddings/exceptions.py not found at {exceptions_path}")
    else:
        print("[OK] agentic_core/embeddings/exceptions.py exists")


def main() -> int:
    print("=" * 60)
    print("check_embedding_provenance_enforcement — ADR-055 W3.1")
    print("=" * 60)

    _check_exceptions_file_exists()
    _check_exception_importable()
    _check_client_references_enforcement()

    if _WARNINGS:
        for w in _WARNINGS:
            print(f"[WARN] {w}")

    if _ERRORS:
        for e in _ERRORS:
            print(f"[ERROR] {e}")
        print(f"\n{len(_ERRORS)} error(s) found. Gate FAILED.")
        return 1

    print(f"\nAll checks passed. Gate OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
