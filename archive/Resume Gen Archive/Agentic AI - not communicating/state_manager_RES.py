# File: state_manager_RES.py
# Version: 16.30
# State serialization and deserialization layer for workflow hops

import json
import os
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from models_RES import (
    ThematicAnalysis,
    ValidationResult,
    ValidationSeverity,
    HopCheckpoint,
    HopStatus
)


class StateSerializer:
    """
    Manages serialization and deserialization of workflow hop outputs.
    
    This class abstracts the file system state layer, providing:
    - Standardized file paths for each hop
    - Type-safe serialization (Python objects -> JSON)
    - Type-safe deserialization (JSON -> Python objects)
    - Support for complex types (ThematicAnalysis, ValidationResult, etc.)
    """
    
    def __init__(self, run_path: str, run_id: str):
        """
        Initialize the StateSerializer.
        
        Args:
            run_path: Absolute path to the run directory
            run_id: Unique identifier for this run
        """
        self.run_path = run_path
        self.run_id = run_id
        
        # This map defines the file system state configuration
        # Each hop has a filename and expected type
        self.HOP_CONFIG = {
            0: {
                "filename": f"{self.run_id}_HOP-0_ThematicAnalysis.json",
                "type": ThematicAnalysis
            },
            1: {
                "filename": f"{self.run_id}_HOP-1_ExtractedData.json",
                "type": dict
            },
            2: {
                "filename": f"{self.run_id}_HOP-2_EnrichedScaffold.json",
                "type": dict
            },
            3: {
                "filename": f"{self.run_id}_HOP-3_ArtistOutput.json",
                "type": dict
            },
            4: {
                "filename": f"{self.run_id}_HOP-4_StagingBuffer.json",
                "type": dict
            },
            5: {
                "filename": f"{self.run_id}_HOP-5_ValidationResults.json",
                "type": "list[ValidationResult]"  # Special handling needed
            },
            7: {
                "filename": f"{self.run_id}_HOP-7_FilePaths.json",
                "type": dict
            },
            8: {
                "filename": f"{self.run_id}_HOP-8_QAReport.json",
                "type": dict
            },
            # HOP-6 is a decision gate, not a file state
        }
    
    def get_path_for_hop(self, hop_num: int) -> str:
        """
        Gets the standardized output path for a given hop.
        
        Args:
            hop_num: The hop number (0-8)
            
        Returns:
            Absolute path to the hop's output file
            
        Raises:
            ValueError: If no config exists for the hop number
        """
        if hop_num not in self.HOP_CONFIG:
            raise ValueError(f"No file path config found for hop {hop_num}")
        return os.path.join(self.run_path, self.HOP_CONFIG[hop_num]['filename'])
    
    def save(self, hop_num: int, data: Any) -> None:
        """
        Serializes and saves hop output data to the file system.
        
        Args:
            hop_num: The hop number
            data: The data to save (will be serialized based on hop type)
            
        Raises:
            ValueError: If no config exists for the hop number
        """
        config = self.HOP_CONFIG.get(hop_num)
        if not config:
            raise ValueError(f"Cannot save: No config for hop {hop_num}")

        output_path = self.get_path_for_hop(hop_num)
        data_to_save = self._serialize(data, config['type'])
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)
    
    def load(self, hop_num: int) -> Any:
        """
        Loads and deserializes hop output data from the file system.
        
        Args:
            hop_num: The hop number
            
        Returns:
            The deserialized data (type depends on hop config)
            
        Raises:
            ValueError: If no config exists for the hop number
            FileNotFoundError: If the hop output file doesn't exist
        """
        config = self.HOP_CONFIG.get(hop_num)
        if not config:
            raise ValueError(f"Cannot load: No config for hop {hop_num}")
            
        input_path = self.get_path_for_hop(hop_num)
        if not os.path.exists(input_path):
            raise FileNotFoundError(
                f"Cannot load state for hop {hop_num}: File not found at {input_path}"
            )
            
        with open(input_path, 'r', encoding='utf-8') as f:
            data_dict = json.load(f)
            
        return self._deserialize(data_dict, config['type'])
    
    def exists(self, hop_num: int) -> bool:
        """
        Checks if a hop's output file exists.
        
        Args:
            hop_num: The hop number
            
        Returns:
            True if the file exists, False otherwise
        """
        try:
            path = self.get_path_for_hop(hop_num)
            return os.path.exists(path)
        except ValueError:
            return False
    
    def _serialize(self, data: Any, expected_type: Any) -> Any:
        """
        Converts live Python objects to JSON-safe dictionaries/lists.
        
        Args:
            data: The Python object to serialize
            expected_type: The expected type (from HOP_CONFIG)
            
        Returns:
            JSON-serializable data
        """
        if expected_type == ThematicAnalysis:
            # Convert dataclass to dict
            return asdict(data)
        
        if expected_type == "list[ValidationResult]":
            # Save ValidationResult list with Enum conversion
            serialized_list = []
            for vr in data:
                vr_dict = asdict(vr)
                # Convert Enum to string name for JSON storage
                vr_dict["severity"] = vr.severity.name
                serialized_list.append(vr_dict)
            return serialized_list
        
        if expected_type == dict:
            # Already JSON-safe
            return data
        
        # Default: assume already serializable
        return data
    
    def _deserialize(self, data_dict: Any, expected_type: Any) -> Any:
        """
        Converts JSON-safe dicts/lists back into live Python objects.
        
        Args:
            data_dict: The deserialized JSON data
            expected_type: The expected type (from HOP_CONFIG)
            
        Returns:
            Reconstructed Python object
        """
        if expected_type == ThematicAnalysis:
            # Use the static method from rag_RES.py
            # Import here to avoid circular dependencies
            from rag_RES import EnhancedJobDescriptionAnalyzer
            return EnhancedJobDescriptionAnalyzer._dict_to_thematic_analysis(data_dict)
        
        if expected_type == "list[ValidationResult]":
            # Re-hydrate ValidationResult list with Enum reconstruction
            deserialized_list = []
            for vr_dict in data_dict:
                # Convert string name back to Enum
                severity_name = vr_dict.get("severity", "INFO")
                vr_dict["severity"] = ValidationSeverity[severity_name]
                deserialized_list.append(ValidationResult(**vr_dict))
            return deserialized_list
        
        if expected_type == dict:
            # Already correct type
            return data_dict
        
        # Default: return as-is
        return data_dict
    
    def delete_hop_file(self, hop_num: int) -> bool:
        """
        Deletes a hop's output file if it exists.
        
        Args:
            hop_num: The hop number
            
        Returns:
            True if file was deleted, False if it didn't exist
        """
        try:
            file_path = self.get_path_for_hop(hop_num)
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except (ValueError, OSError):
            return False
    
    def get_all_hop_files(self) -> Dict[int, str]:
        """
        Gets all hop files that currently exist.
        
        Returns:
            Dictionary mapping hop_num -> file_path for existing files
        """
        existing_files = {}
        for hop_num in self.HOP_CONFIG.keys():
            file_path = self.get_path_for_hop(hop_num)
            if os.path.exists(file_path):
                existing_files[hop_num] = file_path
        return existing_files


