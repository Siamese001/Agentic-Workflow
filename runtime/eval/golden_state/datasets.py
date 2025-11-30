# datasets - Golden dataset loading utilities
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class GoldenCase:
    """Individual golden test case"""
    id: str
    input_data: Dict[str, Any]
    expected_output: Dict[str, Any]
    expected_keypoints: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.expected_keypoints is None:
            self.expected_keypoints = []
        # Support both id and case_id for compatibility
        self.case_id = self.id

@dataclass
class GoldenDataset:
    """Collection of golden test cases"""
    name: str
    description: str
    cases: List[GoldenCase]
    version: str = "1.0"
    
    def get_case(self, case_id: str) -> Optional[GoldenCase]:
        """Get a specific case by ID"""
        for case in self.cases:
            if case.case_id == case_id:
                return case
        return None
    
    def get_all_cases(self) -> List[GoldenCase]:
        """Get all cases"""
        return self.cases.copy()

class GoldenDatasetLoader:
    """Loads and manages golden datasets"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path(__file__).parent / "data"
        self.datasets: Dict[str, GoldenDataset] = {}
    
    def load_dataset(self, dataset_name: str) -> GoldenDataset:
        """Load a specific golden dataset"""
        if dataset_name in self.datasets:
            return self.datasets[dataset_name]
        
        # Mock dataset loading - in real implementation would read from files
        mock_cases = [
            GoldenCase(
                id="test_001",
                input_data={"text": "Hello world", "context": "greeting"},
                expected_output={"classification": "positive", "confidence": 0.9},
                expected_keypoints=["positive_sentiment", "greeting"],
                metadata={"category": "sentiment"}
            ),
            GoldenCase(
                id="test_002", 
                input_data={"text": "This is terrible", "context": "review"},
                expected_output={"classification": "negative", "confidence": 0.85},
                expected_keypoints=["negative_sentiment", "review"],
                metadata={"category": "sentiment"}
            )
        ]
        
        dataset = GoldenDataset(
            name=dataset_name,
            description=f"Mock golden dataset: {dataset_name}",
            cases=mock_cases
        )
        
        self.datasets[dataset_name] = dataset
        return dataset
    
    def load_all_datasets(self) -> Dict[str, GoldenDataset]:
        """Load all available datasets"""
        # Mock loading of standard datasets
        standard_datasets = ["sentiment", "classification", "generation"]
        for dataset_name in standard_datasets:
            self.load_dataset(dataset_name)
        return self.datasets
    
    def get_available_datasets(self) -> List[str]:
        """Get list of available dataset names"""
        return list(self.datasets.keys())

# Global loader instance
_global_loader: Optional[GoldenDatasetLoader] = None

def get_golden_loader() -> GoldenDatasetLoader:
    """Get the global golden dataset loader"""
    global _global_loader
    if _global_loader is None:
        _global_loader = GoldenDatasetLoader()
    return _global_loader

def load_golden_cases(dataset_name: str = "default") -> List[GoldenCase]:
    """Load golden test cases for evaluation"""
    loader = get_golden_loader()
    dataset = loader.load_dataset(dataset_name)
    return dataset.get_all_cases()

def reset_golden_loader() -> None:
    """Reset the global golden loader (for testing)"""
    global _global_loader
    _global_loader = None
