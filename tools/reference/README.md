# `tools/reference` — scope and SSOT

This tree holds **tool-adjacent reference material**: layer walkthroughs, ADG mental models, pytest notes, MCP debugging, transformer templates, and **`_archive/`** (frozen historical copies).

## Authoritative narrative reference

**Prose SSOT for overlapping reference docs:** `docs/reference/_notes/`

- Prefer `_notes` for ingestion pipeline specs, exec process maps, prompts matrices, and other reference that also appears (or should appear) under `docs/reference/_notes/`.
- Some topics exist only under `tools/reference/` (no `_notes` twin) — those remain edited here until promoted.

## Pointer-only files (do not edit here)

The following paths under `tools/reference/` are **stubs**: a few lines pointing at `_notes`. They exist so old bookmarks and relative links inside tooling do not silently fork content.

| Stub | SSOT |
|------|------|
| `agentic_process_mapping_exec.md` | `docs/reference/_notes/agentic_system_process_map_exec.md` |
| `Ingestion Pipeline/*.md` (six files) | Same relative path under `docs/reference/_notes/Ingestion Pipeline/` |

If you need to change ingestion or exec-map content, edit **only** the `_notes` file.

## `_archive/`

Historical process maps and deprecated writeups. **Not** maintained as current spine truth; use for archaeology only.

## Contextual refinement primers

Files under `Contextual Refinement/` here are **not** byte-identical to `docs/reference/_notes/Contextual_Refinement_Model_Primers/` (folder names differ; bodies have diverged). Do **not** replace them with stubs without a manual diff and explicit merge decision.

## Version naming

- `agentic_process_mapping_v30.md` at this root is a **legacy full map** (v30-era layout). The current **executive / spine-substep** summary in `_notes` is `agentic_process_mapping_v40.md`, and the **runtime exec ASCII** is `agentic_system_process_map_exec.md`. When in doubt, follow `_notes` and operating-contract rules in `.cursor/rules/`.
