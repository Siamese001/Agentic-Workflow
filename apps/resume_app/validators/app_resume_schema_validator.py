"""
resume_app/validators – app_resume_schema_validator.py

Apps layer schema validator for resume data structures.
Validates JSON schemas and data consistency for resume generation requests and responses.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class SchemaValidationResult:
    """Schema validation result with detailed feedback"""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    schema_version: str = "1.0"
    validated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    validation_path: str = ""


@dataclass
class SchemaField:
    """Schema field definition"""
    name: str
    field_type: str
    required: bool = True
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    allowed_values: Optional[List[str]] = None
    pattern: Optional[str] = None
    nested_schema: Optional[Dict[str, Any]] = None


class ResumeSchemaValidator:
    """Apps layer resume schema validator

    Validates resume data structures against defined schemas
    for consistency and data integrity.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.schema_version = "1.0"

        # Define resume data schemas
        self._initialize_schemas()

    def validate_resume_request_schema(self, request_data: Dict[str, Any]) -> SchemaValidationResult:
        """Validate resume generation request schema"""
        result = SchemaValidationResult(validation_path="resume_request")

        try:
            # Validate top-level schema
            self._validate_against_schema(request_data, self.resume_request_schema, result)

            # Validate nested structures
            if "personal_info" in request_data:
                self._validate_against_schema(
                    request_data["personal_info"],
                    self.personal_info_schema,
                    result,
                    path="personal_info"
                )

            if "professional_experience" in request_data:
                self._validate_experience_array(request_data["professional_experience"], result)

            if "skills" in request_data:
                self._validate_skills_structure(request_data["skills"], result)

            if "contact_info" in request_data:
                self._validate_against_schema(
                    request_data["contact_info"],
                    self.contact_info_schema,
                    result,
                    path="contact_info"
                )

            result.is_valid = len(result.errors) == 0

        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Schema validation error: {str(e)}")

        return result

    def validate_resume_response_schema(self, response_data: Dict[str, Any]) -> SchemaValidationResult:
        """Validate resume generation response schema"""
        result = SchemaValidationResult(validation_path="resume_response")

        try:
            self._validate_against_schema(response_data, self.resume_response_schema, result)

            # Validate enhanced bullets if present
            if "enhanced_bullets" in response_data:
                self._validate_bullet_array(response_data["enhanced_bullets"], result, "enhanced_bullets")

            # Validate optimized skills if present
            if "optimized_skills" in response_data:
                self._validate_skills_structure(response_data["optimized_skills"], result, "optimized_skills")

            result.is_valid = len(result.errors) == 0

        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Response schema validation error: {str(e)}")

        return result

    def validate_master_resume_schema(self, master_resume_data: Dict[str, Any]) -> SchemaValidationResult:
        """Validate master resume data schema"""
        result = SchemaValidationResult(validation_path="master_resume")

        try:
            # Check required top-level fields
            required_fields = ["personal_info", "professional_experience", "skills"]
            for field in required_fields:
                if field not in master_resume_data:
                    result.errors.append(f"Master resume missing required field: {field}")

            # Validate each section
            if "personal_info" in master_resume_data:
                self._validate_against_schema(
                    master_resume_data["personal_info"],
                    self.personal_info_schema,
                    result,
                    path="master_resume.personal_info"
                )

            if "professional_experience" in master_resume_data:
                self._validate_experience_array(
                    master_resume_data["professional_experience"],
                    result,
                    path="master_resume.professional_experience"
                )

            if "skills" in master_resume_data:
                self._validate_skills_structure(
                    master_resume_data["skills"],
                    result,
                    path="master_resume.skills"
                )

            result.is_valid = len(result.errors) == 0

        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Master resume schema validation error: {str(e)}")

        return result

    def _initialize_schemas(self):
        """Initialize all schema definitions"""

        # Personal info schema
        self.personal_info_schema = {
            "name": SchemaField("name", "string", required=True, min_length=2, max_length=50),
            "location": SchemaField("location", "string", required=False, max_length=100),
            "website": SchemaField("website", "string", required=False, max_length=200),
            "linkedin_url": SchemaField("linkedin_url", "string", required=False, max_length=200)
        }

        # Contact info schema
        self.contact_info_schema = {
            "email": SchemaField("email", "string", required=False, max_length=100),
            "phone": SchemaField("phone", "string", required=False, max_length=20),
            "linkedin_url": SchemaField("linkedin_url", "string", required=False, max_length=200)
        }

        # Single experience schema
        self.experience_schema = {
            "company": SchemaField("company", "string", required=True, min_length=2, max_length=100),
            "title": SchemaField("title", "string", required=True, min_length=2, max_length=100),
            "duration": SchemaField("duration", "string", required=False, max_length=50),
            "start_date": SchemaField("start_date", "string", required=False, max_length=20),
            "end_date": SchemaField("end_date", "string", required=False, max_length=20),
            "bullet_pool": SchemaField("bullet_pool", "array", required=False),
            "highlights": SchemaField("highlights", "array", required=False)
        }

        # Resume request schema
        self.resume_request_schema = {
            "target_role": SchemaField("target_role", "string", required=True, min_length=2, max_length=100),
            "experience_level": SchemaField("experience_level", "string", required=True,
                                          allowed_values=["entry", "junior", "mid", "senior", "lead", "principal", "executive"]),
            "job_description": SchemaField("job_description", "string", required=False, max_length=5000),
            "target_company": SchemaField("target_company", "string", required=False, max_length=100),
            "personal_info": SchemaField("personal_info", "object", required=False),
            "professional_experience": SchemaField("professional_experience", "array", required=False),
            "skills": SchemaField("skills", "object", required=False),
            "contact_info": SchemaField("contact_info", "object", required=False),
            "optimization_focus": SchemaField("optimization_focus", "array", required=False),
            "linkedin_format": SchemaField("linkedin_format", "boolean", required=False)
        }

        # Resume response schema
        self.resume_response_schema = {
            "enhanced_bullets": SchemaField("enhanced_bullets", "array", required=False),
            "professional_summary": SchemaField("professional_summary", "string", required=False, max_length=2000),
            "optimized_skills": SchemaField("optimized_skills", "object", required=False),
            "metadata": SchemaField("metadata", "object", required=False),
            "enhancement_confidence": SchemaField("enhancement_confidence", "number", required=False),
            "provenance_tracking": SchemaField("provenance_tracking", "object", required=False),
            "linkedin_compliance": SchemaField("linkedin_compliance", "object", required=False)
        }

    def _validate_against_schema(self, data: Dict[str, Any], schema: Dict[str, SchemaField],
                                result: SchemaValidationResult, path: str = "") -> None:
        """Validate data against a schema definition"""
        for field_name, field_def in schema.items():
            field_path = f"{path}.{field_name}" if path else field_name

            # Check required fields
            if field_def.required and field_name not in data:
                result.errors.append(f"Missing required field: {field_path}")
                continue

            # Skip validation if field is not present and not required
            if field_name not in data:
                continue

            field_value = data[field_name]

            # Validate field type
            if not self._validate_field_type(field_value, field_def.field_type):
                result.errors.append(f"Invalid type for {field_path}: expected {field_def.field_type}")
                continue

            # Validate string fields
            if field_def.field_type == "string" and isinstance(field_value, str):
                if field_def.min_length and len(field_value) < field_def.min_length:
                    result.errors.append(f"{field_path} too short: minimum {field_def.min_length} characters")
                if field_def.max_length and len(field_value) > field_def.max_length:
                    result.errors.append(f"{field_path} too long: maximum {field_def.max_length} characters")
                if field_def.allowed_values and field_value not in field_def.allowed_values:
                    result.errors.append(f"{field_path} invalid value: must be one of {field_def.allowed_values}")

            # Validate array fields
            elif field_def.field_type == "array" and isinstance(field_value, list):
                if field_def.min_length and len(field_value) < field_def.min_length:
                    result.errors.append(f"{field_path} array too short: minimum {field_def.min_length} items")
                if field_def.max_length and len(field_value) > field_def.max_length:
                    result.errors.append(f"{field_path} array too long: maximum {field_def.max_length} items")

    def _validate_experience_array(self, experiences: List[Dict[str, Any]],
                                  result: SchemaValidationResult, path: str = "professional_experience") -> None:
        """Validate array of experience objects"""
        if not isinstance(experiences, list):
            result.errors.append(f"{path} must be an array")
            return

        for i, exp in enumerate(experiences):
            exp_path = f"{path}[{i}]"
            self._validate_against_schema(exp, self.experience_schema, result, exp_path)

            # Validate bullet points if present
            if "bullet_pool" in exp:
                self._validate_bullet_array(exp["bullet_pool"], result, f"{exp_path}.bullet_pool")
            elif "highlights" in exp:
                self._validate_bullet_array(exp["highlights"], result, f"{exp_path}.highlights")

    def _validate_bullet_array(self, bullets: List[str], result: SchemaValidationResult, path: str) -> None:
        """Validate array of bullet point strings"""
        if not isinstance(bullets, list):
            result.errors.append(f"{path} must be an array of strings")
            return

        for i, bullet in enumerate(bullets):
            bullet_path = f"{path}[{i}]"
            if not isinstance(bullet, str):
                result.errors.append(f"{bullet_path} must be a string")
            elif len(bullet) < 10:
                result.errors.append(f"{bullet_path} too short: minimum 10 characters")
            elif len(bullet) > 600:
                result.errors.append(f"{bullet_path} too long: maximum 600 characters")

    def _validate_skills_structure(self, skills: Dict[str, List[str]],
                                  result: SchemaValidationResult, path: str = "skills") -> None:
        """Validate skills structure (category -> array of skills)"""
        if not isinstance(skills, dict):
            result.errors.append(f"{path} must be an object")
            return

        for category, skill_list in skills.items():
            category_path = f"{path}.{category}"
            if not isinstance(skill_list, list):
                result.errors.append(f"{category_path} must be an array")
                continue

            for i, skill in enumerate(skill_list):
                skill_path = f"{category_path}[{i}]"
                if not isinstance(skill, str):
                    result.errors.append(f"{skill_path} must be a string")
                elif len(skill) < 2:
                    result.errors.append(f"{skill_path} too short: minimum 2 characters")
                elif len(skill) > 50:
                    result.errors.append(f"{skill_path} too long: maximum 50 characters")

    def _validate_field_type(self, value: Any, expected_type: str) -> bool:
        """Validate field type matches expected type"""
        type_mapping = {
            "string": str,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict
        }

        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type is None:
            return False

        return isinstance(value, expected_python_type)

    def get_schema_definitions(self) -> Dict[str, Any]:
        """Get all schema definitions for reference"""
        return {
            "schema_version": self.schema_version,
            "personal_info": {name: field.field_type for name, field in self.personal_info_schema.items()},
            "contact_info": {name: field.field_type for name, field in self.contact_info_schema.items()},
            "experience": {name: field.field_type for name, field in self.experience_schema.items()},
            "resume_request": {name: field.field_type for name, field in self.resume_request_schema.items()},
            "resume_response": {name: field.field_type for name, field in self.resume_response_schema.items()}
        }

    def export_schema_json(self, schema_name: str) -> str:
        """Export schema as JSON string"""
        schema_map = {
            "personal_info": self.personal_info_schema,
            "contact_info": self.contact_info_schema,
            "experience": self.experience_schema,
            "resume_request": self.resume_request_schema,
            "resume_response": self.resume_response_schema
        }

        if schema_name not in schema_map:
            raise ValueError(f"Unknown schema: {schema_name}")

        schema = schema_map[schema_name]
        json_schema = {}

        for field_name, field_def in schema.items():
            field_schema = {
                "type": field_def.field_type,
                "required": field_def.required
            }

            if field_def.min_length is not None:
                field_schema["min_length"] = field_def.min_length
            if field_def.max_length is not None:
                field_schema["max_length"] = field_def.max_length
            if field_def.allowed_values is not None:
                field_schema["allowed_values"] = field_def.allowed_values

            json_schema[field_name] = field_schema

        return json.dumps(json_schema, indent=2)

