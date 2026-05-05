"""apps_repo_brief cert-path utilities.

Importing this package auto-registers the apps_repo_brief FEC producer with
the shared registry.

Plan: .windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md §P1.11
Pattern source: apps_exec/cert/__init__.py
"""
from __future__ import annotations

from apps_shared.cert.fec_producer import register_producer

from apps_repo_brief.cert.fec_producer import produce_fec

register_producer("apps_repo_brief", produce_fec)

__all__ = ["produce_fec"]
