#!/usr/bin/env python3
"""
Prompt Definitions
Section 3: Canonical Repository Tree - Prompt Governance Definitions
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime

# Import additional prompt definitions components
from .system_prompts import get_system_prompt, initialize_system_prompts, update_system_template
from .developer_prompts import get_developer_prompt, list_developer_templates, create_custom_prompt
from .user_prompts import get_user_prompt, format_user_query, generate_response_template

logger = logging.getLogger(__name__)

class PromptDefinition:
    """Core prompt definitions and templates"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.definition_id = self.config.get("definition_id", "")
        self.name = self.config.get("name", "")
        self.category = self.config.get("category", "general")
        self.template = self.config.get("template", "")
        self.parameters = self.config.get("parameters", {})
    
    def create_definition(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new prompt definition"""
        try:
            definition = {
                "definition_id": f"def_{hash(str(prompt_data)) % 10000}",
                "name": prompt_data.get("name", "Unnamed Definition"),
                "category": prompt_data.get("category", "general"),
                "template": prompt_data.get("template", ""),
                "parameters": prompt_data.get("parameters", {}),
                "variables": prompt_data.get("variables", []),
                "examples": prompt_data.get("examples", []),
                "constraints": prompt_data.get("constraints", {}),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "version": "1.0.0"
            }
            
            logger.info(f"Created prompt definition: {definition['definition_id']}")
            return definition
            
        except Exception as e:
            logger.error(f"Failed to create prompt definition: {e}")
            return {"error": str(e)}
    
    def render_template(self, definition_id: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Render prompt template with variables"""
        try:
            # Simulate template rendering
            mock_definitions = {
                "def_1234": {
                    "template": "Hello {name}, you are applying for {role} position. Your skills in {skills} make you a strong candidate.",
                    "parameters": {"name": "string", "role": "string", "skills": "list"}
                }
            }
            
            definition = mock_definitions.get(definition_id, {})
            template = definition.get("template", "")
            
            # Simple variable substitution
            rendered = template
            for key, value in variables.items():
                rendered = rendered.replace(f"{{{key}}}", str(value))
            
            result = {
                "definition_id": definition_id,
                "rendered_prompt": rendered,
                "variables_used": list(variables.keys()),
                "rendered_at": datetime.now().isoformat()
            }
            
            logger.info(f"Rendered template for definition: {definition_id}")
            return result
            
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            return {"error": str(e)}
    
    def validate_parameters(self, definition_id: str, provided_params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate provided parameters against definition requirements"""
        try:
            mock_definitions = {
                "def_1234": {
                    "parameters": {"name": "string", "role": "string", "skills": "list"}
                }
            }
            
            definition = mock_definitions.get(definition_id, {})
            required_params = definition.get("parameters", {})
            
            validation_result = {
                "is_valid": True,
                "missing_params": [],
                "invalid_types": [],
                "extra_params": []
            }
            
            # Check required parameters
            for param_name, param_type in required_params.items():
                if param_name not in provided_params:
                    validation_result["is_valid"] = False
                    validation_result["missing_params"].append(param_name)
                else:
                    # Simple type validation
                    provided_value = provided_params[param_name]
                    if param_type == "string" and not isinstance(provided_value, str):
                        validation_result["is_valid"] = False
                        validation_result["invalid_types"].append(f"{param_name}: expected {param_type}")
                    elif param_type == "list" and not isinstance(provided_value, list):
                        validation_result["is_valid"] = False
                        validation_result["invalid_types"].append(f"{param_name}: expected {param_type}")
            
            # Check for extra parameters
            for param_name in provided_params:
                if param_name not in required_params:
                    validation_result["extra_params"].append(param_name)
            
            logger.info(f"Parameter validation for {definition_id}: {'valid' if validation_result['is_valid'] else 'invalid'}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Parameter validation failed: {e}")
            return {"is_valid": False, "error": str(e)}
    
    def get_definition_info(self, definition_id: str) -> Dict[str, Any]:
        """Get information about a prompt definition"""
        try:
            mock_definitions = {
                "def_1234": {
                    "name": "Resume Generation Prompt",
                    "category": "resume",
                    "template": "Hello {name}, you are applying for {role} position...",
                    "parameters": {"name": "string", "role": "string", "skills": "list"},
                    "variables": ["name", "role", "skills"],
                    "version": "1.0.0"
                }
            }
            
            definition = mock_definitions.get(definition_id, {})
            
            if not definition:
                return {"error": f"Definition {definition_id} not found"}
            
            info = {
                "definition_id": definition_id,
                **definition,
                "parameter_count": len(definition.get("parameters", {})),
                "variable_count": len(definition.get("variables", [])),
                "template_length": len(definition.get("template", ""))
            }
            
            logger.info(f"Retrieved definition info: {definition_id}")
            return info
            
        except Exception as e:
            logger.error(f"Failed to get definition info: {e}")
            return {"error": str(e)}

def create_prompt_definition(config: Optional[Dict[str, Any]] = None) -> PromptDefinition:
    """Factory function to create prompt definition instance"""
    return PromptDefinition(config)

# Re-export components
__all__ = [
    'PromptDefinition', 'create_prompt_definition',
    'get_system_prompt', 'initialize_system_prompts', 'update_system_template',
    'get_developer_prompt', 'list_developer_templates', 'create_custom_prompt',
    'get_user_prompt', 'format_user_query', 'generate_response_template'
]





