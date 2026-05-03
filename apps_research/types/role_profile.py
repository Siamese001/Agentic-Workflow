"""Pydantic schema for apps_research --mode role_profile (plan §P2.3)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RoleSource(BaseModel):
    """A URL-cited source backing a role-profile claim."""

    url: str
    title: str = ""


class RoleProfile(BaseModel):
    """Structured role profile — what a role does, requires, and sources."""

    role: str = Field(..., description="Job title or role label")
    scope: str = Field(..., description="One-paragraph scope description")
    required_skills: list[str] = Field(default_factory=list)
    nice_to_have: list[str] = Field(default_factory=list)
    source_register: list[RoleSource] = Field(default_factory=list)
