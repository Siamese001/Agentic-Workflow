#!/usr/bin/env python3
"""
wave_execution_state.py — Plan lifecycle state management with simplified format support.

Purpose
-------
Reads and updates plan state markers for both legacy table-based plans and
simplified forward-only format plans (FORMAT_VERSION: simplified-plan-format-v1).

Non-mutating dry-run behavior:
    Use --dry-run flag to preview marker updates without writing to files.
    Returns proposed changes as JSON to stdout.

Simplified format markers supported:
    - FORMAT_VERSION: simplified-plan-format-v1
    - PLAN_STATUS
    - CURRENT_WAVE
    - LAST_COMPLETED_WAVE
    - WAVE_STATUS (per-wave)
    - WAVE_COMPLETE (per-wave)
    - PHASE_STATUS (per-phase)
    - PHASE_COMPLETE (per-phase)
    - AUTHORIZATION_STATUS

Backward compatibility:
    - Legacy table-based plans are read-only (no marker updates)
    - Does not require migration of historical plans
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple


@dataclass
class MarkerUpdate:
    """Proposed marker update."""
    marker_type: str  # 'top_level' or 'wave' or 'phase'
    marker_name: str
    old_value: Optional[str]
    new_value: str
    line_num: int
    wave_id: Optional[str] = None
    phase_id: Optional[str] = None


@dataclass
class PlanState:
    """Parsed plan state."""
    format_version: Optional[str]
    plan_status: Optional[str]
    current_wave: Optional[str]
    last_completed_wave: Optional[str]
    last_updated: Optional[str]
    waves: List[Dict[str, Any]]
    markers: List[Dict[str, Any]]


class SimplifiedPlanParser:
    """Parser for simplified-plan-format-v1 plans."""
    
    # Marker patterns
    FORMAT_VERSION_RE = re.compile(r'^FORMAT_VERSION:\s*(\S+)')
    PLAN_STATUS_RE = re.compile(r'^PLAN_STATUS:\s*(\S+)')
    CURRENT_WAVE_RE = re.compile(r'^CURRENT_WAVE:\s*(\S+)')
    LAST_COMPLETED_RE = re.compile(r'^LAST_COMPLETED_WAVE:\s*(\S+)')
    LAST_UPDATED_RE = re.compile(r'^LAST_UPDATED:\s*(\d{4}-\d{2}-\d{2})')
    WAVE_ID_RE = re.compile(r'^WAVE_ID:\s*(W\d+)')
    WAVE_STATUS_RE = re.compile(r'^WAVE_STATUS:\s*(\S+)')
    WAVE_COMPLETE_RE = re.compile(r'^WAVE_COMPLETE:\s*(\S+)')
    AUTHORIZATION_STATUS_RE = re.compile(r'^AUTHORIZATION_STATUS:\s*(\S+)')
    CHECKPOINT_RE = re.compile(r'^CHECKPOINT:\s*(\S+)')
    WAVE_SECTION_RE = re.compile(r'^## Wave \d+')
    PHASE_MARKER_RE = re.compile(r'PHASE_STATUS:\s*(\S+)')
    PHASE_COMPLETE_RE = re.compile(r'PHASE_COMPLETE:\s*(\S+)')
    FENCE_RE = re.compile(r'^```')
    
    def __init__(self, content: str):
        self.lines = content.split('\n')
        self.fenced_ranges = self._get_fenced_code_ranges()
    
    def _get_fenced_code_ranges(self) -> List[Tuple[int, int]]:
        """Return list of (start, end) line ranges for fenced code blocks."""
        ranges = []
        in_fence = False
        fence_start = 0
        
        for i, line in enumerate(self.lines, 1):
            if self.FENCE_RE.match(line):
                if not in_fence:
                    in_fence = True
                    fence_start = i
                else:
                    in_fence = False
                    ranges.append((fence_start, i))
        
        return ranges
    
    def _is_in_fenced_code(self, line_num: int) -> bool:
        """Check if a line number is inside any fenced code block."""
        for start, end in self.fenced_ranges:
            if start <= line_num <= end:
                return True
        return False
    
    def _find_marker(self, pattern: re.Pattern) -> Optional[Tuple[int, str]]:
        """Find first match of pattern, return (line_num, value)."""
        for i, line in enumerate(self.lines, 1):
            if self._is_in_fenced_code(i):
                continue
            match = pattern.match(line)
            if match:
                return (i, match.group(1))
        return None
    
    def _find_all_markers(self, pattern: re.Pattern) -> List[Tuple[int, str]]:
        """Find all matches of pattern, return list of (line_num, value)."""
        results = []
        for i, line in enumerate(self.lines, 1):
            if self._is_in_fenced_code(i):
                continue
            match = pattern.match(line)
            if match:
                results.append((i, match.group(1)))
        return results
    
    def parse(self) -> PlanState:
        """Parse plan state from content."""
        # Top-level markers
        format_version = self._find_marker(self.FORMAT_VERSION_RE)
        plan_status = self._find_marker(self.PLAN_STATUS_RE)
        current_wave = self._find_marker(self.CURRENT_WAVE_RE)
        last_completed = self._find_marker(self.LAST_COMPLETED_RE)
        last_updated = self._find_marker(self.LAST_UPDATED_RE)
        
        # Find wave sections
        wave_sections = []
        current_wave_start = None
        
        for i, line in enumerate(self.lines, 1):
            if self._is_in_fenced_code(i):
                continue
            if self.WAVE_SECTION_RE.match(line):
                if current_wave_start:
                    wave_sections.append((current_wave_start, i - 1))
                current_wave_start = i
        
        if current_wave_start:
            wave_sections.append((current_wave_start, len(self.lines)))
        
        # Parse each wave
        waves = []
        for start, end in wave_sections:
            wave_lines = self.lines[start-1:end]
            wave_id = None
            wave_status = None
            wave_complete = None
            auth_status = None
            phases = []
            
            for j, line in enumerate(wave_lines, start):
                if self._is_in_fenced_code(j):
                    continue
                
                w_id_match = self.WAVE_ID_RE.match(line)
                if w_id_match:
                    wave_id = w_id_match.group(1)
                
                w_status_match = self.WAVE_STATUS_RE.match(line)
                if w_status_match:
                    wave_status = w_status_match.group(1)
                
                w_complete_match = self.WAVE_COMPLETE_RE.match(line)
                if w_complete_match:
                    wave_complete = w_complete_match.group(1)
                
                auth_match = self.AUTHORIZATION_STATUS_RE.match(line)
                if auth_match:
                    auth_status = auth_match.group(1)
                
                # Phase markers
                phase_status_match = self.PHASE_MARKER_RE.search(line)
                if phase_status_match:
                    phases.append({
                        "line_num": j,
                        "status": phase_status_match.group(1),
                    })
            
            waves.append({
                "start_line": start,
                "end_line": end,
                "wave_id": wave_id,
                "wave_status": wave_status,
                "wave_complete": wave_complete,
                "authorization_status": auth_status,
                "phases": phases,
            })
        
        # Collect all markers
        markers = []
        for pattern, name in [
            (self.FORMAT_VERSION_RE, "FORMAT_VERSION"),
            (self.PLAN_STATUS_RE, "PLAN_STATUS"),
            (self.CURRENT_WAVE_RE, "CURRENT_WAVE"),
            (self.LAST_COMPLETED_RE, "LAST_COMPLETED_WAVE"),
            (self.LAST_UPDATED_RE, "LAST_UPDATED"),
        ]:
            result = self._find_marker(pattern)
            if result:
                markers.append({
                    "name": name,
                    "line_num": result[0],
                    "value": result[1],
                })
        
        return PlanState(
            format_version=format_version[1] if format_version else None,
            plan_status=plan_status[1] if plan_status else None,
            current_wave=current_wave[1] if current_wave else None,
            last_completed_wave=last_completed[1] if last_completed else None,
            last_updated=last_updated[1] if last_updated else None,
            waves=waves,
            markers=markers,
        )


def detect_format(content: str) -> Tuple[str, Optional[str]]:
    """Detect plan format. Returns (format_type, format_version)."""
    parser = SimplifiedPlanParser(content)
    state = parser.parse()
    
    if state.format_version:
        return "simplified", state.format_version
    
    return "legacy", None


def propose_marker_updates(
    content: str,
    plan_status: Optional[str] = None,
    current_wave: Optional[str] = None,
    last_completed_wave: Optional[str] = None,
    wave_status: Optional[str] = None,
    wave_complete: Optional[str] = None,
    wave_id: Optional[str] = None,
    authorization_status: Optional[str] = None,
) -> List[MarkerUpdate]:
    """Propose marker updates for a plan."""
    parser = SimplifiedPlanParser(content)
    state = parser.parse()
    updates = []
    
    if state.format_version != "simplified-plan-format-v1":
        return updates  # No updates for legacy format
    
    # Top-level updates
    if plan_status and state.plan_status != plan_status:
        marker = next((m for m in state.markers if m["name"] == "PLAN_STATUS"), None)
        if marker:
            updates.append(MarkerUpdate(
                marker_type="top_level",
                marker_name="PLAN_STATUS",
                old_value=state.plan_status,
                new_value=plan_status,
                line_num=marker["line_num"],
            ))
    
    if current_wave and state.current_wave != current_wave:
        marker = next((m for m in state.markers if m["name"] == "CURRENT_WAVE"), None)
        if marker:
            updates.append(MarkerUpdate(
                marker_type="top_level",
                marker_name="CURRENT_WAVE",
                old_value=state.current_wave,
                new_value=current_wave,
                line_num=marker["line_num"],
            ))
    
    if last_completed_wave and state.last_completed_wave != last_completed_wave:
        marker = next((m for m in state.markers if m["name"] == "LAST_COMPLETED_WAVE"), None)
        if marker:
            updates.append(MarkerUpdate(
                marker_type="top_level",
                marker_name="LAST_COMPLETED_WAVE",
                old_value=state.last_completed_wave,
                new_value=last_completed_wave,
                line_num=marker["line_num"],
            ))
    
    # Wave-level updates
    for wave in state.waves:
        if wave_id and wave["wave_id"] != wave_id:
            continue  # Skip waves that don't match
        
        if wave_status and wave["wave_status"] != wave_status:
            # Find WAVE_STATUS line
            wave_start = wave["start_line"]
            wave_end = wave["end_line"]
            for i in range(wave_start, wave_end + 1):
                line = parser.lines[i-1]
                if parser.WAVE_STATUS_RE.match(line) and not parser._is_in_fenced_code(i):
                    updates.append(MarkerUpdate(
                        marker_type="wave",
                        marker_name="WAVE_STATUS",
                        old_value=wave["wave_status"],
                        new_value=wave_status,
                        line_num=i,
                        wave_id=wave["wave_id"],
                    ))
                    break
        
        if wave_complete and wave["wave_complete"] != wave_complete:
            wave_start = wave["start_line"]
            wave_end = wave["end_line"]
            for i in range(wave_start, wave_end + 1):
                line = parser.lines[i-1]
                if parser.WAVE_COMPLETE_RE.match(line) and not parser._is_in_fenced_code(i):
                    updates.append(MarkerUpdate(
                        marker_type="wave",
                        marker_name="WAVE_COMPLETE",
                        old_value=wave["wave_complete"],
                        new_value=wave_complete,
                        line_num=i,
                        wave_id=wave["wave_id"],
                    ))
                    break
        
        if authorization_status and wave["authorization_status"] != authorization_status:
            wave_start = wave["start_line"]
            wave_end = wave["end_line"]
            for i in range(wave_start, wave_end + 1):
                line = parser.lines[i-1]
                if parser.AUTHORIZATION_STATUS_RE.match(line) and not parser._is_in_fenced_code(i):
                    updates.append(MarkerUpdate(
                        marker_type="wave",
                        marker_name="AUTHORIZATION_STATUS",
                        old_value=wave["authorization_status"],
                        new_value=authorization_status,
                        line_num=i,
                        wave_id=wave["wave_id"],
                    ))
                    break
    
    return updates


def apply_updates(content: str, updates: List[MarkerUpdate]) -> str:
    """Apply marker updates to content."""
    lines = content.split('\n')
    
    # Sort updates by line number in reverse order to avoid line shifting
    sorted_updates = sorted(updates, key=lambda u: u.line_num, reverse=True)
    
    for update in sorted_updates:
        line_idx = update.line_num - 1
        if line_idx < 0 or line_idx >= len(lines):
            continue
        
        old_line = lines[line_idx]
        
        # Replace the value after the colon
        if ':' in old_line:
            marker_part = old_line.split(':')[0]
            new_line = f"{marker_part}: {update.new_value}"
            lines[line_idx] = new_line
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Plan lifecycle state management with simplified format support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse and display plan state
  %(prog)s parse --file plan.md
  
  # Propose marker updates (dry-run)
  %(prog)s update --file plan.md --wave-id W1 --wave-status DONE --wave-complete YES --dry-run
  
  # Apply updates
  %(prog)s update --file plan.md --plan-status DONE --last-completed-wave W4
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Parse command
    parse_parser = subparsers.add_parser('parse', help='Parse plan state')
    parse_parser.add_argument('--file', required=True, help='Plan file path')
    parse_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update plan markers')
    update_parser.add_argument('--file', required=True, help='Plan file path')
    update_parser.add_argument('--plan-status', help='New PLAN_STATUS value')
    update_parser.add_argument('--current-wave', help='New CURRENT_WAVE value')
    update_parser.add_argument('--last-completed-wave', help='New LAST_COMPLETED_WAVE value')
    update_parser.add_argument('--wave-id', help='Target wave ID for wave-level updates')
    update_parser.add_argument('--wave-status', help='New WAVE_STATUS value')
    update_parser.add_argument('--wave-complete', help='New WAVE_COMPLETE value')
    update_parser.add_argument('--authorization-status', help='New AUTHORIZATION_STATUS value')
    update_parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    filepath = Path(args.file)
    if not filepath.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(2)
    
    content = filepath.read_text(encoding='utf-8')
    format_type, format_version = detect_format(content)
    
    if args.command == 'parse':
        parser_obj = SimplifiedPlanParser(content)
        state = parser_obj.parse()
        
        result = {
            "format_type": format_type,
            "format_version": format_version,
            "plan_status": state.plan_status,
            "current_wave": state.current_wave,
            "last_completed_wave": state.last_completed_wave,
            "last_updated": state.last_updated,
            "wave_count": len(state.waves),
            "waves": state.waves,
        }
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Format: {format_type}")
            if format_version:
                print(f"Version: {format_version}")
            print(f"Plan Status: {state.plan_status}")
            print(f"Current Wave: {state.current_wave}")
            print(f"Last Completed: {state.last_completed_wave}")
            print(f"Waves: {len(state.waves)}")
            for wave in state.waves:
                print(f"  {wave['wave_id']}: {wave['wave_status']} (complete: {wave['wave_complete']})")
    
    elif args.command == 'update':
        if format_type != 'simplified':
            print(f"Error: Cannot update legacy format plans. Format: {format_type}", file=sys.stderr)
            sys.exit(3)
        
        updates = propose_marker_updates(
            content,
            plan_status=args.plan_status,
            current_wave=args.current_wave,
            last_completed_wave=args.last_completed_wave,
            wave_status=args.wave_status,
            wave_complete=args.wave_complete,
            wave_id=args.wave_id,
            authorization_status=args.authorization_status,
        )
        
        if not updates:
            print("No updates proposed.")
            sys.exit(0)
        
        print(f"Proposed {len(updates)} updates:")
        for update in updates:
            context = f" ({update.wave_id})" if update.wave_id else ""
            print(f"  Line {update.line_num}{context}: {update.marker_name} = {update.old_value} -> {update.new_value}")
        
        if args.dry_run:
            print("\nDry-run mode: No changes written.")
            result = {
                "dry_run": True,
                "file": args.file,
                "updates": [asdict(u) for u in updates],
            }
            print(json.dumps(result, indent=2))
        else:
            new_content = apply_updates(content, updates)
            filepath.write_text(new_content, encoding='utf-8')
            print(f"\nUpdated {args.file}")


if __name__ == "__main__":
    main()
