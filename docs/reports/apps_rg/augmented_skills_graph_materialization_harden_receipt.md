# Augmented skills graph materialization harden receipt

**STATUS:** PASS

**SQLite:** [augmented_skills_graph.sqlite](C:/Git/Agentic-Workflow-FRESH/artifacts/apps_rg/fact_inventory/augmented_skills_graph.sqlite)

## COUNTS_BEFORE_AFTER
- JSON before: `{'nodes': 236, 'edges': 1400, 'pillars': 29, 'skills': 162, 'active_skills': 106, 'draft_skills': 56, 'phase_bridges': 11, 'confidence_grade': {'HIGH': 27, 'LOW': 28, 'BLOCKED': 29, 'MEDIUM': 78}}`
- JSON after: `{'nodes': 236, 'edges': 1400, 'pillars': 29, 'skills': 162, 'active_skills': 106, 'draft_skills': 56, 'phase_bridges': 11, 'confidence_grade': {'HIGH': 27, 'LOW': 28, 'BLOCKED': 29, 'MEDIUM': 78}}`
- SQLite after: `{'nodes': 498, 'edges': 1400, 'pillars': 53, 'skills': 162, 'active_skills': 106, 'draft_skills': 56, 'phase_bridges': 11}`

## SQL validation
- PLAN_DEFECT_FIXED: confidence_grade separate from support_level
- status: `PASS`
- issues: `[]`
- HIGH skills: `27`
- executive_summary allowed: `27`

Machine-readable: [augmented_skills_graph_materialization_harden_receipt.json](docs/reports/apps_rg/augmented_skills_graph_materialization_harden_receipt.json).
