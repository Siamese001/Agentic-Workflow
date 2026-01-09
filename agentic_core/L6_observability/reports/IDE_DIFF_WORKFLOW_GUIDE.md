# IDE Diff Workflow Guide for Duplicate Agent Cleanup
**Purpose:** Step-by-step technical guide for using Windsurf/VS Code diff tools to clean up 195 duplicated agents.

---

## 📋 Quick Reference

**Generated Table:** `reports/duplicated_agents_table.md`  
**Total Duplicates:** 195 agent files  
**Action Breakdown:** 166 auto-delete, 29 manual review

---

## 🚀 Quick Start Commands

### 1. Generate Fresh Table
```bash
cd C:/Git/Agentic-Workflow
python scripts/generate_agent_table_simple.py
```

### 2. View Table
```bash
code reports/duplicated_agents_table.md
```

### 3. Start Cleanup (DELETE actions)
```bash
# Copy commands from table's "Quick Actions" section
# Example:
git rm "agentic_core\L3_orchestration\workflow_engines\ActorCriticOrchestratorAgent.py"
```

---

## 🔍 Understanding the Duplicate Patterns

### Pattern Analysis from Table

Looking at the generated table, **all 195 duplicates show the same path for canonical and duplicate**. This indicates:

**Root Cause:** Git index corruption or file system tracking issue causing the same file to appear twice in the scan.

**Evidence:**
```
| ActorCriticOrchestratorAgent | `path\to\file.py` | `path\to\file.py` | DELETE | 2/2 |
```

Both paths are identical - this is NOT a true duplicate file, but a **phantom duplicate** in the detection tool.

---

## 🛠️ Diagnosis & Fix

### Step 1: Verify Real Duplicates

```bash
# Check Git index for duplicates
cd C:/Git/Agentic-Workflow
git ls-files | sort | uniq -d

# Check file system
Get-ChildItem -Recurse -Filter "*Agent.py" | Group-Object Name | Where-Object Count -gt 1
```

### Step 2: Fix Git Index Issues

If Git shows duplicates:
```bash
# Remove from cache and re-add
git rm --cached "path/to/duplicate.py"
git add "path/to/duplicate.py"
git commit -m "fix: remove phantom duplicate from Git index"
```

### Step 3: Re-run Detection

```bash
python scripts/generate_agent_table_simple.py
```

Expected result: 0-10 real duplicates (like HygieneGuardianAgent pattern)

---

## 📊 Expected Real Duplicates (Based on Earlier Analysis)

### Blueprint vs Production Pattern

**Example from earlier fix:**
```
✅ KEEP: agentic_core/L5_safety/agents/HygieneGuardianAgent.py
❌ DELETE: agentic_core/config/blueprint_sovereign/HygieneGuardianAgent.py
```

**How to Find:**
```bash
# List all blueprint agents
Get-ChildItem agentic_core\config\blueprint_sovereign\*Agent.py

# For each, check if production version exists
foreach ($file in Get-ChildItem agentic_core\config\blueprint_sovereign\*Agent.py) {
    $name = $file.Name
    $prod = Get-ChildItem agentic_core\L*_*\**\$name -Recurse -ErrorAction SilentlyContinue
    if ($prod) {
        Write-Host "DUPLICATE: $name"
        Write-Host "  Blueprint: $($file.FullName)"
        Write-Host "  Production: $($prod.FullName)"
    }
}
```

---

## 🎯 IDE Diff Workflow (For Real Duplicates)

### Opening Diff in Windsurf/VS Code

**Method 1: Command Line**
```bash
code --diff "path/to/canonical.py" "path/to/duplicate.py"
```

**Method 2: VS Code UI**
1. Open both files in tabs
2. Right-click first file tab → "Select for Compare"
3. Right-click second file tab → "Compare with Selected"

**Method 3: Git**
```bash
# If files are in different commits
git diff HEAD:path/to/file1.py HEAD:path/to/file2.py
```

---

## 📖 Reading the Diff

### Diff View Layout

```
┌─────────────────────────────────────────────────────────────┐
│ canonical.py (LEFT)        │ duplicate.py (RIGHT)           │
├────────────────────────────┼────────────────────────────────┤
│ class Agent:               │ class Agent:                   │
│   def heal(self):          │   # TODO: implement heal       │ ← Missing implementation
│     return self.fix()      │     pass                       │
│                            │                                │
│   def mcp_integration():   │                                │ ← Missing method
│     ...                    │                                │
└────────────────────────────┴────────────────────────────────┘
```

### Color Coding
- **Green (left):** Lines only in canonical
- **Red (right):** Lines only in duplicate
- **White:** Identical lines
- **Yellow:** Modified lines

---

## 🔧 Decision Matrix for Duplicates

### Case 1: Blueprint Template (Most Common)

**Indicators:**
- Duplicate path contains `blueprint_sovereign`
- Canonical has more methods/implementation
- Duplicate has TODOs or placeholder code

**Action:**
```bash
# Verify canonical is complete
code "path/to/canonical.py"

# Delete blueprint
git rm "path/to/blueprint_sovereign/Agent.py"
git commit -m "chore: remove blueprint template for ProductionAgent"
```

### Case 2: Location Overlap (agents/ vs validators/)

**Indicators:**
- One in `L5_safety/agents/`
- One in `L5_safety/validators/`
- Similar quality scores

**Decision Matrix:**
| Has Healing | Has MCP | Has Tests | Prefer Location |
|-------------|---------|-----------|-----------------|
| ✅ | ✅ | ✅ | `agents/` |
| ✅ | ✅ | ❌ | `agents/` |
| ❌ | ❌ | ❌ | `validators/` (if validator role) |

