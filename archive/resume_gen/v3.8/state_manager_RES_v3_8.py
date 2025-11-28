# File: state_manager_RES_v3_8.py
# Version: 3.8.0 - V3.8 Agentic Architecture (Validation Consolidated)
# State serialization and deserialization layer for workflow hops
"""
V3.8 Migration with Backward Compatibility
================================================================================
The StateSerializer class (formerly in this file) is no longer used for
hop-to-hop state management, which is now handled in-memory by the Governor.

The ManifestManager is the primary persistence mechanism for the final workflow state.

V3.8 Note: Validation methods have been consolidated into validator_RES_v3_8.py
================================================================================
"""

import json
import os
from dataclasses import asdict
from typing import Any, Dict, List, Optional
import hashlib
from datetime import datetime

from models_RES import (
    ValidationResult,
    ValidationSeverity,
    HopCheckpoint,
    HopStatus
)


class ManifestManager:
    """
    Manages the run_manifest.json file for a workflow run.
    
    This class handles:
    - Creating initial manifests for new runs
    - Loading manifests for resumed runs
    - Updating manifests with checkpoint data
    - Cryptographic validation of state integrity
    
    In V3.8, this is the primary persistence mechanism for the final workflow state.
    """
    
    def __init__(self, run_path: str):
        """
        Initialize the ManifestManager.
        
        Args:
            run_path: Absolute path to the run directory
        """
        self.run_path = run_path
        self.manifest_path = os.path.join(run_path, "run_manifest.json")
        self._integrity_checksums = {}  # Track checksums for validation
    
    def create_manifest(self, run_id: str, engine_version: str, 
                       job_input: dict, master_resume_hash: str) -> dict:
        """
        Creates and saves a new manifest for a new run.
        
        Args:
            run_id: Unique run identifier
            engine_version: Version of the workflow engine
            job_input: Job input dictionary
            master_resume_hash: SHA256 hash of master resume
            
        Returns:
            The created manifest dictionary
        """
        manifest = {
            "run_id": run_id,
            "engine_version": engine_version,
            "start_time_utc": datetime.utcnow().isoformat() + "Z",
            "job_input": job_input,
            "master_resume_hash": master_resume_hash,
            "hop_checkpoints": [],
            "integrity_checksum": None  # Will be computed on save
        }
        
        self._save_manifest(manifest)
        return manifest
    
    def load_manifest(self) -> dict:
        """
        Loads the manifest from disk with integrity validation.
        
        Returns:
            The manifest dictionary
            
        Raises:
            FileNotFoundError: If manifest doesn't exist
            ValueError: If manifest integrity check fails
        """
        if not os.path.exists(self.manifest_path):
            raise FileNotFoundError(f"Manifest not found at {self.manifest_path}")
        
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        # Validate integrity if checksum exists
        if manifest.get("integrity_checksum"):
            computed_checksum = self._compute_checksum(manifest)
            if computed_checksum != manifest["integrity_checksum"]:
                raise ValueError(f"Manifest integrity check failed. Data may be corrupted.")
        
        return manifest
    
    def add_checkpoint(self, checkpoint: HopCheckpoint) -> None:
        """
        Appends a checkpoint to the manifest.
        
        Note: In V3.8, validation has been consolidated in validator_RES_v3_8.py.
        Validation should be performed before calling this method.
        
        Args:
            checkpoint: The HopCheckpoint to add
        """
        manifest = self.load_manifest()
        
        checkpoint_dict = asdict(checkpoint)
        checkpoint_dict['status'] = checkpoint.status.name
        
        for vr in checkpoint_dict.get('validation_results', []):
            if 'severity' in vr and hasattr(vr['severity'], 'name'):
                vr['severity'] = vr['severity'].name
        
        # Add timestamp if not present
        if 'timestamp' not in checkpoint_dict:
            checkpoint_dict['timestamp'] = datetime.utcnow().isoformat() + "Z"
        
        manifest['hop_checkpoints'].append(checkpoint_dict)
        self._save_manifest(manifest)
    
    def update_checkpoint(self, hop_id: str, updates: dict) -> None:
        """
        Updates an existing checkpoint in the manifest.
        
        Note: In V3.8, validation is handled by validator_RES_v3_8.py.
        
        Args:
            hop_id: The hop_id to update (e.g., "HOP-3")
            updates: Dictionary of fields to update
            
        Raises:
            ValueError: If hop_id not found
        """
        manifest = self.load_manifest()
        checkpoint_found = False
        
        for checkpoint in manifest['hop_checkpoints']:
            if checkpoint.get('hop_id') == hop_id or checkpoint.get('hop_name') == hop_id:
                checkpoint.update(updates)
                checkpoint['last_updated'] = datetime.utcnow().isoformat() + "Z"
                checkpoint_found = True
                break
        
        if not checkpoint_found:
            # Create new checkpoint if doesn't exist
            new_checkpoint = {
                'hop_id': hop_id,
                'hop_name': hop_id,
                'timestamp': datetime.utcnow().isoformat() + "Z",
                **updates
            }
            manifest['hop_checkpoints'].append(new_checkpoint)
        
        self._save_manifest(manifest)
    
    def get_checkpoints(self) -> List[HopCheckpoint]:
        """
        Gets all checkpoints from the manifest as HopCheckpoint objects.
        
        Returns:
            List of HopCheckpoint objects
        """
        manifest = self.load_manifest()
        checkpoints = []
        
        for cp_dict in manifest.get('hop_checkpoints', []):
            # Handle validation results
            validation_results = []
            for vr_dict in cp_dict.get('validation_results', []):
                severity_name = vr_dict.get('severity', 'INFO')
                if isinstance(severity_name, str):
                    vr_dict['severity'] = ValidationSeverity[severity_name]
                validation_results.append(ValidationResult(**vr_dict))
            
            # Handle status
            status_name = cp_dict.get('status', 'PASS')
            if isinstance(status_name, str):
                cp_dict['status'] = HopStatus[status_name]
            cp_dict['validation_results'] = validation_results
            
            # Handle backward compatibility with hop_id vs hop_name
            if 'hop_name' not in cp_dict and 'hop_id' in cp_dict:
                cp_dict['hop_name'] = cp_dict['hop_id']
            
            checkpoints.append(HopCheckpoint(**cp_dict))
        
        return checkpoints
    
    def get_last_successful_checkpoint(self) -> Optional[HopCheckpoint]:
        """
        Gets the last successful checkpoint for resuming.
        
        Returns:
            The last HopCheckpoint with COMPLETED status, or None
        """
        checkpoints = self.get_checkpoints()
        
        for checkpoint in reversed(checkpoints):
            if checkpoint.status in [HopStatus.PASS, HopStatus.COMPLETED]:
                return checkpoint
        
        return None
    
    def _save_manifest(self, manifest_data: dict) -> None:
        """
        Saves the manifest to disk with integrity checksum.
        
        Args:
            manifest_data: The manifest dictionary to save
        """
        # Compute integrity checksum
        manifest_data['integrity_checksum'] = self._compute_checksum(manifest_data)
        
        # Create backup of existing manifest if it exists
        if os.path.exists(self.manifest_path):
            backup_path = self.manifest_path + '.backup'
            os.rename(self.manifest_path, backup_path)
        
        try:
            with open(self.manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest_data, f, indent=2, ensure_ascii=False)
            
            # Remove backup on successful save
            backup_path = self.manifest_path + '.backup'
            if os.path.exists(backup_path):
                os.remove(backup_path)
                
        except Exception as e:
            # Restore from backup on failure
            backup_path = self.manifest_path + '.backup'
            if os.path.exists(backup_path):
                os.rename(backup_path, self.manifest_path)
            raise e
    
    def _compute_checksum(self, manifest_data: dict) -> str:
        """
        Compute SHA256 checksum of manifest data.
        
        Args:
            manifest_data: The manifest dictionary
            
        Returns:
            Hex string of SHA256 checksum
        """
        # Create copy without checksum field
        data_copy = manifest_data.copy()
        data_copy.pop('integrity_checksum', None)
        
        # Serialize deterministically
        json_str = json.dumps(data_copy, sort_keys=True, ensure_ascii=True)
        
        # Compute SHA256
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()


