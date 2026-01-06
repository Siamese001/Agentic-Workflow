# Blueprint Duplicate Metrics Report
**Generated:** 2026-01-06 06:42:21

## Summary
- **Blueprint files found:** 12
- **Diff output directory:** `reports/blueprint_diffs/`

## Metrics Comparison

| Agent | Canonical Lines | Dup Lines | Can Methods | Dup Methods | Can Heal | Dup Heal | Recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CodeSSOTEnforcerAgent | 305 | 316 | 9 | 10 | ✅ | ✅ | ⚠️ REVIEW - dup may have additions |
| ComplianceOrchestratorAgent | 889 | 889 | 22 | 22 | ✅ | ✅ | ✅ DELETE blueprint |
| DocstringComplianceAgent | 115 | 126 | 3 | 4 | ✅ | ✅ | ⚠️ REVIEW - dup may have additions |
| FilesystemAgent | 382 | 393 | 7 | 8 | ✅ | ✅ | ⚠️ REVIEW - dup may have additions |
| GovernanceAgent | 206 | 217 | 2 | 3 | ✅ | ✅ | ⚠️ REVIEW - dup may have additions |
| HierarchyAgent | 1232 | 1243 | 33 | 34 | ✅ | ✅ | ⚠️ REVIEW - dup may have additions |
| InferenceTypeHintAgent | 121 | 132 | 3 | 4 | ✅ | ✅ | ⚠️ REVIEW - dup may have additions |
| LocationAgent | 2083 | 2096 | 51 | 52 | ✅ | ✅ | ⚠️ REVIEW - dup may have additions |
| PascalSovereigntyEnforcerAgent | 322 | 332 | 7 | 8 | ✅ | ✅ | ⚠️ REVIEW - dup may have additions |
| RegressionOracleAgent | 618 | 618 | 18 | 18 | ✅ | ✅ | ✅ DELETE blueprint |
| TestSovereigntyAgent | 258 | 269 | 11 | 12 | ✅ | ✅ | ⚠️ REVIEW - dup may have additions |
| TypeHintEnforcementAgent | 179 | 183 | 8 | 8 | ✅ | ✅ | ⚠️ REVIEW - dup may have additions |

## Diff Files

Generated 12 diff files in `reports/blueprint_diffs/`

```bash
# Open all diffs in Windsurf
code reports/blueprint_diffs/*.patch
```

## Delete Commands (After Review)

```bash
git rm "agentic_core\config\blueprint_sovereign\CodeSSOTEnforcerAgent.py"
git rm "agentic_core\config\blueprint_sovereign\ComplianceOrchestratorAgent.py"
git rm "agentic_core\config\blueprint_sovereign\DocstringComplianceAgent.py"
git rm "agentic_core\config\blueprint_sovereign\FilesystemAgent.py"
git rm "agentic_core\config\blueprint_sovereign\GovernanceAgent.py"
git rm "agentic_core\config\blueprint_sovereign\HierarchyAgent.py"
git rm "agentic_core\config\blueprint_sovereign\InferenceTypeHintAgent.py"
git rm "agentic_core\config\blueprint_sovereign\LocationAgent.py"
git rm "agentic_core\config\blueprint_sovereign\PascalSovereigntyEnforcerAgent.py"
git rm "agentic_core\config\blueprint_sovereign\RegressionOracleAgent.py"
git rm "agentic_core\config\blueprint_sovereign\TestSovereigntyAgent.py"
git rm "agentic_core\config\blueprint_sovereign\TypeHintEnforcementAgent.py"
git commit -m "chore: remove blueprint duplicate agents (Phase 1)"
```
