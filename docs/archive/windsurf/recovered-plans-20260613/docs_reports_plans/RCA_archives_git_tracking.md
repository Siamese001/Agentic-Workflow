# RCA: archives/ Directory Tracking in Git

## Executive Summary
The `archives/` directory is tracked in Git due to a **deliberate architectural decision** made during the repository's "Canon 2025" reorganization. This was not an accident but a conscious governance choice to preserve historical artifacts and semantic cache data.

## Root Cause Analysis

### Primary Commits
- **Commit `61fbf0162`**: "chore: immortalize data/ and archives/ — Canon 2025"
- **Commit `6a892cda3`**: "chore: immortalize data/ and archives/ — Canon 2025" (duplicate entry)

### Key Findings

#### 1. **Intentional "Immortalization" Policy**
- The commits explicitly state "immortalize data/ and archives/" in the message
- This was part of a larger "Canon 2025" repository reorganization effort
- Both `data/` and `archives/` were deliberately preserved as version-controlled assets

#### 2. **Content Analysis**
The `archives/` directory contains:
- **Deprecated agents** (16 files in `archives/deprecated/`)
- **Semantic cache data** (hundreds of cached artifacts in `archives/semantic_cache/`)
- **Historical artifacts** used for reference and regression testing

#### 3. **GitIgnore Status**
- `archives/` is **NOT** listed in `.gitignore`
- Only `.healing_backups/` (the newer backup location) is ignored
- This confirms intentional tracking vs accidental oversight

#### 4. **Repository Governance Context**
Based on commit history and repository structure:
- The repository follows strict architectural governance
- "Canon 2025" represents a major structural milestone
- Decisions to "immortalize" directories are deliberate governance actions

## Architectural Rationale

### Why archives/ is Tracked
1. **Historical Reference**: Deprecated code serves as reference for understanding architectural evolution
2. **Regression Testing**: Semantic cache artifacts provide reproducible test data
3. **Knowledge Preservation**: Maintains provenance of architectural decisions
4. **Compliance**: Some archived artifacts may have compliance or audit requirements

### Alternative Considerations
The repository could have used:
- `.healing_backups/` (current preferred backup location)
- Git LFS for large binary assets
- External artifact storage

## Recommendations

### Current Status: **INTENTIONAL DESIGN**
The `archives/` directory tracking is **working as intended** based on the "Canon 2025" governance decisions.

### Options Going Forward
1. **Maintain Status Quo**: Keep `archives/` tracked (recommended if governance requirements exist)
2. **Migrate to .healing_backups/**: Move content to the preferred backup location
3. **Selective Tracking**: Keep only essential artifacts, migrate large cache data

### Governance Action Required
Any change to this policy should:
- Reference the original "Canon 2025" decision
- Consider impact on regression testing and compliance
- Follow the repository's established change management process

## Conclusion
The `archives/` directory is tracked in Git due to a **deliberate governance decision** made during the "Canon 2025" reorganization. This represents an intentional architectural choice rather than an oversight or error.

**Evidence**: Commit messages explicitly state "immortalize data/ and archives/" with 6,803 files and 1M+ insertions, indicating a large-scale deliberate action.

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