class StateManager:
    """
    High-level state management interface combining manifest and snapshot capabilities.
    V3.8 addition for improved state handling.
    """
    
    def __init__(self, run_path: str):
        """
        Initialize StateManager.
        
        Args:
            run_path: Path to run directory
        """
        self.run_path = run_path
        self.manifest_manager = ManifestManager(run_path)
        self.snapshots = {}
    
    def save_state(self, state_id: str, state_data: dict) -> None:
        """
        Save a state snapshot.
        
        Args:
            state_id: Identifier for the state
            state_data: State data to save
        """
        snapshot = create_state_snapshot(state_data)
        self.snapshots[state_id] = snapshot
        
        # Also persist to file for durability
        snapshot_path = os.path.join(self.run_path, f"state_{state_id}.json")
        with open(snapshot_path, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2)
    
    def load_state(self, state_id: str) -> Optional[dict]:
        """
        Load a state snapshot.
        
        Args:
            state_id: Identifier for the state
            
        Returns:
            State data if found, None otherwise
        """
        # Check in-memory cache first
        if state_id in self.snapshots:
            snapshot = self.snapshots[state_id]
            if validate_state_snapshot(snapshot):
                return snapshot["data"]
        
        # Try loading from file
        snapshot_path = os.path.join(self.run_path, f"state_{state_id}.json")
        if os.path.exists(snapshot_path):
            with open(snapshot_path, 'r', encoding='utf-8') as f:
                snapshot = json.load(f)
            if validate_state_snapshot(snapshot):
                self.snapshots[state_id] = snapshot
                return snapshot["data"]
        
        return None
    
    def merge_state(self, base_state: dict, updates: dict) -> dict:
        """
        Merge state updates into base state.
        
        Args:
            base_state: Base state dictionary
            updates: Updates to apply
            
        Returns:
            Merged state
        """
        return merge_state_updates(base_state, updates)


# Additional utility functions for state management
def create_state_snapshot(data: dict) -> dict:
    """
    Create a snapshot of the current state with metadata.
    
    Args:
        data: The state data to snapshot
        
    Returns:
        Dictionary containing state data and metadata
    """
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "data": data,
        "checksum": hashlib.sha256(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()
    }


def validate_state_snapshot(snapshot: dict) -> bool:
    """
    Validate a state snapshot's integrity.
    
    Args:
        snapshot: The snapshot to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not snapshot.get("data") or not snapshot.get("checksum"):
        return False
    
    computed_checksum = hashlib.sha256(
        json.dumps(snapshot["data"], sort_keys=True).encode()
    ).hexdigest()
    
    return computed_checksum == snapshot["checksum"]


def merge_state_updates(base_state: dict, updates: dict) -> dict:
    """
    Safely merge state updates into base state.
    
    Args:
        base_state: The base state dictionary
        updates: Updates to apply
        
    Returns:
        Merged state dictionary
    """
    merged = base_state.copy()
    
    for key, value in updates.items():
        if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
            # Recursive merge for nested dicts
            merged[key] = merge_state_updates(merged[key], value)
        else:
            # Direct update
            merged[key] = value
    
    return merged


# Module exports
__all__ = [
    'ManifestManager',
    'StateManager',
    'create_state_snapshot',
    'validate_state_snapshot',
    'merge_state_updates'
]
