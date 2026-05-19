"""Deterministic candidate fact id typo repair against an allowlist (no gate weakening)."""
from __future__ import annotations

import re


def _legacy_bullet_id_fixes(s: str) -> str:
    while "bul_ibm__" in s:
        s = s.replace("bul_ibm__", "bul_ibm_", 1)
    if re.match(r"^bul_ib_\d{3}$", s):
        s = "bul_ibm_" + s[7:]
    return s


def _collapse_fact_id_double_underscores(s: str) -> str:
    """Collapse model typos like ``fact_engineering_platform__005`` (no allowlist required)."""
    if not str(s).startswith("fact_"):
        return s
    out = str(s)
    while "__" in out:
        out = out.replace("__", "_", 1)
    return out


def _fact_id_fingerprint(fid: str) -> str:
    return re.sub(r"_", "", str(fid).split("_metric_")[0].lower())


def _strip_interior_whitespace_in_fact_token(s: str) -> str:
    """Remove interior spaces in ``fact_*`` / ``bul_*`` ids (e.g. ``fact_foo_ 003`` → ``fact_foo_003``)."""
    raw = str(s).strip()
    base, sep, metric_tail = raw.partition("_metric_")
    if base.startswith(("fact_", "bul_")):
        base = re.sub(r"\s+", "", base)
    return base + (sep + metric_tail if sep else "")


def repair_fact_id_against_allowlist(fid: str, allowed_fact_ids: set[str] | None = None) -> str:
    """Repair common model typos; optionally map to a unique allowlist member by fingerprint."""
    s = _collapse_fact_id_double_underscores(
        _legacy_bullet_id_fixes(_strip_interior_whitespace_in_fact_token(str(fid)))
    )
    if not allowed_fact_ids:
        return s
    base, _, metric_tail = s.partition("_metric_")
    if base in allowed_fact_ids:
        return s
    fp = _fact_id_fingerprint(base)
    matches = sorted({a for a in allowed_fact_ids if _fact_id_fingerprint(a) == fp})
    if len(matches) == 1:
        return matches[0] + (f"_metric_{metric_tail}" if metric_tail else "")
    m = re.match(r"^(fact_.+_)(\d+)$", base)
    if m:
        prefix, num = m.group(1), m.group(2)
        padded = f"{prefix}{num.zfill(3)}"
        if padded in allowed_fact_ids:
            return padded + (f"_metric_{metric_tail}" if metric_tail else "")
    return s


__all__ = ["repair_fact_id_against_allowlist"]
