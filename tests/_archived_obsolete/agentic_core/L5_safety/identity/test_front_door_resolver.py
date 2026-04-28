"""Tests for L5_safety/identity/front_door_resolver.py."""

import os
import pytest

from agentic_core.interfaces.principal_chain_types import InvokingUserKind, PrincipalChain
from agentic_core.L5_safety.identity.front_door_resolver import (
    FRONT_DOOR_AGENT_ID_ENV_VAR,
    FRONT_DOOR_AUTOMATION_ENV_VARS,
    FRONT_DOOR_INVOKING_USER_OVERRIDE_ENV_VAR,
    FRONT_DOOR_SCOPE_TAG_ENV_VAR,
    AUTOMATION_PRINCIPAL_SENTINEL,
    DEFAULT_FRONT_DOOR_AGENT_ID,
    UNKNOWN_OPERATOR_SENTINEL,
    clear_resolver_cache,
    resolve_front_door_principal,
)


def test_is_automation_context_no_markers():
    """Test _is_automation_context returns False when no automation markers present."""
    # Ensure no automation env vars are set
    for var in FRONT_DOOR_AUTOMATION_ENV_VARS:
        os.environ.pop(var, None)
    
    from agentic_core.L5_safety.identity.front_door_resolver import _is_automation_context
    assert _is_automation_context() is False


def test_is_automation_context_with_ci_marker():
    """Test _is_automation_context returns True when CI env var is set."""
    os.environ["CI"] = "true"
    
    from agentic_core.L5_safety.identity.front_door_resolver import _is_automation_context
    assert _is_automation_context() is True
    
    os.environ.pop("CI", None)


def test_is_automation_context_with_github_actions():
    """Test _is_automation_context returns True for GitHub Actions."""
    os.environ["GITHUB_ACTIONS"] = "true"
    
    from agentic_core.L5_safety.identity.front_door_resolver import _is_automation_context
    assert _is_automation_context() is True
    
    os.environ.pop("GITHUB_ACTIONS", None)


def test_is_automation_context_false_values():
    """Test _is_automation_context returns False for falsey values."""
    for false_val in ["", "0", "false", "no", "False", "NO"]:
        os.environ["CI"] = false_val
        
        from agentic_core.L5_safety.identity.front_door_resolver import _is_automation_context
        assert _is_automation_context() is False
    
    os.environ.pop("CI", None)


def test_resolve_invoking_user_override_takes_precedence():
    """Test AGENTIC_INVOKING_USER override takes precedence over USER."""
    os.environ[FRONT_DOOR_INVOKING_USER_OVERRIDE_ENV_VAR] = "override_user@example.com"
    os.environ["USER"] = "regular_user@example.com"
    
    from agentic_core.L5_safety.identity.front_door_resolver import _resolve_invoking_user
    result = _resolve_invoking_user(is_automation=False)
    
    assert result == "override_user@example.com"
    
    os.environ.pop(FRONT_DOOR_INVOKING_USER_OVERRIDE_ENV_VAR, None)
    os.environ.pop("USER", None)


def test_resolve_invoking_user_user_posix():
    """Test resolve_invoking_user uses USER env var (POSIX)."""
    os.environ["USER"] = "posix_user@example.com"
    
    from agentic_core.L5_safety.identity.front_door_resolver import _resolve_invoking_user
    result = _resolve_invoking_user(is_automation=False)
    
    assert result == "posix_user@example.com"
    
    os.environ.pop("USER", None)


def test_resolve_invoking_user_username_windows():
    """Test resolve_invoking_user uses USERNAME env var (Windows)."""
    os.environ["USERNAME"] = "windows_user@example.com"
    
    from agentic_core.L5_safety.identity.front_door_resolver import _resolve_invoking_user
    result = _resolve_invoking_user(is_automation=False)
    
    assert result == "windows_user@example.com"
    
    os.environ.pop("USERNAME", None)


