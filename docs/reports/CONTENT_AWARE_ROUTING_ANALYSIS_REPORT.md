# Content-Aware Routing Analysis Report

## Evaluation of Proposed Strategies Against Existing Agent Capabilities

**Date**: January 27, 2026
**Analyst**: Cascade
**Scope**: Overlap analysis between proposed Content-Aware Routing strategies and existing Agentic-Workflow capabilities

---

## Executive Summary

The proposed Content-Aware Routing strategies represent a **significant architectural enhancement** that would extend beyond current agent capabilities. While existing agents provide foundational structural enforcement, they lack the **semantic content analysis** required for intelligent artifact routing.

**Key Finding**: The proposal introduces **novel capabilities** not currently present in the codebase, with minimal functional overlap.

---

## Current Agent Capabilities Analysis

### 1. Structure Blueprint (`structure_blueprint.py`)

**Existing Features:**

- **AST-based routing** for Python files using class/import analysis
- **Static filename matching** via patterns and prefixes
- **Root whitelist enforcement** via `ROOT_PROTECTED_FILES` (static + dynamic)
- **Depth-based validation** per sovereign root
- **App-specific routing** based on filename prefixes (`rg_`, `lic_`, etc.)

**Current Limitations:**

- **No content-aware analysis** for non-Python files
- **No semantic classification** of artifacts (reports, logs, data)
- **Static routing only** - cannot analyze file content for routing decisions
- **No "File DNA" concept** - routing based purely on structural patterns

### 2. LocationAgent & HierarchyAgent

**Existing Features:**

- **Territorial integrity enforcement** via structural validation
- **File relocation** based on structural violations
- **Depth enforcement** with smart re-alignment
- **Semantic alignment scoring** for Python files (AST-based)

**Current Limitations:**

- **Python-centric validation** - AST analysis only works for .py files
- **No artifact detection** for Markdown, JSON, CSV files
- **No content-based routing** decisions

### 3. Existing Root Enforcement

**Current Implementation:**

```python
# Static whitelist approach
ROOT_PROTECTED_FILES: frozenset[str] = {
    "pyproject.toml", "README.md", "agent_discovery_full.json",
    # ... ~20 core infrastructure files
}
```

**Limitations:**

- **Explicit enumeration only** - no semantic rules
- **No dynamic classification** - each file must be manually listed
- **No "unclaimed baggage" handling** - unknown files are just violations

---

## Proposed Strategies vs. Existing Capabilities

### Strategy 1: "Artifact Routing Table" (ART)

**Proposal**: Define signatures for non-code files based on internal structure

```python
# Example: If Markdown contains ## Findings or ## Recommendations → Route to docs/reports
```

**Overlap Analysis**: ❌ **NO OVERLAP**

- Existing agents have **no content analysis** for Markdown files
- **No semantic signature detection** capability
- **Current routing is structure-only**, not content-aware

**Gap Assessment**: **COMPLETELY NEW CAPABILITY**

### Strategy 2: "Gravity Wells" (Inverse Dependency)

**Proposal**: Folders that "own" patterns, banning them from root

```python
# Example: docs/reports becomes "Gravity Well" for *.md files containing "Assessment"
```

**Overlap Analysis**: ❌ **NO OVERLAP**

- Current agents use **whitelist approach**, not pattern ownership
- **No content pattern matching** for routing decisions
- **No inverse dependency logic** implemented

**Gap Assessment**: **COMPLETELY NEW CAPABILITY**

### Strategy 3: "Root Customs" Whitelist

**Proposal**: Invert logic - only allow explicitly whitelisted files in root

```python
# ROOT_IMMUTABLE_WHITELIST concept
```

**Overlap Analysis**: ⚠️ **PARTIAL OVERLAP**

- ✅ **Existing**: `ROOT_PROTECTED_FILES` provides whitelist functionality
- ❌ **Missing**: Inverted logic for "everything else is unclaimed baggage"
- ❌ **Missing**: Automatic routing of unclaimed files to `archives/unclassified`

**Gap Assessment**: **ENHANCEMENT OF EXISTING CAPABILITY**

---

## Detailed Capability Gap Analysis

### Content Analysis Capabilities

