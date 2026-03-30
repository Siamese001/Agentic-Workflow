"""
Wave 5: Phantom Edge Detector Test
CI gate that blacklists known fake prefixes and fails the build if they appear.
"""

import re
from pathlib import Path
from typing import List, Set

import pytest

from agentic_core.adg.extraction.static_scanner import ADGStaticScanner


class TestPhantomEdgeDetector:
    """CI gate: Blacklist known phantom prefixes and fail build if found."""
    
    # Known phantom prefixes from historical corruption
    BLACKLISTED_PREFIXES: List[str] = [
        'urg_read_',          # From static_scanner corruption (633 instances)
        'test_dummy_',        # Obvious test-only fakes
        'fake_',              # Intentionally fake
        'phantom_',           # Explicitly phantom
        'corrupt_',           # Marked as corruption
        'synthetic_emit_',    # Synthetic emitter patterns
        '_debug_placeholder_', # Debug-only placeholders
    ]
    
    # Edge kinds that should never have certain prefixes
    SUSPICIOUS_EDGE_KINDS = {
        'reads_through': ['urg_read_'],  # reads_through should never have urg_read_
    }
    
    def test_no_blacklisted_symbols_in_adg_output(self, tmp_path):
        """
        CRITICAL CI GATE: Fail build if blacklisted phantom symbols appear.
        
        This test prevents corruption like the 633 urg_read_ phantom edges
        from reaching production undetected.
        """
        repo_root = tmp_path.parent
        
        scanner = ADGStaticScanner(repo_root=repo_root)
        result = scanner.scan()
        
        violations: List[dict] = []
        
        for edge in result.edges:
            symbol = edge.symbol or ''
            
            for prefix in self.BLACKLISTED_PREFIXES:
                if symbol.startswith(prefix):
                    violations.append({
                        'prefix': prefix,
                        'symbol': symbol,
                        'source_file': edge.source_file,
                        'line_no': edge.line_no,
                        'edge_kind': edge.edge_kind,
                        'relation': edge.relation_type,
                    })
                    break
        
        if violations:
            # Format violation report
            report_lines = [
                "",
                "=" * 70,
                "PHANTOM EDGE DETECTOR: CRITICAL VIOLATIONS FOUND",
                "=" * 70,
                f"Total violations: {len(violations)}",
                "",
                "Violations by prefix:",
            ]
            
            by_prefix = {}
            for v in violations:
                by_prefix.setdefault(v['prefix'], []).append(v)
            
            for prefix, prefix_violations in by_prefix.items():
                report_lines.append(f"\n  {prefix}: {len(prefix_violations)} instances")
                for v in prefix_violations[:5]:  # Show first 5 of each
                    report_lines.append(
                        f"    - {v['symbol']} ({v['edge_kind']}) "
                        f"in {v['source_file']}:{v['line_no']}"
                    )
                if len(prefix_violations) > 5:
                    report_lines.append(f"    ... and {len(prefix_violations) - 5} more")
            
            report_lines.extend([
                "",
                "These are KNOWN PHANTOM SYMBOLS from historical corruption.",
                "The ADG has been compromised with fake edges.",
                "Build is FAILED to prevent corrupted data from reaching production.",
                "=" * 70,
            ])
            
            pytest.fail("\n".join(report_lines))
    
    def test_suspicious_edge_kind_symbol_combinations(self, tmp_path):
        """Flag suspicious combinations like reads_through + urg_read_."""
        repo_root = tmp_path.parent
        
        scanner = ADGStaticScanner(repo_root=repo_root)
        result = scanner.scan()
        
        violations = []
        
        for edge in result.edges:
            edge_kind = edge.edge_kind or ''
            symbol = edge.symbol or ''
            
            # Check each edge kind's forbidden prefixes
            for kind, forbidden_prefixes in self.SUSPICIOUS_EDGE_KINDS.items():
                if kind in edge_kind:
                    for prefix in forbidden_prefixes:
                        if symbol.startswith(prefix):
                            violations.append({
                                'edge_kind': edge_kind,
                                'symbol': symbol,
                                'prefix': prefix,
                                'source_file': edge.source_file,
                                'line_no': edge.line_no,
                            })
        
        if violations:
            report = "\n".join(
                f"  - {v['edge_kind']} edge with symbol '{v['symbol']}' "
                f"in {v['source_file']}:{v['line_no']}"
                for v in violations[:20]
            )
            pytest.fail(
                f"Found {len(violations)} suspicious edge kind + symbol combinations:\n{report}\n"
                f"(showing first 20 of {len(violations)})"
            )
    
    def test_symbol_naming_conventions(self, tmp_path):
        """Enforce that symbols follow expected naming patterns."""
        repo_root = tmp_path.parent
        
        scanner = ADGStaticScanner(repo_root=repo_root)
        result = scanner.scan()
        
        # Valid Python identifier pattern
        valid_identifier = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
        
        # Suspicious patterns
        suspicious_patterns = [
            (r'^_+\d+$', 'numeric-only with underscores'),  # _42, __123
            (r'^\d', 'starts with digit'),  # 123symbol
            (r'[^a-zA-Z0-9_]', 'non-identifier characters'),  # symbol-with-dashes, symbol.with.dots
            (r'_{5,}', 'excessive underscores'),  # symbol_____name
        ]
        
        violations = []
        
        for edge in result.edges:
            symbol = edge.symbol or ''
            
            # Skip qualified names (module.Class.method)
            base_symbol = symbol.split('.')[-1] if '.' in symbol else symbol
            
            # Skip ADG namespace prefixes
            if base_symbol.startswith('ADG::'):
                continue
            
            # Check for suspicious patterns
            for pattern, description in suspicious_patterns:
                if re.search(pattern, base_symbol):
                    violations.append({
                        'symbol': symbol,
                        'base': base_symbol,
                        'issue': description,
                        'source_file': edge.source_file,
                        'line_no': edge.line_no,
                    })
                    break
        
        # Allow some flexibility but flag if >1% of symbols are suspicious
        if result.edges:
            violation_rate = len(violations) / len(result.edges)
            if violation_rate > 0.01:  # 1% threshold
                report = "\n".join(
                    f"  - '{v['symbol']}' ({v['issue']}) in {v['source_file']}:{v['line_no']}"
                    for v in violations[:15]
                )
                pytest.fail(
                    f"Suspicious symbol rate {violation_rate:.2%} exceeds 1% threshold.\n"
                    f"Found {len(violations)} suspicious symbols:\n{report}\n"
                    f"(showing first 15 of {len(violations)})"
                )