def test_resolve_invoking_user_logname_fallback():
    """Test resolve_invoking_user uses LOGNAME as fallback."""
    os.environ["LOGNAME"] = "logname_user@example.com"
    
    from agentic_core.L5_safety.identity.front_door_resolver import _resolve_invoking_user
    result = _resolve_invoking_user(is_automation=False)
    
    assert result == "logname_user@example.com"
    
    os.environ.pop("LOGNAME", None)


def test_resolve_invoking_user_automation_sentinel():
    """Test resolve_invoking_user returns automation sentinel in automation context."""
    from agentic_core.L5_safety.identity.front_door_resolver import _resolve_invoking_user
    result = _resolve_invoking_user(is_automation=True)
    
    assert result == AUTOMATION_PRINCIPAL_SENTINEL


def test_resolve_invoking_user_unknown_sentinel():
    """Test resolve_invoking_user returns unknown sentinel when no env vars."""
    from agentic_core.L5_safety.identity.front_door_resolver import _resolve_invoking_user
    result = _resolve_invoking_user(is_automation=False)
    
    assert result == UNKNOWN_OPERATOR_SENTINEL


def test_resolve_scope_tag_explicit_override():
    """Test resolve_scope_tag uses explicit override when provided."""
    os.environ[FRONT_DOOR_SCOPE_TAG_ENV_VAR] = "custom_scope"
    
    from agentic_core.L5_safety.identity.front_door_resolver import _resolve_scope_tag
    result = _resolve_scope_tag()
    
    assert result == "custom_scope"
    
    os.environ.pop(FRONT_DOOR_SCOPE_TAG_ENV_VAR, None)


def test_resolve_scope_tag_default_session_pid():
    """Test resolve_scope_tag uses session:<pid> format by default."""
    from agentic_core.L5_safety.identity.front_door_resolver import _resolve_scope_tag
    result = _resolve_scope_tag()
    
    assert result.startswith("session:")
    # Should be a hex representation of the PID
    pid_hex = result.split(":")[1]
    assert len(pid_hex) > 0
    int(pid_hex, 16)  # Verify it's valid hex


def test_resolve_agent_id_explicit_override():
    """Test resolve_agent_id uses explicit override when provided."""
    os.environ[FRONT_DOOR_AGENT_ID_ENV_VAR] = "custom_agent"
    
    from agentic_core.L5_safety.identity.front_door_resolver import _resolve_agent_id
    result = _resolve_agent_id()
    
    assert result == "custom_agent"
    
    os.environ.pop(FRONT_DOOR_AGENT_ID_ENV_VAR, None)


def test_resolve_agent_id_default():
    """Test resolve_agent_id returns default when no override."""
    from agentic_core.L5_safety.identity.front_door_resolver import _resolve_agent_id
    result = _resolve_agent_id()
    
    assert result == DEFAULT_FRONT_DOOR_AGENT_ID


def test_resolve_front_door_principal_human_context():
    """Test resolve_front_door_principal in human context."""
    # Clear cache and env vars
    clear_resolver_cache()
    for var in FRONT_DOOR_AUTOMATION_ENV_VARS:
        os.environ.pop(var, None)
    os.environ.pop(FRONT_DOOR_INVOKING_USER_OVERRIDE_ENV_VAR, None)
    os.environ.pop(FRONT_DOOR_SCOPE_TAG_ENV_VAR, None)
    os.environ.pop(FRONT_DOOR_AGENT_ID_ENV_VAR, None)
    os.environ.pop("USER", None)
    os.environ.pop("USERNAME", None)
    os.environ.pop("LOGNAME", None)
    
    chain = resolve_front_door_principal()
    
    assert chain.invoking_user == UNKNOWN_OPERATOR_SENTINEL
    assert chain.invoking_user_kind == InvokingUserKind.SYSTEM  # No USER/USERNAME = SYSTEM
    assert chain.auth_method == "env:local_operator"
    assert chain.agent_id == DEFAULT_FRONT_DOOR_AGENT_ID
    assert chain.scope_tag.startswith("session:")
    assert chain.delegation_depth == 0
    assert chain.parent_agent_id is None
    assert len(chain.handoff_history) == 0
    assert len(chain.scopes) == 0


