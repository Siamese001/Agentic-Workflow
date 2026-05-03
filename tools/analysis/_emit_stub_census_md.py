"""Render apps_shared/STUB_CENSUS.md from the census JSON."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from datetime import datetime, timezone

_CENSUS = Path("artifacts/analysis/apps_shared_stub_census.json")
_OUT = Path("apps_shared/STUB_CENSUS.md")


def _main() -> int:
    data = json.loads(_CENSUS.read_text(encoding="utf-8"))
    stubs = data["stubs"]
    by_category: dict[str, list[dict]] = defaultdict(list)
    for s in stubs:
        by_category[s["category"]].append(s)

    lines: list[str] = []
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines.append("# apps_shared Stub Census")
    lines.append("")
    lines.append(f"**Generated:** {ts}")
    lines.append(
        "**Source:** `python tools/analysis/audit_apps_shared_stubs.py`  "
    )
    lines.append(
        f"**Input:** `{_CENSUS.as_posix()}`  "
    )
    lines.append(
        "**Plan:** "
        "[`apps-shared-stub-audit-7dfe16`]"
        "(../.windsurf/plans/apps-shared-stub-audit-7dfe16.md)"
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Scanned files:** {data['scanned_files']}")
    lines.append(f"- **Total stubs:** {data['stub_total']}")
    legit_pct = 100.0 * data["legit_total"] / max(1, data["stub_total"])
    lines.append(
        f"- **Legitimate:** {data['legit_total']} "
        f"({legit_pct:.1f}%)"
    )
    lines.append(f"- **Real gaps:** {data['real_gap_total']}")
    lines.append("")
    lines.append("## Category counts")
    lines.append("")
    lines.append("| Category | Count | Meaning |")
    lines.append("|---|---:|---|")
    category_meanings = {
        "Protocol": "`typing.Protocol` subclass — interface declaration, no body",
        "ABC": "explicit `abc.ABC` subclass or `@abstractmethod` method",
        "ImplicitABC": (
            "class name suggests abstract (Base/Abstract/Client/Checker/"
            "Processor/Provider/Adapter) AND has `NotImplementedError` method — duck-typed abstract"
        ),
        "TypedDict": "`TypedDict` subclass — fields declaration",
        "TemplateMethodHook": (
            "private hook method (`_*`) on Base/Abstract/Executor/Invoker class — subclasses override"
        ),
        "ContextManagerStub": (
            "dunder context-manager method (`__enter__`/`__aexit__`/etc.) with no-op body"
        ),
        "NullObject": (
            "module-level function with descriptive docstring + no-op body — graceful-fallback pattern"
        ),
        "DeprecationShim": "file under `_compat/` — backward-compat shim",
        "HealerConvention": (
            "`heal`/`heal_repository` structured no-op per apps_lic convention"
        ),
        "RealGap": "none of the above — human follow-up required",
    }
    for cat, n in sorted(
        data["category_counts"].items(), key=lambda kv: -kv[1]
    ):
        lines.append(f"| `{cat}` | {n} | {category_meanings.get(cat, '—')} |")
    lines.append("")
    lines.append("## Stub-kind counts")
    lines.append("")
    lines.append("| Kind | Count | AST shape |")
    lines.append("|---|---:|---|")
    kind_meanings = {
        "Pass": "`pass` after optional docstring",
        "Ellipsis": "`...` after optional docstring",
        "RetNone": "`return None` or bare `return` after optional docstring",
        "DocOnly": "docstring with no executable statements",
        "NotImpl": "`raise NotImplementedError`",
    }
    for k, n in sorted(data["kind_counts"].items(), key=lambda kv: -kv[1]):
        lines.append(f"| `{k}` | {n} | {kind_meanings.get(k, '—')} |")
    lines.append("")
    lines.append("## Per-category details")
    lines.append("")
    cat_order = [
        "RealGap",
        "Protocol",
        "ABC",
        "ImplicitABC",
        "TypedDict",
        "TemplateMethodHook",
        "ContextManagerStub",
        "NullObject",
        "DeprecationShim",
        "HealerConvention",
    ]
    for cat in cat_order:
        items = by_category.get(cat, [])
        if not items:
            continue
        lines.append(f"### {cat} ({len(items)})")
        lines.append("")
        lines.append(category_meanings.get(cat, ""))
        lines.append("")
        lines.append("| File | Line | Symbol | Stub | Rationale |")
        lines.append("|---|---:|---|---|---|")
        for s in sorted(items, key=lambda x: (x["file_path"], x["line_number"])):
            rationale = s["rationale"].replace("|", "\\|")
            lines.append(
                f"| `{s['file_path']}` "
                f"| {s['line_number']} "
                f"| `{s['qualified_name']}` "
                f"| {s['stub_kind']} "
                f"| {rationale} |"
            )
        lines.append("")

    lines.append("## Regenerating")
    lines.append("")
    lines.append("```bash")
    lines.append("python tools/analysis/audit_apps_shared_stubs.py")
    lines.append("python tools/analysis/_emit_stub_census_md.py")
    lines.append("```")
    lines.append("")
    lines.append("## Consumer notes")
    lines.append("")
    lines.append(
        "The `tools/analysis/_apps_completeness_review2.py` scanner "
        "consumes the census JSON (W4 of plan `apps-shared-stub-audit-7dfe16`) "
        "and emits a `RealGaps` column distinguishing legitimate Protocol/ABC "
        "pattern stubs from real gaps. Without the census, that column falls "
        "back to the total stub count."
    )
    lines.append("")
    lines.append("## Adding a new stub?")
    lines.append("")
    lines.append(
        "If your new function/method genuinely needs a stub body, prefer "
        "one of these legitimate patterns (in order of preference):"
    )
    lines.append("")
    lines.append(
        "1. Inherit from `abc.ABC` + `@abstractmethod` — most explicit, "
        "static type checkers + CI gates understand it."
    )
    lines.append(
        "2. Inherit from `typing.Protocol` — structural typing; no runtime "
        "cost; best when the class describes an interface rather than a "
        "base implementation."
    )
    lines.append(
        "3. Structured no-op dict (see `apps_lic/RUNBOOK.md` "
        "`#heal-method-notimpl-convention`) — for legitimately-stateless "
        "adapters where `raise NotImplementedError` would force every "
        "caller into exception handling."
    )
    lines.append(
        "4. Null-object module-level function with descriptive docstring "
        "— for graceful-fallback observability/provider wiring."
    )
    lines.append("")
    lines.append(
        "Avoid bare `pass` bodies on script-level (`scripts/`) files — "
        "the audit treats those as RealGap."
    )
    lines.append("")

    _OUT.parent.mkdir(parents=True, exist_ok=True)
    _OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {_OUT} ({len(lines)} lines, {len(_OUT.read_text(encoding='utf-8'))} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
