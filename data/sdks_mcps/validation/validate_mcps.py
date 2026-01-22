"""MCP Validation Script - Validates all schemas and cross-references
Ensures data/sdks_mcps/ is the immutable single source of truth.
"""

import json
import os
import sys

import jsonschema


def validate_json_schema(schema: dict[str, object]) -> list[str]:
    """Validate a JSON schema against Draft 07 specification.

    Args:
        schema: JSON schema dictionary

    Returns:
        List of validation errors
    """
    errors = []

    try:
        # Check for required fields
        if "$schema" not in schema:
            errors.append("Missing $schema field")
        elif schema["$schema"] != "http://json-schema.org/draft-07/schema#":
            errors.append(f"Invalid schema version: {schema.get('$schema')}")

        # Validate against meta-schema
        with open("draft-07.json") as f:
            meta_schema = json.load(f)

        jsonschema.validate(schema, meta_schema)

    except FileNotFoundError:
        errors.append("Draft-07 meta-schema not found")
    except jsonschema.ValidationError as e:
        errors.append(f"Schema validation error: {e.message}")
    except Exception as e:
        errors.append(f"Unexpected validation error: {e}")

    return errors


def validate_mcp_catalogs() -> dict[str, object]:
    """Validate all MCP catalog files."""
    results = {"valid": True, "errors": [], "catalogs": {}}

    catalog_dir = Path("mcp_catalog")
    catalog_files = ["openai_mcp_v3.json", "anthropic_mcp_v2.json", "google_mcp_v1.json"]

    for catalog_file in catalog_files:
        catalog_path = catalog_dir / catalog_file

        if not catalog_path.exists():
            results["errors"].append(f"Missing catalog: {catalog_file}")
            results["valid"] = False
            continue

        try:
            with open(catalog_path) as f:
                catalog = json.load(f)

            # Validate catalog structure
            catalog_errors = []

            # Required fields
            required_fields = ["title", "description", "version", "provider", "models"]
            for field in required_fields:
                if field not in catalog:
                    catalog_errors.append(f"Missing required field: {field}")

            # Validate models section
            if "models" in catalog:
                for model_name, model_config in catalog["models"].items():
                    if "context_window" not in model_config:
                        catalog_errors.append(f"Model {model_name} missing context_window")
                    if "pricing" not in model_config:
                        catalog_errors.append(f"Model {model_name} missing pricing")

            # Validate cross-references
            if "structured_output_schemas" in catalog:
                for schema_name, schema_ref in catalog["structured_output_schemas"].items():
                    if "file" not in schema_ref:
                        catalog_errors.append(f"Schema {schema_name} missing file reference")
                    else:
                        # Check if referenced file exists
                        ref_path = Path(schema_ref["file"])
                        if not ref_path.exists():
                            catalog_errors.append(
                                f"Referenced file not found: {schema_ref['file']}"
                            )

            if "tool_specifications" in catalog:
                for tool_name, tool_ref in catalog["tool_specifications"].items():
                    if "file" not in tool_ref:
                        catalog_errors.append(f"Tool spec {tool_name} missing file reference")
                    else:
                        ref_path = Path(tool_ref["file"])
                        if not ref_path.exists():
                            catalog_errors.append(f"Referenced file not found: {tool_ref['file']}")

            results["catalogs"][catalog_file] = {
                "valid": len(catalog_errors) == 0,
                "errors": catalog_errors,
            }

            if catalog_errors:
                results["errors"].extend([f"{catalog_file}: {err}" for err in catalog_errors])
                results["valid"] = False

        except json.JSONDecodeError as e:
            results["errors"].append(f"Invalid JSON in {catalog_file}: {e}")
            results["valid"] = False
        except Exception as e:
            results["errors"].append(f"Error validating {catalog_file}: {e}")
            results["valid"] = False

    return results


def validate_python_files() -> dict[str, object]:
    """Validate all Python files for syntax and imports."""
    results = {"valid": True, "errors": [], "files": {}}

    python_dirs = [
        "openai_sdk",
        "anthropic_sdk",
        "google_vertex_sdk",
        "client_wrappers",
        "reference_clients",
    ]

    for python_dir in python_dirs:
        for py_file in Path(python_dir).rglob("*.py"):
            try:
                # Check syntax
                with open(py_file) as f:
                    code = f.read()

                compile(code, str(py_file), "exec")

                # Check imports
                # NOTE: importlib.tool is not a standard module. This line will likely cause an AttributeError.
                # It's kept as-is to adhere to "Do not change logic" for non-syntax errors.
                spec = importlib.tool.spec_from_file_location("module", py_file)
                if spec and spec.loader:
                    module = importlib.tool.module_from_spec(spec)

                    # Check for environment variable references
                    env_vars = []
                    for line in code.split("\n"):
                        if "os.getenv(" in line:
                            # Extract env var name
                            start = line.find("os.getenv(") + 9
                            end = line.find(")", start)
                            if start > 8 and end > start:
                                env_var = line[start:end].strip("\"'")
                                env_vars.append(env_var)

                    results["files"][str(py_file)] = {
                        "valid": True,
                        "syntax_valid": True,
                        "env_vars": env_vars,
                    }

            except SyntaxError as e:
                results["errors"].append(f"Syntax error in {py_file}: {e}")
                results["valid"] = False
                results["files"][str(py_file)] = {"valid": False, "error": str(e)}
            except Exception as e:
                results["errors"].append(f"Error checking {py_file}: {e}")
                results["valid"] = False
                results["files"][str(py_file)] = {"valid": False, "error": str(e)}

    return results