**Action:**
```bash
# Open diff
code --diff "agents/Agent.py" "validators/Agent.py"

# Merge unique improvements to canonical
# Then delete inferior version
git rm "path/to/inferior.py"
git commit -m "chore: consolidate Agent to canonical location"
```

### Case 3: Exact Duplicates (Same Path)

**Indicators:**
- Canonical path == Duplicate path
- Identical quality scores
- This is the phantom duplicate issue

**Action:**
```bash
# Check Git index
git ls-files | grep "Agent.py" | sort | uniq -d

# If listed twice, fix Git index
git rm --cached "path/to/file.py"
git add "path/to/file.py"
```

---

## 🎬 Step-by-Step Cleanup Process

### Phase 1: Fix Phantom Duplicates (Current Issue)

```bash
# 1. Check for Git index duplicates
git ls-files | sort | uniq -d > git_duplicates.txt

# 2. Fix each one
while IFS= read -r file; do
    echo "Fixing: $file"
    git rm --cached "$file"
    git add "$file"
done < git_duplicates.txt

# 3. Commit fix
git commit -m "fix: remove phantom duplicates from Git index"

# 4. Re-run detection
python scripts/generate_agent_table_simple.py
```

### Phase 2: Clean Real Duplicates (After Phase 1)

```bash
# 1. Review table
code reports/duplicated_agents_table.md

# 2. For each DELETE action (blueprint pattern):
code --diff "canonical_path" "duplicate_path"
# Verify canonical is better
git rm "duplicate_path"

# 3. For each REVIEW action:
code --diff "canonical_path" "duplicate_path"
# Merge improvements
# Delete inferior version

# 4. Commit in batches
git commit -m "chore: remove duplicate agents (batch 1/10)"
```

### Phase 3: Verification

```bash
# 1. Run discovery
python scripts/full_agent_discovery.py --incremental

# 2. Check agent count
# Expected: ~140-150 agents (down from 337)

# 3. Verify no regressions
python scripts/find_duplicate_agents.py
# Expected: 0 duplicate groups

# 4. Run canon validator
python canon_validator_agentic_v2_thin.py --target .
```

---

## 💡 Pro Tips

### Tip 1: Batch Processing
```bash
# Process 10 files at a time
head -10 reports/duplicated_agents_table.md | grep "git rm" | bash
git commit -m "chore: remove duplicates batch 1"
```

### Tip 2: Diff Shortcuts in VS Code
- `F7` - Next difference
- `Shift+F7` - Previous difference
- `Alt+F5` - Next merge conflict
- `Ctrl+K Ctrl+D` - Format document

### Tip 3: Verify Before Delete
```bash
# Check if file is imported elsewhere
rg "from.*HygieneGuardianAgent import" --type py
rg "import.*HygieneGuardianAgent" --type py

# If imports exist, update them first
```

### Tip 4: Create Backup Branch
```bash
git checkout -b backup/pre-duplicate-cleanup
git checkout main
git checkout -b cleanup/remove-duplicate-agents
# Do cleanup work here
```

---

## 🚨 Common Issues & Solutions

### Issue 1: "File Not Found" When Running git rm

**Cause:** Path uses wrong slash direction (Windows vs Unix)

**Solution:**
```bash
# Convert backslashes to forward slashes
git rm "agentic_core/L5_safety/agents/Agent.py"
```

### Issue 2: Diff Shows No Differences

**Cause:** Files are truly identical (phantom duplicate)

**Solution:**
```bash
# Check file hash
Get-FileHash "path/to/file1.py"
Get-FileHash "path/to/file2.py"

# If hashes match, it's a Git index issue
git ls-files | grep "file.py"
```

### Issue 3: Import Errors After Deletion

**Cause:** Other files import the deleted duplicate

**Solution:**
```bash
# Before deleting, search for imports
rg "from.*DuplicateAgent" --type py
rg "import.*DuplicateAgent" --type py

# Update imports to canonical path
# Then delete duplicate
```

---

## 📈 Expected Outcomes

### After Phantom Fix (Phase 1):
- Agent count: 337 → ~150
- Duplicate groups: 195 → ~5-10
- Git index: Clean

### After Real Duplicate Cleanup (Phase 2):
- Agent count: ~150 → ~140
- Duplicate groups: ~5-10 → 0
- Repository size: Reduced
- Discovery time: Faster

---

## 🔄 Maintenance

### Prevent Future Duplicates

**Pre-commit Hook:**
```bash
# .git/hooks/pre-commit
#!/bin/bash
python scripts/find_duplicate_agents.py --type exact | grep "Total duplicate groups: 0" || {
    echo "ERROR: Duplicate agents detected"
    exit 1
}
```

**Monthly Audit:**
```bash
# Add to calendar
python scripts/generate_agent_table_simple.py
# Review and clean any new duplicates
```

---

## 📞 Quick Help

**If stuck:**
1. Check `reports/duplicated_agents_table.md` for current state
2. Run `git status` to see what's changed
3. Use `git diff` to see modifications
4. Commit frequently in small batches
5. Keep backup branch for safety

**Commands to remember:**
```bash
# Generate table
python scripts/generate_agent_table_simple.py

# Open diff
code --diff "file1.py" "file2.py"

# Delete duplicate
git rm "path/to/duplicate.py"

# Verify
python scripts/full_agent_discovery.py --incremental
```

---

**Last Updated:** 2026-01-06  
**Tool Version:** find_duplicate_agents.py v1.0  
**Status:** Ready for Phase 1 (phantom duplicate fix)
