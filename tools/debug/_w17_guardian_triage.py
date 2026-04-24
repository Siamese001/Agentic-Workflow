"""W17.b-tail triage: classify all ``# guardian:`` markers in prod code.

Writes structured report to ``artifacts/guardian_lint/w17_triage_2026-04-24.txt``.
Used to scope ADR-027 and the bulk-fix CLI.
"""
from __future__ import annotations

import re
import subprocess
from collections import Counter
from pathlib import Path


EXCLUDE_TOKENS = ("docs/", "archives/", ".md:", "tools/archive/", "_backup", ".backup")


def classify() -> dict[str, list[str]]:
    result = subprocess.run(
        ["git", "grep", "-En", "# guardian:"],
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
    )
    lines = result.stdout.splitlines()
    prod = [l for l in lines if not any(x in l.lower() for x in EXCLUDE_TOKENS)]

    canonical: list[str] = []
    malformed: list[str] = []
    bare: list[str] = []
    for line in prod:
        m = re.search(r"# guardian:\s*(.*)", line)
        if not m:
            continue
        rest = m.group(1).strip()
        if rest.startswith("allow-") and "--" in rest:
            canonical.append(line)
        elif rest.startswith("allow-"):
            malformed.append(line)
        else:
            bare.append(line)
    return {"canonical": canonical, "malformed": malformed, "bare": bare}


def top_dirs(lines: list[str], n: int = 10) -> list[tuple[str, int]]:
    counter: Counter[str] = Counter()
    for line in lines:
        path = line.split(":", 1)[0].replace("\\", "/")
        bucket = "/".join(path.split("/")[:2])
        counter[bucket] += 1
    return counter.most_common(n)


def main() -> None:
    result = classify()
    out = Path("artifacts/guardian_lint/w17_triage_2026-04-24.txt")
    out.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("W17.b-tail guardian marker triage")
    lines.append("=" * 60)
    for bucket, items in result.items():
        lines.append(f"\n{bucket.upper()}: {len(items)} sites")
        lines.append("-" * 40)
        for d, n in top_dirs(items):
            lines.append(f"  {n:5d}  {d}")
    # Sample malformed separator patterns
    lines.append("\nMALFORMED sample patterns (first 15):")
    lines.append("-" * 40)
    seen: set[str] = set()
    for line in result["malformed"]:
        m = re.search(r"# guardian:\s*(allow-\S+\s*[^a-zA-Z0-9_\s]+\s*)", line)
        if m:
            pat = m.group(1).strip()
            if pat not in seen:
                seen.add(pat)
                lines.append(f"  {pat}")
                if len(seen) >= 15:
                    break
    # Sample bare markers
    lines.append("\nBARE sample markers (first 10):")
    lines.append("-" * 40)
    for line in result["bare"][:10]:
        lines.append(f"  {line[:160]}")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report: {out}")
    print(f"canonical={len(result['canonical'])}  malformed={len(result['malformed'])}  bare={len(result['bare'])}")


if __name__ == "__main__":
    main()