def test_resolve_front_door_principal_human_with_user():
    """Test resolve_front_door_principal with USER env var set."""
    clear_resolver_cache()
    os.environ["USER"] = "human@example.com"
    
    chain = resolve_front_door_principal()
    
    assert chain.invoking_user == "human@example.com"
    assert chain.invoking_user_kind == InvokingUserKind.HUMAN
    assert chain.auth_method == "env:local_operator"
    
    os.environ.pop("USER", None)


def test_resolve_front_door_principal_automation_context():
    """Test resolve_front_door_principal in automation context."""
    clear_resolver_cache()
    os.environ["CI"] = "true"
    
    chain = resolve_front_door_principal()
    
    assert chain.invoking_user == AUTOMATION_PRINCIPAL_SENTINEL
    assert chain.invoking_user_kind == InvokingUserKind.AUTOMATION
    assert chain.auth_method == "env:automation"
    
    os.environ.pop("CI", None)


def test_resolve_front_door_principal_caching():
    """Test resolve_front_door_principal caches results."""
    clear_resolver_cache()
    os.environ["USER"] = "test_user@example.com"
    
    chain1 = resolve_front_door_principal()
    chain2 = resolve_front_door_principal()
    
    # Should return the same object (cached)
    assert chain1 is chain2
    
    os.environ.pop("USER", None)


def test_resolve_front_door_principal_refresh_bypasses_cache():
    """Test refresh=True bypasses cache and re-resolves."""
    clear_resolver_cache()
    os.environ["USER"] = "user1@example.com"
    
    chain1 = resolve_front_door_principal()
    assert chain1.invoking_user == "user1@example.com"
    
    os.environ["USER"] = "user2@example.com"
    
    # Without refresh, should still return cached value
    chain2 = resolve_front_door_principal(refresh=False)
    assert chain2.invoking_user == "user1@example.com"
    
    # With refresh, should pick up new value
    chain3 = resolve_front_door_principal(refresh=True)
    assert chain3.invoking_user == "user2@example.com"
    
    os.environ.pop("USER", None)


def test_clear_resolver_cache():
    """Test clear_resolver_cache resets the cache."""
    os.environ["USER"] = "test_user@example.com"
    
    chain1 = resolve_front_door_principal()
    clear_resolver_cache()
    
    chain2 = resolve_front_door_principal(refresh=False)
    
    # Should be different objects after cache clear
    assert chain1 is not chain2
    
    os.environ.pop("USER", None)


