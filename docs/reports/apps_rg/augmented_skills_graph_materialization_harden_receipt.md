# Augmented skills graph materialization harden receipt

**STATUS:** PASS

**SQLite:** [augmented_skills_graph.sqlite](C:/Git/Agentic-Workflow-FRESH/artifacts/apps_rg/fact_inventory/augmented_skills_graph.sqlite)

## COUNTS_BEFORE_AFTER
- JSON before: `{'nodes': 236, 'edges': 1421, 'pillars': 29, 'skills': 163, 'active_skills': 125, 'draft_skills': 38, 'phase_bridges': 11, 'confidence_grade': {'HIGH': 45, 'LOW': 10, 'BLOCKED': 29, 'MEDIUM': 79}}`
- JSON after: `{'nodes': 236, 'edges': 1421, 'pillars': 29, 'skills': 163, 'active_skills': 125, 'draft_skills': 38, 'phase_bridges': 11, 'confidence_grade': {'HIGH': 45, 'LOW': 10, 'BLOCKED': 29, 'MEDIUM': 79}}`
- SQLite after: `{'nodes': 501, 'edges': 1421, 'pillars': 53, 'skills': 163, 'active_skills': 125, 'draft_skills': 38, 'phase_bridges': 11}`

## SQL validation
- PLAN_DEFECT_FIXED: confidence_grade separate from support_level
- status: `PASS`
- issues: `[]`
- HIGH skills: `45`
- executive_summary allowed: `42`

Machine-readable: [augmented_skills_graph_materialization_harden_receipt.json](docs/reports/apps_rg/augmented_skills_graph_materialization_harden_receipt.json).
