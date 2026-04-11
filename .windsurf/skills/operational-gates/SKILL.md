---
name: operational-gates
description: Consolidated operational gates including rollback checkpoints and MCP tool validation. Replaces rollback-gate and mcp-tool-verify. Enforces explicit rollback checkpoints before multi-file phases and validates MCP tool parameters to prevent hallucinated usage.
metadata:
  enforcement_layer: pre-commit
  enforcement_timing: before_work
  enforcement_type: structural
---

# Operational Gates Skill (Consolidated)

Consolidated skill that merges `rollback-gate` and `mcp-tool-verify` into unified operational gate enforcement.

## Files

- **`rollback_checkpoint_protocol.md`** — Explicit rollback checkpoint creation before multi-file phases with validation and recovery procedures
- **`mcp_tool_validation_checklist.md`** — MCP tool parameter verification against documentation to prevent hallucinated API usage
- **`phase_gate_validation.md`** — Pre-phase gate validation to ensure all checkpoints and tool validations pass
- **`recovery_procedures.md`** — Step-by-step recovery when gates fail or checkpoints are invalid
- **`gate_evidence_template.md`** — Evidence format for documenting gate validation and recovery actions

## When to use

- Before starting any phase touching more than 3 files
- Before any refactor that spans multiple modules
- After phase execution when validation fails
- When using any MCP tool with parameters not previously validated
- Before committing multi-file changes
- When recovering from failed operations or gate violations

## Rollback Checkpoint Protocol

### Checkpoint Creation (MANDATORY before multi-file phases)

**Before the first file edit in any phase touching >3 files:**

1. **Create checkpoint**: Capture current git state and file contents
2. **Validate checkpoint**: Verify checkpoint is complete and accessible
3. **Document scope**: List exact files to be modified with justification
4. **Set recovery point**: Establish clean rollback point
5. **Write to evidence**: Document checkpoint in `## ROLLBACK_CHECKPOINT` section

**Format required**:
```
## ROLLBACK_CHECKPOINT
**Checkpoint ID**: <unique identifier>
**Files to modify**: N
**Scope justification**: <reason for multi-file operation>
**Baseline commit**: <git commit hash>
**Checkpoint created**: <timestamp>
**Recovery commands**: <exact commands to restore>
```

### Checkpoint Validation

Every checkpoint MUST include:
- **Git state**: Clean working directory with no uncommitted changes
- **File backups**: Complete content of all files to be modified
- **Recovery script**: Exact commands to restore state
- **Validation test**: Command to verify checkpoint integrity

### Rollback Execution

**When rollback is required:**
1. **STOP all operations** — do not continue with any edits
2. **Execute recovery commands** from checkpoint
3. **Verify restoration** — confirm all files restored to baseline
4. **Document rollback** — record in evidence with success/failure status
5. **Analyze failure** — determine why original phase failed

## MCP Tool Validation Protocol

### Pre-Call Validation (MANDATORY for all MCP tool usage)

**Before any MCP tool call:**

1. **Verify tool exists** — Check tool name against MCP server documentation
2. **Validate parameters** — Ensure all parameters match documented schema
3. **Check parameter types** — Verify parameter types and constraints
4. **Test tool availability** — Confirm tool is accessible and responding
5. **Document validation** — Record validation results in evidence

### Parameter Validation Checklist

**For each MCP tool call:**
- [ ] Tool name exists in MCP server documentation
- [ ] All required parameters are provided
- [ ] Parameter types match schema (string, int, bool, array, object)
- [ ] Optional parameters have correct defaults
- [ ] Array parameters have correct item types
- [ ] Object parameters have correct structure
- [ ] No undocumented parameters are included
- [ ] Parameter values are within allowed ranges/constraints

### Common MCP Tool Validation Patterns

#### File-based MCP Tools
```python
# ❌ FORBIDDEN: Hallucinated parameter (server: filesystem — tool: write_file)
write_file(path="some/path", content="data", extra_param="not_real")

# ✅ CORRECT: Only documented parameters
write_file(path="some/path", content="data")
```

#### Search MCP Tools
```python
# ❌ FORBIDDEN: Wrong parameter type
find_by_name(SearchDirectory="path", Pattern="*.py")  # SearchDirectory should be path

# ✅ CORRECT: Proper parameter names and types
find_by_name(SearchDirectory="path", Pattern="*.py")
```

