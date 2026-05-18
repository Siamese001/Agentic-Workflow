"""Shared detection of mock/test fixture language in competencies proof payloads.

Used by X2 (REAL_LLM hygiene) and L6 shadow anomaly classification. Values are lowercase
substrings matched against normalized proof text blobs.
"""
from __future__ import annotations

# Substrings (matched case-insensitively) — keep aligned with competencies X2 gate contract tests.
MOCK_FIXTURE_MARKER_SNIPPETS: tuple[str, ...] = (
    "mocked_runtime_slice",
    "mock slice",
    "provider not requested",
    "mocked provider",
    "test fixture",
    "plumbing-only",
)


def scan_mock_fixture_markers(text: str) -> list[str]:
    """Return ordered unique snippets found in *text* (case-insensitive)."""
    if not text or not str(text).strip():
        return []
    low = str(text).lower()
    found: list[str] = []
    seen: set[str] = set()
    for s in MOCK_FIXTURE_MARKER_SNIPPETS:
        if s.lower() in low and s not in seen:
            found.append(s)
            seen.add(s)
    return found


__all__ = ["MOCK_FIXTURE_MARKER_SNIPPETS", "scan_mock_fixture_markers"]
