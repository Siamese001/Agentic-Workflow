# SVP Engineering Reviewer Hub

Status: **Active navigation hub**.

This directory used to hold a narrow "System Value Proposition" packet for the
retrieval subsystem. The current GitHub-facing SVP Engineering story is broader:
Agentic Workflow is a deterministic AI control plane for governed enterprise
agents.

Use this page as a reviewer path for CTO, SVP Engineering, platform leadership,
and hiring audiences.

---

## Start Here

| Audience | Read first | Why |
|---|---|---|
| Hiring manager / recruiter | [`../RECRUITER_GUIDE.md`](../RECRUITER_GUIDE.md) | Plain-English role fit and leadership signal |
| CTO / SVP Engineering | [`../EXECUTIVE_OVERVIEW.md`](../EXECUTIVE_OVERVIEW.md) | Bottom-line thesis and platform-leadership narrative |
| Engineering reviewer | [`../RUNTIME_CONTROL_PLANE.md`](../RUNTIME_CONTROL_PLANE.md) | Technical model for routing, context, execution, exit, write control, replay, and learning |
| Governance reviewer | [`../SVP_ENGINEERING_GOVERNANCE_README.md`](../SVP_ENGINEERING_GOVERNANCE_README.md) | Codex-primary governance, ADG CI, and runtime proof model |
| Deep technical reviewer | [`../architecture/REVIEWER_GUIDE.md`](../architecture/REVIEWER_GUIDE.md) | Proof commands and inspection path |

---

## What This Repository Demonstrates

- **Platform strategy:** the agent is not the product; the governed runtime
  around the agent is the product.
- **System design:** route authority, verified context, bounded execution,
  runtime gates, controlled writes, replay, and shadow learning are separated
  into explicit responsibilities.
- **Governance maturity:** Codex-primary execution discipline, commit-time
  gates, ADG CI, and runtime proof are distinct evidence layers.
- **Operating judgment:** the repo is built to keep AI-assisted development fast
  without turning architecture into a pile of local exceptions.
- **Reviewer proof:** architecture claims are paired with commands and files a
  reviewer can inspect.

---

## Proof Commands

Run these from the repository root:

```bash
python scripts/governance/verify_codex_primary.py
python scripts/governance/verify_codex_enforcement_home.py --json
python ops_scripts/ci/run_architecture_proof.py
```

For the full README and reviewer path, start at [`../../README.md`](../../README.md).

---

## Historical Retrieval SVP Packet

The following files are retained as historical retrieval-system notes. They are
not the current source of truth for repository-wide SVP Engineering positioning
and should not be treated as current ROI, roadmap, or support commitments:

- [`Retrieval_System_SVP.md`](./Retrieval_System_SVP.md)
- [`Technical_Implementation_Guide.md`](./Technical_Implementation_Guide.md)
- [`demo_script.py`](./demo_script.py)

When updating public GitHub-facing positioning, prefer the active documents
listed in [Start Here](#start-here).

---

Last updated: June 2026.