#### MCP Server Tools
```python
# ❌ FORBIDDEN: Undocumented tool parameter
adg_node(node_id="123", include_extra_data=True)

# ✅ CORRECT: Only documented parameters
adg_node(node_id="123")
```

## Phase Gate Validation

### Pre-Phase Gate Checklist

**Before any multi-file phase:**

1. **Rollback checkpoint created and validated**
2. **All MCP tools validated for planned usage**
3. **Dependency graph analysis completed**
4. **Scope declared and justified**
5. **Test requirements identified**
6. **Environmental contracts verified (if needed)**

### Gate Failure Recovery

**If any gate fails:**
1. **STOP phase execution** immediately
2. **Execute rollback** to last valid checkpoint
3. **Document failure** in evidence with specific gate that failed
4. **Analyze root cause** of gate failure
5. **Plan recovery** before retrying phase

## Evidence Requirements

### Rollback Evidence
```
## ROLLBACK_CHECKPOINT
**Checkpoint ID**: CHK-20260326-001
**Files to modify**: 5
**Scope justification**: Cross-layer refactor affecting L2-L4
**Baseline commit**: a1b2c3d4
**Checkpoint created**: 2026-03-26T10:30:00Z
**Recovery commands**: git checkout --force <baseline>; restore files from backup
```

### MCP Tool Validation Evidence
```
## MCP_TOOL_VALIDATION
**Tool**: write_file (server: filesystem)
**Parameters validated**: path (string), content (string)
**Validation result**: ✅ PASS
**Documentation source**: MCP filesystem server v1.0
**Test call**: write_file(path="test.txt", content="test") - SUCCESS
```

### Gate Failure Evidence
```
## GATE_FAILURE
**Failed gate**: Rollback checkpoint validation
**Error**: Checkpoint backup incomplete for file X
**Recovery executed**: ✅ SUCCESS
**Root cause**: Disk space insufficient during backup
**Prevention**: Added disk space check to checkpoint protocol
```

## Constitutional Requirements Enforced

- **§9.1:** Repair gates must pass before any edit
- **§5.4:** CI integrity gates enforcement
- **§2.6:** ADG accelerator tools validation
- **§3.1:** Evidence contract compliance

## Enforcement Scripts

| Requirement | Enforcement Script(s) |
|-------------|---------------------|
| Rollback checkpoints | Custom checkpoint validation script |
| MCP tool validation | MCP parameter verification script |
| Phase gate validation | Multi-file phase gate checker |
| Recovery procedures | Rollback and recovery automation |

**Single entrypoint:** `python ops_scripts/ci/run_contract_gates.py`

## Common Failure Patterns

### Rollup Checkpoint Failures
- ❌ Insufficient disk space for backups
- ❌ Network drives unavailable during backup
- ❌ File permissions preventing backup creation
- ❌ Checkpoint corruption due to interrupted process

### MCP Tool Validation Failures
- ❌ Using deprecated tool names
- ❌ Parameter name typos (e.g., "SearchDirectory" vs "path")
- ❌ Wrong parameter types (string vs int vs bool)
- ❌ Missing required parameters
- ❌ Including undocumented parameters

### Phase Gate Failures
- ❌ Missing rollback checkpoint for multi-file phase
- ❌ Incomplete MCP tool validation
- ❌ Scope not justified by dependency graph
- ❌ Test requirements not identified

## Recovery Procedures

### Automatic Recovery
1. **Detect failure** during gate validation
2. **Execute rollback** to last valid checkpoint
3. **Verify restoration** of all files and state
4. **Log recovery** with success/failure status
5. **Notify user** of recovery completion

### Manual Recovery
1. **Identify failure point** from evidence logs
2. **Execute manual rollback** commands
3. **Validate restoration** manually
4. **Document manual recovery** in evidence
5. **Plan retry** with corrected approach

## Forbidden Patterns

- ❌ Multi-file phases without rollback checkpoints
- ❌ MCP tool usage without parameter validation
- ❌ Proceeding when gates fail
- ❌ Using undocumented MCP tool parameters
- ❌ Skipping checkpoint validation
- ❌ Ignoring gate failure evidence
- ❌ Manual recovery without documentation
- ❌ Retry without addressing root cause
