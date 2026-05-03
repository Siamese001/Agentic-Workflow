"""URL-cited source-register renderer (plan §P2.1).

Produces a deterministic Markdown section listing every source URL
contained in a CompanyBrief-shaped dict, numbered for cross-reference
from body text (`[1]`, `[2]`, …). Designed to be diff-stable — same
input always yields byte-identical output so snapshot tests work.
"""

from __future__ import annotations

from typing import Any, Iterable


def _extract_urls(brief: Any) -> list[str]:
    """Pull URL strings from ``brief.source_register`` (or dict equivalent).

    Accepts the pydantic CompanyBrief model or a plain dict. Returns a
    deduplicated list preserving first-seen order.
    """
    register: Iterable[Any]
    if hasattr(brief, "source_register"):
        register = brief.source_register or []
    elif isinstance(brief, dict):
        register = brief.get("source_register", []) or []
    else:
        register = []

    seen: set[str] = set()
    urls: list[str] = []
    for entry in register:
        url = ""
        if isinstance(entry, dict):
            url = str(entry.get("url", "") or "")
        elif hasattr(entry, "url"):
            url = str(getattr(entry, "url", "") or "")
        elif isinstance(entry, str):
            url = entry
        url = url.strip()
        if url and url not in seen:
            seen.add(url)
            urls.append(url)
    return urls


def render(brief: Any) -> str:
    """Render the source register as a Markdown numbered reference list.

    Args:
        brief: a CompanyBrief pydantic model or dict with
            ``source_register: list[{url: str, ...}]``.

    Returns:
        Markdown section as a single string. Always ends with a newline.
        Empty register → a single ``_No sources recorded._`` line.
    """
    urls = _extract_urls(brief)
    if not urls:
        return "## Sources\n\n_No sources recorded._\n"

    lines = ["## Sources", ""]
    for idx, url in enumerate(urls, start=1):
        lines.append(f"[{idx}]: {url}")
    return "\n".join(lines) + "\n"
