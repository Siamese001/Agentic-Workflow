# The Overlord Protocol: MCP Integration Guide

## Overview

The "Overlord" is Windsurf itself, equipped with 6 powerful MCPs that manage and enhance the Subatomic Agentic Architecture. This protocol defines when and how to use each MCP to oversee the Python-based agents.

## MCP-to-Agent Mapping

### 1. Sequential Thinking → Sherlock (Root Cause Analysis)

**Trigger:** When Sherlock reports a confusing error or when bugs persist across multiple validation cycles.

**Usage Pattern:**

```text
Use sequential-thinking to analyze this traceback in observability/debug/sherlock_trace.md.
Don't guess. Formulate a hypothesis, check the dependency graph, and validate the fix logic.
```

**Integration Points:**

- Read from: `observability/debug/` directory
- Output to: `observability/analysis/` directory
- Prevents: Fix loops where one fix creates two more bugs

### 2. Playwright → Red Sentinel (Visual Testing)

**Trigger:** When testing UI flows, JavaScript-heavy features, or user experience validation.

**Usage Pattern:**

```text
Use playwright to launch the dev server. Navigate to /login.
Attempt 5 hostile inputs (SQL injection, massive strings) and screenshot results.
Save screenshots to observability/snapshots/
```

**Integration Points:**
- Screenshots saved to: `observability/snapshots/` (Depth 3 compliant)
- Gives Python agents visual reference for UI issues
- Tests: Forms, navigation, error handling, responsive design

### 3. Brave Search → Truth Keeper (External Validation)

**Trigger:** When using external libraries, checking for deprecations, or validating best practices.

**Usage Pattern:**

```text
Use brave-search to check pydantic v2 migration guide.
Verify if @field_validator usage matches latest best practices.
```

**Integration Points:**
- Validates: `requirements.txt`, library versions, API patterns
- Prevents: Architecture becoming legacy on day one
- Updates: Documentation and implementation patterns

### 4. Memory → OmniContext (Architectural Wisdom)

**Trigger:** When making architectural decisions or enforcing project-specific rules.

**Usage Pattern:**

```text
Save to memory: "All sovereign domains must use pydantic for data validation."
Recall: What are our rules for file naming in agentic_core?
```

**Integration Points:**
- Stores: Architectural decisions, coding standards, project wisdom
- Replaces: Repasting rules in every prompt
- Enforces: Consistency across all code generation

### 5. Filesystem → Compliance Governor (Self-Auditing)

**Trigger:** Before creating files, when cleaning up, or enforcing directory structure.

**Usage Pattern:**

```text
Use filesystem to scan for violations of Min Depth 3 rule.
Move any root files (except whitelist) to config/orphans/
Verify new file paths before creation.
```

**Integration Points:**
- Enforces: Three Laws of Subatomic Governance
- Auto-fixes: File placement violations
- Audits: Directory structure compliance

### 6. Figma → Style Dictator (Visual Contract)

**Trigger:** When generating UI components, updating design tokens, or performing visual QA.

**Usage Pattern:**

```text
Use the Figma MCP to inspect the 'Design Tokens' page. Extract all color variables and typography styles. Generate a Python dataclass in config/ui_constants.py that enforces these values.
```

**Integration Points:**
- Design tokens extracted from: Figma Design System file
- Code generated to: `config/ui_constants.py` (Depth 3)
- Components generated to: `apps_lic/templates/components/` (Depth 4)
- Prevents: Visual drift between design and implementation

## Overlord Workflow Examples

### Debugging Complex Issues
1. Python agents fail → Sherlock logs error
2. Use sequential-thinking to analyze
3. Use brave-search to check related issues
4. Use filesystem to verify file structure
5. Generate fix with memory of past decisions

### Testing New Features
1. Use playwright for visual testing
2. Use filesystem to ensure compliance
3. Use memory to recall testing patterns
4. Use brave-search for latest practices
5. Use sequential-thinking for complex scenarios

### Architectural Changes
1. Use memory to recall existing patterns
2. Use brave-search for best practices
3. Use filesystem to plan structure
4. Use sequential-thinking for implementation
5. Use playwright to validate UI changes

