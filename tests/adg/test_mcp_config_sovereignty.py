"""Tests for ops_scripts/ci/check_mcp_config_sovereignty.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ops_scripts.ci.check_mcp_config_sovereignty import (
    DENOMINATOR_SENSITIVE_FILES,
    REPO_ROOT,
    SOVEREIGN_WRITE_TERRITORIES,
    validate_mcp_sovereignty,
)

pytestmark = pytest.mark.unit

REPO_ROOT_STR = str(REPO_ROOT)

_VALID_COMMENT = (
    "Filesystem MCP — allowedDirectories LOCKED to repo root only. "
    "Constitutional Rule #0: NEVER write to .windsurf/plans/ or any out-of-repo path. "
    "Sovereign write territories: docs/reports/plans/, artifacts/adg/, artifacts/memory/, "
    "ops_scripts/ci/, tools/. "
    "Read-sensitive paths (NEVER write ad-hoc): "
    "agentic_core/adg/schema.py, "
    "agentic_core/adg/extraction/static_scanner.py, "
    "agentic_core/runtime/lifecycle_trace_contract.py. "
    "Generated/gitignored paths excluded: artifacts/adg/scan_result_cache.json, "
    "artifacts/memory/knowledge_graph.sqlite."
)

_COMPLIANT_CONFIG = {
    "mcpServers": {
        "filesystem": {
            "_comment": _VALID_COMMENT,
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", REPO_ROOT_STR],
            "disabled": False,
        }
    }
}


def _write_config(tmp_path: Path, config: dict) -> Path:
    p = tmp_path / "mcp_config.json"
    p.write_text(json.dumps(config), encoding="utf-8")
    return p


# ===========================================================================
# Positive — compliant config passes
# ===========================================================================


class TestCompliantConfig:
    def test_no_violations(self, tmp_path: Path) -> None:
        p = _write_config(tmp_path, _COMPLIANT_CONFIG)
        assert validate_mcp_sovereignty(p) == []

    def test_returns_list(self, tmp_path: Path) -> None:
        p = _write_config(tmp_path, _COMPLIANT_CONFIG)
        result = validate_mcp_sovereignty(p)
        assert isinstance(result, list)

    def test_real_repo_mcp_config_passes(self) -> None:
        real = REPO_ROOT / "mcp_config.json"
        if not real.exists():
            pytest.skip("mcp_config.json not present")
        violations = validate_mcp_sovereignty(real)
        assert violations == [], f"Real mcp_config.json has violations: {violations}"


# ===========================================================================
# Rule 1: filesystem key must be present
# ===========================================================================


class TestMissingFilesystemKey:
    def test_missing_filesystem_key_reported(self, tmp_path: Path) -> None:
        cfg = {"mcpServers": {"redis": {"command": "npx", "args": []}}}
        p = _write_config(tmp_path, cfg)
        v = validate_mcp_sovereignty(p)
        assert any("MISSING_FILESYSTEM" in x for x in v)

    def test_empty_mcpServers_reported(self, tmp_path: Path) -> None:
        p = _write_config(tmp_path, {"mcpServers": {}})
        v = validate_mcp_sovereignty(p)
        assert any("MISSING_FILESYSTEM" in x for x in v)


# ===========================================================================
# Rule 2: filesystem must not be disabled
# ===========================================================================


class TestFilesystemDisabled:
    def test_disabled_true_reported(self, tmp_path: Path) -> None:
        cfg = dict(_COMPLIANT_CONFIG)
        cfg["mcpServers"] = {
            "filesystem": {**_COMPLIANT_CONFIG["mcpServers"]["filesystem"], "disabled": True}
        }
        p = _write_config(tmp_path, cfg)
        v = validate_mcp_sovereignty(p)
        assert any("FILESYSTEM_DISABLED" in x for x in v)

    def test_disabled_false_not_reported(self, tmp_path: Path) -> None:
        p = _write_config(tmp_path, _COMPLIANT_CONFIG)
        v = validate_mcp_sovereignty(p)
        assert not any("FILESYSTEM_DISABLED" in x for x in v)


# ===========================================================================
# Rule 3: filesystem args must not contain out-of-repo paths
# ===========================================================================


class TestFilesystemOutOfRepoArg:
    def test_user_path_in_args_reported(self, tmp_path: Path) -> None:
        cfg = {
            "mcpServers": {
                "filesystem": {
                    "_comment": _VALID_COMMENT,
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:\\Users\\amita\\projects"],
                    "disabled": False,
                }
            }
        }
        p = _write_config(tmp_path, cfg)
        v = validate_mcp_sovereignty(p)
        assert any("FILESYSTEM_OUT_OF_REPO_ARG" in x for x in v)

    def test_repo_root_arg_not_reported(self, tmp_path: Path) -> None:
        p = _write_config(tmp_path, _COMPLIANT_CONFIG)
        v = validate_mcp_sovereignty(p)
        assert not any("FILESYSTEM_OUT_OF_REPO_ARG" in x for x in v)


# ===========================================================================
# Rule 4: _comment must document sovereign territories + Rule #0
# ===========================================================================


class TestFilesystemComment:
    def test_missing_comment_reported(self, tmp_path: Path) -> None:
        cfg = {
            "mcpServers": {
                "filesystem": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", REPO_ROOT_STR],
                    "disabled": False,
                }
            }
        }
        p = _write_config(tmp_path, cfg)
        v = validate_mcp_sovereignty(p)
        assert any("FILESYSTEM_MISSING_COMMENT" in x for x in v)

    def test_comment_missing_rule0_reported(self, tmp_path: Path) -> None:
        cfg = {
            "mcpServers": {
                "filesystem": {
                    "_comment": "some comment without rule reference",
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", REPO_ROOT_STR],
                    "disabled": False,
                }
            }
        }
        p = _write_config(tmp_path, cfg)
        v = validate_mcp_sovereignty(p)
        assert any("FILESYSTEM_COMMENT_MISSING_RULE0" in x for x in v)

    @pytest.mark.parametrize("territory", SOVEREIGN_WRITE_TERRITORIES)
    def test_comment_missing_territory_reported(self, tmp_path: Path, territory: str) -> None:
        stripped = _VALID_COMMENT.replace(territory, "")
        cfg = {
            "mcpServers": {
                "filesystem": {
                    "_comment": stripped,
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", REPO_ROOT_STR],
                    "disabled": False,
                }
            }
        }
        p = _write_config(tmp_path, cfg)
        v = validate_mcp_sovereignty(p)
        assert any("FILESYSTEM_COMMENT_MISSING_TERRITORY" in x and territory in x for x in v)

    @pytest.mark.parametrize("sensitive", DENOMINATOR_SENSITIVE_FILES)
    def test_comment_missing_sensitive_file_reported(self, tmp_path: Path, sensitive: str) -> None:
        stripped = _VALID_COMMENT.replace(sensitive, "")
        cfg = {
            "mcpServers": {
                "filesystem": {
                    "_comment": stripped,
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", REPO_ROOT_STR],
                    "disabled": False,
                }
            }
        }
        p = _write_config(tmp_path, cfg)
        v = validate_mcp_sovereignty(p)
        assert any("FILESYSTEM_COMMENT_MISSING_SENSITIVE" in x and sensitive in x for x in v)


# ===========================================================================
# Rule 5: forbidden out-of-repo path fragments in any server
# ===========================================================================


class TestForbiddenPathFragments:
    def test_windsurf_plans_in_args_reported(self, tmp_path: Path) -> None:
        cfg = {
            "mcpServers": {
                "filesystem": {
                    "_comment": _VALID_COMMENT,
                    "command": "npx",
                    "args": [
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        REPO_ROOT_STR,
                        ".windsurf\\plans",
                    ],
                    "disabled": False,
                }
            }
        }
        p = _write_config(tmp_path, cfg)
        v = validate_mcp_sovereignty(p)
        assert any("FORBIDDEN_PATH" in x for x in v)

    def test_user_home_in_cwd_reported(self, tmp_path: Path) -> None:
        cfg = {
            "mcpServers": {
                "some_server": {
                    "command": "python",
                    "args": ["tool.py"],
                    "cwd": "C:\\Users\\amita\\projects",
                }
            }
        }
        p = _write_config(tmp_path, cfg)
        v = validate_mcp_sovereignty(p)
        assert any("FORBIDDEN_PATH" in x and "some_server" in x for x in v)

    def test_no_forbidden_path_in_compliant_config(self, tmp_path: Path) -> None:
        p = _write_config(tmp_path, _COMPLIANT_CONFIG)
        v = validate_mcp_sovereignty(p)
        assert not any("FORBIDDEN_PATH" in x for x in v)


# ===========================================================================
# Edge cases
# ===========================================================================


class TestEdgeCases:
    def test_missing_file_returns_violation(self, tmp_path: Path) -> None:
        missing = tmp_path / "nonexistent.json"
        v = validate_mcp_sovereignty(missing)
        assert any("MISSING" in x for x in v)

    def test_malformed_json_returns_violation(self, tmp_path: Path) -> None:
        p = tmp_path / "mcp_config.json"
        p.write_text("{not valid json", encoding="utf-8")
        v = validate_mcp_sovereignty(p)
        assert any("PARSE_ERROR" in x for x in v)

    def test_empty_mcpServers_missing_filesystem(self, tmp_path: Path) -> None:
        p = _write_config(tmp_path, {"mcpServers": {}})
        v = validate_mcp_sovereignty(p)
        assert len(v) >= 1

    def test_returns_empty_list_not_none(self, tmp_path: Path) -> None:
        p = _write_config(tmp_path, _COMPLIANT_CONFIG)
        result = validate_mcp_sovereignty(p)
        assert result is not None
        assert result == []

    def test_multiple_violations_all_reported(self, tmp_path: Path) -> None:
        cfg = {"mcpServers": {}}
        p = _write_config(tmp_path, cfg)
        v = validate_mcp_sovereignty(p)
        assert len(v) >= 1

    def test_violation_strings_are_nonempty(self, tmp_path: Path) -> None:
        cfg = {"mcpServers": {}}
        p = _write_config(tmp_path, cfg)
        v = validate_mcp_sovereignty(p)
        assert all(isinstance(x, str) and len(x) > 0 for x in v)

    def test_missing_mcpServers_key_entirely(self, tmp_path: Path) -> None:
        p = _write_config(tmp_path, {})
        v = validate_mcp_sovereignty(p)
        assert any("MISSING_FILESYSTEM" in x for x in v)

    def test_filesystem_entry_with_no_args_key(self, tmp_path: Path) -> None:
        cfg = {
            "mcpServers": {
                "filesystem": {
                    "_comment": _VALID_COMMENT,
                    "command": "npx",
                    "disabled": False,
                }
            }
        }
        p = _write_config(tmp_path, cfg)
        v = validate_mcp_sovereignty(p)
        assert v == []


# ===========================================================================
# Creative / adversarial — bypass attempts
# ===========================================================================


class TestAdversarialBypass:
    def test_uppercase_users_path_caught(self, tmp_path: Path) -> None:
        """Case-sensitivity bypass: C:\\USERS\\... (uppercased) must still be caught."""
        cfg = {
            "mcpServers": {
                "filesystem": {
                    "_comment": _VALID_COMMENT,
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:\\USERS\\amita\\projects"],
                    "disabled": False,
                }
            }
        }
        p = _write_config(tmp_path, cfg)
        v = validate_mcp_sovereignty(p)
        assert any("FILESYSTEM_OUT_OF_REPO_ARG" in x or "FORBIDDEN_PATH" in x for x in v)

    def test_forward_slash_users_path_caught(self, tmp_path: Path) -> None:
        """Mixed-slash bypass: C:/Users/amita/... must still be caught."""
        cfg = {
            "mcpServers": {
                "filesystem": {
                    "_comment": _VALID_COMMENT,
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:/Users/amita/projects"],
                    "disabled": False,
                }
            }
        }
        p = _write_config(tmp_path, cfg)
        v = validate_mcp_sovereignty(p)
        assert any("FILESYSTEM_OUT_OF_REPO_ARG" in x or "FORBIDDEN_PATH" in x for x in v)

    def test_windsurf_plans_forward_slash_caught(self, tmp_path: Path) -> None:
        """.windsurf/plans with forward slash must be caught."""
        cfg = {
            "mcpServers": {
                "filesystem": {
                    "_comment": _VALID_COMMENT,
                    "command": "npx",
                    "args": [
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        REPO_ROOT_STR,
                        ".windsurf/plans",
                    ],
                    "disabled": False,
                }
            }
        }
        p = _write_config(tmp_path, cfg)
        v = validate_mcp_sovereignty(p)
        assert any("FORBIDDEN_PATH" in x for x in v)

    def test_trailing_slash_on_repo_root_passes(self, tmp_path: Path) -> None:
        """Trailing slash variant of repo root should still pass (not an out-of-repo path)."""
        root_with_slash = REPO_ROOT_STR.rstrip("/\\") + "\\"
        cfg = {
            "mcpServers": {
                "filesystem": {
                    "_comment": _VALID_COMMENT,
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", root_with_slash],
                    "disabled": False,
                }
            }
        }
        p = _write_config(tmp_path, cfg)
        v = validate_mcp_sovereignty(p)
        assert not any("FILESYSTEM_OUT_OF_REPO_ARG" in x for x in v)

    def test_comment_rule0_lowercase_variant_accepted(self, tmp_path: Path) -> None:
        """'rule #0' lowercase should be accepted (gate checks case-insensitively)."""
        comment_lower = _VALID_COMMENT.replace("Constitutional Rule #0", "constitutional rule #0")
        cfg = {
            "mcpServers": {
                "filesystem": {
                    "_comment": comment_lower,
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", REPO_ROOT_STR],
                    "disabled": False,
                }
            }
        }
        p = _write_config(tmp_path, cfg)
        v = validate_mcp_sovereignty(p)
        assert not any("FILESYSTEM_COMMENT_MISSING_RULE0" in x for x in v)

    def test_subpath_of_repo_root_is_allowed(self, tmp_path: Path) -> None:
        """A subdirectory of the repo root (e.g. docs/) is within-repo — must not fire OUT_OF_REPO."""
        subpath = REPO_ROOT_STR + "\\docs"
        cfg = {
            "mcpServers": {
                "filesystem": {
                    "_comment": _VALID_COMMENT,
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", subpath],
                    "disabled": False,
                }
            }
        }
        p = _write_config(tmp_path, cfg)
        v = validate_mcp_sovereignty(p)
        assert not any("FILESYSTEM_OUT_OF_REPO_ARG" in x for x in v)

    def test_completely_different_drive_caught(self, tmp_path: Path) -> None:
        """Path on a different drive (D:\\) must be caught as out-of-repo."""
        cfg = {
            "mcpServers": {
                "filesystem": {
                    "_comment": _VALID_COMMENT,
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", "D:\\SomeOtherProject"],
                    "disabled": False,
                }
            }
        }
        p = _write_config(tmp_path, cfg)
        v = validate_mcp_sovereignty(p)
        assert any("FILESYSTEM_OUT_OF_REPO_ARG" in x for x in v)

    def test_disabled_string_true_not_caught(self, tmp_path: Path) -> None:
        """disabled='true' (string) is not the same as disabled=True (bool) — gate uses strict bool check."""
        cfg = {
            "mcpServers": {
                "filesystem": {
                    "_comment": _VALID_COMMENT,
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", REPO_ROOT_STR],
                    "disabled": "true",
                }
            }
        }
        p = _write_config(tmp_path, cfg)
        v = validate_mcp_sovereignty(p)
        assert not any("FILESYSTEM_DISABLED" in x for x in v)

    def test_sibling_server_with_forbidden_cwd_caught(self, tmp_path: Path) -> None:
        """A non-filesystem server with forbidden cwd must be caught even if filesystem is compliant."""
        cfg = {
            "mcpServers": {
                "filesystem": {
                    "_comment": _VALID_COMMENT,
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", REPO_ROOT_STR],
                    "disabled": False,
                },
                "rogue_server": {
                    "command": "python",
                    "args": ["tool.py"],
                    "cwd": "C:\\Users\\amita\\.windsurf\\plans",
                },
            }
        }
        p = _write_config(tmp_path, cfg)
        v = validate_mcp_sovereignty(p)
        assert any("FORBIDDEN_PATH" in x and "rogue_server" in x for x in v)
        assert not any("MISSING_FILESYSTEM" in x for x in v)


# ===========================================================================
# Idempotency & determinism
# ===========================================================================


class TestIdempotency:
    def test_same_file_same_result_twice(self, tmp_path: Path) -> None:
        """validate_mcp_config is deterministic — two calls return identical results."""
        p = _write_config(tmp_path, _COMPLIANT_CONFIG)
        r1 = validate_mcp_sovereignty(p)
        r2 = validate_mcp_sovereignty(p)
        assert r1 == r2

    def test_violation_list_same_result_twice(self, tmp_path: Path) -> None:
        cfg = {"mcpServers": {}}
        p = _write_config(tmp_path, cfg)
        r1 = validate_mcp_sovereignty(p)
        r2 = validate_mcp_sovereignty(p)
        assert r1 == r2

    def test_violation_codes_are_unique_per_config(self, tmp_path: Path) -> None:
        """Each violation message should contain a distinct violation code."""
        cfg = {"mcpServers": {}}
        p = _write_config(tmp_path, cfg)
        v = validate_mcp_sovereignty(p)
        codes = [x.split(":")[0] for x in v]
        assert len(codes) == len(set(codes)), f"Duplicate violation codes: {codes}"
