# File Classification Analysis Plan

Execute comprehensive file classification analysis using FileClassificationAgent on all SSOT-approved folders to generate detailed renaming proposals with import updates and agent name improvements.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Analysis Steps

1. **Extract SSOT Folder Structure**
   - Parse `SOVEREIGN_TERRITORIES` from structure_blueprint.py
   - Identify all approved folders (agentic_core, apps_rg, apps_lic, apps_shared, tests, ops_scripts, etc.)
   - Map depth-2 and depth-3 subfolders within agentic_core

2. **Run FileClassificationAgent Analysis**
   - Initialize agent with dry_run=True to capture proposals without execution
   - Execute on all SSOT-approved folders
   - Capture violation statistics and proposed renamings by file type (AGENT, CLASS, MIXIN, etc.)

3. **Generate Detailed Renaming Report**
   - For each proposed renaming, calculate:
     - Source and destination file paths
     - Import statement changes required across codebase
     - Test file updates needed
     - Potential collision conflicts
   - Create diff previews for each affected file

4. **Agent Name Signal Analysis**
   - Identify low-signal agent names (generic, unclear purpose)
   - Review agent classes and their actual functionality
   - Propose high-signal alternatives that clearly communicate purpose
   - Group by architectural layer (L0-L6, Apps)

5. **Create Implementation Package**
   - Detailed file-by-file renaming matrix
   - Import update scripts for each renaming
   - Test migration plans
   - Risk assessment and rollback procedures

## Expected Deliverables

- JSON report with all proposed changes
- Markdown summary with implementation priorities
- File diff previews for major changes
- Test case updates for each renamed agent
- Agent name improvement proposals with rationale

## Key Focus Areas

- Base agents in `agentic_core/base_agents/` (critical inheritance hierarchy)
- L5 safety validators and guardrails (security-critical)
- L3 orchestration engines (workflow coordination)
- App-specific engines (apps_rg, apps_lic)
- Test file naming consistency

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

