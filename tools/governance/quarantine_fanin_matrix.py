"""Build fan-in matrix for apps_rg quarantine candidates (plan apps-rg-quarantine-ssot-fanin-delete-c7e4a1)."""
from __future__ import annotations

import json
import re
import sqlite3
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ADG_DB = REPO / "artifacts" / "adg" / "adg_indexed_05232026_1851.sqlite"
SCAN_ROOTS = ("apps_rg", "apps_shared", "apps_eval", "tests", "ops_scripts", "agentic_core/runtime/entry")
SKIP = {".venv", "__pycache__", "node_modules", ".git", "artifacts", "archives"}

CANDIDATES = (
    {
        "id": "C1_dry_run",
        "path": "apps_rg/runtime/dry_run/",
        "patterns": (r"runtime\.dry_run", r"runtime/dry_run", r"executive_summary_demo"),
    },
    {
        "id": "C2_internal",
        "path": "apps_rg/runtime/internal/",
        "patterns": (r"runtime\.internal", r"runtime/internal", r"lane_batch"),
    },
    {
        "id": "C3_hops",
        "path": "apps_rg/integrations/hops/",
        "patterns": (r"integrations\.hops", r"integrations/hops"),
    },
    {
        "id": "C4_engines",
        "path": "apps_rg/engines/",
        "patterns": (r"apps_rg\.engines", r"apps_rg/engines"),
    },
)


@dataclass
class Row:
    id: str
    path: str
    exists_on_disk: bool
    py_files: int
    fan_in_adg: int | None = None
    fan_out_adg: int | None = None
    static_importers: list[str] = field(default_factory=list)
    product_importers: list[str] = field(default_factory=list)
    test_importers: list[str] = field(default_factory=list)
    verdict: str = "PENDING"
    notes: str = ""


def _rglob_py(root: Path) -> list[Path]:
    if not root.exists():
        return []
    out: list[Path] = []
    for p in root.rglob("*.py"):
        if any(s in p.parts for s in SKIP):
            continue
        out.append(p)
    return out


def _static_scan(patterns: tuple[str, ...]) -> list[str]:
    hits: list[str] = []
    for root_name in SCAN_ROOTS:
        root = REPO / root_name
        if not root.exists():
            continue
        for py in _rglob_py(root):
            try:
                text = py.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if any(re.search(p, text) for p in patterns):
                hits.append(py.relative_to(REPO).as_posix())
    return sorted(set(hits))


def _adg_fan(path_prefix: str) -> tuple[int | None, int | None]:
    if not ADG_DB.is_file():
        return None, None
    con = sqlite3.connect(f"file:{ADG_DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        """
        SELECT fan_in, fan_out FROM mv_hotspot_centrality
        WHERE resolved_path LIKE ? || '%'
        """,
        (path_prefix,),
    ).fetchall()
    con.close()
    if not rows:
        return 0, 0
    return max(r["fan_in"] for r in rows), max(r["fan_out"] for r in rows)


def _classify_importers(importers: list[str]) -> tuple[list[str], list[str], list[str]]:
    product: list[str] = []
    tests: list[str] = []
    other: list[str] = []
    for imp in importers:
        if imp.startswith("tests/"):
            tests.append(imp)
        elif imp.startswith("apps_rg/") and "/runtime/sections/" not in imp and not imp.startswith("apps_rg/runtime/dry_run"):
            if "test" in imp.lower():
                tests.append(imp)
            elif imp.startswith(("apps_rg/__main__", "apps_rg/runtime/dispatch/", "apps_rg/runtime/bindings/", "apps_rg/l2_recipe/")):
                product.append(imp)
            else:
                other.append(imp)
        elif imp.startswith("tests/") or "/test_" in imp:
            tests.append(imp)
        else:
            other.append(imp)
    return product, tests, other


def _w11_delete_ready(row: Row) -> str:
    if not row.exists_on_disk:
        return "ALREADY_ABSENT"
    if row.product_importers:
        return "KEEP"
    if row.test_importers or row.static_importers:
        if row.id == "C1_dry_run":
            return "MIGRATE_THEN_DELETE"
        if row.id == "C2_internal":
            return "KEEP_TEST_SUPPORT"
        if row.id in ("C3_hops", "C4_engines"):
            return "KEEP"
    if row.fan_in_adg == 0 and row.fan_out_adg == 0 and not row.static_importers:
        return "DELETE_READY"
    if row.id == "C1_dry_run" and row.test_importers and not row.product_importers:
        return "MIGRATE_THEN_DELETE"
    return "DEFER"


def build_matrix() -> dict:
    rows: list[Row] = []
    for spec in CANDIDATES:
        prefix = spec["path"]
        root = REPO / prefix.rstrip("/")
        exists = root.exists()
        py_count = len(_rglob_py(root)) if exists else 0
        fi, fo = _adg_fan(prefix)
        importers = _static_scan(spec["patterns"])
        product, tests, other = _classify_importers(importers)
        row = Row(
            id=spec["id"],
            path=prefix,
            exists_on_disk=exists,
            py_files=py_count,
            fan_in_adg=fi,
            fan_out_adg=fo,
            static_importers=importers,
            product_importers=product,
            test_importers=tests,
        )
        if other:
            row.notes = f"other_importers={len(other)}"
        row.verdict = _w11_delete_ready(row)
        rows.append(row)
    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "adg_snapshot": ADG_DB.name if ADG_DB.is_file() else "missing",
        "plan_id": "apps-rg-quarantine-ssot-fanin-delete-c7e4a1",
        "rows": [asdict(r) for r in rows],
        "delete_ready_ids": [r.id for r in rows if r.verdict == "DELETE_READY"],
    }


def write_artifacts(data: dict) -> tuple[Path, Path]:
    out_dir = REPO / "artifacts" / "governance"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "quarantine_fanin_matrix_20260524.json"
    md_path = out_dir / "quarantine_fanin_matrix_20260524.md"
    json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    lines = [
        "# Quarantine fan-in matrix (2026-05-24)",
        "",
        f"- **Plan:** `apps-rg-quarantine-ssot-fanin-delete-c7e4a1`",
        f"- **ADG:** `{data['adg_snapshot']}`",
        f"- **Generated (UTC):** {data['generated_utc']}",
        "",
        "| ID | Path | Verdict | ADG fan-in | Product importers | Test importers |",
        "|----|------|---------|------------|-------------------|----------------|",
    ]
    for row in data["rows"]:
        lines.append(
            f"| {row['id']} | `{row['path']}` | **{row['verdict']}** | "
            f"{row.get('fan_in_adg', 'n/a')} | {len(row['product_importers'])} | {len(row['test_importers'])} |"
        )
    lines.extend(
        [
            "",
            "## DELETE_READY",
            "",
            ", ".join(data["delete_ready_ids"]) if data["delete_ready_ids"] else "_none_",
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path


def main() -> int:
    data = build_matrix()
    jp, mp = write_artifacts(data)
    print(json.dumps({"json": str(jp), "md": str(mp), "rows": len(data["rows"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
