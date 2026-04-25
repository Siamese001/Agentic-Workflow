"""Wave-I smoke: registry loader singleton determinism + swap."""

from agentic_core.L5_safety.identity.registry_loader import (
    get_active_registry_snapshot,
    set_active_registry_snapshot,
    clear_active_snapshot,
    build_registry_snapshot,
    AgentRegistryEntry,
)


def main() -> None:
    clear_active_snapshot()
    s1 = get_active_registry_snapshot()
    s2 = get_active_registry_snapshot()
    assert s1 is s2, "loader must memoize"
    boot_digest = s1.registry_digest

    rich = build_registry_snapshot(
        policy_version="v4.1.0",
        agents=(
            AgentRegistryEntry(
                agent_id="AgentX",
                allowed_scope_ceiling=("read",),
                allowed_inbound_handoff_scopes=(),
                owner_principal="amita",
                registered_at_tick=1,
            ),
        ),
    )
    set_active_registry_snapshot(rich)
    s3 = get_active_registry_snapshot()
    assert s3.policy_version == "v4.1.0"
    assert s3.registry_digest != boot_digest, "swap must change digest"

    clear_active_snapshot()
    s4 = get_active_registry_snapshot()
    assert s4.registry_digest == boot_digest, "clear must restore bootstrap"
    print("Wave-I smoke: OK digest=", boot_digest[:16])


if __name__ == "__main__":
    main()
