# Notion MCP Row Templates

> Use `database_id` (column 3 of AGENTS.md Notion Workspace Map) for writes.
> Data source IDs (column 2) are read-only — they return 404 on `API-post-page`.
> Call: `notion.API-post-page` with `parent: {type: "database_id", database_id: "<id>"}` and `properties: {...}`.
> For updates: `notion.API-patch-page` with `page_id` + modified `properties`.

---

## §1. ADR Registry (new ADR)

**Database ID**: `6ed25e12-bd92-4352-ac7a-3a971311f024`
**Trigger**: New file matching `docs/architecture/adr/ADR-*.md`

```json
{
  "parent": {"type": "database_id", "database_id": "6ed25e12-bd92-4352-ac7a-3a971311f024"},
  "properties": {
    "Name": {"title": [{"text": {"content": "ADR-<NNN>: <short-title>"}}]},
    "ADR ID": {"rich_text": [{"text": {"content": "ADR-<NNN>"}}]},
    "Status": {"select": {"name": "<Proposed|Accepted|Superseded|Deprecated>"}},
    "Impact Layers": {"multi_select": [{"name": "L0"}, {"name": "L3"}]},
    "Summary": {"rich_text": [{"text": {"content": "<one-paragraph summary>"}}]},
    "Filename": {"rich_text": [{"text": {"content": "docs/architecture/adr/ADR-<NNN>-<slug>.md"}}]},
    "Decision Date": {"date": {"start": "<YYYY-MM-DD>"}}
  }
}
```

**Note**: Verify exact property names against the live schema via `API-retrieve-a-data-source` on `e59d7640-dc09-48f9-8bdc-b0c94bf98c2a` before first use if unsure. If a property is missing in the actual schema, drop it from the POST body — Notion 400s on unknown properties.

---

## §2. MCP Registry (config or gate change)

**Database ID**: `59693bbc-71b1-4c63-bc9f-b31eb8b08a0e`
**Trigger**: Modified `.windsurf/mcp_config.json` or gate behavior in `.windsurf/scripts/*_gate.py`

### New server row
```json
{
  "parent": {"type": "database_id", "database_id": "59693bbc-71b1-4c63-bc9f-b31eb8b08a0e"},
  "properties": {
    "Server Name": {"title": [{"text": {"content": "<server-id-from-mcp_config>"}}]},
    "Status": {"select": {"name": "Active"}},
    "Transport": {"select": {"name": "<command|serverUrl|url>"}},
    "Capability Scope": {"rich_text": [{"text": {"content": "<what this MCP is authoritative for>"}}]},
    "Authority": {"rich_text": [{"text": {"content": "<one SSOT capability>"}}]},
    "Last Validated": {"date": {"start": "<YYYY-MM-DD>"}},
    "Notes": {"rich_text": [{"text": {"content": "<config notes / behavior>"}}]},
    "Linked ADR": {"rich_text": [{"text": {"content": "ADR-<NNN>"}}]}
  }
}
```

### Patch existing row (find via query then patch)
```json
{
  "page_id": "<existing-page-id>",
  "properties": {
    "Notes": {"rich_text": [{"text": {"content": "<YYYY-MM-DD> (context): <change-description> | <prior-notes-preserved>"}}]},
    "Last Validated": {"date": {"start": "<YYYY-MM-DD>"}}
  }
}
```

---

## §3. HITL Decision Ledger (resolved scored question)

**Database ID**: `18bb9145-1320-4191-8b14-6c309776bcf5`
**Trigger**: Any scored `ask_user_question` reaches user selection

```json
{
  "parent": {"type": "database_id", "database_id": "18bb9145-1320-4191-8b14-6c309776bcf5"},
  "properties": {
    "Name": {"title": [{"text": {"content": "<YYYY-MM-DD>: <decision-type>: <short-title>"}}]},
    "Decision Type": {"select": {"name": "<architecture_choice|refactor_scope|anti_pattern|deletion_strategy|dependency_addition|test_strategy|error_handling>"}},
    "Selected Option": {"rich_text": [{"text": {"content": "<chosen-option-label>"}}]},
    "Rationale": {"rich_text": [{"text": {"content": "<why-this-option-won>"}}]},
    "Repo Area": {"rich_text": [{"text": {"content": "<most-specific-path>"}}]},
    "Confidence Score": {"number": 0.85},
    "Date": {"date": {"start": "<YYYY-MM-DD>"}}
  }
}
```

---

## §4. Backlog Items (plan status update)

**Database ID**: `aa8d2507-101e-4384-81d9-60ea3fe33876` (renamed 2026-04-23 from `Wave/Phase Convergence`)
**Trigger**: Created or status-changed `.windsurf/plans/<name>-<6hex>.md`

Title property is **`Phase Title`** (not `Name`). Status select options: `Todo | In Progress | Done | Blocked | Descoped | Complete`.

**Typed fields** (live as of 2026-04-23 W6): `P-Band`, `Impact Score`, `Fan-In`, `Coverage Gap %`, `Layer`, `Surface`, `Last Scored`, `Plan` (relation → Plans DB).

ALWAYS populate the typed fields when writing a row. The legacy `Priority` number property was **removed** in W6 — writing to it will 400.

