"""Generate a compact legacy editor Canvas summary for ADG CI burndown.

The **readable gate tables** live in markdown (``adg_burndown_report.md``) — this
script refreshes that report and opens it by default. The canvas is optional
dashboard chrome (stats + band table + blockers only); it does not embed all 48
gates as JSON (that produced an unreadable source dump).

Invoked from ``emit_mandatory_adg_burndown_report()`` after markdown emit.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any
from tools.reports.adg_burndown_report import build_burndown_bcg_findings

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from tools.reports.adg_burndown_report import (
    BURNDOWN_TABLE_DEFAULT,
    REPO,
    build_burndown_bcg_findings,
    _describe,
    _latest_gate_results,
    _load_burndown,
    _load_gate_results,
    _verdict_display,
)

CANVAS_BASENAME = "adg-ci-burndown.canvas.tsx"


def _cursor_canvases_dir() -> Path:
    override = os.environ.get("CURSOR_CANVASES_DIR", "").strip()
    if override:
        return Path(override)
    slug = os.environ.get("CURSOR_PROJECT_SLUG", "c-Git-Agentic-Workflow-FRESH").strip()
    if not slug:
        slug = "c-Git-Agentic-Workflow-FRESH"
    return Path.home() / ".cursor" / "projects" / slug / "canvases"


def _canvas_bypassed() -> bool:
    return os.environ.get("ADG_BURNDOWN_CANVAS_BYPASS", "").strip() in (
        "1",
        "true",
        "yes",
    )


def _readable_markdown_path() -> Path:
    return (REPO / "artifacts" / "adg" / "adg_burndown_report.md").resolve()


def build_canvas_payload(
    gate_results_path: Path,
    burndown_path: Path,
) -> dict[str, Any]:
    """Small payload only — full gate grid stays in markdown."""
    gates_doc = _load_gate_results(gate_results_path)
    burndown = _load_burndown(burndown_path)
    gates: list[dict[str, Any]] = gates_doc["gates"]
    summary = gates_doc.get("summary", {})

    bands = [
        [
            band,
            str(burndown.get("summary", {}).get(band, {}).get("label", band)),
            int(burndown.get("summary", {}).get(band, {}).get("gross", 0)),
            int(burndown.get("summary", {}).get(band, {}).get("guardian", 0)),
            int(burndown.get("summary", {}).get(band, {}).get("net", 0)),
            int(burndown.get("summary", {}).get(band, {}).get("diff", 0)),
        ]
        for band in ("P0", "P1", "P2", "P3")
    ]

    from tools.reports.gate_signal_catalog import display_verdict_sub, needs_fix

    blockers: list[list[str | int]] = []
    for g in gates:
        if not needs_fix(g):
            continue
        blockers.append(
            [
                str(g.get("gate_id", "?")),
                str(g.get("band", "?")),
                display_verdict_sub(g),
                int(g.get("violation_count", 0)),
                " ".join(_describe(g).split())[:72],
            ]
        )
    blockers.sort(key=lambda r: (-int(r[3]), str(r[0])))

    try:
        gate_label = gate_results_path.relative_to(REPO.resolve()).as_posix()
    except ValueError:
        gate_label = gate_results_path.name

    return {
        "generated": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "snapshot": str(gates_doc.get("timestamp", "n/a")),
        "source": gate_label,
        "overall_pass": gates_doc.get("overall_exit_code", 1) == 0,
        "total_gates": int(gates_doc.get("total_gates", len(gates))),
        "summary": [
            int(summary.get("block_pass", 0)),
            int(summary.get("block_fail", 0)),
            int(summary.get("ratchet_pass", 0)),
            int(summary.get("ratchet_regressed", 0)),
            int(summary.get("warn", 0)),
        ],
        "p0_clean": bool(burndown.get("p0_clean")),
        "bands": bands,
        "blockers": blockers,
        "markdown_rel": "artifacts/adg/adg_burndown_report.md",
        "bcg_brief": build_burndown_bcg_findings(gates_doc, burndown)["brief"],
    }


def _tsx_source(payload: dict[str, Any]) -> str:
    # Compact JSON — keeps the .canvas.tsx source short; tables render in Canvas UI.
    data_json = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    return f"""import {{
  Callout,
  Card,
  CardBody,
  CardHeader,
  Grid,
  H1,
  Stack,
  Stat,
  Table,
  Text,
  UsageBar,
}} from "cursor/canvas";

const DATA = {data_json} as const;

type Row = readonly (string | number)[];

function diffLabel(diff: number): string {{
  return diff >= 0 ? `+${{diff}}` : String(diff);
}}

