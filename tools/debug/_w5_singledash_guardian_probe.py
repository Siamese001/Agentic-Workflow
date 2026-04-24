"""Probe single-dash guardian comments that fail strict extraction.

The extractor requires `# guardian: allow-X -- <justification>`.
Find sites that use `# guardian: allow-X - <justification>` (single dash)
or other near-miss separators.
"""
from __future__ import annotations
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOTS = ("agentic_core", "apps_rg", "apps_shared", "apps_lic", "apps_eval",
         "apps_exec", "apps_research", "apps_rfp", "apps_underwriting_ai",
         "tools", "ops_scripts", "system_learning", "infrastructure")
EXCLUDE = (r"(^|[/\\])__pycache__[/\\]", r"(^|[/\\])archives?[/\\]",
           r"(^|[/\\])tests[/\\]", r"(^|[/\\])tools[/\\]debug[/\\]")

# Match `# guardian: allow-X SEP justification` where SEP is NOT --
# Allow letters/digits/dashes in token name.
RX_BARE = re.compile(r"#\s*guardian:\s*(allow-[A-Za-z0-9_-]+)\s*(?:\n|$)")
RX_SINGLE_DASH = re.compile(r"#\s*guardian:\s*(allow-[A-Za-z0-9_-]+)\s+-\s+(\S+)")
RX_COLON = re.compile(r"#\s*guardian:\s*(allow-[A-Za-z0-9_-]+)\s*:\s+(\S+)")
RX_DOUBLE_DASH = re.compile(r"#\s*guardian:\s*(allow-[A-Za-z0-9_-]+)\s+--\s+(\S+)")

categories = {
    "BARE_NO_JUSTIFICATION": (RX_BARE, set()),
    "SINGLE_DASH_SEPARATOR":  (RX_SINGLE_DASH, set()),
    "COLON_SEPARATOR":        (RX_COLON, set()),
    "CANONICAL_DOUBLE_DASH":  (RX_DOUBLE_DASH, set()),
}

counts: dict[str, int] = defaultdict(int)
samples: dict[str, list[tuple[str, int, str]]] = defaultdict(list)
token_by_cat: dict[str, Counter] = defaultdict(Counter)

for root in ROOTS:
    p = Path(root)
    if not p.exists():
        continue
    for py in p.rglob("*.py"):
        sp = str(py)
        if any(re.search(pat, sp) for pat in EXCLUDE):
            continue
        try:
            text = py.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for ln_idx, line in enumerate(text.splitlines(), 1):
            if "guardian:" not in line:
                continue
            # Test categories in priority order — most specific first
            for cat, (rx, _) in categories.items():
                m = rx.search(line)
                if m:
                    counts[cat] += 1
                    token_by_cat[cat][m.group(1)] += 1
                    if len(samples[cat]) < 8:
                        samples[cat].append((sp, ln_idx, line.strip()[:140]))
                    break

print("Guardian comment style distribution:")
for cat, n in sorted(counts.items(), key=lambda t: -t[1]):
    print(f"  {n:>5}  {cat}")

print("\nTop tokens per non-canonical category:")
for cat in ("BARE_NO_JUSTIFICATION", "SINGLE_DASH_SEPARATOR", "COLON_SEPARATOR"):
    if not token_by_cat[cat]:
        continue
    print(f"\n--- {cat} ---")
    for tok, n in token_by_cat[cat].most_common(10):
        print(f"  {n:>4}  {tok}")

print("\nSamples per non-canonical category:")
for cat in ("BARE_NO_JUSTIFICATION", "SINGLE_DASH_SEPARATOR", "COLON_SEPARATOR"):
    if not samples[cat]:
        continue
    print(f"\n--- {cat} ({counts[cat]} total) ---")
    for fp, ln, txt in samples[cat]:
        print(f"  {fp}:{ln}")
        print(f"    {txt}")

sys.exit(0)