def validate_schemas() -> dict[str, object]:
    """Validate all JSON schema files."""
    results = {"valid": True, "errors": [], "schemas": {}}

    schema_files = [
        "openai_sdk/v1.53.0/structured_output_schemas/resume_extract_v4.json",
        "openai_sdk/v1.53.0/structured_output_schemas/lic_message_v3.json",
        "openai_sdk/v1.53.0/tool_calling_spec/full_tool_set_v2025.json",
        "anthropic_sdk/v0.34.2/tool_use_v2/exact_tool_format_we_send.json",
        "google_vertex_sdk/v1.68.0/code_execution_tool_spec/gemini_code_interpreter_v2.json",
    ]

    for schema_file in schema_files:
        schema_path = Path(schema_file)

        if not schema_path.exists():
            results["errors"].append(f"Missing schema file: {schema_file}")
            results["valid"] = False
            continue

        try:
            with open(schema_path) as f:
                schema = json.load(f)

            # Validate schema structure
            schema_errors = validate_json_schema(schema)

            results["schemas"][schema_file] = {
                "valid": len(schema_errors) == 0,
                "errors": schema_errors,
            }

            if schema_errors:
                results["errors"].extend([f"{schema_file}: {err}" for err in schema_errors])
                results["valid"] = False

        except json.JSONDecodeError as e:
            results["errors"].append(f"Invalid JSON in {schema_file}: {e}")
            results["valid"] = False
        except Exception as e:
            results["errors"].append(f"Error validating {schema_file}: {e}")
            results["valid"] = False

    return results


def check_environment_variables() -> dict[str, object]:
    """Check for required environment variables."""
    results = {"valid": True, "errors": [], "env_vars": {}}

    required_vars = {
        "OPENAI_API_KEY": "OpenAI client",
        "ANTHROPIC_API_KEY": "Anthropic client",
        "GOOGLE_CLOUD_PROJECT": "Google Vertex AI",
    }

    for var_name, description in required_vars.items():
        var_value = os.getenv(var_name)
        results["env_vars"][var_name] = {
            "present": var_value is not None,
            "description": description,
        }

        if var_value is None:
            results["errors"].append(f"Missing environment variable: {var_name} ({description})")
            # Don't fail validation for missing env vars, just warn

    return results


def main():
    """Run all validation checks."""

    # Change to sdks_mcps directory
    os.chdir(Path(__file__).parent.parent)

    # Run validations
    mcp_results = validate_mcp_catalogs()
    python_results = validate_python_files()
    schema_results = validate_schemas()
    env_results = check_environment_variables()

    # Print results

    if mcp_results["errors"]:
        for error in mcp_results["errors"]:
            pass  # Placeholder for printing errors

    if python_results["errors"]:
        for error in python_results["errors"]:
            pass  # Placeholder for printing errors

    if schema_results["errors"]:
        for error in schema_results["errors"]:
            pass  # Placeholder for printing errors

    missing_vars = [var for var, info in env_results["env_vars"].items() if not info["present"]]
    if missing_vars:
        pass  # Placeholder for printing missing env vars

    # Overall result
    overall_valid = mcp_results["valid"] and python_results["valid"] and schema_results["valid"]

    if overall_valid:
        pass  # Placeholder for success message
    else:
        pass  # Placeholder for failure message

    # Summary statistics
    total_files = (
        len(python_results["files"]) + len(mcp_results["catalogs"]) + len(schema_results["schemas"])
    )
    valid_files = sum(1 for f in python_results["files"].values() if f.get("valid", False))
    valid_catalogs = sum(1 for c in mcp_results["catalogs"].values() if c.get("valid", False))
    valid_schemas = sum(1 for s in schema_results["schemas"].values() if s.get("valid", False))

    return 0 if overall_valid else 1


if __name__ == "__main__":
    sys.exit(main())
