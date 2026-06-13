# Zero-Loss Originals — durable, tracked archive

Source bodies removed during zero-loss refactors (constitutional §10 zero-loss
refactor, §9 archival-over-deletion). This directory lives under `docs/archive/`
— the **only git-tracked** archive location. Root `archives/`,
`ops_scripts/archives/`, and `artifacts/healing_backups/` are all `.gitignored`
local-only sinks, so artifacts that must survive review/clones belong here.

## 2026-05-25 — RootCustomsAgent legacy orphan body
- File: `2026-05-25/agentic_core__L0_routing__reasoning__RootCustomsAgent_legacy_orphan_body.py` (748 lines)
- Origin: orphaned body extracted from
  `agentic_core/L0_routing/reasoning/RootCustomsAgent.py` during a zero-loss
  refactor on 2026-05-25.
- Why relocated (2026-06-13): it was the sole file stranded in the deprecated,
  `.gitignored` root `archives/` folder (removed from SSOT 2026-04-21 per
  `agentic_core/L0_routing/config/path_constants.py`). Because root `archives/`
  is never committed, this zero-loss original existed only on one local disk;
  relocated here so it survives review and clones.
- Recoverability note: the same code is also recoverable from the pre-2026-05-25
  git history of `RootCustomsAgent.py`; this directory is the explicit artifact.
