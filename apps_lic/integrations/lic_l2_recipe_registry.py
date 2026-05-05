"""
Recipe registry adapter for apps_lic L2 recipes.

This module implements the recipe registry pattern for apps_lic:
- agentic_core owns the recipe resolution protocol and execution lifecycle
- apps_lic owns only domain recipe declarations and registered L2 step adapter implementations
- apps_lic/__main__.py owns neither
"""

from pathlib import Path
from typing import Any, Callable, Dict, Optional
import yaml


# Registry storage
_static_recipes: Dict[str, Dict[str, Any]] = {}
_managed_recipes: Dict[str, Dict[str, Any]] = {}


def register_static_recipe(
    app_name: str,
    dag_path: str,
    step_adapters: Dict[str, Callable],
    recipe_id: Optional[str] = None,
) -> str:
    """
    Register a static L2 recipe for the R4 deterministic pipeline.
    
    Args:
        app_name: The application name (e.g., "apps_lic")
        dag_path: Path to the static DAG YAML file
        step_adapters: Dictionary mapping step names to adapter functions
        recipe_id: Optional recipe ID (defaults to app_name + "_static")
        
    Returns:
        The registered recipe ID
    """
    if recipe_id is None:
        recipe_id = f"{app_name}_static"
    
    _static_recipes[recipe_id] = {
        "app_name": app_name,
        "dag_path": dag_path,
        "step_adapters": step_adapters,
        "recipe_type": "static",
    }
    
    return recipe_id


def register_managed_recipe(
    app_name: str,
    dag_path: str,
    step_adapters: Dict[str, Callable],
    recipe_id: Optional[str] = None,
) -> str:
    """
    Register a managed L2 recipe for the R3R4 managed workflow pipeline.
    
    Args:
        app_name: The application name (e.g., "apps_lic")
        dag_path: Path to the managed DAG YAML file
        step_adapters: Dictionary mapping step names to adapter functions
        recipe_id: Optional recipe ID (defaults to app_name + "_managed")
        
    Returns:
        The registered recipe ID
    """
    if recipe_id is None:
        recipe_id = f"{app_name}_managed"
    
    _managed_recipes[recipe_id] = {
        "app_name": app_name,
        "dag_path": dag_path,
        "step_adapters": step_adapters,
        "recipe_type": "managed",
    }
    
    return recipe_id


def resolve_recipe(
    app_name: str,
    route_family: str = "static",
) -> Optional[Callable]:
    """
    Resolve a recipe for the given app and route family.
    
    Args:
        app_name: The application name (e.g., "apps_lic")
        route_family: The route family ("static" or "managed")
        
    Returns:
        The resolved recipe callable, or None if not found
        
    Note:
        Resolution failure must fail closed through Exit V6.
        This function returns None to signal that the caller must handle
        the failure by emitting an R5 terminal packet.
    """
    if route_family == "static":
        recipe_id = f"{app_name}_static"
        recipe = _static_recipes.get(recipe_id)
    elif route_family == "managed":
        recipe_id = f"{app_name}_managed"
        recipe = _managed_recipes.get(recipe_id)
    else:
        return None
    
    if recipe is None:
        return None
    
    # Return a callable that executes the recipe
    def recipe_executor(context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the registered recipe."""
        # Load DAG definition
        dag_path = Path(recipe["dag_path"])
        if not dag_path.exists():
            raise FileNotFoundError(f"DAG file not found: {dag_path}")
        
        with open(dag_path) as f:
            dag = yaml.safe_load(f)
        
        # Execute steps in order
        result = context.copy()
        for step_def in dag.get("stages", []):
            # Support both 'stage_id' (from DAG) and 'name'/'step' keys
            step_name = step_def.get("stage_id") or step_def.get("name") or step_def.get("step")
            if step_name is None:
                raise ValueError(f"Step definition missing stage_id/name/step: {step_def}")
            
            adapter = recipe["step_adapters"].get(step_name)
            
            if adapter is None:
                raise ValueError(f"No adapter registered for step: {step_name}")
            
            result = adapter(result, step_def)
        
        return result
    
    return recipe_executor


def get_registered_recipes() -> Dict[str, Dict[str, Any]]:
    """Return all registered recipes (for testing and introspection)."""
    return {
        "static": _static_recipes.copy(),
        "managed": _managed_recipes.copy(),
    }


def clear_registry():
    """Clear all registered recipes (for testing)."""
    _static_recipes.clear()
    _managed_recipes.clear()


# Default recipe registration for apps_lic
def _register_default_recipes():
    """Register default apps_lic recipes."""
    from apps_lic.integrations import lic_l2_step_adapters as adapters
    
    repo_root = Path(__file__).resolve().parents[2]
    
    # Register static R4 recipe
    register_static_recipe(
        app_name="apps_lic",
        dag_path=str(repo_root / "apps_lic" / "config" / "apps_lic_static_dag.yaml"),
        step_adapters={
            # E1 Prep
            "load_manifest": adapters.load_manifest,
            "bind_route_policy_blueprint_replay": adapters.bind_route_policy_blueprint_replay,
            "freeze_execution_context": adapters.freeze_execution_context,
            # E2 Valid (mapped to validation functions)
            "validate_context": adapters.validate_manifest_schema,  # Main validation entry
            # E3 Exec
            "plan_message": adapters.plan_message,
            "compile_prompt": adapters.compile_prompt,
            "compose_draft": adapters.compose_draft_using_compiled_prompt_artifact,
            # E4 Heal (optional - only used when repair needed)
            "compile_repair_prompt_if_needed": adapters.compile_repair_prompt_if_needed,
            "omit_unsupported_claims": adapters.omit_unsupported_claims,
            "remove_forbidden_antipatterns": adapters.remove_forbidden_antipatterns,
            "repair_channel_length": adapters.repair_channel_length,
            "repair_ask_friction": adapters.repair_ask_friction,
            "repair_voice_rules": adapters.repair_voice_rules,
            # E5 Seal
            "seal_output": adapters.seal_l2_artifact_for_exit,
        },
        recipe_id="apps_lic_static",
    )

    # Register managed R3R4 recipe
    register_managed_recipe(
        app_name="apps_lic",
        dag_path=str(repo_root / "apps_lic" / "config" / "apps_lic_managed_dag.yaml"),
        step_adapters={
            # R3 Research Phase (stages 1-4)
            "validate_request_for_briefing": adapters.validate_request_for_briefing,
            "authorize_research": adapters.authorize_research,
            "call_apps_research": adapters.research_bridge_adapter,
            "validate_research_and_build_manifest": adapters.validate_research_and_build_manifest,
            # R4 Outreach Phase (stages 5-8) - mirrors static DAG
            "plan_message": adapters.plan_message,
            "compose_draft": adapters.compose_draft_using_compiled_prompt_artifact,
            "seal_output": adapters.seal_l2_artifact_for_exit,
            "emit_managed_workflow_receipt": adapters.emit_managed_workflow_receipt,
        },
        recipe_id="apps_lic_managed",
    )


# Register default recipes on module load
_register_default_recipes()


if __name__ == "__main__":
    # Self-test
    print("lic_l2_recipe_registry loaded successfully")
    recipes = get_registered_recipes()
    print(f"Static recipes: {len(recipes['static'])}")
    print(f"Managed recipes: {len(recipes['managed'])}")
    for recipe_id in recipes['static']:
        print(f"  - {recipe_id}")