class ManifestManager:
    """
    Manages the run_manifest.json file for a workflow run.
    
    This class handles:
    - Creating initial manifests for new runs
    - Loading manifests for resumed runs
    - Updating manifests with checkpoint data
    """
    
    def __init__(self, run_path: str):
        """
        Initialize the ManifestManager.
        
        Args:
            run_path: Absolute path to the run directory
        """
        self.run_path = run_path
        self.manifest_path = os.path.join(run_path, "run_manifest.json")
    
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
        from datetime import datetime
        
        manifest = {
            "run_id": run_id,
            "engine_version": engine_version,
            "start_time_utc": datetime.utcnow().isoformat() + "Z",
            "job_input": job_input,
            "master_resume_hash": master_resume_hash,
            "hop_checkpoints": []
        }
        
        self._save_manifest(manifest)
        return manifest
    
    def load_manifest(self) -> dict:
        """
        Loads the manifest from disk.
        
        Returns:
            The manifest dictionary
            
        Raises:
            FileNotFoundError: If manifest doesn't exist
        """
        if not os.path.exists(self.manifest_path):
            raise FileNotFoundError(f"Manifest not found at {self.manifest_path}")
        
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def add_checkpoint(self, checkpoint: HopCheckpoint) -> None:
        """
        Appends a checkpoint to the manifest.
        
        Args:
            checkpoint: The HopCheckpoint to add
        """
        manifest = self.load_manifest()
        
        # Convert checkpoint to dict with enum serialization
        checkpoint_dict = asdict(checkpoint)
        
        # Convert HopStatus enum to string name
        checkpoint_dict['status'] = checkpoint.status.name
        
        # Convert ValidationSeverity enums in validation_results
        for vr in checkpoint_dict.get('validation_results', []):
            if 'severity' in vr and hasattr(vr['severity'], 'name'):
                vr['severity'] = vr['severity'].name
        
        manifest['hop_checkpoints'].append(checkpoint_dict)
        self._save_manifest(manifest)
    
    def update_checkpoint(self, hop_id: str, updates: dict) -> None:
        """
        Updates an existing checkpoint in the manifest.
        
        Args:
            hop_id: The hop_id to update (e.g., "HOP-3")
            updates: Dictionary of fields to update
        """
        manifest = self.load_manifest()
        for checkpoint in manifest['hop_checkpoints']:
            if checkpoint['hop_id'] == hop_id:
                checkpoint.update(updates)
                break
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
            # Reconstruct ValidationResult objects
            validation_results = []
            for vr_dict in cp_dict.get('validation_results', []):
                severity_name = vr_dict.get('severity', 'INFO')
                vr_dict['severity'] = ValidationSeverity[severity_name]
                validation_results.append(ValidationResult(**vr_dict))
            
            # Reconstruct HopStatus enum
            status_name = cp_dict.get('status', 'PASS')
            cp_dict['status'] = HopStatus[status_name]
            cp_dict['validation_results'] = validation_results
            
            checkpoints.append(HopCheckpoint(**cp_dict))
        
        return checkpoints
    
    def _save_manifest(self, manifest_data: dict) -> None:
        """
        Saves the manifest to disk.
        
        Args:
            manifest_data: The manifest dictionary to save
        """
        # TODO: Add file locking for thread-safety if needed
        with open(self.manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)