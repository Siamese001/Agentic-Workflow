# Fix Rules-to-Notion Documentation Drift

> Close the gap between documented Notion registries and actual filesystem-SSOT reality.

---

## Context (SCQA)

- **Situation** — AGENTS.md documents a "Constitutional Rules Registry" in Notion with write trigger "On rule addition/modification". User repeatedly tries to sync rules to Notion, but it never works.
- **Complication** — The Constitutional Rules Registry database (`1c1379bc-32ca-4216-898a-3672f0316f69`) was **archived on 2026-05-02** per `notion_db_consolidation_2026_05_02.py`. It was an aspirational mirror that never had working automation. Rules are actually filesystem-SSOT at `.cursor/rules/*.md`.
- **Question** — How do we align documentation with reality, remove the broken expectation, and add lightweight validation without re-introducing Notion complexity?
- **Answer** — Update AGENTS.md to remove stale registry entry, add filesystem-SSOT clarity, and create a CI gate for rule validation. Do NOT recreate the Notion database.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `AGENTS.md` Notion Workspace Map | Contains stale Constitutional Rules Registry entry | 🔲 Read + Edit |
| `ops_scripts/maintenance/notion_db_consolidation_2026_05_02.py` | Confirms registry archived 2026-05-02 | ✅ Read |
| `.cursor/rules/` directory | Filesystem-SSOT for 47 rules | ✅ Verified |
| `.cursor/hooks.json` | No rule-specific hooks exist | 🔲 Verify |

---

## Wave Structure

| Wave | Phase IDs | Focus | Status |
|------|-----------|-------|--------|
| W1 | 1.1-1.3 | Documentation fix + CI gate + verification | 🟢 IN PROGRESS |

**Total: 1 wave, ~12K tokens**

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| 1.1 | AGENTS.md cleanup | `AGENTS.md` Notion Workspace Map | Must preserve other registry entries | ~2K | 🔲 |
| 1.2 | Filesystem-SSOT annotation | `AGENTS.md` + `.cursor/rules/README.md` | Clarify authority boundary | ~2K | 🔲 |
| 1.3 | Rules validation gate | `ops_scripts/ci/check_rules_filesystem_integrity.py` | Lightweight schema check | ~5K | 🔲 |
| 1.4 | Notion registration | Create Plans DB row via `API-post-page` | Requires canonical status | ~3K | 🔲 |

---

## Execution Plan

### Wave 1 — Documentation Alignment

**Phase 1.1 — Remove stale Constitutional Rules Registry entry**

Edit `AGENTS.md` Notion Workspace Map:
- Delete the "Constitutional Rules Registry" row
- Add footnote: "Rules are filesystem-SSOT at `.cursor/rules/` — no Notion mirror exists"

**Phase 1.2 — Add filesystem-SSOT clarity**

Add to AGENTS.md after Notion Workspace Map:
```
### Filesystem-SSOT Canonical Sources (No Notion Mirror)

| Content | Path | Write Trigger |
|---------|------|---------------|
| Rules | `.cursor/rules/*.md` | Filesystem only; no automated Notion sync |
| ADRs | `docs/architecture/adr/*.md` | Filesystem only since 2026-05-02 consolidation |
```

**Phase 1.3 — CI gate for rules validation**

New file: `ops_scripts/ci/check_rules_filesystem_integrity.py`

Checks:
- All `.md` files in `.cursor/rules/` have frontmatter
- No duplicate rule titles
- File names match kebab-case convention
- References in rules actually point to valid files

**Phase 1.4 — Notion registration**

Create Plans DB row:
- Slug: `fix-rules-notion-drift-c4e7b2`
- Status: "In Progress"
- AI Summary: "Closes rules-to-Notion drift. Removes stale Constitutional Rules Registry from AGENTS.md, adds filesystem-SSOT annotation, creates CI validation gate."

---

## Definition of Done

| # | Criterion | Verification | Status |
|---|---|---|---|
| DoD-1 | Constitutional Rules Registry removed from AGENTS.md | `grep -c "Constitutional Rules Registry" AGENTS.md` returns 0 | 🔲 |
| DoD-2 | Filesystem-SSOT section added to AGENTS.md | Section exists with rules + ADR rows | 🔲 |
| DoD-3 | CI gate exists and passes | `python ops_scripts/ci/check_rules_filesystem_integrity.py` exits 0 | 🔲 |
| DoD-4 | Gate registered in run_contract_gates.py | Entry in assurance_gates list | 🔲 |
| DoD-5 | Plan registered in Notion | Plans DB row exists with Status="Completed" | 🔲 |

---

## Rollback Strategy

1. Revert AGENTS.md edits: `git checkout AGENTS.md`
2. Delete CI gate file
3. Archive Notion plan row (set Status="Retired")

---

## Non-Goals

- ❌ Recreate Constitutional Rules Registry in Notion
- ❌ Add automated Notion sync for rules
- ❌ Migrate rules to any database
- ❌ Add new hooks for rule changes

---

## Verification-vs-Deferral

| Item | Verified This Plan | Deferred |
|---|---|---|
| Documentation cleanup | ✅ | — |
| CI gate creation | ✅ | — |
| Rule content validation (substantive) | — | ✅ Manual review |
| Historical rule archival | — | ✅ Out of scope |
