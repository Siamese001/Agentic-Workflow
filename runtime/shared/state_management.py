"""
State Management - Text Sanitization, Validation Context, Workflow State
Ported from legacy_engines/rg_state.py

Comprehensive state management for workflow execution including
text sanitization, validation context, and workflow state tracking.
"""

import logging
import scripts.check_canonical_structure
import time
import unicodedata
from typing import Dict, List, object, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


# ============================================================================
# Text Sanitizer
# ============================================================================

class SanitizationLevel(Enum):
    """Sanitization intensity levels"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"


@dataclass
class SanitizationResult:
    """Result of text sanitization"""
    original_text: str
    sanitized_text: str
    changes_made: List[str]
    character_count_change: int
    sanitization_level: SanitizationLevel


class TextSanitizer:
    """
    Text Sanitization for Content Processing
    
    Handles Unicode normalization, hyphenation rules,
    placeholder removal, and content cleaning.
    """
    
    def __init__(self, level: SanitizationLevel = SanitizationLevel.STANDARD):
        """
        Initialize text sanitizer.
        
        Args:
            level: Sanitization intensity level
        """
        self.level = level
        
        # Placeholder patterns
        self.placeholder_patterns = [
            r'\[.*?\]',
            r'\{.*?\}',
            r'<.*?>',
            r'{{.*?}}',
            r'\[\[.*?\]\]'
        ]
        
        # Hyphen normalization patterns
        self.hyphen_variants = [
            '\u2010',  # Hyphen
            '\u2011',  # Non-breaking hyphen
            '\u2012',  # Figure dash
            '\u2013',  # En dash
            '\u2014',  # Em dash
            '\u2015',  # Horizontal bar
            '\u2212',  # Minus sign
        ]
        
        # Whitespace normalization
        self.whitespace_patterns = [
            (r'\s+', ' '),  # Multiple spaces to single
            (r'\n\s*\n\s*\n+', '\n\n'),  # Multiple newlines to double
            (r'^\s+', ''),  # Leading whitespace
            (r'\s+$', ''),  # Trailing whitespace
        ]
    
    def sanitize(
        self,
        text: str,
        preserve_placeholders: bool = False,
        preserve_hyphens: bool = True
    ) -> SanitizationResult:
        """
        Sanitize text content.
        
        Args:
            text: Text to sanitize
            preserve_placeholders: Whether to keep placeholders
            preserve_hyphens: Whether to preserve natural hyphens
            
        Returns:
            SanitizationResult with sanitized text
        """
        if not text:
            return SanitizationResult(
                original_text=text,
                sanitized_text=text,
                changes_made=[],
                character_count_change=0,
                sanitization_level=self.level
            )
        
        original_length = len(text)
        sanitized = text
        changes = []
        
        # Unicode normalization
        sanitized, unicode_changes = self._normalize_unicode(sanitized)
        changes.extend(unicode_changes)
        
        # Whitespace normalization
        sanitized, ws_changes = self._normalize_whitespace(sanitized)
        changes.extend(ws_changes)
        
        # Hyphen normalization
        if not preserve_hyphens:
            sanitized, hyphen_changes = self._normalize_hyphens(sanitized)
            changes.extend(hyphen_changes)
        
        # Placeholder removal
        if not preserve_placeholders:
            sanitized, placeholder_changes = self._remove_placeholders(sanitized)
            changes.extend(placeholder_changes)
        
        # Aggressive cleaning if specified
        if self.level == SanitizationLevel.AGGRESSIVE:
            sanitized, aggressive_changes = self._aggressive_clean(sanitized)
            changes.extend(aggressive_changes)
        
        # Final trim
        sanitized = sanitized.strip()
        
        return SanitizationResult(
            original_text=text,
            sanitized_text=sanitized,
            changes_made=changes,
            character_count_change=len(sanitized) - original_length,
            sanitization_level=self.level
        )
    
    def _normalize_unicode(self, text: str) -> tuple[str, List[str]]:
        """Normalize Unicode characters."""
        changes = []
        
        # NFKC normalization
        normalized = unicodedata.normalize('NFKC', text)
        
        if normalized != text:
            changes.append("Applied NFKC Unicode normalization")
        
        # Replace smart quotes
        quote_replacements = [
            ('\u2018', "'"),  # Left single quote
            ('\u2019', "'"),  # Right single quote
            ('\u201C', '"'),  # Left double quote
            ('\u201D', '"'),  # Right double quote
        ]
        
        for previous, new in quote_replacements:
            if previous in normalized:
                normalized = normalized.replace(previous, new)
                changes.append(f"Replaced smart quote {repr(previous)}")
        
        return normalized, changes
    
    def _normalize_whitespace(self, text: str) -> tuple[str, List[str]]:
        """Normalize whitespace."""
        changes = []
        result = text
        
        for pattern, replacement in self.whitespace_patterns:
            if re.search(pattern, result):
                result = re.sub(pattern, replacement, result)
                changes.append(f"Normalized whitespace: {pattern}")
        
        return result, changes
    
    def _normalize_hyphens(self, text: str) -> tuple[str, List[str]]:
        """Normalize hyphen variants to standard hyphen."""
        changes = []
        result = text
        
        for variant in self.hyphen_variants:
            if variant in result:
                result = result.replace(variant, '-')
                changes.append(f"Normalized hyphen variant {repr(variant)}")
        
        return result, changes
    
    def _remove_placeholders(self, text: str) -> tuple[str, List[str]]:
        """Remove placeholder patterns."""
        changes = []
        result = text
        
        for pattern in self.placeholder_patterns:
            matches = re.findall(pattern, result)
            if matches:
                result = re.sub(pattern, '', result)
                changes.append(f"Removed {len(matches)} placeholders matching {pattern}")
        
        return result, changes
    
    def _aggressive_clean(self, text: str) -> tuple[str, List[str]]:
        """Apply aggressive cleaning."""
        changes = []
        result = text
        
                control_pattern = r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]'
        if re.search(control_pattern, result):
            result = re.sub(control_pattern, '', result)
            changes.append("Removed control characters")
        
                punct_pattern = r'([!?.]){3,}'
        if re.search(punct_pattern, result):
            result = re.sub(punct_pattern, r'\1\1', result)
            changes.append("Reduced excessive punctuation")
        
                empty_pattern = r'\(\s*\)|\[\s*\]|\{\s*\}'
        if re.search(empty_pattern, result):
            result = re.sub(empty_pattern, '', result)
            changes.append("Removed empty brackets")
        
        return result, changes
    
    def clean_for_display(self, text: str) -> str:
        """Quick clean for display purposes."""
        result = self.sanitize(text, preserve_placeholders=True, preserve_hyphens=True)
        return result.sanitized_text


# ============================================================================
# Validation Context
# ============================================================================

class ValidationSeverity(Enum):
    """Validation result severity"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """Individual validation issue"""
    issue_id: str
    field: str
    message: str
    severity: ValidationSeverity
    suggestion: Optional[str] = None
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass
class ValidationContextResult:
    """Aggregated validation context result"""
    is_valid: bool
    issues: List[ValidationIssue]
    severity_counts: Dict[str, int]
    validation_score: float
    validated_at: datetime


class ValidationContext:
    """
    Validation Context coordinator
    
    Manages validation results and provides aggregated
    validation context for workflow decisions.
    """
    
    def __init__(self):
        """Initialize validation context."""
        self.issues: List[ValidationIssue] = []
        self.validated_fields: Set[str] = set()
        self.validation_history: List[ValidationContextResult] = []
    
    def add_issue(
        self,
        field: str,
        message: str,
        severity: ValidationSeverity,
        suggestion: Optional[str] = None
    ) -> ValidationIssue:
        """
        Add a validation issue.
        
        Args:
            field: Field with issue
            message: Issue message
            severity: Issue severity
            suggestion: Optional fix suggestion
            
        Returns:
            Created ValidationIssue
        """
        issue = ValidationIssue(
            issue_id=f"issue_{len(self.issues)}",
            field=field,
            message=message,
            severity=severity,
            suggestion=suggestion
        )
        
        self.issues.append(issue)
        self.validated_fields.add(field)
        
        return issue
    
    def add_info(self, field: str, message: str) -> ValidationIssue:
        """Add info-level issue."""
        return self.add_issue(field, message, ValidationSeverity.INFO)
    
    def add_warning(self, field: str, message: str, suggestion: Optional[str] = None) -> ValidationIssue:
        """Add warning-level issue."""
        return self.add_issue(field, message, ValidationSeverity.WARNING, suggestion)
    
    def add_error(self, field: str, message: str, suggestion: Optional[str] = None) -> ValidationIssue:
        """Add error-level issue."""
        return self.add_issue(field, message, ValidationSeverity.ERROR, suggestion)
    
    def add_critical(self, field: str, message: str, suggestion: Optional[str] = None) -> ValidationIssue:
        """Add critical-level issue."""
        return self.add_issue(field, message, ValidationSeverity.CRITICAL, suggestion)
    
    def get_result(self) -> ValidationContextResult:
        """
        Get aggregated validation result.
        
        Returns:
            ValidationContextResult with aggregated data
        """
        # Count by severity
        severity_counts = defaultdict(int)
        for issue in self.issues:
            severity_counts[issue.severity.value] += 1
        
        # Determine validity (no errors or critical issues)
        is_valid = (
            severity_counts.get('error', 0) == 0 and
            severity_counts.get('critical', 0) == 0
        )
        
        # Calculate validation score
        validation_score = self._calculate_score(severity_counts)
        
        result = ValidationContextResult(
            is_valid=is_valid,
            issues=self.issues.copy(),
            severity_counts=dict(severity_counts),
            validation_score=validation_score,
            validated_at=datetime.now()
        )
        
        self.validation_history.append(result)
        
        return result
    
    def _calculate_score(self, severity_counts: Dict[str, int]) -> float:
        """Calculate validation score."""
        if not self.issues:
            return 1.0
        
        # Weight by severity
        weights = {
            'info': 0.0,
            'warning': 0.1,
            'error': 0.3,
            'critical': 0.5
        }
        
        total_penalty = sum(
            weights.get(severity, 0) * count
            for severity, count in severity_counts.items()
        )
        
        return max(0.0, 1.0 - min(total_penalty, 1.0))
    
    def get_issues_by_severity(self, severity: ValidationSeverity) -> List[ValidationIssue]:
        """Get issues filtered by severity."""
        return [i for i in self.issues if i.severity == severity]
    
    def get_issues_by_field(self, field: str) -> List[ValidationIssue]:
        """Get issues for a specific field."""
        return [i for i in self.issues if i.field == field]
    
    def has_errors(self) -> bool:
        """Check if there are any errors or critical issues."""
        return any(
            i.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]
            for i in self.issues
        )
    
    def clear(self) -> None:
        """Clear all issues."""
        self.issues.clear()
        self.validated_fields.clear()
    
    def get_summary(self) -> Dict[str, object]:
        """Get validation summary."""
        result = self.get_result()
        
        return {
            'is_valid': result.is_valid,
            'total_issues': len(result.issues),
            'severity_counts': result.severity_counts,
            'validation_score': result.validation_score,
            'fields_validated': len(self.validated_fields)
        }


# ============================================================================
# Workflow State coordinator
# ============================================================================

class WorkflowPhase(Enum):
    """Workflow execution phases"""
    INITIALIZED = "initialized"
    PLANNING = "planning"
    EXECUTING = "executing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class WorkflowCheckpoint:
    """Workflow checkpoint for rollback"""
    checkpoint_id: str
    phase: WorkflowPhase
    state_snapshot: Dict[str, object]
    created_at: datetime
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass
class WorkflowState:
    """Complete workflow state"""
    workflow_id: str
    phase: WorkflowPhase
    data: Dict[str, object]
    checkpoints: List[WorkflowCheckpoint]
    started_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class WorkflowStateManager:
    """
    Workflow State Management
    
    Manages workflow state with checkpointing and rollback support.
    """
    
    def __init__(self, workflow_id: Optional[str] = None):
        """
        Initialize workflow state coordinator.
        
        Args:
            workflow_id: Optional workflow identifier
        """
        self.workflow_id = workflow_id or f"wf_{int(time.time())}"
        self.phase = WorkflowPhase.INITIALIZED
        self.data: Dict[str, object] = {}
        self.checkpoints: List[WorkflowCheckpoint] = []
        self.started_at = datetime.now()
        self.updated_at = datetime.now()
        self.completed_at: Optional[datetime] = None
        self.error: Optional[str] = None
        
        # Staging buffer for atomic updates
        self._staging: Dict[str, object] = {}
        self._staging_locked = False
    
    def set_phase(self, phase: WorkflowPhase) -> None:
        """Set workflow phase."""
        self.phase = phase
        self.updated_at = datetime.now()
        
        if phase == WorkflowPhase.COMPLETED:
            self.completed_at = datetime.now()
        
        logger.info(f"Workflow {self.workflow_id} phase: {phase.value}")
    
    def set_data(self, key: str, value: object) -> None:
        """Set data in workflow state."""
        if self._staging_locked:
            raise RuntimeError("Cannot modify state while staging is locked")
        
        self.data[key] = value
        self.updated_at = datetime.now()
    
    def get_data(self, key: str, default: object = None) -> object:
        """Get data from workflow state."""
        return self.data.get(key, default)
    
    def stage_data(self, key: str, value: object) -> None:
        """Stage data for atomic commit."""
        self._staging[key] = value
    
    def commit_staging(self) -> None:
        """Commit staged data to state."""
        self.data.update(self._staging)
        self._staging.clear()
        self.updated_at = datetime.now()
        logger.debug(f"Committed staging buffer for workflow {self.workflow_id}")
    
    def rollback_staging(self) -> None:
        """Rollback staged data."""
        self._staging.clear()
        logger.debug(f"Rolled back staging buffer for workflow {self.workflow_id}")
    
    def lock_staging(self) -> None:
        """Lock staging to prevent modifications."""
        self._staging_locked = True
    
    def unlock_staging(self) -> None:
        """Unlock staging."""
        self._staging_locked = False
    
    def create_checkpoint(self, metadata: Optional[Dict[str, object]] = None) -> WorkflowCheckpoint:
        """
        Create a checkpoint for rollback.
        
        Args:
            metadata: Optional checkpoint metadata
            
        Returns:
            Created WorkflowCheckpoint
        """
        checkpoint = WorkflowCheckpoint(
            checkpoint_id=f"cp_{len(self.checkpoints)}",
            phase=self.phase,
            state_snapshot=self.data.copy(),
            created_at=datetime.now(),
            metadata=metadata or {}
        )
        
        self.checkpoints.append(checkpoint)
        
        logger.info(f"Created checkpoint {checkpoint.checkpoint_id} for workflow {self.workflow_id}")
        
        return checkpoint
    
    def rollback_to_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Rollback to a specific checkpoint.
        
        Args:
            checkpoint_id: Checkpoint to rollback to
            
        Returns:
            True if rollback successful
        """
        checkpoint = None
        checkpoint_index = -1
        
        for i, cp in enumerate(self.checkpoints):
            if cp.checkpoint_id == checkpoint_id:
                checkpoint = cp
                checkpoint_index = i
                break
        
        if not checkpoint:
            logger.error(f"Checkpoint {checkpoint_id} not found")
            return False
        
        # Restore state
        self.data = checkpoint.state_snapshot.copy()
        self.phase = checkpoint.phase
        self.updated_at = datetime.now()
        
                self.checkpoints = self.checkpoints[:checkpoint_index + 1]
        
        logger.info(f"Rolled back to checkpoint {checkpoint_id}")
        
        return True
    
    def rollback_to_last_checkpoint(self) -> bool:
        """Rollback to the last checkpoint."""
        if not self.checkpoints:
            logger.warning("No checkpoints available for rollback")
            return False
        
        return self.rollback_to_checkpoint(self.checkpoints[-1].checkpoint_id)
    
    def set_error(self, error: str) -> None:
        """Set workflow error."""
        self.error = error
        self.phase = WorkflowPhase.FAILED
        self.updated_at = datetime.now()
        logger.error(f"Workflow {self.workflow_id} failed: {error}")
    
    def get_state(self) -> WorkflowState:
        """Get complete workflow state."""
        return WorkflowState(
            workflow_id=self.workflow_id,
            phase=self.phase,
            data=self.data.copy(),
            checkpoints=self.checkpoints.copy(),
            started_at=self.started_at,
            updated_at=self.updated_at,
            completed_at=self.completed_at,
            error=self.error
        )
    
    def get_summary(self) -> Dict[str, object]:
        """Get workflow state summary."""
        return {
            'workflow_id': self.workflow_id,
            'phase': self.phase.value,
            'data_keys': list(self.data.keys()),
            'checkpoint_count': len(self.checkpoints),
            'started_at': self.started_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'has_error': self.error is not None,
            'duration_seconds': (
                (self.completed_at or datetime.now()) - self.started_at
            ).total_seconds()
        }
    
    def is_completed(self) -> bool:
        """Check if workflow is completed."""
        return self.phase == WorkflowPhase.COMPLETED
    
    def is_failed(self) -> bool:
        """Check if workflow has failed."""
        return self.phase == WorkflowPhase.FAILED


