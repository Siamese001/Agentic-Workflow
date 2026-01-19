"""
HealerMixin Redirect Module

This module re-exports HealerMixin from its canonical location.
The canonical location is: agentic_core.L5_safety.validators.healer_mixin

RCA: 53+ files were importing from this path but the file was missing,
causing cascading import failures across the entire agent ecosystem.

SSOT: The canonical HealerMixin lives in L5_safety/validators/healer_mixin.py
This file exists only for backwards compatibility.
"""
from agentic_core.L5_safety.validators.healer_mixin import (
    HealerMixin,
)

__all__ = ['HealerMixin']
