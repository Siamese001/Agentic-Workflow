"""Resolve apps_rg lane JD material from ref, inline text, recipe ``jd_data``, or DEFAULT_SSOT.

U0 passes through ``job_description_ref`` / ``job_description_text`` only; this module is for
downstream modular lanes and dispatch argv defaults.
"""

from __future__ import annotations

import functools
import hashlib
import json
import logging
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

# Extensions allowed for local JD artifacts (lowercased suffixes).
ALLOWED_JD_SUFFIXES: frozenset[str] = frozenset({".txt", ".md", ".json", ".yaml", ".yml", ".markdown"})

_ALLOWED_MIME_PREFIXES: tuple[str, ...] = ("text/",)
_ALLOWED_MIME_EXACT: frozenset[str] = frozenset(
    {
        "application/json",
        "application/yaml",
        "application/x-yaml",
    }
)
_URI_FETCH_MAX_BYTES = 2_000_000

_DEFAULT_FILE = Path(__file__).resolve().parent.parent / "config" / "default_jd_targeting.txt"
DEFAULT_JD_TARGETING_PATH: Path = _DEFAULT_FILE


class JdSource(StrEnum):
    RUN_SPECIFIC = "RUN_SPECIFIC"
    DEFAULT_SSOT = "DEFAULT_SSOT"


class JdResolutionError(RuntimeError):
    """Fail-closed JD load (missing file, disallowed type, empty required material, etc.)."""


@dataclass(frozen=True, slots=True)
class ResolvedJD:
    description: str
    title: str
    company: str
    jd_source: JdSource
    jd_digest: str
    ref_used: str


@functools.lru_cache(maxsize=1)
def default_jd_targeting_text() -> str:
    """Return UTF-8 text from the canonical default JD hint file (stripped)."""
    return _DEFAULT_FILE.read_text(encoding="utf-8").strip()