class TestPhantomPrefixPrevention:
    """Prevent new phantom patterns from entering the codebase."""
    
    def test_no_hardcoded_emit_reads_through_calls(self):
        """Scan static_scanner.py for hardcoded _emit_reads_through with numeric suffixes."""
        scanner_file = Path(__file__).parent.parent.parent.parent / "adg" / "extraction" / "static_scanner.py"
        
        if not scanner_file.exists():
            pytest.skip("Cannot find static_scanner.py source")
        
        content = scanner_file.read_text(encoding='utf-8', errors='replace')
        
        # Pattern: _emit_reads_through("...", "...", "prefix_NNN")
        phantom_pattern = re.compile(
            r'_emit_reads_through\([^)]*"\w+_\d+"\s*\)',
            re.MULTILINE
        )
        
        matches = phantom_pattern.findall(content)
        
        if matches:
            sample = "\n".join(f"  {m[:80]}..." if len(m) > 80 else f"  {m}" for m in matches[:10])
            pytest.fail(
                f"Found {len(matches)} hardcoded _emit_reads_through calls with numeric suffixes:\n"
                f"{sample}\n"
                f"These are likely phantom edges. Remove them."
            )
    
    def test_scanner_source_no_debug_placeholders(self):
        """Ensure static_scanner.py doesn't contain debug placeholder patterns."""
        scanner_file = Path(__file__).parent.parent.parent.parent / "adg" / "extraction" / "static_scanner.py"
        
        if not scanner_file.exists():
            pytest.skip("Cannot find static_scanner.py source")
        
        content = scanner_file.read_text(encoding='utf-8', errors='replace')
        
        # Look for common debug placeholder patterns
        placeholder_patterns = [
            (r'_emit_reads_through\([^)]*"(test|dummy|fake|placeholder)', 'placeholder emit'),
            (r'#.*DEBUG.*\n.*_emit_', 'debug comment before emit'),
            (r'"\w+_\d{3,}"', 'numeric suffix with 3+ digits (likely auto-generated)'),
        ]
        
        violations = []
        for pattern, description in placeholder_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(description)
        
        if violations:
            pytest.fail(
                f"Found potential debug placeholder patterns in static_scanner.py:\n" +
                "\n".join(f"  - {v}" for v in violations) +
                "\nRemove debug code before committing."
            )
