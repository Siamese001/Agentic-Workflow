#!/usr/bin/env python3
"""
L4 Memory Layer - Resume Generator Memory Management
Preserves intermediate artifacts and atomic lineage
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field
import hashlib
import json
import uuid

import sys
sys.path.append(r'C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic_Workflow-10_11\agentic_workflow\RG_capabilities')
from rg_atomic_spec import ATOMIC_RG_SPEC

class MemoryArtifact(BaseModel):
    """Individual memory artifact with lineage tracking"""
    artifact_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    artifact_type: str
    content: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.now)
    source_step: str
    source_bucket: str
    content_hash: str
    lineage_chain: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def __init__(self, **data):
        super().__init__(**data)
        # Generate content hash if not provided
        if not self.content_hash:
            self.content_hash = self._generate_content_hash()
    
    def _generate_content_hash(self) -> str:
        """Generate hash of content for integrity checking"""
        content_str = json.dumps(self.content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()[:16]

class K1Memory(BaseModel):
    """Memory for K1 Extract step"""
    artifacts: List[MemoryArtifact] = Field(default_factory=list)
    extraction_cache: Dict[str, MemoryArtifact] = Field(default_factory=dict)
    lineage_start: datetime = Field(default_factory=datetime.now)
    
    def store_extraction_result(self, 
                               resume_data: Dict[str, Any], 
                               job_data: Dict[str, Any]) -> List[MemoryArtifact]:
        """Store K1 extraction results in memory"""
        
        # Store resume extraction artifact
        resume_artifact = MemoryArtifact(
            artifact_type="resume_extraction",
            content=resume_data,
            source_step="k1",
            source_bucket="routing"
        )
        
        # Store job extraction artifact
        job_artifact = MemoryArtifact(
            artifact_type="job_extraction",
            content=job_data,
            source_step="k1",
            source_bucket="job_workflow"
        )
        
        self.artifacts.extend([resume_artifact, job_artifact])
        self.extraction_cache["resume"] = resume_artifact
        self.extraction_cache["job"] = job_artifact
        
        return [resume_artifact, job_artifact]

class K2Memory(BaseModel):
    """Memory for K2 Clean step"""
    artifacts: List[MemoryArtifact] = Field(default_factory=list)
    cleaning_cache: Dict[str, MemoryArtifact] = Field(default_factory=dict)
    
    def store_cleaning_result(self, 
                             cleaned_resume: Dict[str, Any], 
                             cleaned_job: Dict[str, Any],
                             source_artifacts: List[MemoryArtifact]) -> List[MemoryArtifact]:
        """Store K2 cleaning results with lineage"""
        
        # Build lineage chain
        lineage_chain = [artifact.artifact_id for artifact in source_artifacts]
        
        # Store cleaned resume artifact
        resume_artifact = MemoryArtifact(
            artifact_type="cleaned_resume",
            content=cleaned_resume,
            source_step="k2",
            source_bucket="formatting",
            lineage_chain=lineage_chain
        )
        
        # Store cleaned job artifact
        job_artifact = MemoryArtifact(
            artifact_type="cleaned_job",
            content=cleaned_job,
            source_step="k2",
            source_bucket="formatting",
            lineage_chain=lineage_chain
        )
        
        self.artifacts.extend([resume_artifact, job_artifact])
        self.cleaning_cache["resume"] = resume_artifact
        self.cleaning_cache["job"] = job_artifact
        
        return [resume_artifact, job_artifact]

class K3Memory(BaseModel):
    """Memory for K3 Quant step"""
    artifacts: List[MemoryArtifact] = Field(default_factory=list)
    quant_cache: Dict[str, MemoryArtifact] = Field(default_factory=dict)
    
    def store_quantification_result(self, 
                                   alignment_scores: Dict[str, Any], 
                                   quality_metrics: Dict[str, Any],
                                   source_artifacts: List[MemoryArtifact]) -> List[MemoryArtifact]:
        """Store K3 quantification results with lineage"""
        
        lineage_chain = [artifact.artifact_id for artifact in source_artifacts]
        
        # Store alignment scores artifact
        alignment_artifact = MemoryArtifact(
            artifact_type="job_alignment_scores",
            content=alignment_scores,
            source_step="k3",
            source_bucket="quant",
            lineage_chain=lineage_chain
        )
        
        # Store quality metrics artifact
        quality_artifact = MemoryArtifact(
            artifact_type="resume_quality_metrics",
            content=quality_metrics,
            source_step="k3",
            source_bucket="quant",
            lineage_chain=lineage_chain
        )
        
        self.artifacts.extend([alignment_artifact, quality_artifact])
        self.quant_cache["alignment"] = alignment_artifact
        self.quant_cache["quality"] = quality_artifact
        
        return [alignment_artifact, quality_artifact]

class K4Memory(BaseModel):
    """Memory for K4 Rewrite step (NO-OP)"""
    artifacts: List[MemoryArtifact] = Field(default_factory=list)
    rewrite_cache: Dict[str, MemoryArtifact] = Field(default_factory=dict)
    
    def store_rewrite_result(self, 
                           rewritten_content: Dict[str, Any],
                           source_artifacts: List[MemoryArtifact]) -> List[MemoryArtifact]:
        """Store K4 rewrite results (NO-OP) with lineage"""
        
        lineage_chain = [artifact.artifact_id for artifact in source_artifacts]
        
        # Store rewrite artifact (empty/no-op)
        rewrite_artifact = MemoryArtifact(
            artifact_type="rewritten_content",
            content=rewritten_content,
            source_step="k4",
            source_bucket="rewrite",
            lineage_chain=lineage_chain,
            metadata={"note": "NO-OP implementation - empty rewrite bucket"}
        )
        
        self.artifacts.append(rewrite_artifact)
        self.rewrite_cache["content"] = rewrite_artifact
        
        return [rewrite_artifact]

class K5Memory(BaseModel):
    """Memory for K5 SkillMap step (NO-OP)"""
    artifacts: List[MemoryArtifact] = Field(default_factory=list)
    skillmap_cache: Dict[str, MemoryArtifact] = Field(default_factory=dict)
    
    def store_skill_mapping_result(self, 
                                 skill_mapping: Dict[str, Any],
                                 source_artifacts: List[MemoryArtifact]) -> List[MemoryArtifact]:
        """Store K5 skill mapping results (NO-OP) with lineage"""
        
        lineage_chain = [artifact.artifact_id for artifact in source_artifacts]
        
        # Store skill mapping artifact (empty/no-op)
        skillmap_artifact = MemoryArtifact(
            artifact_type="skill_mapping",
            content=skill_mapping,
            source_step="k5",
            source_bucket="skills",
            lineage_chain=lineage_chain,
            metadata={"note": "NO-OP implementation - empty skills bucket"}
        )
        
        self.artifacts.append(skillmap_artifact)
        self.skillmap_cache["mapping"] = skillmap_artifact
        
        return [skillmap_artifact]

class K6Memory(BaseModel):
    """Memory for K6 Section Assembly step (NO-OP)"""
    artifacts: List[MemoryArtifact] = Field(default_factory=list)
    assembly_cache: Dict[str, MemoryArtifact] = Field(default_factory=dict)
    
    def store_assembly_result(self, 
                            assembled_sections: Dict[str, Any],
                            source_artifacts: List[MemoryArtifact]) -> List[MemoryArtifact]:
        """Store K6 section assembly results (NO-OP) with lineage"""
        
        lineage_chain = [artifact.artifact_id for artifact in source_artifacts]
        
        # Store assembly artifact (empty/no-op)
        assembly_artifact = MemoryArtifact(
            artifact_type="assembled_sections",
            content=assembled_sections,
            source_step="k6",
            source_bucket="sections",
            lineage_chain=lineage_chain,
            metadata={"note": "NO-OP implementation - empty sections bucket"}
        )
        
        self.artifacts.append(assembly_artifact)
        self.assembly_cache["sections"] = assembly_artifact
        
        return [assembly_artifact]

class K7Memory(BaseModel):
    """Memory for K7 Format step"""
    artifacts: List[MemoryArtifact] = Field(default_factory=list)
    formatting_cache: Dict[str, MemoryArtifact] = Field(default_factory=dict)
    
    def store_formatting_result(self, 
                              formatted_resume: Dict[str, Any],
                              source_artifacts: List[MemoryArtifact]) -> List[MemoryArtifact]:
        """Store K7 formatting results with lineage"""
        
        lineage_chain = [artifact.artifact_id for artifact in source_artifacts]
        
        # Store formatting artifact
        formatting_artifact = MemoryArtifact(
            artifact_type="formatted_resume",
            content=formatted_resume,
            source_step="k7",
            source_bucket="formatting",
            lineage_chain=lineage_chain
        )
        
        self.artifacts.append(formatting_artifact)
        self.formatting_cache["resume"] = formatting_artifact
        
        return [formatting_artifact]

class K8Memory(BaseModel):
    """Memory for K8 Validation step"""
    artifacts: List[MemoryArtifact] = Field(default_factory=list)
    validation_cache: Dict[str, MemoryArtifact] = Field(default_factory=dict)
    
    def store_validation_result(self, 
                              validation_results: Dict[str, Any],
                              source_artifacts: List[MemoryArtifact]) -> List[MemoryArtifact]:
        """Store K8 validation results with lineage"""
        
        lineage_chain = [artifact.artifact_id for artifact in source_artifacts]
        
        # Store validation artifact
        validation_artifact = MemoryArtifact(
            artifact_type="validation_results",
            content=validation_results,
            source_step="k8",
            source_bucket="validators",
            lineage_chain=lineage_chain
        )
        
        self.artifacts.append(validation_artifact)
        self.validation_cache["results"] = validation_artifact
        
        return [validation_artifact]

class RGWorkflowMemory(BaseModel):
    """Complete workflow memory tracking all artifacts and lineage"""
    
    # Memory for all steps
    k1_memory: K1Memory = Field(default_factory=K1Memory)
    k2_memory: K2Memory = Field(default_factory=K2Memory)
    k3_memory: K3Memory = Field(default_factory=K3Memory)
    k4_memory: K4Memory = Field(default_factory=K4Memory)
    k5_memory: K5Memory = Field(default_factory=K5Memory)
    k6_memory: K6Memory = Field(default_factory=K6Memory)
    k7_memory: K7Memory = Field(default_factory=K7Memory)
    k8_memory: K8Memory = Field(default_factory=K8Memory)
    
    # Global memory tracking
    all_artifacts: List[MemoryArtifact] = Field(default_factory=list)
    lineage_graph: Dict[str, List[str]] = Field(default_factory=dict)
    bucket_usage: Dict[str, int] = Field(default_factory=dict)
    
    # Memory metadata
    workflow_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    total_artifacts: int = 0
    
    def __init__(self, **data):
        super().__init__(**data)
        # Initialize bucket usage tracking
        self._initialize_bucket_tracking()
    
    def _initialize_bucket_tracking(self):
        """Initialize bucket usage tracking from atomic spec"""
        buckets = [
            "routing", "parameters", "quant", "bullets", "rewrite", "skills",
            "sections", "job_workflow", "ats", "templates", "formatting",
            "seniority", "tone", "constraints", "validators", "mission"
        ]
        
        for bucket in buckets:
            self.bucket_usage[bucket] = 0
    
    def store_k1_artifacts(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> List[MemoryArtifact]:
        """Store K1 artifacts and update tracking"""
        artifacts = self.k1_memory.store_extraction_result(resume_data, job_data)
        
        for artifact in artifacts:
            self.all_artifacts.append(artifact)
            self.lineage_graph[artifact.artifact_id] = artifact.lineage_chain
            self.bucket_usage[artifact.source_bucket] += 1
        
        self.last_updated = datetime.now()
        self.total_artifacts = len(self.all_artifacts)
        
        return artifacts
    
    def store_k2_artifacts(self, cleaned_resume: Dict[str, Any], cleaned_job: Dict[str, Any]) -> List[MemoryArtifact]:
        """Store K2 artifacts and update tracking"""
        source_artifacts = self.k1_memory.artifacts
        artifacts = self.k2_memory.store_cleaning_result(cleaned_resume, cleaned_job, source_artifacts)
        
        for artifact in artifacts:
            self.all_artifacts.append(artifact)
            self.lineage_graph[artifact.artifact_id] = artifact.lineage_chain
            self.bucket_usage[artifact.source_bucket] += 1
        
        self.last_updated = datetime.now()
        self.total_artifacts = len(self.all_artifacts)
        
        return artifacts
    
    def store_k3_artifacts(self, alignment_scores: Dict[str, Any], quality_metrics: Dict[str, Any]) -> List[MemoryArtifact]:
        """Store K3 artifacts and update tracking"""
        source_artifacts = self.k2_memory.artifacts
        artifacts = self.k3_memory.store_quantification_result(alignment_scores, quality_metrics, source_artifacts)
        
        for artifact in artifacts:
            self.all_artifacts.append(artifact)
            self.lineage_graph[artifact.artifact_id] = artifact.lineage_chain
            self.bucket_usage[artifact.source_bucket] += 1
        
        self.last_updated = datetime.now()
        self.total_artifacts = len(self.all_artifacts)
        
        return artifacts
    
    def store_k4_artifacts(self, rewritten_content: Dict[str, Any]) -> List[MemoryArtifact]:
        """Store K4 artifacts and update tracking"""
        source_artifacts = self.k3_memory.artifacts
        artifacts = self.k4_memory.store_rewrite_result(rewritten_content, source_artifacts)
        
        for artifact in artifacts:
            self.all_artifacts.append(artifact)
            self.lineage_graph[artifact.artifact_id] = artifact.lineage_chain
            self.bucket_usage[artifact.source_bucket] += 1
        
        self.last_updated = datetime.now()
        self.total_artifacts = len(self.all_artifacts)
        
        return artifacts
    
    def store_k5_artifacts(self, skill_mapping: Dict[str, Any]) -> List[MemoryArtifact]:
        """Store K5 artifacts and update tracking"""
        source_artifacts = self.k4_memory.artifacts
        artifacts = self.k5_memory.store_skill_mapping_result(skill_mapping, source_artifacts)
        
        for artifact in artifacts:
            self.all_artifacts.append(artifact)
            self.lineage_graph[artifact.artifact_id] = artifact.lineage_chain
            self.bucket_usage[artifact.source_bucket] += 1
        
        self.last_updated = datetime.now()
        self.total_artifacts = len(self.all_artifacts)
        
        return artifacts
    
    def store_k6_artifacts(self, assembled_sections: Dict[str, Any]) -> List[MemoryArtifact]:
        """Store K6 artifacts and update tracking"""
        source_artifacts = self.k5_memory.artifacts
        artifacts = self.k6_memory.store_assembly_result(assembled_sections, source_artifacts)
        
        for artifact in artifacts:
            self.all_artifacts.append(artifact)
            self.lineage_graph[artifact.artifact_id] = artifact.lineage_chain
            self.bucket_usage[artifact.source_bucket] += 1
        
        self.last_updated = datetime.now()
        self.total_artifacts = len(self.all_artifacts)
        
        return artifacts
    
    def store_k7_artifacts(self, formatted_resume: Dict[str, Any]) -> List[MemoryArtifact]:
        """Store K7 artifacts and update tracking"""
        source_artifacts = self.k6_memory.artifacts
        artifacts = self.k7_memory.store_formatting_result(formatted_resume, source_artifacts)
        
        for artifact in artifacts:
            self.all_artifacts.append(artifact)
            self.lineage_graph[artifact.artifact_id] = artifact.lineage_chain
            self.bucket_usage[artifact.source_bucket] += 1
        
        self.last_updated = datetime.now()
        self.total_artifacts = len(self.all_artifacts)
        
        return artifacts
    
    def store_k8_artifacts(self, validation_results: Dict[str, Any]) -> List[MemoryArtifact]:
        """Store K8 artifacts and update tracking"""
        source_artifacts = self.k7_memory.artifacts
        artifacts = self.k8_memory.store_validation_result(validation_results, source_artifacts)
        
        for artifact in artifacts:
            self.all_artifacts.append(artifact)
            self.lineage_graph[artifact.artifact_id] = artifact.lineage_chain
            self.bucket_usage[artifact.source_bucket] += 1
        
        self.last_updated = datetime.now()
        self.total_artifacts = len(self.all_artifacts)
        
        return artifacts
    
    def get_artifact_by_id(self, artifact_id: str) -> Optional[MemoryArtifact]:
        """Get artifact by ID"""
        for artifact in self.all_artifacts:
            if artifact.artifact_id == artifact_id:
                return artifact
        return None
    
    def get_artifacts_by_step(self, step_name: str) -> List[MemoryArtifact]:
        """Get all artifacts for a specific step"""
        step_memories = {
            "k1": self.k1_memory,
            "k2": self.k2_memory,
            "k3": self.k3_memory,
            "k4": self.k4_memory,
            "k5": self.k5_memory,
            "k6": self.k6_memory,
            "k7": self.k7_memory,
            "k8": self.k8_memory
        }
        
        step_memory = step_memories.get(step_name)
        return step_memory.artifacts if step_memory else []
    
    def get_artifacts_by_bucket(self, bucket_name: str) -> List[MemoryArtifact]:
        """Get all artifacts for a specific bucket"""
        return [artifact for artifact in self.all_artifacts if artifact.source_bucket == bucket_name]
    
    def get_lineage_chain(self, artifact_id: str) -> List[str]:
        """Get lineage chain for an artifact"""
        return self.lineage_graph.get(artifact_id, [])
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get comprehensive memory summary"""
        return {
            "workflow_id": self.workflow_id,
            "total_artifacts": self.total_artifacts,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "bucket_usage": dict(self.bucket_usage),
            "step_artifact_counts": {
                "k1": len(self.k1_memory.artifacts),
                "k2": len(self.k2_memory.artifacts),
                "k3": len(self.k3_memory.artifacts),
                "k4": len(self.k4_memory.artifacts),
                "k5": len(self.k5_memory.artifacts),
                "k6": len(self.k6_memory.artifacts),
                "k7": len(self.k7_memory.artifacts),
                "k8": len(self.k8_memory.artifacts)
            },
            "lineage_graph_size": len(self.lineage_graph),
            "atomic_buckets_tracked": len(self.bucket_usage)
        }

