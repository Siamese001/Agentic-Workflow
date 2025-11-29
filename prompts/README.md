# Prompts Registry

OpenAI-aligned prompt organization system for the Agentic Workflow repository.

## Structure

- **`system/`** - Core system prompts and constitutional constraints
- **`developer/`** - Developer-facing prompts for debugging and tool usage
- **`user/`** - User interaction prompts and templates
- **`injections/`** - Contextual prompt injections and instructional prompts

## Versioning

Prompts should be versioned using semantic naming:
- `resume_planner_v1.md`
- `outreach_writer_v2.md`
- `safety_validator_v1.md`

## Metadata

Each prompt should include:
- Purpose description
- Expected inputs schema
- Expected outputs schema
- Version information
- Usage examples
