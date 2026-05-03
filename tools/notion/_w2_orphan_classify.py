"""W2 one-shot — classify the 38 unique orphan slugs by Cascade confidence."""
import json
import re
from collections import Counter
from pathlib import Path

log = Path("artifacts/windsurf/backlog_plan_linkage_misses.jsonl")
slug_counts: Counter = Counter()
for line in log.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    try:
        slug_counts[json.loads(line)["slug"]] += 1
    except Exception:
        pass

# Heuristic classification rules:
#   parenthetical/sentinel/note  -> DELETE  (very high confidence, not a real slug)
#   "(NEW" or ".md (" markers     -> DELETE  (never scaffolded, prose contamination)
#   "_INDEX_*"                    -> DELETE  (sentinel)
#   ends with stale-pattern       -> CATCH-ALL (real-looking name, no plan)
#   resembles known-pattern slug  -> CATCH-ALL with some confidence
#   ambiguous                     -> AUTHOR-GATE
def classify(slug: str) -> tuple[str, float, str]:
    s = slug.strip()
    if "(" in s and ")" in s:
        return "delete", 0.95, "parenthetical prose, not a real slug"
    if "NEW" in s and "scaffolded" in s.lower():
        return "delete", 0.93, "marked for future scaffolding, never created"
    if s.startswith("_INDEX_"):
        return "delete", 0.92, "internal index sentinel"
    if s.endswith(".py") or s.endswith(".md"):
        return "delete", 0.88, "filename-as-slug — capture-marker bug"
    # "real-looking" slug pattern: kebab-case, ends with 6-hex or descriptive
    if re.match(r"^[a-z0-9]+(-[a-z0-9]+)+$", s):
        # Has a 6-hex tail?
        if re.search(r"-[a-f0-9]{6}$", s):
            return "catch-all", 0.82, "real-looking slug w/ 6hex; plan never written but format is canonical"
        return "catch-all", 0.70, "real-looking slug w/o 6hex; ambiguous origin"
    return "ambiguous", 0.50, "no heuristic match"


print(f"{'CONF':>5}  {'ACTION':<10}  {'ROWS':>4}  SLUG  -- RATIONALE")
print("-" * 130)
buckets: dict[str, list] = {"delete": [], "catch-all": [], "ambiguous": []}
for slug, n in slug_counts.most_common():
    action, conf, rationale = classify(slug)
    buckets[action].append((conf, n, slug, rationale))
    print(f"{conf:>5.2f}  {action:<10}  {n:>4}  {slug[:60]:<60}  -- {rationale}")

print()
print(f"Summary:")
for k in ("delete", "catch-all", "ambiguous"):
    rows = sum(n for _, n, _, _ in buckets[k])
    slugs = len(buckets[k])
    print(f"  {k:<12} {slugs:>2} unique slugs  /  {rows:>3} rows")