```json
{
  "parent": {"type": "database_id", "database_id": "aa8d2507-101e-4384-81d9-60ea3fe33876"},
  "properties": {
    "Phase Title": {"title": [{"text": {"content": "[P<band>] W<N> P<M> — <phase-name>"}}]},
    "Plan File": {"rich_text": [{"text": {"content": "<name>-<6hex>.md"}}]},
    "Plan": {"relation": [{"id": "<plans-page-id-for-this-slug>"}]},
    "Wave ID": {"rich_text": [{"text": {"content": "W<N>"}}]},
    "Phase ID": {"rich_text": [{"text": {"content": "P<M>"}}]},
    "Status": {"select": {"name": "<Todo|In Progress|Done|Blocked|Descoped|Complete>"}},
    "P-Band": {"select": {"name": "<P0|P1|P2|P3|P4|P5|UNSCORED>"}},
    "Impact Score": {"number": 220.87},
    "Fan-In": {"number": 4},
    "Coverage Gap %": {"number": 1.0},
    "Layer": {"select": {"name": "<L0|L1|L2|L3|L4|L5|L6|L_APP|L_OPS|L_TOOLS|L_SHARED>"}},
    "Surface": {"select": {"name": "<Security|Write|Execution|State|Observability|None>"}},
    "Last Scored": {"date": {"start": "<YYYY-MM-DD>"}},
    "Blocking Items": {"rich_text": [{"text": {"content": "<free-text describing blocker; NO scalar data>"}}]},
    "Blocking ADR": {"rich_text": [{"text": {"content": "ADR-<NNN>"}}]},
    "Est Tokens": {"number": 50000},
    "Actual Tokens": {"number": null},
    "Last Updated": {"date": {"start": "<YYYY-MM-DD>"}}
  }
}
```

**Scorer SSOT**: `tools/priority/deferred_scope_scorer.py` produces `P-Band` and `Impact Score` from `(Layer, Fan-In, Surface, Coverage Gap %)`. Do not hand-assign bands — call the scorer.

**Related Plans DB**: `6aba34d9-4d0b-4f4c-b956-b2bdea541ca9` (data_source `ac53d31b-3068-4039-9ebe-856c12caab32`). Every new `Backlog Items` row must set its `Plan` relation to the corresponding Plans page (one per unique plan slug).

**Backlog Snapshot page**: `34b27693-f55c-81b4-93ba-efec5755a20e` — read with `API-get-block-children` for dashboards; do NOT paginate Wave/Phase for top-N queries.

**Known live schema** (verified 2026-04-23): title=`Phase Title`, file=`Plan File` (basename only), relation=`Plan`, typed bands via `P-Band`/`Impact Score`.

---

## §5. SC/AP Violation Backlog (new violation from ADG)

**Database ID**: `0a3b8072-eabd-4516-9473-3c321bb011ff`
**Trigger**: `generate_full_adg.py` produced a NEW SC or AP row not present in previous snapshot

One row per new violation:

```json
{
  "parent": {"type": "database_id", "database_id": "0a3b8072-eabd-4516-9473-3c321bb011ff"},
  "properties": {
    "Name": {"title": [{"text": {"content": "<SC-N|AP-N>: <file-basename>:<line>"}}]},
    "Category": {"select": {"name": "<SC-1|SC-2|AP-1|AP-2|...>"}},
    "Severity": {"select": {"name": "<P0|P1|P2|P3>"}},
    "File": {"rich_text": [{"text": {"content": "<relative-path-from-repo-root>"}}]},
    "Line": {"number": 42},
    "Symbol": {"rich_text": [{"text": {"content": "<function-or-class-name>"}}]},
    "Layer": {"select": {"name": "<L0|L1|L2|L3|L4|L5|L6>"}},
    "Status": {"select": {"name": "Open"}},
    "Detected In Snapshot": {"rich_text": [{"text": {"content": "adg_indexed_<timestamp>.sqlite"}}]},
    "Detected Date": {"date": {"start": "<YYYY-MM-DD>"}}
  }
}
```

---

## §6. Other Databases (lower-frequency writes)

| Database | Database ID | Trigger |
|---|---|---|
| Constitutional Rules Registry | `1c1379bc-32ca-4216-898a-3672f0316f69` | Rule added/modified in `.windsurf/rules/` |
| SVP Engineering Reviews | `6660be70-638e-4698-826a-aa7e8c17d7fd` | SVP review completed on a module |
| Anti-Pattern Burndown | `80b30bc9-6622-4288-aa4c-6fc526b6a5c5` | Burndown run or ratchet-ceiling change |

For these, retrieve the live schema via `API-retrieve-a-data-source` (read-only ID from AGENTS.md column 2) before first use, then apply the pattern from §1–§5.

---

## Checklist Before Committing the Writeback

- [ ] Using `database_id` (column 3 of AGENTS.md), NOT `data_source_id`
- [ ] Property names match the live schema (verify via retrieve-a-data-source if new)
- [ ] Title property uses the correct title-property name (varies by DB: `Name`, `Server Name`, etc.)
- [ ] Did not duplicate prose that lives on disk — row references the file, doesn't repeat it
- [ ] Added a `WRITEBACK:` receipt line per SKILL.md receipt format
