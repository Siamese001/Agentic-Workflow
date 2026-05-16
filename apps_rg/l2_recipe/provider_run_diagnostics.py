"""Persist unified provider/generation diagnostics for apps_rg CLI runs."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def redact_endpoint(url: str) -> str:
    """Redact host in http(s) URLs; keep scheme and port if present."""
    s = str(url or "").strip()
    if not s:
        return ""
    return re.sub(
        r"//[^/]+",
        "//<redacted-host>",
        s,
        count=1,
    )


def write_provider_generation_diagnostics(
    artifact_dir: str | Path | None,
    payload: dict[str, Any],
    *,
    raw_provider_text: str | None = None,
) -> Path | None:
    """Write ``apps_rg_provider_generation_diagnostics.json`` (+ optional raw snippet)."""
    if artifact_dir is None or not str(artifact_dir).strip():
        return None
    base = Path(str(artifact_dir))
    base.mkdir(parents=True, exist_ok=True)
    if raw_provider_text is not None and raw_provider_text.strip():
        snip = base / "outputs" / "raw_provider_text_snippet.txt"
        snip.parent.mkdir(parents=True, exist_ok=True)
        txt = raw_provider_text
        if len(txt) > 24_000:
            txt = txt[:24_000] + "\n... [truncated for diagnostics file]\n"
        snip.write_text(txt, encoding="utf-8")
        refs = payload.setdefault("artifact_refs", {})
        refs["raw_provider_text_snippet_relpath"] = "outputs/raw_provider_text_snippet.txt"
    out = base / "apps_rg_provider_generation_diagnostics.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out


__all__ = ["redact_endpoint", "write_provider_generation_diagnostics"]
