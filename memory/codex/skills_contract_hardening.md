# Codex skill-contract hardening

Date: 2026-07-13

## Decision

Repository-owned Codex skills are procedural, on-demand adapters. Always-on policy remains in
`AGENTS.md`, `.codex/rules/`, hooks, and CI. A skill may explain how to comply with a rule, but skill
activation is not itself proof that the rule was enforced.

## Active catalog

- Remove deprecated per-server redirect skills from `.codex/skills`.
- Route configured MCP use through `mcp-integration`; keep `adg-sqlite` separate for structural graph
  analysis.
- Keep templates and planned-only capability rosters outside the active skill namespace.

## Contract gates

The skill control plane validates:

1. YAML frontmatter and Agent Skills field/type/name constraints.
2. Intent-focused descriptions and active-catalog integrity.
3. Internal resource links and optional `agents/openai.yaml` interface metadata.
4. Trigger and output-evaluation fixtures for high-risk core skills.

Canonical entrypoint: `python ops_scripts/ci/run_skill_contract_gates.py`.

## Authoring

New skills use `.codex/templates/skill-template.md`, include only reusable procedural knowledge, and
add `agents/openai.yaml` plus `evals/` when the skill is user-facing or high risk. Detailed variants
belong in one-level-deep references rather than the main `SKILL.md`.
