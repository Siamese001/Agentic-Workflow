# Memory MCP Entity Templates

> Fill each shape and paste into `memory.create_entities` (new entity) or `memory.add_observations` (existing entity).
> All four entity types below are **protected** — they survive `mem_cleanup_stale` (30-day purge).
> SSOT: `@c:/Git/Agentic-Workflow/artifacts/memory/knowledge_graph.sqlite`

---

## §1. ProceduralPattern

Use for: fix recipes, tool-usage gotchas, debugging playbooks, MCP protocol quirks.

```json
{
  "entities": [{
    "name": "ProceduralPattern:<ConciseCamelCaseName>",
    "entityType": "ProceduralPattern",
    "observations": [
      "<one-line summary of what this pattern fixes>",
      "<recall-actionable step 1: exact command/flag/path>",
      "<recall-actionable step 2>",
      "<guard against the next-session misread — what NOT to do>",
      "<discovered: <YYYY-MM-DD>, validated: <YYYY-MM-DD>>"
    ]
  }]
}
```

Relations (recommended):
```json
{
  "relations": [{
    "from": "DebugSession:<YYYY-MM-DD-Slug>",
    "relationType": "produced_pattern",
    "to": "ProceduralPattern:<ConciseCamelCaseName>"
  }]
}
```

**Good name examples** (from existing memory):
- `ProceduralPattern:PytestMCPDiscoveryServialCollection`
- `ProceduralPattern:legacy editorHookSessionIdConsistency`

---

## §2. ProjectContext

Use for: project status, current blocker, next action. One entity per tracked project/wave/initiative.

```json
{
  "entities": [{
    "name": "Project:<KebabProjectName>",
    "entityType": "ProjectContext",
    "observations": [
      "status=<active|blocked|complete>, wave=<wave-id>, phase=<phase-id>",
      "next_action: <exact-command-or-decision-needed>",
      "blocker: <what's-holding-progress OR none>",
      "plan_path: @c:/Git/Agentic-Workflow-FRESH/plans/<name>-<6hex>.md",
      "notion_row: <page_id-if-applicable>",
      "last_updated: <YYYY-MM-DD>"
    ]
  }]
}
```

**Good name examples**:
- `Project:RuntimeHITL-W5`
- `Project:QwenRoutingUnification`

Update via `add_observations` on status change; do NOT create a new entity per wave update.

---

## §3. Architectural Invariants (stored as ProceduralPattern)

Use for: rules about code topology that must not be violated. Companion to constitutional rules; stored in memory so Claude Code recalls them during analysis.

> ⚠️ **MCP constraint**: The memory MCP's `ALLOWED_ENTITY_TYPES` does NOT include `ArchitecturalInvariant`. Use `ProceduralPattern` with an `INVARIANT:` prefix in the first observation — the type-router treats it as a first-class invariant and the entity is still protected from auto-purge.

```json
{
  "entities": [{
    "name": "ProceduralPattern:<ConciseCamelCaseName>Invariant",
    "entityType": "ProceduralPattern",
    "observations": [
      "INVARIANT: <one-sentence rule in imperative>",
      "scope: <which-layers-files-patterns-this-applies-to>",
      "enforcement: <rule-file | hook-script | ci-gate-name>",
      "violation_examples: <concrete-patterns-that-break-it>",
      "canonical_pattern: <concrete-pattern-that-satisfies-it-or-cross-ref-to-another-entity>",
      "doctrine_ref: <docs/architecture/file.md OR constitutional.md §N>"
    ]
  }]
}
```

**Name examples**:
- `ProceduralPattern:QwenSingleGatewayInvariant`
- `ProceduralPattern:ADGWinsConflictsInvariant`

---

## §4. EpisodicEvent

Use for: rare one-time occurrences with long-term reference value (a historic incident, a named migration). Prefer `ProceduralPattern` when recurrence is possible.

```json
{
  "entities": [{
    "name": "EpisodicEvent:<YYYY-MM-DD-SluggedTitle>",
    "entityType": "EpisodicEvent",
    "observations": [
      "date: <YYYY-MM-DD>",
      "what_happened: <one-line factual summary>",
      "impact: <what-it-changed>",
      "linked_artifacts: [<docs/reports/rca/<file>.md>, <plans/<name>-<hex>.md>]",
      "resolved: <yes-with-pattern-X | no-open>"
    ]
  }]
}
```

---

## Checklist Before Committing the Writeback

- [ ] Name uses the convention `<Type>:<ConciseCamelCaseOrKebab>`
- [ ] entityType is one of the 4 protected types (NOT `general`)
- [ ] Each observation is recall-actionable (no diary prose)
- [ ] Paths referenced in observations are verifiable (exist on disk)
- [ ] If updating, use `add_observations` — do NOT recreate the entity
- [ ] Emitted a `WRITEBACK:` receipt line (see SKILL.md)