def test_resolve_front_door_principal_thread_safety():
    """Test that resolver is thread-safe (basic smoke test)."""
    import threading
    
    clear_resolver_cache()
    os.environ["USER"] = "thread_test_user@example.com"
    
    chains = []
    errors = []
    
    def resolve_and_collect():
        try:
            chain = resolve_front_door_principal()
            chains.append(chain)
        except (ValueError, RuntimeError, OSError) as e:
            errors.append(e)
    
    threads = [threading.Thread(target=resolve_and_collect) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    assert len(errors) == 0, f"Thread safety errors: {errors}"
    assert len(chains) == 5
    # All threads should get the same cached object
    assert all(c is chains[0] for c in chains)
    
    os.environ.pop("USER", None)


def test_resolve_front_door_principal_with_custom_scope():
    """Test resolve_front_door_principal respects custom scope tag."""
    clear_resolver_cache()
    os.environ[FRONT_DOOR_SCOPE_TAG_ENV_VAR] = "production"
    
    chain = resolve_front_door_principal()
    
    assert chain.scope_tag == "production"
    
    os.environ.pop(FRONT_DOOR_SCOPE_TAG_ENV_VAR, None)


def test_resolve_front_door_principal_with_custom_agent_id():
    """Test resolve_front_door_principal respects custom agent ID."""
    clear_resolver_cache()
    os.environ[FRONT_DOOR_AGENT_ID_ENV_VAR] = "gateway_agent"
    
    chain = resolve_front_door_principal()
    
    assert chain.agent_id == "gateway_agent"
    
    os.environ.pop(FRONT_DOOR_AGENT_ID_ENV_VAR, None)


def test_resolve_front_door_principal_with_user_override():
    """Test resolve_front_door_principal respects invoking user override."""
    clear_resolver_cache()
    os.environ[FRONT_DOOR_INVOKING_USER_OVERRIDE_ENV_VAR] = "admin@example.com"
    os.environ["USER"] = "regular@example.com"
    
    chain = resolve_front_door_principal()
    
    assert chain.invoking_user == "admin@example.com"
    
    os.environ.pop(FRONT_DOOR_INVOKING_USER_OVERRIDE_ENV_VAR, None)
    os.environ.pop("USER", None)


def test_resolve_front_door_principal_github_actions_context():
    """Test resolve_front_door_principal detects GitHub Actions automation."""
    clear_resolver_cache()
    os.environ["GITHUB_ACTIONS"] = "true"
    
    chain = resolve_front_door_principal()
    
    assert chain.invoking_user_kind == InvokingUserKind.AUTOMATION
    assert chain.auth_method == "env:automation"
    
    os.environ.pop("GITHUB_ACTIONS", None)


def test_resolve_front_door_principal_gitlab_ci_context():
    """Test resolve_front_door_principal detects GitLab CI automation."""
    clear_resolver_cache()
    os.environ["GITLAB_CI"] = "true"
    
    chain = resolve_front_door_principal()
    
    assert chain.invoking_user_kind == InvokingUserKind.AUTOMATION
    assert chain.auth_method == "env:automation"
    
    os.environ.pop("GITLAB_CI", None)


def test_resolve_front_door_principal_jenkins_context():
    """Test resolve_front_door_principal detects Jenkins automation."""
    clear_resolver_cache()
    os.environ["JENKINS_URL"] = "http://jenkins.example.com"
    
    chain = resolve_front_door_principal()
    
    assert chain.invoking_user_kind == InvokingUserKind.AUTOMATION
    assert chain.auth_method == "env:automation"
    
    os.environ.pop("JENKINS_URL", None)


def test_resolve_front_door_principal_circleci_context():
    """Test resolve_front_door_principal detects CircleCI automation."""
    clear_resolver_cache()
    os.environ["CIRCLECI"] = "true"
    
    chain = resolve_front_door_principal()
    
    assert chain.invoking_user_kind == InvokingUserKind.AUTOMATION
    assert chain.auth_method == "env:automation"
    
    os.environ.pop("CIRCLECI", None)


def test_resolve_front_door_principal_buildkite_context():
    """Test resolve_front_door_principal detects Buildkite automation."""
    clear_resolver_cache()
    os.environ["BUILDKITE"] = "true"
    
    chain = resolve_front_door_principal()
    
    assert chain.invoking_user_kind == InvokingUserKind.AUTOMATION
    assert chain.auth_method == "env:automation"
    
    os.environ.pop("BUILDKITE", None)


def test_resolve_front_door_principal_automation_explicit_user():
    """Test automation context with explicit user override."""
    clear_resolver_cache()
    os.environ["CI"] = "true"
    os.environ[FRONT_DOOR_INVOKING_USER_OVERRIDE_ENV_VAR] = "ci_user@example.com"
    
    chain = resolve_front_door_principal()
    
    assert chain.invoking_user == "ci_user@example.com"
    assert chain.invoking_user_kind == InvokingUserKind.AUTOMATION
    assert chain.auth_method == "env:automation"
    
    os.environ.pop("CI", None)
    os.environ.pop(FRONT_DOOR_INVOKING_USER_OVERRIDE_ENV_VAR, None)
