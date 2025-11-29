#!/usr/bin/env python3
"""
Golden Datasets
Section 17: Evaluation Framework - Golden dataset management
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class DatasetType(str, Enum):
    """Dataset type enumeration"""
    PLANNING = "planning"
    EXECUTION = "execution"
    ORCHESTRATION = "orchestration"
    GENERAL = "general"

@dataclass
class GoldenDataset:
    """Golden dataset for evaluation"""
    dataset_id: str
    dataset_type: DatasetType
    test_cases: List[Dict[str, Any]]
    expected_outputs: List[Dict[str, Any]]

class GoldenDatasetManager:
    """Manages golden datasets for evaluation"""
    
    def __init__(self):
        self.datasets: Dict[str, GoldenDataset] = {}
    
    def register_dataset(self, dataset: GoldenDataset) -> bool:
        """Register golden dataset"""
        try:
            self.datasets[dataset.dataset_id] = dataset
            logger.info(f"Golden dataset registered: {dataset.dataset_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to register dataset: {e}")
            return False
    
    def get_dataset(self, dataset_id: str) -> Optional[GoldenDataset]:
        """Get golden dataset by ID"""
        return self.datasets.get(dataset_id)

# Re-export components
__all__ = [
    'GoldenDatasetManager', 'GoldenDataset', 'DatasetType'
]
