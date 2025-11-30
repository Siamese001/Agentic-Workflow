# lic_k7_assembly - K7 assembly engine
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class K7Assembly:
    """K7 assembly data structure"""
    final_content: str = ""
    components: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.components is None:
            self.components = []
        if self.metadata is None:
            self.metadata = {}

class LIC_K7_Assembly:
    """K7 assembly engine"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    def assemble_final_message(self, components: Dict[str, Any]) -> K7Assembly:
        """Assemble final message from all components"""
        content_parts = []
        component_names = []

        for key, value in components.items():
            if hasattr(value, 'content'):
                content_parts.append(value.content)
                component_names.append(key)
            elif isinstance(value, str):
                content_parts.append(value)
                component_names.append(key)

        final_content = "\n\n".join(content_parts)

        return K7Assembly(
            final_content=final_content,
            components=component_names,
            metadata={"original_components": components}
        )

    def run(self, input_data: Dict[str, Any]) -> K7Assembly:
        """Run final assembly"""
        return self.assemble_final_message(input_data)
