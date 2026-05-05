"""
apps_repo_brief — Repo-to-Executive-Brief translation app.

Generates audience-specific executive briefs (recruiter / CTO / SVP Eng /
board / head_of_ai) from a technical repository using the canonical agentic
spine: U0 → L1 → L0 → C0 → PA → L2 → Exit → L6.

This app does NOT own:
- C0 retrieval (core responsibility)
- Prompt Assembly compilation (core responsibility)
- L2 execution / provider calls (core responsibility)
- Exit disposition (core responsibility)
- L6 learning (after-runtime only, core responsibility)
- Durable writes (UWG only)

Migration: Canonical rename of apps_exec (which implied runtime execution).
Compatibility shim retained in apps_exec until zero-hard-refs gate passes (W5).

Plan: .windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md
"""
from __future__ import annotations

APP_NAME: str = "apps_repo_brief"
APP_VERSION: str = "1.0.0"
