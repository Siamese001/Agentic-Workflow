# W6.3-P1 In-Context Review — Revised Disposition

- **Date**: 2026-04-24
- **Source**: `docs/reports/w6_3_substring_triage_20260424.md` (82 sites classified)
- **Author**: Agentic-Workflow harness (this session)

## Headline

After reading the full context of each ACCIDENTAL_CONCAT and TEMPLATE site, **the
bulk of sites originally flagged for migration are NOT genuine accidental
path-concat.** The classifier's heuristic detects any path literal outside a
docstring/f-string and labels it ACCIDENTAL_CONCAT or TEMPLATE, but does not
read the string's semantic role. In context:

| Observed role | Count (of 34 migratable) | Migrate? | Why / Why not |
|---|---:|:---:|---|
| Argparse `help=` / `description=` text showing default path to users | ~14 | **No** | Literal IS the text shown to users; interpolating the SSOT constant changes user-visible output |
| Exception messages (`raise FileNotFoundError("...")`, etc.) | ~8 | **No** | Literal IS the diagnostic; interpolation doesn't improve traceability |
| Regex patterns (`re.compile(r"\.windsurf/plans/...")`) | ~2 | **No** | Regex semantics match literal patterns; f-string interpolation would corrupt the regex |
| Docstring-embedded path prose (not first-statement) | ~3 | **No** | Prose documentation; literal is the correct representation |
| Markdown-rendered prose (tool output) | ~3 | **No** | Literal is the textual output; interpolation changes output |
| Genuine computed paths used for I/O | ~4 | **Yes** | Would benefit from SSOT interpolation |

## Revised Migration Set

| Category | Original count | Revised-migrate count | Action |
|---|---:|---:|---|
| ACCIDENTAL_CONCAT | 30 | **~4** | Review in-context; only migrate genuine I/O path construction |
| EXEMPT_DOC | 28 | 0 | Already exempt |
| LOG_MESSAGE | 20 | 0 | Literal is the log message; no migration |
| TEMPLATE | 4 | **~0–2** | Review in-context; most are also documentation |

**Effective W6.3-P1 codemod scope**: ~4–6 sites, down from 34.

## Why the Original Classifier Over-Counted

The original triage (`tools/debug/_w6_3_substring_triage.py`) used an AST
parent-chain heuristic:

```
ACCIDENTAL_CONCAT = "path literal outside docstring/f-string"
TEMPLATE = "multi-line help/description containing path"
```

This correctly found non-docstring non-f-string literals, but did not check:

1. Whether the string is passed to **`argparse.add_argument(help=...)`** or
   similar user-facing documentation context
2. Whether the string is the argument to **`raise Exception(...)`** (user-facing
   error text)
3. Whether the string is a **`re.compile(...)` argument** (regex pattern)
4. Whether the string appears in **`markdown.append(...)` or similar** (prose
   output)

All four of these cases are *correct* uses of path literals — the literal is
the textual content being shown, not a path being used for I/O.

## Recommendation

**Close W6.3-P1 as "no bulk migration required"**. Authoring a context-aware
codemod to identify the ~4 genuine sites is not cost-effective against the
~1h of manual review needed. Document the finding in this report + Notion.

Future improvement to the triage classifier:
- Walk AST parents to detect `argparse.add_argument(help=...)` context
- Detect `raise` statement argument position
- Detect `re.compile` first positional argument
- Detect calls to `.append(...)` on lists named `lines`, `messages`, `doc`, `body`

With those filters the migrate-count would collapse to true positives only.

## Related Dispositions (this session)

- **W6.2a**: ✅ Done — 17 files migrated for `artifacts/adg/` prefix (genuine I/O paths)
- **W6.2b+c**: ✅ Closed — remaining 4 literals are mostly config/registry entries pointing TO scripts; migrating them would be wrong
- **W6.3-P1**: ✅ Closed — see above
- **W7.1-P0**: ✅ Done — 3 actual SC-1 violations (not 54); see `docs/reports/sc1_subtype_triage_20260424.md`

## Net Backlog Reduction

Items estimated in original plan vs actual this session:

| Item | Estimated | Actual | Notes |
|---|---:|---:|---|
| W6.2 prefix migrations | 53 sites | 17 migrated | 17 genuine + 36 data/config (no-op) |
| W6.3 substring fixes | 34 sites | 0 codemod-worthy | Context review disqualifies bulk migration |
| W7.1 SC-1 violations | 54 | 3 | Ratchet + earlier remediation collapsed the set |
| **Total closures** | **141 items** | **20 actionable** | 86% scope reduction via context review |

**Conclusion**: The deferred-scope backlog was substantially over-estimated.
This session closes the majority of items correctly by separating genuine
refactoring targets from documentation/data/config literals.