export default function AdgCiBurndownCanvas() {{
  const overallTone = DATA.overall_pass ? "success" : "danger";
  const [blockPass, blockFail, ratchetPass, ratchetRegressed, warn] = DATA.summary;
  const bandNetTotal =
    DATA.bands.reduce((s, row) => s + Number(row[4]), 0) || 1;

  return (
    <Stack gap={{20}} style={{{{ padding: 20, maxWidth: 960 }}}}>
      <H1>ADG CI Burndown (summary)</H1>
      <Text tone="secondary" size="small">
        {{DATA.generated}} · {{DATA.snapshot}} · {{DATA.total_gates}} gates
      </Text>
      <Callout tone={{overallTone}} title={{DATA.overall_pass ? "PASS" : "BLOCKED"}}>
        <Text>{{DATA.bcg_brief.business_read}}</Text>
        <Text>
          Full gate table (48 rows): {{DATA.markdown_rel}} — open in editor, then
          Markdown preview (Ctrl+Shift+V).
        </Text>
      </Callout>

      <Grid columns={{5}} gap={{16}}>
        <Stat value={{blockPass}} label="block_pass" tone="success" />
        <Stat value={{blockFail}} label="block_fail" tone={{blockFail > 0 ? "danger" : undefined}} />
        <Stat value={{ratchetPass}} label="ratchet_pass" tone="info" />
        <Stat value={{ratchetRegressed}} label="ratchet_regressed" tone={{ratchetRegressed > 0 ? "warning" : undefined}} />
        <Stat value={{warn}} label="warn" />
      </Grid>

      <Card>
        <CardHeader>Burndown by band</CardHeader>
        <CardBody>
          <UsageBar
            total={{bandNetTotal}}
            topLeftLabel="P0–P3 net"
            segments={{DATA.bands.map((row) => ({{
              id: String(row[0]),
              value: Number(row[4]),
            }}))}}
          />
          <Table
            framed
            striped
            stickyHeader
            headers={{["Band", "Label", "Gross", "Guardian", "Net", "Diff"]}}
            columnAlign={{["left", "left", "right", "right", "right", "right"]}}
            rows={{DATA.bands.map((row: Row) => [
              String(row[0]),
              String(row[1]),
              String(row[2]),
              String(row[3]),
              String(row[4]),
              diffLabel(Number(row[5])),
            ])}}
          />
        </CardBody>
      </Card>

      {{DATA.blockers.length > 0 ? (
        <Card>
          <CardHeader>Top blockers</CardHeader>
          <CardBody style={{{{ padding: 0 }}}}>
            <Table
              framed
              striped
              stickyHeader
              headers={{["Gate", "Band", "Enf", "Verdict", "Findings", "Description"]}}
              rowTone={{DATA.blockers.map(() => "danger" as const)}}
              rows={{DATA.blockers.map((row: Row) => [
                String(row[0]),
                String(row[1]),
                String(row[2]),
                String(row[3]),
                String(row[4]),
                String(row[5]),
              ])}}
            />
          </CardBody>
        </Card>
      ) : (
        <Callout tone="success" title="No blockers">
          <Text>See markdown report for full gate list.</Text>
        </Callout>
      )}}
    </Stack>
  );
}}
"""


def _open_in_cursor(path: Path, label: str) -> None:
    if os.environ.get("ADG_BURNDOWN_NO_OPEN", "").strip() in ("1", "true", "yes"):
        return
    cursor_bin = shutil.which("cursor") or shutil.which("cursor.exe")
    if not cursor_bin:
        print(f"[adg_burndown_canvas] cursor CLI not on PATH — open {label} manually", file=sys.stderr)
        return
    try:
        subprocess.run([cursor_bin, "-r", str(path)], check=False, timeout=30)
        print(f"[adg_burndown_canvas] opened {label}: {path}", file=sys.stderr)
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"[adg_burndown_canvas] open {label} failed: {exc}", file=sys.stderr)


def emit_adg_burndown_canvas(
    gate_results: Path | None = None,
    burndown: Path | None = None,
    *,
    open_markdown: bool = True,
    open_canvas: bool = False,
) -> int:
    """Write compact canvas; prefer opening markdown tables for reading."""
    burndown_path = (burndown or BURNDOWN_TABLE_DEFAULT).resolve()
    try:
        gate_path = (gate_results or _latest_gate_results()).resolve()
    except FileNotFoundError as exc:
        print(f"[adg_burndown_canvas] skipped: {exc}", file=sys.stderr)
        return 0

    if not gate_path.is_file() or not burndown_path.is_file():
        print("[adg_burndown_canvas] skipped: missing inputs", file=sys.stderr)
        return 0

    md_path = _readable_markdown_path()
    if open_markdown and md_path.is_file():
        print(f"[adg_burndown_canvas] READABLE_TABLES={md_path}", file=sys.stderr)
        _open_in_cursor(md_path, "markdown report")

    if _canvas_bypassed():
        return 0

    try:
        payload = build_canvas_payload(gate_path, burndown_path)
        out_dir = _cursor_canvases_dir()
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / CANVAS_BASENAME
        out_path.write_text(_tsx_source(payload), encoding="utf-8")
        line_count = len(out_path.read_text(encoding="utf-8").splitlines())
        print(f"[adg_burndown_canvas] CANVAS_PATH={out_path} ({line_count} lines)", file=sys.stderr)
        if open_canvas:
            _open_in_cursor(out_path, "canvas summary")
    except OSError as exc:
        print(f"[adg_burndown_canvas] write failed: {exc}", file=sys.stderr)
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    del argv
    from tools.reports.adg_burndown_report import emit_mandatory_adg_burndown_report

    return emit_mandatory_adg_burndown_report(print_inline=False)


if __name__ == "__main__":
    raise SystemExit(main())
