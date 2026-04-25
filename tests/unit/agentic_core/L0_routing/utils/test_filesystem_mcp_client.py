"""Smoke tests for filesystem_mcp_client — wave 19."""

import pytest

mod = pytest.importorskip("agentic_core.L0_routing.utils.filesystem_mcp_client")


def test_module_imports_clean():
    assert mod is not None


def test_FilesystemMCPClient_class_present():
    assert hasattr(mod, "FilesystemMCPClient")
    assert isinstance(mod.FilesystemMCPClient, type)


def test_FilesystemMCPClientFactory_class_present():
    assert hasattr(mod, "FilesystemMCPClientFactory")
    assert isinstance(mod.FilesystemMCPClientFactory, type)


def test_get_filesystem_client_callable():
    assert callable(mod.get_filesystem_client)
