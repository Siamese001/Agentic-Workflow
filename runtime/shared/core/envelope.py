"""Signal Envelope - Type-safe data flow through the pipeline.

This module implements the Envelope Pattern to ensure type safety,
auditability, and error isolation throughout the unified signal pipeline.
"""

import hashlib
import json
import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from dataclasses import dataclass, field

from pydantic import BaseModel, Field, validator
from pydantic.generics import GenericModel

logger = logging.getLogger(__name__)

# Type variables for generic envelope
T = TypeVar('T')


class PipelineStageStatus(str, Enum):
    """Status of pipeline stage execution."""
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    RETRYING = "RETRYING"


class PayloadType(str, Enum):
    """Types of payloads supported by the envelope."""
    RESUME_DATA = "resume_data"
    OUTREACH_DATA = "outreach_data"
    RAW_TEXT = "raw_text"
    DICT_DATA = "dict_data"
    ERROR_PAYLOAD = "error_payload"


class PayloadBase(BaseModel):
    """Base class for all payload types."""
    payload_type: PayloadType
    content_hash: str = Field(default_factory=lambda: "")
    
    class Config:
        use_enum_values = True


class ResumeData(PayloadBase):
    """Resume-specific payload data."""
    payload_type: PayloadType = PayloadType.RESUME_DATA
    sections: Dict[str, Any] = Field(default_factory=dict)
    target_role: Optional[str] = None
    experience_years: Optional[int] = None
    skills: List[str] = Field(default_factory=list)
    
    @validator('content_hash', pre=True, always=True)
    def generate_hash(cls, v, values):
        """Generate content hash from sections."""
        if 'sections' in values and values['sections']:
            content = json.dumps(values['sections'], sort_keys=True)
            return hashlib.sha256(content.encode()).hexdigest()[:16]
        return v


class OutreachData(PayloadBase):
    """Outreach-specific payload data."""
    payload_type: PayloadType = PayloadType.OUTREACH_DATA
    recipient_info: Dict[str, Any] = Field(default_factory=dict)
    sender_info: Dict[str, Any] = Field(default_factory=dict)
    campaign_context: Dict[str, Any] = Field(default_factory=dict)
    personalization_points: List[str] = Field(default_factory=list)
    
    @validator('content_hash', pre=True, always=True)
    def generate_hash(cls, v, values):
        """Generate content hash from recipient and context."""
        if 'recipient_info' in values or 'campaign_context' in values:
            content = json.dumps({
                'recipient': values.get('recipient_info', {}),
                'campaign': values.get('campaign_context', {})
            }, sort_keys=True)
            return hashlib.sha256(content.encode()).hexdigest()[:16]
        return v


class RawText(PayloadBase):
    """Raw text payload."""
    payload_type: PayloadType = PayloadType.RAW_TEXT
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('content_hash', pre=True, always=True)
    def generate_hash(cls, v, values):
        """Generate hash from text content."""
        if 'text' in values and values['text']:
            return hashlib.sha256(values['text'].encode()).hexdigest()[:16]
        return v


class DictData(PayloadBase):
    """Generic dictionary payload."""
    payload_type: PayloadType = PayloadType.DICT_DATA
    data: Dict[str, Any]
    
    @validator('content_hash', pre=True, always=True)
    def generate_hash(cls, v, values):
        """Generate hash from data."""
        if 'data' in values and values['data']:
            content = json.dumps(values['data'], sort_keys=True)
            return hashlib.sha256(content.encode()).hexdigest()[:16]
        return v


class ErrorPayload(PayloadBase):
    """Error payload for failed stages."""
    payload_type: PayloadType = PayloadType.ERROR_PAYLOAD
    error_type: str
    error_message: str
    original_payload_type: Optional[PayloadType] = None
    stack_trace: Optional[str] = None


