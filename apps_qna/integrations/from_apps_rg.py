"""apps_rg outputs -> ExperienceLibrary adapter.

apps_rg (resume generator) historically produces a JSON or YAML resume bank
under `apps_rg/data/` or a runtime-emitted bundle. Today's contract is loose;
this adapter accepts a YAML file in the canonical schema:

    points:
      - title: "..."
        one_liner: "..."
        technical_depth_tags: ["agentic", "governance"]
    star_bank:
      stories:
        - name: "..."
          situation: "..."
          task: "..."
          action: "..."
          result: "..."
          lesson: "..."
          tags: ["governance"]
    rca_bank:
      - name: "..."
        situation: "..."
        task: "..."
        root_cause: "..."
        action: "..."
        result: "..."
        operating_model_change: "..."

If apps_rg gains a structured emission contract later, swap this loader for
that contract; the typed return shape stays stable.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from apps_qna.types.qna_types import ExperienceLibrary


def load_experience_yaml(path: Path) -> ExperienceLibrary:
    """Load and validate an experience YAML file."""
    if not path.is_file():
        raise FileNotFoundError(f"Experience YAML not found: {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return ExperienceLibrary.model_validate(raw)


def empty_library() -> ExperienceLibrary:
    """Return an empty (but valid) ExperienceLibrary for placeholder runs."""
    return ExperienceLibrary()
