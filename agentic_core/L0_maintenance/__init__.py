from __future__ import annotations
'''L0 Maintenance - System maintenance and bootstrap operations.'''

# Lazy imports for backward compatibility
def __getattr__(name):
    if name == 'bases':
        from agentic_core.L0_maintenance import bases
        return bases
    elif name == 'MaintenanceBaseAgent':
        from agentic_core.L0_maintenance.bases import MaintenanceBaseAgent
        return MaintenanceBaseAgent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

