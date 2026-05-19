"""Build markdown hyperlinks for repo-relative receipt paths (offline ops only)."""

from __future__ import annotations


def path_link(path: str, *, label: str | None = None) -> dict[str, str]:
    """Return {path, markdown} where markdown is a clickable repo-relative link."""
    norm = path.replace("\\", "/").lstrip("./")
    name = label or norm.rsplit("/", 1)[-1]
    return {"path": norm, "markdown": f"[{name}]({norm})"}


def paths_link(paths: list[str]) -> list[dict[str, str]]:
    return [path_link(p) for p in paths]


def enrich_manifest_links(manifest: dict) -> dict:
    """Add *_links arrays alongside string path lists (non-destructive)."""
    out = dict(manifest)
    for key in ("files_changed", "reports_generated", "artifacts"):
        if key in out and isinstance(out[key], list) and out[key] and isinstance(out[key][0], str):
            out[f"{key}_links"] = paths_link(out[key])
    for ref_key in ("schema_ref", "plan_ref", "upstream_plan_ref", "receipt_markdown"):
        if ref_key in out and isinstance(out[ref_key], str):
            out[f"{ref_key}_link"] = path_link(out[ref_key])
    return out