| Capability | Current State | Proposed State | Gap |
|------------|---------------|----------------|-----|
| Python AST Analysis | ✅ Implemented | ✅ Maintained | None |
| Markdown Content Analysis | ❌ None | ✅ Full semantic parsing | **NEW** |
| JSON Schema Detection | ❌ None | ✅ Structure-based routing | **NEW** |
| CSV Data Classification | ❌ None | ✅ Content pattern matching | **NEW** |
| File DNA Signatures | ❌ None | ✅ Multi-format signatures | **NEW** |

### Routing Intelligence

| Feature | Current Implementation | Proposed Enhancement | Overlap |
|---------|----------------------|---------------------|---------|
| Filename-based routing | ✅ Pattern matching | ✅ Enhanced | Partial |
| Content-based routing | ❌ None | ✅ Semantic analysis | **NEW** |
| Root whitelist | ✅ Static list | ✅ Inverted logic | Enhancement |
| Automatic classification | ❌ Manual only | ✅ AI-assisted | **NEW** |

---

## Implementation Recommendations

### 1. **Strategy 3 (Root Customs) - Immediate Implementation**

**Rationale**: Builds on existing `ROOT_PROTECTED_FILES` infrastructure
**Effort**: Low - primarily logic inversion
**Impact**: High - immediate "Clean Root" enforcement

### 2. **Strategy 1 (Artifact Routing) - Medium-term Implementation**

**Rationale**: Addresses the biggest gap (non-Python file handling)
**Effort**: Medium - requires content parsing infrastructure
**Impact**: Very High - enables intelligent artifact management

### 3. **Strategy 2 (Gravity Wells) - Long-term Implementation**

**Rationale**: Most complex but powerful pattern ownership system
**Effort**: High - requires new pattern matching engine
**Impact**: High - advanced territorial enforcement

---

## Technical Implementation Path

### Phase 1: Root Customs Implementation

```python
# Extend existing ROOT_PROTECTED_FILES to inverted logic
ROOT_IMMUTABLE_WHITELIST = frozenset({
    "pyproject.toml", "README.md", ".gitignore",
    # ... existing core files
})

def is_unclaimed_baggage(file_path: Path) -> bool:
    """Check if file is not on whitelist and should be routed."""
    return file_path.name not in ROOT_IMMUTABLE_WHITELIST
```

### Phase 2: Content Analysis Infrastructure

```python
# New capability - no existing overlap
class ContentAnalyzer:
    def analyze_markdown(self, file_path: Path) -> dict:
        """Parse markdown for semantic signatures."""

    def analyze_json(self, file_path: Path) -> dict:
        """Parse JSON for structure patterns."""

    def classify_artifact(self, file_path: Path) -> str:
        """Return target location based on content."""
```

### Phase 3: Artifact Routing Table

```python
# New capability - extends existing routing logic
ARTIFACT_ROUTING_TABLE = {
    "markdown_report": {
        "signatures": ["## Findings", "## Recommendations", "## Assessment"],
        "target": "docs/reports",
        "extensions": [".md"]
    },
    "data_export": {
        "signatures": [{"type": "array", "columns": ["timestamp", "value"]}],
        "target": "data/processed",
        "extensions": [".json", ".csv"]
    }
}
```

---

## Conclusion

The proposed Content-Aware Routing strategies represent a **significant evolution** beyond current agent capabilities:

1. **Minimal Overlap**: Only Strategy 3 has partial overlap with existing whitelist functionality
2. **Major Gaps**: Content analysis, semantic classification, and intelligent routing are entirely new capabilities
3. **Strong Value Proposition**: Addresses the current weakness in non-Python file management
4. **Implementation Feasibility**: Strategies can be implemented incrementally with existing agent architecture

**Recommendation**: Proceed with implementation as proposed, starting with Strategy 3 (Root Customs) as the foundation, then adding content analysis capabilities for Strategies 1 and 2.

---

## Next Steps

1. **Implement Strategy 3** - Invert existing whitelist logic
2. **Develop Content Analysis Infrastructure** - New capability for parsing non-Python files
3. **Create Artifact Routing Table** - Semantic signature detection system
4. **Integrate with Existing Agents** - Extend LocationAgent/HierarchyAgent capabilities
5. **Test and Validate** - Ensure compatibility with existing structural enforcement

The proposed changes would significantly enhance the repository's "Clean Root" policy without disrupting existing structural enforcement capabilities.
