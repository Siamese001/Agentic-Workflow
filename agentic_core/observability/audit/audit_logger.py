"""
Audit Logger - Comprehensive Agent Action Tracking

RESPONSIBILITIES:
- Structured JSON logging of all agent actions
- Before/after diffs for code mutations
- LLM prompt/response hash tracking
- Forensic trail for rogue behavior detection
- Compliance audit support

Placed in observability/audit per SSOT semantic registry:
  "Audit logging and forensic tracking for agent actions"
"""
import hashlib
import json
import logging
from datetime import datetime
from difflib import unified_diff
from pathlib import Path
from typing import Any, Dict, List, Optional

Logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Comprehensive audit Logger for all agent actions.
    
    Provides:
    - Structured JSON logging (JSONL format)
    - Before/after code diffs
    - LLM interaction tracking
    - Agent identity and Violation tracking
    - Forensic analysis support
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize audit Logger.
        
        Args:
            project_root: Project root directory
        """
        self.project_root = project_root.resolve()
        self.log_dir = self.project_root / 'runtime' / 'audit'
        self.log_path = self.log_dir / 'audit_log.jsonl'
        
        # Create log directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize log file with header if new
        if not self.log_path.exists():
            self._write_header()
        
        Logger.info(f"[AUDIT] Initialized audit Logger: {self.log_path}")
    
    def _write_header(self) -> None:
        """Write header comment to new log file."""
        header = {
            "type": "header",
            "version": "1.0",
            "created_at": datetime.utcnow().isoformat(),
            "description": "Sovereign Agentic AI Audit Log - All agent actions tracked"
        }
        with self.log_path.open('a', encoding='utf-8') as f:
            json.dump(header, f)
            f.write('\n')
    
    def log_heal_attempt(
        self,
        agent_name: str,
        file_path: str,
        ViolationType: str,
        original_code: str,
        healed_code: str,
        prompt: Optional[str] = None,
        response: Optional[str] = None,
        applied: bool = False,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        [HARDENING 9] Log a healing attempt with full forensic details.
        
        Args:
            agent_name: Name of the agent performing the heal
            file_path: Path to file being healed
            ViolationType: Type of Violation being fixed
            original_code: Original code content
            healed_code: Healed code content
            prompt: LLM prompt used (optional)
            response: LLM response received (optional)
            applied: Whether the heal was applied
            error: Error message if heal failed
            metadata: Additional metadata
        """
        # Compute hashes for integrity verification
        before_hash = hashlib.sha256(original_code.encode('utf-8')).hexdigest()
        after_hash = hashlib.sha256(healed_code.encode('utf-8')).hexdigest()
        
        # Compute prompt/response hashes if provided
        prompt_hash = hashlib.sha256(prompt.encode('utf-8')).hexdigest() if prompt else None
        response_hash = hashlib.sha256(response.encode('utf-8')).hexdigest() if response else None
        
        # Generate diff
        diff_lines = list(unified_diff(
            original_code.splitlines(keepends=True),
            healed_code.splitlines(keepends=True),
            fromfile=f"before/{Path(file_path).name}",
            tofile=f"after/{Path(file_path).name}",
            n=3  # 3 lines of context
        ))
        
        # Truncate diff if too large (keep first and last 50 lines)
        if len(diff_lines) > 100:
            diff_lines = diff_lines[:50] + ['... (truncated) ...\n'] + diff_lines[-50:]
        
        entry = {
            "type": "heal_attempt",
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent_name,
            "file": str(file_path),
            "ViolationType": ViolationType,
            "hashes": {
                "before": before_hash,
                "after": after_hash,
                "prompt": prompt_hash,
                "response": response_hash
            },
            "metrics": {
                "original_lines": len(original_code.splitlines()),
                "healed_lines": len(healed_code.splitlines()),
                "diff_lines": len([l for l in diff_lines if l.startswith(('+', '-'))]),
                "unchanged": before_hash == after_hash
            },
            "diff": ''.join(diff_lines),
            "applied": applied,
            "error": error,
            "metadata": metadata or {}
        }
        
        self._write_entry(entry)
        
        if applied:
            Logger.info(f"[AUDIT] Heal applied: {agent_name} -> {Path(file_path).name}")
        else:
            Logger.warning(f"[AUDIT] Heal rejected: {agent_name} -> {Path(file_path).name}")
    
    def log_agent_discovery(
        self,
        agent_name: str,
        agent_class: str,
        discovery_path: str,
        instantiation_success: bool,
        error: Optional[str] = None
    ) -> None:
        """
        Log agent discovery and instantiation.
        
        Args:
            agent_name: Name of discovered agent
            agent_class: Full class name
            discovery_path: Path where agent was discovered
            instantiation_success: Whether instantiation succeeded
            error: Error message if instantiation failed
        """
        entry = {
            "type": "agent_discovery",
            "timestamp": datetime.utcnow().isoformat(),
            "agent_name": agent_name,
            "agent_class": agent_class,
            "discovery_path": discovery_path,
            "success": instantiation_success,
            "error": error
        }
        
        self._write_entry(entry)
    
    def log_structural_change(
        self,
        agent_name: str,
        operation: str,
        source_files: List[str],
        target_files: List[str],
        reason: str,
        applied: bool,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log structural changes (fission, fusion, moves).
        
        Args:
            agent_name: Name of agent performing operation
            operation: Type of operation (fission, fusion, move)
            source_files: Source file paths
            target_files: Target file paths
            reason: Reason for structural change
            applied: Whether change was applied
            metadata: Additional metadata
        """
        entry = {
            "type": "structural_change",
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent_name,
            "operation": operation,
            "source_files": source_files,
            "target_files": target_files,
            "reason": reason,
            "applied": applied,
            "metadata": metadata or {}
        }
        
        self._write_entry(entry)
    
    def log_security_event(
        self,
        event_type: str,
        Severity: str,
        description: str,
        agent_name: Optional[str] = None,
        file_path: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log security-related events.
        
        Args:
            event_type: Type of security event
            Severity: Severity level (low, medium, high, critical)
            description: Event description
            agent_name: Agent involved (if applicable)
            file_path: File involved (if applicable)
            details: Additional details
        """
        entry = {
            "type": "security_event",
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "Severity": Severity,
            "description": description,
            "agent": agent_name,
            "file": file_path,
            "details": details or {}
        }
        
        self._write_entry(entry)
        
        if Severity in ['high', 'critical']:
            Logger.error(f"[AUDIT] SECURITY EVENT [{Severity.upper()}]: {description}")
    
    def log_validation_result(
        self,
        validator_name: str,
        file_path: str,
        validation_type: str,
        passed: bool,
        violations: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log validation results.
        
        Args:
            validator_name: Name of validator
            file_path: File being validated
            validation_type: Type of validation
            passed: Whether validation passed
            violations: List of violations found
            metadata: Additional metadata
        """
        entry = {
            "type": "ValidationResult",
            "timestamp": datetime.utcnow().isoformat(),
            "validator": validator_name,
            "file": str(file_path),
            "validation_type": validation_type,
            "passed": passed,
            "violations": violations,
            "violation_count": len(violations),
            "metadata": metadata or {}
        }
        
        self._write_entry(entry)
    
    def log_llm_interaction(
        self,
        agent_name: str,
        operation: str,
        prompt_hash: str,
        response_hash: str,
        model: str,
        tokens_used: Optional[int] = None,
        latency_ms: Optional[float] = None,
        success: bool = True,
        error: Optional[str] = None
    ) -> None:
        """
        Log LLM interactions for audit trail.
        
        Args:
            agent_name: Agent making the LLM call
            operation: Type of operation (heal, embed, etc.)
            prompt_hash: SHA256 hash of prompt
            response_hash: SHA256 hash of response
            model: Model name used
            tokens_used: Token count (if available)
            latency_ms: Response latency in milliseconds
            success: Whether call succeeded
            error: Error message if failed
        """
        entry = {
            "type": "llm_interaction",
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent_name,
            "operation": operation,
            "model": model,
            "prompt_hash": prompt_hash,
            "response_hash": response_hash,
            "tokens_used": tokens_used,
            "latency_ms": latency_ms,
            "success": success,
            "error": error
        }
        
        self._write_entry(entry)
    
    def _write_entry(self, entry: Dict[str, Any]) -> None:
        """
        Write entry to audit log file.
        
        Args:
            entry: Log entry dictionary
        """
        try:
            with self.log_path.open('a', encoding='utf-8') as f:
                json.dump(entry, f, ensure_ascii=False)
                f.write('\n')
        except Exception as e:
            Logger.error(f"[AUDIT] Failed to write log entry: {e}")
    
    def query_logs(
        self,
        entry_type: Optional[str] = None,
        agent_name: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query audit logs with filters.
        
        Args:
            entry_type: Filter by entry type
            agent_name: Filter by agent name
            since: Filter by timestamp (entries after this time)
            limit: Maximum number of entries to return
            
        Returns:
            List of matching log entries
        """
        if not self.log_path.exists():
            return []
        
        results = []
        
        try:
            with self.log_path.open('r', encoding='utf-8') as f:
                for line in f:
                    if len(results) >= limit:
                        break
                    
                    try:
                        entry = json.loads(line)
                        
                        # Apply filters
                        if entry_type and entry.get('type') != entry_type:
                            continue
                        
                        if agent_name and entry.get('agent') != agent_name:
                            continue
                        
                        if since:
                            entry_time = datetime.fromisoformat(entry.get('timestamp', ''))
                            if entry_time < since:
                                continue
                        
                        results.append(entry)
                        
                    except json.JSONDecodeError:
                        continue
        
        except Exception as e:
            Logger.error(f"[AUDIT] Failed to query logs: {e}")
        
        return results
    
    def generate_summary_report(self, hours: int = 24) -> Dict[str, Any]:
        """
        Generate summary report of recent audit activity.
        
        Args:
            hours: Number of hours to include in report
            
        Returns:
            Summary statistics dictionary
        """
        since = datetime.utcnow().timestamp() - (hours * 3600)
        since_dt = datetime.fromtimestamp(since)
        
        entries = self.query_logs(since=since_dt, limit=10000)
        
        summary = {
            "period_hours": hours,
            "total_entries": len(entries),
            "by_type": {},
            "by_agent": {},
            "heals": {
                "attempted": 0,
                "applied": 0,
                "rejected": 0
            },
            "security_events": {
                "total": 0,
                "by_severity": {}
            }
        }
        
        for entry in entries:
            entry_type = entry.get('type', 'unknown')
            summary['by_type'][entry_type] = summary['by_type'].get(entry_type, 0) + 1
            
            agent = entry.get('agent')
            if agent:
                summary['by_agent'][agent] = summary['by_agent'].get(agent, 0) + 1
            
            if entry_type == 'heal_attempt':
                summary['heals']['attempted'] += 1
                if entry.get('applied'):
                    summary['heals']['applied'] += 1
                else:
                    summary['heals']['rejected'] += 1
            
            if entry_type == 'security_event':
                summary['security_events']['total'] += 1
                Severity = entry.get('Severity', 'unknown')
                summary['security_events']['by_severity'][Severity] = \
                    summary['security_events']['by_severity'].get(Severity, 0) + 1
        
        return summary
