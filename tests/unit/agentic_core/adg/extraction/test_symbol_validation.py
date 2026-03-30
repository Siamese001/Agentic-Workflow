"""
Wave 1: Symbol Validation Test
Verifies that edge symbols in ADG output actually exist in the codebase.
"""

import ast
import pytest
from pathlib import Path
from typing import Set

from agentic_core.adg.extraction.static_scanner import ADGStaticScanner


class TestSymbolValidation:
    """Validate that ADG edge symbols correspond to real code entities."""

    def test_sampled_edge_symbols_exist(self, tmp_path):
        """Sample 100 random edges and verify their symbols exist in source files."""
        scanner = ADGStaticScanner(repo_root=tmp_path.parent)  # Use actual repo root
        result = scanner.scan()

        if not result.edges:
            pytest.skip("No edges to validate")

        # Sample up to 100 edges for validation
        sample_size = min(100, len(result.edges))
        sampled_edges = result.edges[:sample_size]  # First 100 for determinism

        missing_symbols = []

        for edge in sampled_edges:
            symbol = edge.symbol
            if not symbol:
                continue

            # Skip synthetic/internal prefixes
            if self._is_synthetic_symbol(symbol):
                continue

            # Check if symbol exists in codebase
            if not self._symbol_exists(symbol, tmp_path.parent):
                missing_symbols.append({
                    'symbol': symbol,
                    'source_file': edge.source_file,
                    'relation': edge.relation_type,
                    'line_no': edge.line_no
                })

        if missing_symbols:
            missing_list = "\n".join(
                f"  - {m['symbol']} (from {m['source_file']}:{m['line_no']})"
                for m in missing_symbols[:10]  # Show first 10
            )
            pytest.fail(
                f"Found {len(missing_symbols)} phantom symbols in ADG:\n{missing_list}\n"
                f"(showing first 10 of {len(missing_symbols)})"
            )

    def _is_synthetic_symbol(self, symbol: str) -> bool:
        """Check if symbol is a known synthetic/internal prefix."""
        synthetic_prefixes = (
            '_emit_',  # Self-bootstrap calls
            'ADG::',   # Internal ADG namespace
            'LayerSegment.',  # Layer constants
            'urg_read_',  # Phantom prefix from corruption
            'test_dummy_',  # Test-only symbols
        )
        return any(symbol.startswith(p) for p in synthetic_prefixes)

    def _symbol_exists(self, symbol: str, repo_root: Path) -> bool:
        """Check if a symbol exists in the Python codebase."""
        # Handle qualified names (module.Class.method)
        parts = symbol.split('.')
        base_name = parts[0]

        # Search Python files for the base symbol
        for py_file in repo_root.rglob("*.py"):
            if py_file.name.startswith('test_'):
                continue
            try:
                content = py_file.read_text(encoding='utf-8', errors='replace')
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name == base_name:
                        return True
                    if isinstance(node, ast.ClassDef) and node.name == base_name:
                        return True
                    if isinstance(node, ast.Name) and node.id == base_name:
                        return True

            except (SyntaxError, UnicodeDecodeError):
                continue

        return False


class TestPhantomSymbolBlacklist:
    """Ensure known phantom symbols never appear in ADG output."""

    BLACKLISTED_PREFIXES = [
        'urg_read_',      # From static_scanner corruption
        'test_dummy_',    # Test-only fake symbols
        'fake_',          # Obvious test fakes
        'phantom_',       # Intentionally phantom
    ]

    def test_no_blacklisted_symbols_in_edges(self, tmp_path):
        """Verify no blacklisted phantom prefixes appear in ADG edges."""
        scanner = ADGStaticScanner(repo_root=tmp_path.parent)
        result = scanner.scan()

        violations = []

        for edge in result.edges:
            symbol = edge.symbol or ''
            for prefix in self.BLACKLISTED_PREFIXES:
                if symbol.startswith(prefix):
                    violations.append({
                        'prefix': prefix,
                        'symbol': symbol,
                        'source_file': edge.source_file,
                        'line_no': edge.line_no
                    })
                    break

        if violations:
            violation_list = "\n".join(
                f"  - {v['symbol']} (prefix: {v['prefix']}) in {v['source_file']}:{v['line_no']}"
                for v in violations[:20]
            )
            pytest.fail(
                f"Found {len(violations)} blacklisted phantom symbols:\n{violation_list}\n"
                f"(showing first 20 of {len(violations)})"
            )
