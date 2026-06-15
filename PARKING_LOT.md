# 🅿️ PARKING LOT — the one place ideas go so you can let them go

> **NORTH STAR (the only thing that ships):** apps_rg E2E, 11/11 lanes X3_ALLOW,
> sliding-scale graph skills, assembled DOCX in hand.

## The contract (read this every time you add a line)

1. **Capturing ≠ committing.** A line here means "I will not forget it." It does
   NOT mean "I will do it." You are allowed to think *good idea — parked* and walk away.
2. **Nothing here is worked until 11/11 lanes are green.** This is a holding pen,
   not a queue. The lot is what makes it safe to NOT act.
3. **You WILL see this again.** Reviewed every Monday. That guarantee is what lets
   your brain release the idea instead of building it now.

## The only decision

```
Is this literally one of the 11 lanes / a graph-skill / the DOCX?
   YES → work it now (it's north-star).
   NO  → one line below. Walk away. It is safe.
```

## How to capture (≤5 seconds, no formatting, no plan)

`- [U|P|N] <date> one line — whatever it was`

- `[U]` unrelated to north star
- `[P]` partially related (the scary one — STILL goes here; if it's truly needed
  for a lane you'll hit it while building that lane, and it'll be waiting right here)
- `[N]` genuinely north-star (the only tag allowed to graduate to real work now)

---

## Inbox (append-only — never delete, only move to "Resolved" at weekly review)

<!-- add new lines at the TOP. one line each. -->
- [P] 2026-06-15 CORRECTION (report §8 fix, post-lanes): verified-dead orphan CI gates = 4, NOT 118/230 (proper scan incl. adg_gate_manifest.yaml + cross-imports + all tracked files: 281/285 WIRED). "−230 gates / 282→50" claim is UNSUPPORTED — only 4 removable as dead code; deeper cuts = deliberate per-gate retirement of WIRED gates (policy decision, not orphan sweep). Evidence: /tmp/orphans.json this session.
- [P] 2026-06-15 H3 auto-park gate (the missing relevance primitive — RCA'd this session): PreToolUse on Write/Edit to off-north-star paths (.claude/**, plans/**, ops_scripts/ci/**) while lanes<11/11 → fire AskUserQuestion; "Park it" = option1 [RECOMMENDED ⭐ confidence≈0.82, justified by last-100 base-rate 18% north-star]; on Park, auto-append here. Gate auto-disables at 11/11. Build AFTER green (building it now IS the drift).
- [P] 2026-06-15 Gate cleanup: delete verified-dead orphan CI contract gates (ops_scripts/ci only; NOT runtime/workflows/ADG-truth). Orphan-scan method proven this session (/tmp/orphan_verify.py). Execute AFTER 11/11 lanes green.
- [P] 2026-06-15 Build behavior hooks H1 (parking-lot weekly nudge) + H2 (north-star scoreboard) + H7 (WIP=1 gate). H1 is the only one arguably justified pre-green; rest parked.


## Resolved / promoted (weekly-review outcomes only)

<!-- at Monday review: each line becomes done | promoted-to-lane-work | dropped -->