class RGMemoryManager:
    """Memory manager for Resume Generator workflows"""
    
    def __init__(self):
        self.active_memories: Dict[str, RGWorkflowMemory] = {}
        self.atomic_spec = ATOMIC_RG_SPEC
    
    def create_workflow_memory(self, workflow_id: str) -> RGWorkflowMemory:
        """Create new workflow memory"""
        memory = RGWorkflowMemory(workflow_id=workflow_id)
        self.active_memories[workflow_id] = memory
        return memory
    
    def get_workflow_memory(self, workflow_id: str) -> Optional[RGWorkflowMemory]:
        """Get existing workflow memory"""
        return self.active_memories.get(workflow_id)
    
    def cleanup_workflow_memory(self, workflow_id: str) -> None:
        """Remove workflow memory from active memories"""
        if workflow_id in self.active_memories:
            del self.active_memories[workflow_id]
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get statistics about all workflow memories"""
        total_memories = len(self.active_memories)
        total_artifacts = sum(len(memory.all_artifacts) for memory in self.active_memories.values())
        
        return {
            "total_active_memories": total_memories,
            "total_stored_artifacts": total_artifacts,
            "average_artifacts_per_memory": total_artifacts / total_memories if total_memories > 0 else 0,
            "atomic_spec_buckets": len(self.atomic_spec)
        }
