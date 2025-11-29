"""
Output Layer Prompts - Instructional Injection v5 Framework

Implements Output Layer instructions (26-30) for subatomic agents.
"""

from typing import Optional

class OutputLayer:
    """Output Layer prompt templates for structured, compliant, and efficient output generation."""
    
    @staticmethod
    def strict_json_output() -> str:
        """26. Strict JSON-Only Output Mode - Require deterministic, schema-compliant JSON."""
        return """
# STRICT JSON OUTPUT REQUIREMENT

OUTPUT FORMAT: JSON ONLY
- No explanatory text before or after JSON
- No markdown formatting or code blocks
- No comments or annotations within JSON
- Pure, valid JSON structure only

VALIDATION REQUIREMENTS:
- Must parse with standard JSON parser
- All required fields present
- Data types match schema exactly
- No trailing commas or syntax errors
- Proper nesting and structure

ERROR HANDLING:
- If output cannot be generated as valid JSON: {"error": "JSON generation failed"}
- If processing fails: {"error": "Processing failed", "reason": "specific reason"}
- Always maintain JSON structure even for errors

COMPLIANCE CHECK:
- Validate JSON syntax before output
- Ensure schema compliance
- Check for forbidden content
- Verify field completeness

OUTPUT MUST BE VALID JSON AND NOTHING ELSE.
"""
    
    @staticmethod
    def schema_enforcement(schema: dict, example: Optional[dict] = None) -> str:
        """27. Schema Enforcement & Examples - Supply schema and valid example."""
        import json
        schema_json = json.dumps(schema, indent=2)
        
        example_text = ""
        if example:
            example_json = json.dumps(example, indent=2)
            example_text = f"""
# VALID OUTPUT EXAMPLE
{example_json}
"""
        
        return f"""
# SCHEMA ENFORCEMENT

REQUIRED SCHEMA:
{schema_json}
{example_text}
SCHEMA COMPLIANCE RULES:
1. All required fields must be present
2. Field types must match exactly (string, number, boolean, array, object)
3. Nested objects must follow specified structure
4. Arrays must contain elements of specified type
5. Optional fields may be omitted but must match type if included
6. No additional fields beyond schema specification

VALIDATION CHECKLIST:
- [ ] All required fields present
- [ ] Correct data types for all fields
- [ ] Proper nesting structure
- [ ] Valid array element types
- [ ] No extra unauthorized fields
- [ ] Values within allowed ranges/constraints

OUTPUT MUST CONFORM TO THIS SCHEMA EXACTLY.
"""
    
    @staticmethod
    def stability_contracts(field_order: list, naming_convention: str = "snake_case") -> str:
        """28. Stability Contracts - Preserve field order and naming across outputs."""
        order_text = "\n".join([f"{i+1}. {field}" for i, field in enumerate(field_order)])
        
        return f"""
# STABILITY CONTRACT REQUIREMENTS

FIELD ORDER (MUST BE MAINTAINED):
{order_text}

NAMING CONVENTION: {naming_convention}

STABILITY RULES:
1. Field order must be identical across all outputs
2. Field names must use consistent naming convention
3. Data types must remain stable across executions
4. Optional fields must be consistently included/excluded
5. No field reordering or renaming between runs
6. Maintain backward compatibility for schema changes

CONSISTENCY REQUIREMENTS:
- Same input should produce same field structure
- Field positions must not vary between executions
- Naming patterns must be predictable and stable
- Structure must be reproducible and reliable

CONTRACT VIOLATIONS:
- Field reordering: Critical error
- Name changes: Breaking change
- Type changes: Schema version required
- Missing fields: Data integrity issue

MAINTAIN STRUCTURAL STABILITY ACROSS ALL EXECUTIONS.
"""
    
    @staticmethod
    def error_envelope_normalization() -> str:
        """29. Error Envelope Normalization - Standardize failures into structured error objects."""
        return """
# ERROR ENVELOPE STANDARDIZATION

SUCCESS OUTPUT FORMAT:
{
  "status": "success",
  "data": {...actual_output...},
  "metadata": {
    "processing_time": "string",
    "confidence": "number",
    "version": "string"
  }
}

ERROR OUTPUT FORMAT:
{
  "status": "error",
  "error": {
    "code": "string",
    "message": "string",
    "details": "string",
    "recoverable": "boolean"
  },
  "metadata": {
    "processing_time": "string",
    "failed_step": "string",
    "version": "string"
  }
}

ERROR CODES:
- "validation_error": Input validation failed
- "processing_error": Core processing failed
- "tool_error": External tool failure
- "safety_error": Safety constraint violation
- "resource_error": Resource limitation exceeded
- "system_error": Internal system failure

ENVELOPE RULES:
1. Always include status field ("success" or "error")
2. Use standardized error structure for all failures
3. Include metadata for audit and debugging
4. Never mix success and error formats
5. Provide actionable error messages
6. Include recovery information when possible

ALL OUTPUTS MUST USE STANDARDIZED SUCCESS/ERROR ENVELOPES.
"""
    
    @staticmethod
    def minimality_constraints(max_fields: Optional[int] = None, max_depth: Optional[int] = None, max_array_length: Optional[int] = None) -> str:
        """30. Minimality Constraints - Limit output size to enforce clarity and conciseness."""
        constraints = []
        if max_fields:
            constraints.append(f"Maximum fields: {max_fields}")
        if max_depth:
            constraints.append(f"Maximum nesting depth: {max_depth}")
        if max_array_length:
            constraints.append(f"Maximum array length: {max_array_length}")
            
        constraints_text = "\n".join([f"- {constraint}" for constraint in constraints])
        
        return f"""
# MINIMALITY CONSTRAINTS

SIZE LIMITATIONS:
{constraints_text}

PRINCIPLES OF MINIMALITY:
1. Include only essential information
2. Avoid redundant or duplicate data
3. Use concise but descriptive field names
4. Eliminate unnecessary nesting levels
5. Limit array length to essential items
6. Prefer aggregated data over raw dumps

OPTIMIZATION STRATEGIES:
- Combine related fields into objects
- Use arrays instead of repeated fields
- Summarize rather than enumerate when possible
- Remove intermediate calculation results
- Exclude debugging or temporary data
- Focus on final, actionable output

VALIDATION CHECKS:
- Count total fields against maximum
- Measure nesting depth
- Verify array lengths
- Check for redundant information
- Assess information density

OUTPUT MUST BE CONCISE, ESSENTIAL, AND WITHIN SIZE CONSTRAINTS.
"""
