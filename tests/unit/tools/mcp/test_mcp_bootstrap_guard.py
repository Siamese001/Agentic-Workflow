from __future__ import annotations

from tools.mcp import mcp_bootstrap


def test_codex_cmd_launcher_wrapper_is_not_a_guard_target() -> None:
    cmdline = [
        r"C:\Windows\system32\cmd.EXE",
        "/c",
        "python",
        "-u",
        "-m",
        "tools.mcp.launch_adg_sqlite_mcp",
    ]

    assert mcp_bootstrap._match_cmdline_marker(
        cmdline,
        ("tools.mcp.launch_adg_sqlite_mcp",),
    )
    assert mcp_bootstrap._is_windows_launcher_wrapper("cmd.exe", cmdline) is True


def test_python_mcp_child_process_remains_a_guard_target() -> None:
    cmdline = [
        r"C:\Users\amita\AppData\Local\Programs\Python\Python312\python.exe",
        "-u",
        "-m",
        "tools.mcp.launch_adg_sqlite_mcp",
    ]

    assert mcp_bootstrap._is_windows_launcher_wrapper("python.exe", cmdline) is False
    assert (
        mcp_bootstrap._match_cmdline_marker(
            cmdline,
            ("tools.mcp.launch_adg_sqlite_mcp",),
        )
        == "tools.mcp.launch_adg_sqlite_mcp"
    )


def test_powershell_launcher_wrapper_is_not_a_guard_target() -> None:
    cmdline = [
        "pwsh.exe",
        "-NoProfile",
        "-Command",
        "python -u C:/Git/Agentic-Workflow-FRESH/tools/memory/adg_memory_server.py",
    ]

    assert mcp_bootstrap._is_windows_launcher_wrapper("pwsh.exe", cmdline) is True

