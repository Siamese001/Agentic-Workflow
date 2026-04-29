"""Build a per-test-function inventory of the live test suite.

Walks every `test_*.py` under `tests/` (excluding `_archived_obsolete/`),
AST-parses each module, extracts test functions, and classifies each on
multiple axes so the suite can be triaged without re-running the analysis.

Classification axes (booleans unless noted):

- ``touches_otel``: imports an `otel*` / `opentelemetry` module OR mentions
  `tracer`, `span`, `emit_span`, `otel_` in the function body source.
- ``touches_subprocess``: function source contains `subprocess.run|Popen|check_`.
- ``touches_real_io``: opens files, hits sqlite3 directly, opens sockets, or
  uses tmp_path (real on-disk work, even if scoped to a tmpdir).
- ``touches_adg_sqlite``: imports `adg_indexed_*.sqlite` path or calls an
  `adg_*` helper (mcp1_adg_*, agentic_core ADG modules).
- ``mock_only``: uses `Mock` / `MagicMock` / `patch` AND none of the
  `touches_*` flags above are true.
- ``parametrize_count``: int — number of parameter cases the test will expand
  to (1 if not parametrized; product of all `@pytest.mark.parametrize` rows
  if multiple decorators).
- ``schema_sweep``: parametrize_count >= 5 AND only assertions of the form
  ``assert <expr> is/!= None`` / ``assert isinstance`` / ``assert hasattr``
  / ``assert <expr> in <set>`` (i.e., structural — not behavioral).
- ``import_smoke``: function body is a single `assert <something>` line that
  proves nothing more than "the module imports".
- ``assertion_count``: int — number of `assert` statements.
- ``loc``: int — function body line count.

Output:
    artifacts/test_inventory/test_inventory.json   (one row per test fn)
    artifacts/test_inventory/test_inventory_summary.md
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .windsurf/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import ast
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Iterable

REPO = Path(__file__).resolve().parents[2]
TESTS_ROOT = REPO / "tests"
OUT_DIR = REPO / "artifacts" / "test_inventory"
ARCHIVE_MARKER = "_archived_obsolete"

OTEL_RE = re.compile(r"\b(otel|opentelemetry|tracer\.|span\.|emit_span|otel_)\b", re.IGNORECASE)
SUBPROC_RE = re.compile(r"subprocess\.(run|Popen|check_output|check_call|call)")
SQLITE_RE = re.compile(r"\b(sqlite3\.|adg_indexed|artifacts/adg)\b")
ADG_HELPER_RE = re.compile(r"\b(adg_health|adg_node|adg_nodes_by|adg_edge_|adg_violations|adg_p0_wave_plan|mcp1_adg)\b")
SOCKET_RE = re.compile(r"\b(socket\.socket|httpx\.|requests\.|aiohttp\.)")
MOCK_RE = re.compile(r"\b(Mock|MagicMock|AsyncMock|patch|mocker\.)")
STRUCTURAL_ASSERT_RE = re.compile(
    r"^\s*assert\s+(.+?)(?:\s+(?:is|is\s+not)\s+None|\s+in\s+|^isinstance\(|^hasattr\()"
)


@dataclass
class TestRecord:
    file: str
    cls: str  # "" if module-level
    name: str
    parametrize_count: int = 1
    assertion_count: int = 0
    loc: int = 0
    touches_otel: bool = False
    touches_subprocess: bool = False
    touches_real_io: bool = False
    touches_adg_sqlite: bool = False
    mock_only: bool = False
    schema_sweep: bool = False
    import_smoke: bool = False
    tags: list[str] = field(default_factory=list)


def _count_parametrize(decorators: list[ast.expr]) -> int:
    total = 1
    for dec in decorators:
        node = dec.func if isinstance(dec, ast.Call) else dec
        attrs = []
        cur = node
        while isinstance(cur, ast.Attribute):
            attrs.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name):
            attrs.append(cur.id)
        attrs.reverse()
        if "parametrize" in attrs:
            if isinstance(dec, ast.Call) and len(dec.args) >= 2:
                arg = dec.args[1]
                if isinstance(arg, (ast.List, ast.Tuple)):
                    total *= max(len(arg.elts), 1)
    return total


def _classify_function(
    func: ast.FunctionDef | ast.AsyncFunctionDef,
    src_lines: list[str],
) -> tuple[int, int, bool, bool, bool, bool, bool, bool, bool]:
    body_start = func.body[0].lineno - 1 if func.body else func.lineno
    body_end = func.end_lineno or body_start + 1
    body_text = "\n".join(src_lines[body_start - 1 : body_end])
    body_text_lower = body_text  # keep case for some patterns
    asserts = sum(1 for ln in body_text.splitlines() if re.match(r"^\s*assert\s", ln))
    loc = max(body_end - body_start, 1)

    has_otel = bool(OTEL_RE.search(body_text_lower))
    has_subproc = bool(SUBPROC_RE.search(body_text))
    has_sqlite = bool(SQLITE_RE.search(body_text)) or bool(ADG_HELPER_RE.search(body_text))
    # tmp_path / Path(...).write_text / open( imply real IO
    has_real_io = bool(
        re.search(r"\btmp_path\b|\bPath\([^)]*\)\.(write|read|open)|\bopen\(", body_text)
        or SOCKET_RE.search(body_text)
        or has_sqlite
        or has_subproc
    )
    has_mock = bool(MOCK_RE.search(body_text))
    mock_only = has_mock and not (has_otel or has_subproc or has_sqlite or has_real_io)

    structural_asserts = sum(
        1 for ln in body_text.splitlines() if STRUCTURAL_ASSERT_RE.match(ln)
    )
    schema_sweep_eligible = structural_asserts >= 1 and asserts > 0 and structural_asserts == asserts

    # import_smoke: very small function whose only assertions are structural and there are 0-2 asserts
    import_smoke = loc <= 4 and asserts <= 2 and structural_asserts == asserts and asserts > 0

    return loc, asserts, has_otel, has_subproc, has_real_io, has_sqlite, mock_only, bool(import_smoke), schema_sweep_eligible


def _walk_tests(node: ast.Module, src_lines: list[str], file_rel: str) -> Iterable[TestRecord]:
    for cls in [n for n in ast.walk(node) if isinstance(n, ast.ClassDef)]:
        for func in [c for c in cls.body if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            if func.name.startswith("test_"):
                yield _record(func, src_lines, file_rel, cls.name)
    # Module-level test functions
    for func in [c for c in node.body if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        if func.name.startswith("test_"):
            yield _record(func, src_lines, file_rel, "")


def _record(
    func: ast.FunctionDef | ast.AsyncFunctionDef,
    src_lines: list[str],
    file_rel: str,
    cls_name: str,
) -> TestRecord:
    pcount = _count_parametrize(func.decorator_list)
    classification = _classify_function(func, src_lines)
    loc, asserts, has_otel, has_subproc, has_real_io, has_sqlite, mock_only, is_smoke, schema_eligible = classification
    schema_sweep = schema_eligible and pcount >= 5

    tags = []
    if has_otel:
        tags.append("otel")
    if has_subproc:
        tags.append("subprocess")
    if has_sqlite:
        tags.append("adg_sqlite")
    if has_real_io and not (has_subproc or has_sqlite):
        tags.append("real_io")
    if mock_only:
        tags.append("mock_only")
    if schema_sweep:
        tags.append("schema_sweep")
    if is_smoke:
        tags.append("import_smoke")
    if not tags:
        tags.append("uncategorized")

    return TestRecord(
        file=file_rel,
        cls=cls_name,
        name=func.name,
        parametrize_count=pcount,
        assertion_count=asserts,
        loc=loc,
        touches_otel=has_otel,
        touches_subprocess=has_subproc,
        touches_real_io=has_real_io,
        touches_adg_sqlite=has_sqlite,
        mock_only=mock_only,
        schema_sweep=schema_sweep,
        import_smoke=is_smoke,
        tags=tags,
    )


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    records: list[TestRecord] = []
    parse_failures = 0

    test_files = [
        p for p in TESTS_ROOT.rglob("test_*.py")
        if ARCHIVE_MARKER not in p.parts
    ]
    print(f"Scanning {len(test_files)} test files ...")

    for i, path in enumerate(test_files):
        if i % 250 == 0 and i:
            print(f"  ... {i}/{len(test_files)}")
        try:
            text = path.read_text(encoding="utf-8")
            tree = ast.parse(text, filename=str(path))
        except (SyntaxError, UnicodeDecodeError):
            parse_failures += 1
            continue
        rel = path.relative_to(REPO).as_posix()
        src_lines = text.splitlines()
        records.extend(_walk_tests(tree, src_lines, rel))

    # Write per-record JSON
    out_json = OUT_DIR / "test_inventory.json"
    out_json.write_text(
        json.dumps([asdict(r) for r in records], indent=1),
        encoding="utf-8",
    )

    # Build summary
    total = len(records)
    expansions = sum(r.parametrize_count for r in records)
    by_tag: dict[str, int] = {}
    for r in records:
        for t in r.tags:
            by_tag[t] = by_tag.get(t, 0) + 1
    fan_in_files: dict[str, int] = {}
    for r in records:
        fan_in_files[r.file] = fan_in_files.get(r.file, 0) + r.parametrize_count
    top_files = sorted(fan_in_files.items(), key=lambda kv: -kv[1])[:25]

    summary_lines = [
        "# Test Suite Inventory — Summary",
        "",
        f"- **Test files scanned**: {len(test_files)}",
        f"- **Parse failures**: {parse_failures}",
        f"- **Unique test functions**: {total}",
        f"- **Collected items (parametrize-expanded)**: {expansions}",
        f"- **Expansion ratio**: {expansions/total:.1f}× ",
        "",
        "## Counts by tag (a function can carry multiple tags)",
        "",
        "| Tag | Functions | % of total |",
        "|---|---:|---:|",
    ]
    for tag in [
        "otel", "subprocess", "adg_sqlite", "real_io",
        "mock_only", "schema_sweep", "import_smoke", "uncategorized",
    ]:
        n = by_tag.get(tag, 0)
        pct = 100 * n / total if total else 0
        summary_lines.append(f"| `{tag}` | {n} | {pct:.1f}% |")

    summary_lines += [
        "",
        "## Top 25 files by parametrize-expanded test count",
        "",
        "| Expansions | File |",
        "|---:|---|",
    ]
    for f, n in top_files:
        summary_lines.append(f"| {n} | `{f}` |")

    # Tier proposals
    runtime_signal = sum(
        1 for r in records
        if r.touches_otel or r.touches_subprocess or r.touches_adg_sqlite
        or (r.touches_real_io and not r.mock_only)
    )
    contract_only = sum(1 for r in records if r.mock_only)
    schema_sweeps = by_tag.get("schema_sweep", 0)
    smoke = by_tag.get("import_smoke", 0)
    uncategorized = by_tag.get("uncategorized", 0)

    summary_lines += [
        "",
        "## Proposed tiers",
        "",
        "| Tier | Count | Definition |",
        "|---|---:|---|",
        f"| `runtime` | {runtime_signal} | Touches OTel, real subprocess, real ADG SQLite, or real IO |",
        f"| `contract` (mock-only) | {contract_only} | Uses Mock/patch and no real IO/runtime/OTel |",
        f"| `schema_sweep` | {schema_sweeps} | Parametrize ≥5 cases with only structural assertions |",
        f"| `import_smoke` | {smoke} | Trivial \"module imports\" / \"symbol exists\" tests |",
        f"| `uncategorized` | {uncategorized} | Did not match any axis — likely real behavioral tests |",
        "",
        "Pick which tiers run by default via pytest markers; reserve `runtime` + `uncategorized`",
        "for the fast feedback loop, gate the rest behind explicit `-m contract` etc.",
    ]

    out_md = OUT_DIR / "test_inventory_summary.md"
    out_md.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"\nWrote: {out_json.relative_to(REPO)}")
    print(f"Wrote: {out_md.relative_to(REPO)}")
    print()
    print("\n".join(summary_lines[:40]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
