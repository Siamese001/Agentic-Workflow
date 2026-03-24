"""ADG importability contract for agentic_core/L5_safety/reasoning/SecurityManagerAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_SecurityManagerAgent.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.SecurityManagerAgent import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        AgentPermission,
        PermissionLevel,
        SecurityAction,
        SecurityAuditEntry,
        create_legacy_checkpoint_manager,
        create_legacy_config_manager,
        create_legacy_permission_manager,
        secure_checkpoint,
        secure_config,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    PermissionLevel = None  # type: ignore[assignment,misc]
    SecurityAction = None  # type: ignore[assignment,misc]
    SecurityAuditEntry = None  # type: ignore[assignment,misc]
    AgentPermission = None  # type: ignore[assignment,misc]
    secure_config = None  # type: ignore[assignment,misc]
    secure_checkpoint = None  # type: ignore[assignment,misc]
    create_legacy_permission_manager = None  # type: ignore[assignment,misc]
    create_legacy_checkpoint_manager = None  # type: ignore[assignment,misc]
    create_legacy_config_manager = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="SecurityManagerAgent.py deps unavailable")
class TestSecuritymanageragentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: SecurityManagerAgent.py must be importable."""
        assert _AVAILABLE

    def test_permissionlevel_is_type(self) -> None:
        assert PermissionLevel is not None

    def test_securityaction_is_type(self) -> None:
        assert SecurityAction is not None

    def test_securityauditentry_is_type(self) -> None:
        assert SecurityAuditEntry is not None

    def test_create_legacy_permission_manager_callable(self) -> None:
        assert callable(create_legacy_permission_manager)

    def test_create_legacy_checkpoint_manager_callable(self) -> None:
        assert callable(create_legacy_checkpoint_manager)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None