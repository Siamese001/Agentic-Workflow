"""Byte-level diff of the 4 duplicated-surface families for Wave 1 of
plan apps-cross-app-precursors-c94c71.

Computes:
  - per-file SHA256 + LOC
  - all pairwise (i, j) similarity ratios via difflib.SequenceMatcher
  - family verdict per plan rule:
      PASS  : >=80%% of pairs byte-identical AND zero divergent pairs (>=20%% diff)
      DIVERGE: any pair with >=20%% difference
      else NEAR (mostly similar but not byte-identical)
  - emits a Markdown report at docs/reports/apps_common_duplication_report.md

Usage:
    python tools/analysis/diff_duplicated_families.py

No external deps; stdlib only.
"""
from __future__ import annotations

import difflib
import hashlib
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REPORT_PATH = REPO / "docs" / "reports" / "apps_common_duplication_report.md"

FAMILIES: dict[str, list[str]] = {
    "repo_signal_service": [
        "apps_eval/services/repo_signal_service.py",
        "apps_exec/services/repo_signal_service.py",
        "apps_lic/services/repo_signal_service.py",
        "apps_research/services/repo_signal_service.py",
        "apps_rg/utils/repo_signal_service.py",
    ],
    "observability_adapter": [
        "apps_eval/integrations/observability_adapter.py",
        "apps_exec/integrations/observability_adapter.py",
        "apps_lic/integrations/observability_adapter.py",
        "apps_research/integrations/observability_adapter.py",
        "apps_rg/integrations/observability_adapter.py",
        "apps_underwriting_ai/integrations/observability_adapter.py",
    ],
    "spine_adapter": [
        "apps_eval/spine/eval_spine_adapter.py",
        "apps_exec/spine/exec_spine_adapter.py",
        "apps_research/spine/research_spine_adapter.py",
        "apps_rg/engines/rg_spine_adapter.py",
    ],
    "ingress_runner": [
        "apps_eval/integrations/eval_ingress_runner.py",
        "apps_exec/integrations/exec_ingress_runner.py",
        "apps_lic/integrations/lic_ingress_runner.py",
        "apps_research/integrations/research_ingress_runner.py",
        "apps_rg/integrations/rg_ingress_runner.py",
        "apps_underwriting_ai/integrations/underwriting_ingress_runner.py",
    ],
}


@dataclass
class FileInfo:
    path: str
    sha256: str
    loc: int
    bytes: int
    content: str = field(repr=False)


def load_file(rel: str) -> FileInfo:
    p = REPO / rel
    data = p.read_bytes()
    text = data.decode("utf-8", errors="replace")
    return FileInfo(
        path=rel,
        sha256=hashlib.sha256(data).hexdigest(),
        loc=text.count("\n") + (0 if text.endswith("\n") else 1),
        bytes=len(data),
        content=text,
    )


@dataclass
class PairResult:
    a: str
    b: str
    ratio: float
    identical: bool
    divergent: bool


def pair_diff(a: FileInfo, b: FileInfo) -> PairResult:
    if a.sha256 == b.sha256:
        return PairResult(a.path, b.path, 1.0, True, False)
    ratio = difflib.SequenceMatcher(
        None, a.content, b.content, autojunk=False
    ).ratio()
    divergent = ratio < 0.80
    return PairResult(a.path, b.path, ratio, False, divergent)


@dataclass
class FamilyReport:
    name: str
    files: list[FileInfo]
    pairs: list[PairResult]

    @property
    def identical_count(self) -> int:
        return sum(1 for p in self.pairs if p.identical)

    @property
    def near_count(self) -> int:
        return sum(1 for p in self.pairs if not p.identical and not p.divergent)

    @property
    def divergent_count(self) -> int:
        return sum(1 for p in self.pairs if p.divergent)

    @property
    def verdict(self) -> str:
        if not self.pairs:
            return "N/A"
        identical_frac = self.identical_count / len(self.pairs)
        if self.divergent_count > 0:
            return "DIVERGE"
        if identical_frac >= 0.80:
            return "PASS"
        return "NEAR"


def analyze_family(name: str, rels: list[str]) -> FamilyReport:
    files = [load_file(r) for r in rels]
    pairs = [pair_diff(a, b) for a, b in combinations(files, 2)]
    return FamilyReport(name=name, files=files, pairs=pairs)


def render_markdown(reports: list[FamilyReport]) -> str:
    lines: list[str] = []
    lines.append("# apps_common Duplication Classification Report")
    lines.append("")
    lines.append(
        "Wave 1 deliverable for plan `apps-cross-app-precursors-c94c71`. "
        "Byte-level pairwise diff of 4 duplicated-surface families."
    )
    lines.append("")
    lines.append(
        "**Verdict rules**  "
        "PASS = >=80% pairs byte-identical AND zero divergent pairs (<20% diff).  "
        "DIVERGE = any pair with >=20% diff.  "
        "NEAR = mostly similar but not byte-identical, no divergent pairs."
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Family | Files | Identical pairs | Near pairs | Divergent pairs | Verdict |")
    lines.append("|---|---:|---:|---:|---:|---|")
    for r in reports:
        lines.append(
            f"| `{r.name}` | {len(r.files)} | {r.identical_count} | "
            f"{r.near_count} | {r.divergent_count} | **{r.verdict}** |"
        )
    lines.append("")

    for r in reports:
        lines.append(f"## Family: `{r.name}` ({r.verdict})")
        lines.append("")
        lines.append("### Files")
        lines.append("")
        lines.append("| Path | SHA256 (prefix) | LOC | Bytes |")
        lines.append("|---|---|---:|---:|")
        for f in r.files:
            lines.append(f"| `{f.path}` | `{f.sha256[:16]}` | {f.loc} | {f.bytes} |")
        lines.append("")
        lines.append("### Pairwise similarity")
        lines.append("")
        lines.append("| File A | File B | Ratio | Class |")
        lines.append("|---|---|---:|---|")
        for p in r.pairs:
            klass = (
                "IDENTICAL" if p.identical
                else ("DIVERGENT" if p.divergent else "NEAR")
            )
            lines.append(
                f"| `{p.a}` | `{p.b}` | {p.ratio:.3f} | {klass} |"
            )
        lines.append("")

    lines.append("## Wave 5 gating decision")
    lines.append("")
    for r in reports:
        action = (
            "Extract to `apps_common/`"
            if r.verdict == "PASS"
            else f"STAY per-app (verdict={r.verdict})"
        )
        lines.append(f"- **`{r.name}`** -> {action}")
    lines.append("")
    lines.append(
        "_Generated by `tools/analysis/diff_duplicated_families.py`._"
    )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    reports = [analyze_family(name, rels) for name, rels in FAMILIES.items()]
    md = render_markdown(reports)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(md, encoding="utf-8")
    print(f"Wrote {REPORT_PATH.relative_to(REPO)}")
    for r in reports:
        print(
            f"  {r.name:28s} verdict={r.verdict:8s} "
            f"identical={r.identical_count} near={r.near_count} "
            f"divergent={r.divergent_count}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
