"""Resolve apps_rg lane briefing text from filesystem path, https URI, or DEFAULT_SSOT.

U0 passes through ``briefing_artifact_ref`` only; this module is downstream (lanes / modular adapter).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from apps_rg.runtime.briefing_ssot import DEFAULT_TARGETING_BRIEFING_PATH, default_targeting_briefing_text

# Extensions allowed for local briefing artifacts (lowercased suffixes).
ALLOWED_BRIEFING_SUFFIXES: frozenset[str] = frozenset({".txt", ".md", ".json", ".yaml", ".yml", ".markdown"})

_ALLOWED_MIME_PREFIXES: tuple[str, ...] = ("text/",)
_ALLOWED_MIME_EXACT: frozenset[str] = frozenset(
    {
        "application/json",
        "application/yaml",
        "application/x-yaml",
    }
)
_URI_FETCH_MAX_BYTES = 2_000_000


class BriefingSource(StrEnum):
    RUN_SPECIFIC = "RUN_SPECIFIC"
    DEFAULT_SSOT = "DEFAULT_SSOT"


class BriefingResolutionError(RuntimeError):
    """Fail-closed briefing load (missing file, disallowed type, empty required ref, etc.)."""


@dataclass(frozen=True, slots=True)
class ResolvedBriefing:
    text: str
    briefing_source: BriefingSource
    briefing_digest: str
    ref_used: str


def _sha256_utf8(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _allowed_local_suffix(path: Path) -> None:
    suf = path.suffix.lower()
    if suf not in ALLOWED_BRIEFING_SUFFIXES:
        raise BriefingResolutionError(
            f"briefing artifact extension {suf!r} not in allowed set {sorted(ALLOWED_BRIEFING_SUFFIXES)}"
        )


def _looks_like_filesystem_ref(ref: str) -> bool:
    r = ref.strip()
    if r.startswith(("http://", "https://")):
        return False
    if "/" in r or "\\" in r:
        return True
    low = r.lower()
    return any(low.endswith(s) for s in ALLOWED_BRIEFING_SUFFIXES)


def _mime_allowed(ctype: str | None, *, url_path: str) -> bool:
    if ctype:
        primary = ctype.split(";")[0].strip().lower()
        if primary in _ALLOWED_MIME_EXACT:
            return True
        if primary.startswith(_ALLOWED_MIME_PREFIXES):
            return True
    p = Path(urlparse(url_path).path or "")
    return p.suffix.lower() in ALLOWED_BRIEFING_SUFFIXES


def _fetch_uri(ref: str) -> tuple[str, str | None]:
    req = Request(ref, headers={"User-Agent": "apps_rg-briefing/1"})
    with urlopen(req, timeout=45) as resp:  # noqa: S310 — intentional user-supplied briefing URL
        raw_ct = resp.headers.get("Content-Type")
        ctype = raw_ct.split(";")[0].strip().lower() if raw_ct else None
        if not _mime_allowed(ctype, url_path=ref):
            raise BriefingResolutionError(
                f"briefing URI content-type not allowed (got {ctype!r} for {ref!r})"
            )
        raw = resp.read(_URI_FETCH_MAX_BYTES + 1)
    if len(raw) > _URI_FETCH_MAX_BYTES:
        raise BriefingResolutionError(f"briefing URI response exceeds {_URI_FETCH_MAX_BYTES} bytes")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BriefingResolutionError(f"briefing URI body is not valid utf-8: {ref!r}") from exc
    return text, ctype


def resolve_briefing_for_lanes(
    *,
    briefing_artifact_ref: str | None,
    require_run_specific: bool = False,
) -> ResolvedBriefing:
    """Load briefing text for modular lanes / dispatch defaults.

    Parameters
    ----------
    briefing_artifact_ref:
        Optional filesystem path, ``https`` ``http`` URI, or inline text (only when not path-like).
    require_run_specific:
        When True, empty ref fails closed (no DEFAULT_SSOT fallback).
    """
    ref = str(briefing_artifact_ref or "").strip()
    if not ref:
        if require_run_specific:
            raise BriefingResolutionError("required briefing_artifact_ref is empty")
        text = default_targeting_briefing_text()
        digest = _sha256_utf8(text)
        return ResolvedBriefing(
            text=text,
            briefing_source=BriefingSource.DEFAULT_SSOT,
            briefing_digest=digest,
            ref_used=f"DEFAULT_SSOT:{DEFAULT_TARGETING_BRIEFING_PATH.as_posix()}",
        )

    if ref.startswith(("http://", "https://")):
        body, _ctype = _fetch_uri(ref)
        body = body.strip()
        if not body:
            raise BriefingResolutionError(f"briefing URI returned empty body: {ref!r}")
        return ResolvedBriefing(
            text=body,
            briefing_source=BriefingSource.RUN_SPECIFIC,
            briefing_digest=_sha256_utf8(body),
            ref_used=ref,
        )

    p = Path(ref)
    if p.is_file():
        _allowed_local_suffix(p)
        try:
            text = p.read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise BriefingResolutionError(f"cannot read briefing file {p}: {exc}") from exc
        if not text:
            raise BriefingResolutionError(f"briefing file is empty: {p}")
        return ResolvedBriefing(
            text=text,
            briefing_source=BriefingSource.RUN_SPECIFIC,
            briefing_digest=_sha256_utf8(text),
            ref_used=str(p.resolve()),
        )

    if _looks_like_filesystem_ref(ref):
        raise BriefingResolutionError(f"briefing artifact path does not exist or is not a file: {ref!r}")

    return ResolvedBriefing(
        text=ref,
        briefing_source=BriefingSource.RUN_SPECIFIC,
        briefing_digest=_sha256_utf8(ref),
        ref_used="inline:text",
    )


__all__ = [
    "ALLOWED_BRIEFING_SUFFIXES",
    "BriefingResolutionError",
    "BriefingSource",
    "ResolvedBriefing",
    "resolve_briefing_for_lanes",
]