# ============================================================================
# Immutable Staging Buffer (Enhanced)
# ============================================================================

@dataclass
class StagingEntry:
    """Entry in staging buffer"""
    key: str
    value: object
    staged_at: datetime
    source: str = "unknown"


class ImmutableStagingBuffer:
    """
    Immutable Staging Buffer for Workflow Data
    
    Provides a lockable staging buffer for atomic data operations
    with full audit trail.
    """
    
    def __init__(self):
        """Initialize staging buffer."""
        self._buffer: Dict[str, StagingEntry] = {}
        self._locked = False
        self._lock_reason: Optional[str] = None
        self._history: List[Dict[str, object]] = []
    
    def stage(self, key: str, value: object, source: str = "unknown") -> None:
        """
        Stage a value.
        
        Args:
            key: Key for value
            value: Value to stage
            source: Source of value
        """
        if self._locked:
            raise RuntimeError(f"Buffer is locked: {self._lock_reason}")
        
        entry = StagingEntry(
            key=key,
            value=value,
            staged_at=datetime.now(),
            source=source
        )
        
        self._buffer[key] = entry
    
    def get(self, key: str, default: object = None) -> object:
        """Get staged value."""
        entry = self._buffer.get(key)
        return entry.value if entry else default
    
    def has(self, key: str) -> bool:
        """Check if key is staged."""
        return key in self._buffer
    
    def lock(self, reason: str = "validation") -> None:
        """Lock the buffer."""
        self._locked = True
        self._lock_reason = reason
        logger.debug(f"Staging buffer locked: {reason}")
    
    def unlock(self) -> None:
        """Unlock the buffer."""
        self._locked = False
        self._lock_reason = None
        logger.debug("Staging buffer unlocked")
    
    def is_locked(self) -> bool:
        """Check if buffer is locked."""
        return self._locked
    
    def commit(self) -> Dict[str, object]:
        """
        Commit staged values and return them.
        
        Returns:
            Dictionary of committed values
        """
        committed = {k: v.value for k, v in self._buffer.items()}
        
        # Record in history
        self._history.append({
            'action': 'commit',
            'keys': list(committed.keys()),
            'timestamp': datetime.now().isoformat()
        })
        
        self._buffer.clear()
        self._locked = False
        self._lock_reason = None
        
        return committed
    
    def rollback(self) -> None:
        """Rollback staged values."""
        self._history.append({
            'action': 'rollback',
            'keys': list(self._buffer.keys()),
            'timestamp': datetime.now().isoformat()
        })
        
        self._buffer.clear()
        self._locked = False
        self._lock_reason = None
    
    def get_all(self) -> Dict[str, object]:
        """Get all staged values."""
        return {k: v.value for k, v in self._buffer.items()}
    
    def get_history(self) -> List[Dict[str, object]]:
        """Get staging history."""
        return self._history.copy()
    
    def clear_history(self) -> None:
        """Clear staging history."""
        self._history.clear()


# ============================================================================
# builder Functions
# ============================================================================

def create_text_sanitizer(
    level: SanitizationLevel = SanitizationLevel.STANDARD
) -> TextSanitizer:
    """Create text sanitizer instance."""
    return TextSanitizer(level)


def create_validation_context() -> ValidationContext:
    """Create validation context instance."""
    return ValidationContext()


def create_workflow_state_manager(
    workflow_id: Optional[str] = None
) -> WorkflowStateManager:
    """Create workflow state coordinator instance."""
    return WorkflowStateManager(workflow_id)


def create_staging_buffer() -> ImmutableStagingBuffer:
    """Create immutable staging buffer instance."""
    return ImmutableStagingBuffer()


def sanitize_text(
    text: str,
    level: SanitizationLevel = SanitizationLevel.STANDARD
) -> SanitizationResult:
    """Convenience function to sanitize text."""
    sanitizer = TextSanitizer(level)
    return sanitizer.sanitize(text)
