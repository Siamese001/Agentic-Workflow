"""Mutable run state shared across generate_full_adg phases (ADR-081)."""

from __future__ import annotations

dispatcher_exit_code: int = 0
dispatcher_results_path: str = ""