### Visual Component Generation
1. Use Figma to inspect design specifications
2. Extract layout and styling from Auto-Layout
3. Generate frontend code with design tokens
4. Use filesystem to ensure proper placement
5. Validate with playwright screenshots

### Visual QA Audits
1. Use Figma to get reference design
2. Use playwright to capture live implementation
3. Compare visual elements and positioning
4. Report deviations greater than 5%
5. Update code or design as needed

## Command Templates

### Debug Mode
```text
I'm seeing [error] in [file]. Use sequential-thinking to analyze the trace in observability/debug/. Check our memory for similar issues, then propose a fix that maintains our architectural principles.
```

### Test Mode
```text
Test the [feature] using playwright. Navigate to [path], perform [actions], and verify no errors appear. Save screenshots to observability/snapshots/ with descriptive names.
```

### Audit Mode
```text
Use filesystem to audit our directory structure. List any files violating Min Depth 3 or in root (except whitelist). Move violations to config/orphans/ and report findings.
```

### Research Mode
```text
Use brave-search to investigate [library/practice]. Check for deprecations, version updates, or better alternatives. Summarize findings and suggest actions.
```

### Memory Mode
```text
Save to memory: [architectural decision]. Include context, rationale, and scope. Tag with relevant domain (e.g., validation, testing, structure).
```

### Design Token Mode
```text
Use the Figma MCP to inspect the 'Design Tokens' page. Extract all color variables and typography styles. Generate a Python dataclass in config/ui_constants.py that enforces these values.
```

### Component Generation Mode
```text
Inspect the 'UserDashboard' frame in Figma. Generate the HTML/CSS structure for this card. Ensure the CSS classes map to the variables defined in config/ui_constants.py. Save the file to apps_lic/templates/dashboard.html.
```

### Visual QA Mode
```text
Perform a Visual QA. Use Figma to get the design spec for the Login Frame. Use Playwright to screenshot the live page. Compare the padding and button colors. Report any deviations greater than 5%.
```

## Integration with Python Agents

The Overlord doesn't replace Python agents - it empowers them:

1. **Pre-Validation:** Use MCPs to prepare environment before agents run
2. **Post-Analysis:** Use MCPs to analyze agent results and outputs
3. **Exception Handling:** Use MCPs when agents encounter edge cases
4. **Enhancement:** Use MCPs to add capabilities agents don't have

## The Three Visual Workflows

### 1. The Style Dictator (Design Tokens)
**Purpose:** Maintain single source of truth for visual properties.

**Steps:**
1. Read Figma Design System file
2. Extract colors, fonts, spacing variables
3. Generate `config/ui_constants.py` with dataclasses
4. Update when Figma changes

**When to Use:**
- Before starting any UI development
- When design system updates
- To ensure consistency across components

### 2. The Pixel-Perfect Architect (Design-to-Code)
**Purpose:** Convert Figma components directly to code.

**Steps:**
1. Select component in Figma
2. Analyze Auto-Layout properties
3. Map to CSS Flexbox/Grid
4. Generate code in correct directory
5. Apply design tokens from Style Dictator

**When to Use:**
- Creating new UI components
- Implementing responsive designs
- Ensuring design fidelity

### 3. The Visual Auditor (Drift Detection)
**Purpose:** Detect differences between design and implementation.

**Steps:**
1. Get reference image from Figma
2. Screenshot live app with Playwright
3. Compare visual elements
4. Report deviations >5%
5. Flag issues for correction

**When to Use:**
- Before releases
- After major UI changes
- Regular QA cycles

## Best Practices

1. **Always verify compliance** before file operations
2. **Document decisions** in memory for future reference
3. **Use sequential thinking** for complex problems (>3 steps)
4. **Test visually** when UI changes are involved
5. **Stay current** with external library updates
6. **Sync visually** with Figma before UI changes
7. **Audit regularly** for visual drift

## Emergency Procedures

When Python agents fail completely:
1. Use filesystem to check for structural issues
2. Use memory to recall recent changes
3. Use sequential-thinking to diagnose
4. Use brave-search for known issues
5. Use playwright to verify basic functionality
6. Use Figma to check for visual deviations

---

*This protocol evolves with the system. Update when new patterns emerge.*