class StageResult(BaseModel):
    """Result of a pipeline stage execution."""
    stage_name: str
    status: PipelineStageStatus
    duration_ms: float
    output_hash: str
    error_message: Optional[str] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('output_hash', pre=True, always=True)
    def generate_output_hash(cls, v, values):
        """Generate hash of stage output for verification."""
        # In practice, this would be computed from actual output
        # For now, generate based on stage name and status
        content = f"{values.get('stage_name', '')}:{values.get('status', '')}:{values.get('duration_ms', 0)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class SignalEnvelope(GenericModel, Generic[T]):
    """Type-safe envelope for data flowing through the pipeline."""
    
    # Identification
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parent_trace_id: Optional[str] = None  # For distributed tracing
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Payload (strictly typed)
    payload: T
    
    # Audit trail
    history: List[StageResult] = Field(default_factory=list)
    
    # Context metadata
    metadata: Dict[str, str] = Field(default_factory=dict)
    
    # Error state
    has_errors: bool = False
    error_count: int = 0
    
    class Config:
        arbitrary_types_allowed = True
        use_enum_values = True
    
    def mark_stage_start(self, stage_name: str) -> None:
        """Mark the start of a stage execution.
        
        Args:
            stage_name: Name of the stage
        """
        # Check if stage already completed
        if self.has_completed_stage(stage_name):
            logger.debug(f"Stage {stage_name} already completed for envelope {self.id}")
            return
        
        # Add pending result
        result = StageResult(
            stage_name=stage_name,
            status=PipelineStageStatus.PENDING,
            duration_ms=0.0,
            output_hash=""
        )
        self.history.append(result)
        self._touch()
    
    def mark_stage_complete(
        self,
        stage_name: str,
        duration_ms: float,
        output_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Mark a stage as successfully completed.
        
        Args:
            stage_name: Name of the stage
            duration_ms: Execution duration in milliseconds
            output_hash: Hash of the stage output
            metadata: Optional metadata
        """
        # Update or add result
        for i, result in enumerate(self.history):
            if result.stage_name == stage_name:
                self.history[i] = StageResult(
                    stage_name=stage_name,
                    status=PipelineStageStatus.SUCCESS,
                    duration_ms=duration_ms,
                    output_hash=output_hash or hashlib.sha256(f"{stage_name}:{duration_ms}".encode()).hexdigest()[:16],
                    metadata=metadata or {}
                )
                break
        else:
            # Add new result
            self.history.append(StageResult(
                stage_name=stage_name,
                status=PipelineStageStatus.SUCCESS,
                duration_ms=duration_ms,
                output_hash=output_hash or hashlib.sha256(f"{stage_name}:{duration_ms}".encode()).hexdigest()[:16],
                metadata=metadata or {}
            ))
        
        self._touch()
    
    def mark_stage_failed(
        self,
        stage_name: str,
        error_message: str,
        duration_ms: float = 0.0,
        retry_count: int = 0
    ) -> None:
        """Mark a stage as failed.
        
        Args:
            stage_name: Name of the stage
            error_message: Error message
            duration_ms: Execution duration before failure
            retry_count: Number of retries attempted
        """
        # Update or add result
        for i, result in enumerate(self.history):
            if result.stage_name == stage_name:
                self.history[i] = StageResult(
                    stage_name=stage_name,
                    status=PipelineStageStatus.FAILED,
                    duration_ms=duration_ms,
                    output_hash="",
                    error_message=error_message,
                    retry_count=retry_count
                )
                break
        else:
            # Add new result
            self.history.append(StageResult(
                stage_name=stage_name,
                status=PipelineStageStatus.FAILED,
                duration_ms=duration_ms,
                output_hash="",
                error_message=error_message,
                retry_count=retry_count
            ))
        
        self.has_errors = True
        self.error_count += 1
        self._touch()
    
    def mark_stage_skipped(self, stage_name: str, reason: Optional[str] = None) -> None:
        """Mark a stage as skipped.
        
        Args:
            stage_name: Name of the stage
            reason: Reason for skipping
        """
        # Update or add result
        for i, result in enumerate(self.history):
            if result.stage_name == stage_name:
                self.history[i] = StageResult(
                    stage_name=stage_name,
                    status=PipelineStageStatus.SKIPPED,
                    duration_ms=0.0,
                    output_hash="",
                    metadata={"reason": reason} if reason else {}
                )
                break
        else:
            # Add new result
            self.history.append(StageResult(
                stage_name=stage_name,
                status=PipelineStageStatus.SKIPPED,
                duration_ms=0.0,
                output_hash="",
                metadata={"reason": reason} if reason else {}
            ))
        
        self._touch()
    
    def has_completed_stage(self, stage_name: str) -> bool:
        """Check if a stage has been completed successfully.
        
        Args:
            stage_name: Name of the stage
            
        Returns:
            True if completed successfully
        """
        for result in self.history:
            if result.stage_name == stage_name:
                return result.status == PipelineStageStatus.SUCCESS
        return False
    
    def get_stage_result(self, stage_name: str) -> Optional[StageResult]:
        """Get the result for a specific stage.
        
        Args:
            stage_name: Name of the stage
            
        Returns:
            Stage result if found
        """
        for result in self.history:
            if result.stage_name == stage_name:
                return result
        return None
    
    def get_last_completed_stage(self) -> Optional[str]:
        """Get the name of the last completed stage.
        
        Returns:
            Stage name if found
        """
        for result in reversed(self.history):
            if result.status == PipelineStageStatus.SUCCESS:
                return result.stage_name
        return None
    
    def get_failed_stages(self) -> List[str]:
        """Get list of failed stage names.
        
        Returns:
            List of failed stage names
        """
        return [r.stage_name for r in self.history if r.status == PipelineStageStatus.FAILED]
    
    def calculate_total_duration(self) -> float:
        """Calculate total duration of completed stages.
        
        Returns:
            Total duration in milliseconds
        """
        return sum(r.duration_ms for r in self.history if r.status != PipelineStageStatus.PENDING)
    
    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert envelope to dictionary for serialization.
        
        Returns:
            Dictionary representation
        """
        return {
            "id": str(self.id),
            "trace_id": self.trace_id,
            "parent_trace_id": self.parent_trace_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "payload": self.payload.dict() if hasattr(self.payload, 'dict') else self.payload,
            "history": [r.dict() for r in self.history],
            "metadata": self.metadata,
            "has_errors": self.has_errors,
            "error_count": self.error_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SignalEnvelope":
        """Create envelope from dictionary.
        
        Args:
            data: Dictionary data
            
        Returns:
            Signal envelope instance
        """
        # Recreate payload based on type
        payload_data = data.get("payload", {})
        payload_type = payload_data.get("payload_type", "dict_data")
        
        if payload_type == "resume_data":
            payload = ResumeData(**payload_data)
        elif payload_type == "outreach_data":
            payload = OutreachData(**payload_data)
        elif payload_type == "raw_text":
            payload = RawText(**payload_data)
        else:
            payload = DictData(**payload_data)
        
        # Recreate history
        history = [StageResult(**r) for r in data.get("history", [])]
        
        # Create envelope
        envelope = cls(
            id=uuid.UUID(data["id"]),
            trace_id=data["trace_id"],
            parent_trace_id=data.get("parent_trace_id"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            payload=payload,
            history=history,
            metadata=data.get("metadata", {}),
            has_errors=data.get("has_errors", False),
            error_count=data.get("error_count", 0)
        )
        
        return envelope
    
    @classmethod
    def from_legacy_dict(cls, data: Dict[str, Any], metadata: Optional[Dict[str, str]] = None) -> "SignalEnvelope":
        """Create envelope from legacy dict format for backward compatibility.
        
        Args:
            data: Legacy dictionary data
            metadata: Optional metadata
            
        Returns:
            Signal envelope instance
        """
        # Determine payload type based on content
        if "sections" in data or "skills" in data:
            payload = ResumeData(**data)
        elif "recipient_info" in data or "campaign_context" in data:
            payload = OutreachData(**data)
        elif isinstance(data, str):
            payload = RawText(text=data)
        else:
            payload = DictData(data=data)
        
        return cls(
            payload=payload,
            metadata=metadata or {}
        )


class EnvelopeFactory:
    """Factory for creating signal envelopes."""
    
    @staticmethod
    def create_envelope(
        data: Any,
        metadata: Optional[Dict[str, str]] = None,
        trace_id: Optional[str] = None,
        parent_trace_id: Optional[str] = None
    ) -> SignalEnvelope:
        """Create a new signal envelope.
        
        Args:
            data: Data to wrap
            metadata: Optional metadata
            trace_id: Optional trace ID
            parent_trace_id: Optional parent trace ID
            
        Returns:
            Signal envelope
        """
        # Auto-wrap legacy data
        if isinstance(data, SignalEnvelope):
            return data
        
        # Create payload based on data type
        if isinstance(data, ResumeData):
            payload = data
        elif isinstance(data, OutreachData):
            payload = data
        elif isinstance(data, RawText):
            payload = data
        elif isinstance(data, DictData):
            payload = data
        elif isinstance(data, dict):
            payload = EnvelopeFactory._create_payload_from_dict(data)
        elif isinstance(data, str):
            payload = RawText(text=data)
        else:
            # Fallback to dict data
            payload = DictData(data={"value": data})
        
        # Create envelope
        envelope = SignalEnvelope(
            payload=payload,
            metadata=metadata or {},
            trace_id=trace_id or str(uuid.uuid4()),
            parent_trace_id=parent_trace_id
        )
        
        logger.debug(f"Created envelope {envelope.id} with payload type {payload.payload_type}")
        return envelope
    
    @staticmethod
    def _create_payload_from_dict(data: Dict[str, Any]) -> Union[ResumeData, OutreachData, DictData]:
        """Create appropriate payload from dictionary.
        
        Args:
            data: Dictionary data
            
        Returns:
            Appropriate payload instance
        """
        # Check for resume indicators
        if any(key in data for key in ["sections", "skills", "experience", "education"]):
            return ResumeData(**data)
        
        # Check for outreach indicators
        if any(key in data for key in ["recipient_info", "campaign_context", "personalization"]):
            return OutreachData(**data)
        
        # Default to dict data
        return DictData(data=data)


# Type aliases for common envelope types
ResumeEnvelope = SignalEnvelope[ResumeData]
OutreachEnvelope = SignalEnvelope[OutreachData]
TextEnvelope = SignalEnvelope[RawText]
DictEnvelope = SignalEnvelope[DictData]