def _sha256_utf8(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_jd_material_to_fields(
    jd_raw: str,
    *,
    target_company: str,
    target_role: str,
) -> tuple[str, str, str]:
    """Return ``(description, title, company)`` — single source of truth for R4 and modular lanes.

    JSON objects may override ``title``, ``description``, and ``company``; CLI ``target_company`` is
    the default company when JSON omits ``company``. Empty description falls back to a stable
    template (including the historical leading ``\" — \"`` when ``target_role`` is empty).
    """
    tr = str(target_role).strip()
    tc = str(target_company).strip()
    jd_text = jd_raw
    jd_title = tr
    company_eff = tc

    st = jd_raw.strip()
    if st.startswith("{"):
        try:
            obj = json.loads(st)
            if isinstance(obj, dict):
                if obj.get("title") is not None and str(obj.get("title")).strip():
                    jd_title = str(obj["title"]).strip()
                if "description" in obj and obj.get("description") is not None:
                    jd_text = str(obj["description"]).strip()
                elif obj:
                    jd_text = json.dumps(obj, sort_keys=True, separators=(",", ":"))
                cj = str(obj.get("company") or "").strip()
                if cj:
                    company_eff = cj
        except json.JSONDecodeError:  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
            pass

    if not str(jd_text).strip():
        jd_text = (
            f"{tr} — resume generation request (apps_rg)."
            if tr
            else " — resume generation request (apps_rg)."
        )

    if not jd_title:
        jd_title = tr

    return jd_text.strip(), jd_title.strip(), company_eff.strip()


def build_canonical_jd_payload(
    jd_raw: str,
    *,
    target_company: str,
    target_role: str,
) -> dict[str, str]:
    """Shape the canonical ``jd_payload`` dict (title / description / company)."""
    description, title, company = normalize_jd_material_to_fields(
        jd_raw,
        target_company=target_company,
        target_role=target_role,
    )
    return {"title": title, "description": description, "company": company}


def canonical_jd_digest(jd_payload: dict[str, str]) -> str:
    """SHA-256 of sorted JSON for ``jd_payload`` (matches historical R4 hashing)."""
    blob = json.dumps(
        {
            "title": jd_payload["title"],
            "description": jd_payload["description"],
            "company": jd_payload["company"],
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _allowed_local_suffix(path: Path) -> None:
    suf = path.suffix.lower()
    if suf not in ALLOWED_JD_SUFFIXES:
        raise JdResolutionError(
            f"job description artifact extension {suf!r} not in allowed set {sorted(ALLOWED_JD_SUFFIXES)}"
        )


def _looks_like_filesystem_ref(ref: str) -> bool:
    r = ref.strip()
    if r.startswith(("http://", "https://")):
        return False
    if "/" in r or "\\" in r:
        return True
    low = r.lower()
    return any(low.endswith(s) for s in ALLOWED_JD_SUFFIXES)


def _mime_allowed(ctype: str | None, *, url_path: str) -> bool:
    if ctype:
        primary = ctype.split(";")[0].strip().lower()
        if primary in _ALLOWED_MIME_EXACT:
            return True
        if primary.startswith(_ALLOWED_MIME_PREFIXES):
            return True
    p = Path(urlparse(url_path).path or "")
    return p.suffix.lower() in ALLOWED_JD_SUFFIXES


def _fetch_uri(ref: str) -> tuple[str, str | None]:
    req = Request(ref, headers={"User-Agent": "apps_rg-jd/1"})
    with urlopen(req, timeout=45) as resp:  # noqa: S310 — intentional user-supplied JD URL
        raw_ct = resp.headers.get("Content-Type")
        ctype = raw_ct.split(";")[0].strip().lower() if raw_ct else None
        if not _mime_allowed(ctype, url_path=ref):
            raise JdResolutionError(
                f"job description URI content-type not allowed (got {ctype!r} for {ref!r})"
            )
        raw = resp.read(_URI_FETCH_MAX_BYTES + 1)
    if len(raw) > _URI_FETCH_MAX_BYTES:
        raise JdResolutionError(f"job description URI response exceeds {_URI_FETCH_MAX_BYTES} bytes")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise JdResolutionError(f"job description URI body is not valid utf-8: {ref!r}") from exc
    return text, ctype


def _load_ref_body(ref: str) -> tuple[str, str]:
    if ref.startswith(("http://", "https://")):
        body, _ctype = _fetch_uri(ref)
        body = body.strip()
        if not body:
            raise JdResolutionError(f"job description URI returned empty body: {ref!r}")
        return body, ref

    p = Path(ref)
    if p.is_file():
        _allowed_local_suffix(p)
        try:
            text = p.read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise JdResolutionError(f"cannot read job description file {p}: {exc}") from exc
        if not text:
            raise JdResolutionError(f"job description file is empty: {p}")
        return text, str(p.resolve())

    if _looks_like_filesystem_ref(ref):
        raise JdResolutionError(f"job description path does not exist or is not a file: {ref!r}")

    return ref.strip(), "inline:ref"


def resolve_jd_for_lanes(
    *,
    job_description_ref: str | None = None,
    job_description_text: str | None = None,
    jd_data: str | None = None,
    target_company: str = "",
    target_role: str = "",
    require_run_specific: bool = False,
) -> ResolvedJD:
    """Load and normalize JD fields for modular lanes / dispatch defaults.

    Precedence: ``job_description_text`` (inline) > ``job_description_ref`` (file/https) >
    ``jd_data`` (recipe blob) > DEFAULT_SSOT file.

    Parameters
    ----------
    require_run_specific:
        When True, all three material sources empty → fail closed (no DEFAULT_SSOT).
    """
    inline = str(job_description_text or "").strip()
    ref = str(job_description_ref or "").strip()
    data = str(jd_data or "").strip()

    if require_run_specific and not (inline or ref or data):
        raise JdResolutionError("required job description material is empty (ref, text, and jd_data)")

    raw: str
    ref_used: str
    source: JdSource

    if inline:
        raw = inline
        ref_used = "inline:job_description_text"
        source = JdSource.RUN_SPECIFIC
    elif ref:
        raw, ref_used = _load_ref_body(ref)
        source = JdSource.RUN_SPECIFIC
    elif data:
        raw = data
        ref_used = "inline:jd_data"
        source = JdSource.RUN_SPECIFIC
    else:
        raw = default_jd_targeting_text()
        if not raw:
            raise JdResolutionError(f"DEFAULT_SSOT job description file is empty: {_DEFAULT_FILE}")
        ref_used = f"DEFAULT_SSOT:{_DEFAULT_FILE.as_posix()}"
        source = JdSource.DEFAULT_SSOT
        logger.warning(
            "jd targeting DEFAULT_SSOT: no run-specific JD provided; "
            "resume will target the generic role profile. "
            "Supply job_description_text, job_description_ref, or jd_data for targeted generation."
        )

    payload = build_canonical_jd_payload(
        raw,
        target_company=target_company,
        target_role=target_role,
    )
    description = payload["description"]
    if not description:
        raise JdResolutionError("resolved job description body is empty after normalization")

    digest = canonical_jd_digest(payload)
    return ResolvedJD(
        description=description,
        title=payload["title"],
        company=payload["company"],
        jd_source=source,
        jd_digest=digest,
        ref_used=ref_used,
    )


__all__ = [
    "ALLOWED_JD_SUFFIXES",
    "DEFAULT_JD_TARGETING_PATH",
    "JdResolutionError",
    "JdSource",
    "ResolvedJD",
    "build_canonical_jd_payload",
    "canonical_jd_digest",
    "default_jd_targeting_text",
    "normalize_jd_material_to_fields",
    "resolve_jd_for_lanes",
]
