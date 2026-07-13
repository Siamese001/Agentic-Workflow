---
description: Scaffold or revise a repository-owned Codex skill. Use when creating a new .codex/skills workflow or materially changing an existing skill's trigger, resources, or evaluations.
---

# /skill-creator - Create or revise a Codex skill

Use this workflow to produce a narrow, testable procedural adapter. Do not encode mandatory
repository policy only in a skill; place always-on invariants in `AGENTS.md`, `.codex/rules/`,
hooks, or CI and link to the deterministic control.

## Inputs

- Skill slug in lowercase hyphen-case, no more than 64 characters.
- Concrete user intents that should trigger the skill.
- Near-miss intents that must not trigger it.
- The reusable scripts, references, or assets the workflow genuinely needs.
- The deterministic validation command and owner.

## Procedure

1. **Check for overlap.** Search `.codex/skills/*/SKILL.md` descriptions and bodies. Extend or
   consolidate an existing skill when it owns the same user intent.
2. **Choose the correct surface.** Use a skill for specialized procedure; use rules/hooks/CI for
   mandatory enforcement; use `references/` for detailed knowledge; use `assets/` for output inputs.
3. **Create the folder.** Copy `.codex/templates/skill-template.md` to
   `.codex/skills/<slug>/SKILL.md`. The frontmatter `name` must equal the folder slug.
4. **Write the description first.** Use imperative, intent-focused wording such as
   `Use this skill when ...`; state adjacent-skill boundaries without implementation trivia.
5. **Add resources only when needed.** Prefer `scripts/` for repeated deterministic operations,
   `references/` for on-demand context, and `assets/` for templates or files used in outputs.
6. **Add Codex UI metadata.** Create `agents/openai.yaml` with non-empty `display_name`,
   `short_description`, and `default_prompt` values that match `SKILL.md`.
7. **Add evaluations.** Create `evals/trigger_queries.json` with balanced train/validation positive
   and near-miss negative prompts, plus `evals/evals.json` with at least two realistic output cases.
8. **Test scripts and links.** Run bundled scripts on a success and failure path. Verify every local
   Markdown link and command resolves.
9. **Run the contract gates.** Fix failures rather than adding exceptions by default.

```bash
python ops_scripts/ci/run_skill_contract_gates.py
python -m pytest tests/unit/ops_scripts/ci/test_skill_contract.py -q
```

When `skills-ref` is installed, also run:

```bash
skills-ref validate .codex/skills/<slug>
```

## Authoring rules

- Use only Agent Skills frontmatter fields: `name`, `description`, `license`, `compatibility`,
  `metadata`, and experimental `allowed-tools`.
- Store metadata as string-to-string values. Do not add `trigger`, `deprecated`, or `redirect_to`.
- Keep `SKILL.md` below 500 lines and move variant detail into directly linked references.
- Do not create redirect stubs in the active skills tree. Update inbound links and archive the old
  activation surface in the same change.
- Do not create a per-server MCP skill when `mcp-integration` already owns the routing procedure.
- Do not hard-code a checkout path; resolve the repository root dynamically.
- Use third-person, deterministic instructions. Remove all placeholders before validation.

## Expected layout

```text
.codex/skills/<slug>/
|-- SKILL.md
|-- agents/openai.yaml
|-- evals/trigger_queries.json
|-- evals/evals.json
|-- scripts/          # optional
|-- references/       # optional
`-- assets/           # optional
```
