"""Stub for canon_validator module."""


class CanonValidator:
    """Stub for canon validation."""
    def __init__(self, *args, **kwargs):
        self.rules = []
    
    def validate(self, target) -> bool:
        return True
    
    def get_violations(self):
        return []
    
    def validate_design_compliance(self, file_path: str = None, figma_node_id: str = None, component_id: str = None, **kwargs) -> dict:
        """
        Validate design compliance between code and Figma design tokens.
        
        Args:
            file_path: Path to the source file to validate
            figma_node_id: Figma node ID to check against
        
        Returns:
            dict with 'compliant', 'violations', 'fixes_applied' keys
        """
        return {
            "compliant": True,
            "violations": [],
            "fixes_applied": []
        }
