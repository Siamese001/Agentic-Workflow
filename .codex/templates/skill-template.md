---
name: <skill-slug>
description: <one-paragraph description that auto-invocation will match against. Lead with the capability and the MCP/tool it wraps. State WHEN to invoke (which user intents trigger it). State distinctions from sibling skills it could be confused with. Cite the upstream source if this skill adapts an external doc.>
metadata:
  enforcement_layer: behavioural | deterministic
  enforcement_timing: before_work | during_work | after_work
  enforcement_type: tool_routing | invariant_check | scaffold | retrieval_discipline
---

# <Skill Title>

**PREREQUISITE:** <env vars, MCP servers, or constitutional rules that must be in place. State the gate file and the actionable error the user will see if missing. Delete this section if there is no prerequisite.>

<One-paragraph plain-English summary: what this skill does, what problem it solves, and what would go wrong without it. End with the upstream reference if any: "Adapts the upstream <foo> docs (<url>) to the legacy editor MCP architecture.">

**Sibling skills:** <list 1–3 skills that overlap. State the boundary: "Use X for A, this skill for B.">

## When to Invoke

| User intent / trigger | Action |
|---|---|
| <e.g. "user asks to search the web for upstream issues"> | Run `<tool-name>` with `<param defaults>` |
| <e.g. "user provides a known URL"> | Run `<other-tool>` instead |
| <e.g. "user asks about repo internals"> | Do NOT use this skill — use `<sibling-skill>` |

## Hard Routing Rules (do not violate)

| Rule | Why |
|---|---|
| <e.g. "Use this skill ONLY for external content"> | <reason> |
| <e.g. "One MCP call per response (constitutional §25)"> | <reason> |

## Standard Procedure

1. **Identify intent** — match user prompt to the trigger table above.
2. **Check prerequisites** — env keys, MCP health, ADG snapshot, etc.
3. **Pick parameters** — default to cost-conscious params unless user requested deep mode.
4. **Invoke ONE tool** in its own response (constitutional §25 if MCP).
5. **Cite sources / capture findings** — every external fact gets a URL; durable findings go to Memory MCP.

## Forbidden Patterns

- ❌ <Anti-pattern 1 — typically routing to wrong MCP, batching MCP calls, or pre-emptive tool use>
- ❌ <Anti-pattern 2>
- ❌ <Anti-pattern 3>

## References

- Upstream documentation: <url>
- MCP server config: `.mcp.json` → `<server-id>`
- Auth gate (if any): `.codex/governance/scripts/<gate>.py`
- Intent detection: `.codex/governance/scripts/pre_prompt_classifier.py` (`_<SKILL>_SIGNALS`)
- Authority registry: `docs/guides/MCP_Registry.md` → `<server-id>`
- Sibling skill: `<sibling-name>`
- Constitutional rules: `.codex/rules/<rule>.md` §<N>
