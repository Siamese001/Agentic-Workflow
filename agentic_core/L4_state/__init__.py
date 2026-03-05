"""L4 State Layer — Persistent state and data sovereignty only.

This layer provides persistent storage, caching, and state management.
No execution logic or agent orchestration belongs in this layer.
Only state types, storage providers, and persistence utilities are exported.
"""


# Sovereignty assertion: This layer contains NO agents with execute() methods
# Any agent classes belong in L2 (Execute) or L3 (Route) layers only
