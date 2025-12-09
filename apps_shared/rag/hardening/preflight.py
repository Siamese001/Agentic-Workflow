"""
runtime/shared/preflight.py
Pre-Flight Engine Validation Module

Ported from legacy resume gen Job_Workflow_v61.27.json
Implements pre-flight validation tests to verify engine capabilities:
  - VALIDATE_ITERATION: Verify correct array iteration
  - VALIDATE_STRUCTURAL_PARSE: Verify structural rule enforcement
  - File manifest checks
  - Dependency validation
"""

from __future__ import annotations

import hashlib
import importlib
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMERATIONS
# =============================================================================

class PreflightTestType(Enum):
    """Types of pre-flight tests."""
    ITERATION = auto()
    STRUCTURAL_PARSE = auto()
    FILE_MANIFEST = auto()
    DEPENDENCY = auto()
    SCHEMA_VERSION = auto()
    ENVIRONMENT = auto()
    CAPABILITY = auto()


class PreflightResult(Enum):
    """Results of pre-flight tests."""
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    WARN = "WARN"


class PreflightAction(Enum):
    """Actions to take on pre-flight failure."""
    HALT_WITH_ENGINE_COMPLIANCE_ERROR = "HALT_WITH_ENGINE_COMPLIANCE_ERROR"
    HALT_AND_REPORT = "HALT_AND_REPORT"
    WARN_AND_CONTINUE = "WARN_AND_CONTINUE"
    SKIP = "SKIP"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class PreflightTestResult:
    """Result from a single pre-flight test."""
    test_id: str
    test_type: PreflightTestType
    result: PreflightResult
    description: str
    duration_ms: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "test_id": self.test_id,
            "test_type": self.test_type.name,
            "result": self.result.value,
            "description": self.description,
            "duration_ms": self.duration_ms,
            "details": self.details,
            "error_message": self.error_message,
            "timestamp": self.timestamp,
        }


@dataclass
class PreflightReport:
    """Report from pre-flight validation."""
    success: bool
    tests_run: int
    tests_passed: int
    tests_failed: int
    tests_skipped: int
    results: List[PreflightTestResult]
    total_duration_ms: float
    halt_reason: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "summary": {
                "run": self.tests_run,
                "passed": self.tests_passed,
                "failed": self.tests_failed,
                "skipped": self.tests_skipped,
            },
            "total_duration_ms": self.total_duration_ms,
            "halt_reason": self.halt_reason,
            "timestamp": self.timestamp,
            "tests": [r.to_dict() for r in self.results],
        }


@dataclass
class IterationTest:
    """Configuration for iteration validation test."""
    test_id: str = "VALIDATE_ITERATION"
    description: str = "Verifies the engine can correctly iterate through a full array without premature termination"
    input_data: List[Any] = field(default_factory=lambda: ["A", "B", "C"])
    expected_output_count: int = 3


@dataclass
class StructuralParseTest:
    """Configuration for structural parse validation test."""
    test_id: str = "VALIDATE_STRUCTURAL_PARSE"
    description: str = "Verifies the engine's validation parser can correctly enforce a string-based structural rule"
    input_data: str = "A | B | C | D"
    rule_structure: str = "X | Y | Z"
    expected_result: PreflightResult = PreflightResult.FAIL


@dataclass
class FileManifestTest:
    """Configuration for file manifest validation test."""
    test_id: str = "VALIDATE_FILE_MANIFEST"
    description: str = "Verifies all required files are present"
    required_files: List[str] = field(default_factory=list)
    base_path: Optional[str] = None
    blocking: bool = True


@dataclass
class DependencyTest:
    """Configuration for dependency validation test."""
    test_id: str = "VALIDATE_DEPENDENCIES"
    description: str = "Verifies all required Python packages are installed"
    required_packages: List[str] = field(default_factory=list)
    version_constraints: Dict[str, str] = field(default_factory=dict)


@dataclass
class SchemaVersionTest:
    """Configuration for schema version validation test."""
    test_id: str = "VALIDATE_SCHEMA_VERSIONS"
    description: str = "Verifies schema files match expected versions"
    version_pins: Dict[str, str] = field(default_factory=dict)


@dataclass
class PreflightConfig:
    """Configuration for pre-flight validation."""
    on_failure: PreflightAction = PreflightAction.HALT_WITH_ENGINE_COMPLIANCE_ERROR
    run_iteration_test: bool = True
    run_structural_test: bool = True
    run_file_manifest_test: bool = True
    run_dependency_test: bool = True
    run_schema_version_test: bool = True
    run_environment_test: bool = True
    
    # Test configurations
    iteration_test: IterationTest = field(default_factory=IterationTest)
    structural_test: StructuralParseTest = field(default_factory=StructuralParseTest)
    file_manifest_test: FileManifestTest = field(default_factory=FileManifestTest)
    dependency_test: DependencyTest = field(default_factory=DependencyTest)
    schema_version_test: SchemaVersionTest = field(default_factory=SchemaVersionTest)
    
    # Environment requirements
    min_python_version: Tuple[int, int] = (3, 9)
    required_env_vars: List[str] = field(default_factory=list)


# =============================================================================
# PRE-FLIGHT VALIDATOR
# =============================================================================

class PreflightValidator:
    """
    Pre-Flight Engine Validation.
    
    Runs a suite of tests before workflow execution to verify
    that the engine and environment are properly configured.
    """
    
    def __init__(self, config: Optional[PreflightConfig] = None) -> None:
        self.config = config or PreflightConfig()
        self._custom_tests: List[Callable[[], PreflightTestResult]] = []
        
    def add_custom_test(self, test_fn: Callable[[], PreflightTestResult]) -> None:
        """Add a custom pre-flight test."""
        self._custom_tests.append(test_fn)
        
    def run_all(self) -> PreflightReport:
        """
        Run all configured pre-flight tests.
        
        Returns:
            PreflightReport with all test results
        """
        import time
        start_time = time.time()
        results: List[PreflightTestResult] = []
        halt_reason: Optional[str] = None
        
        # Run iteration test
        if self.config.run_iteration_test:
            result = self._run_iteration_test()
            results.append(result)
            if result.result == PreflightResult.FAIL:
                halt_reason = f"Iteration test failed: {result.error_message}"
                if self.config.on_failure == PreflightAction.HALT_WITH_ENGINE_COMPLIANCE_ERROR:
                    return self._create_report(results, start_time, halt_reason)
                    
        # Run structural parse test
        if self.config.run_structural_test:
            result = self._run_structural_test()
            results.append(result)
            if result.result == PreflightResult.FAIL and result.error_message:
                halt_reason = f"Structural test failed: {result.error_message}"
                if self.config.on_failure == PreflightAction.HALT_WITH_ENGINE_COMPLIANCE_ERROR:
                    return self._create_report(results, start_time, halt_reason)
                    
        # Run file manifest test
        if self.config.run_file_manifest_test and self.config.file_manifest_test.required_files:
            result = self._run_file_manifest_test()
            results.append(result)
            if result.result == PreflightResult.FAIL and self.config.file_manifest_test.blocking:
                halt_reason = f"File manifest test failed: {result.error_message}"
                if self.config.on_failure == PreflightAction.HALT_AND_REPORT:
                    return self._create_report(results, start_time, halt_reason)
                    
        # Run dependency test
        if self.config.run_dependency_test and self.config.dependency_test.required_packages:
            result = self._run_dependency_test()
            results.append(result)
            if result.result == PreflightResult.FAIL:
                halt_reason = f"Dependency test failed: {result.error_message}"
                if self.config.on_failure == PreflightAction.HALT_AND_REPORT:
                    return self._create_report(results, start_time, halt_reason)
                    
        # Run schema version test
        if self.config.run_schema_version_test and self.config.schema_version_test.version_pins:
            result = self._run_schema_version_test()
            results.append(result)
            if result.result == PreflightResult.FAIL:
                halt_reason = f"Schema version test failed: {result.error_message}"
                    
        # Run environment test
        if self.config.run_environment_test:
            result = self._run_environment_test()
            results.append(result)
            if result.result == PreflightResult.FAIL:
                halt_reason = f"Environment test failed: {result.error_message}"
                if self.config.on_failure == PreflightAction.HALT_WITH_ENGINE_COMPLIANCE_ERROR:
                    return self._create_report(results, start_time, halt_reason)
                    
        # Run custom tests
        for test_fn in self._custom_tests:
            try:
                result = test_fn()
                results.append(result)
            except Exception as e:
                results.append(PreflightTestResult(
                    test_id="CUSTOM_TEST",
                    test_type=PreflightTestType.CAPABILITY,
                    result=PreflightResult.FAIL,
                    description="Custom test execution",
                    error_message=str(e),
                ))
                
        return self._create_report(results, start_time, halt_reason)
    
    def _run_iteration_test(self) -> PreflightTestResult:
        """Test that iteration works correctly."""
        import time
        start_time = time.time()
        
        test_config = self.config.iteration_test
        input_data = test_config.input_data
        expected_count = test_config.expected_output_count
        
        # Simulate iteration
        actual_count = 0
        collected = []
        
        for item in input_data:
            actual_count += 1
            collected.append(item)
            
        duration = (time.time() - start_time) * 1000
        
        if actual_count == expected_count:
            return PreflightTestResult(
                test_id=test_config.test_id,
                test_type=PreflightTestType.ITERATION,
                result=PreflightResult.PASS,
                description=test_config.description,
                duration_ms=duration,
                details={"expected": expected_count, "actual": actual_count, "items": collected},
            )
        else:
            return PreflightTestResult(
                test_id=test_config.test_id,
                test_type=PreflightTestType.ITERATION,
                result=PreflightResult.FAIL,
                description=test_config.description,
                duration_ms=duration,
                details={"expected": expected_count, "actual": actual_count},
                error_message=f"Expected {expected_count} iterations, got {actual_count}",
            )
    
    def _run_structural_test(self) -> PreflightTestResult:
        """Test structural parsing validation."""
        import time
        start_time = time.time()
        
        test_config = self.config.structural_test
        input_data = test_config.input_data
        rule_structure = test_config.rule_structure
        expected_result = test_config.expected_result
        
        # Parse structures
        input_parts = [p.strip() for p in input_data.split('|')]
        rule_parts = [p.strip() for p in rule_structure.split('|')]
        
        # Check if structures match
        structures_match = len(input_parts) == len(rule_parts)
        
        # Determine actual result
        actual_result = PreflightResult.PASS if structures_match else PreflightResult.FAIL
        
        duration = (time.time() - start_time) * 1000
        
        # The test passes if the actual result matches expected
        test_passed = actual_result == expected_result
        
        return PreflightTestResult(
            test_id=test_config.test_id,
            test_type=PreflightTestType.STRUCTURAL_PARSE,
            result=PreflightResult.PASS if test_passed else PreflightResult.FAIL,
            description=test_config.description,
            duration_ms=duration,
            details={
                "input_parts": len(input_parts),
                "rule_parts": len(rule_parts),
                "expected_result": expected_result.value,
                "actual_result": actual_result.value,
            },
            error_message=None if test_passed else f"Structural validation mismatch",
        )
    
    def _run_file_manifest_test(self) -> PreflightTestResult:
        """Test that required files exist."""
        import time
        start_time = time.time()
        
        test_config = self.config.file_manifest_test
        base_path = Path(test_config.base_path) if test_config.base_path else Path.cwd()
        
        missing_files = []
        found_files = []
        
        for file_name in test_config.required_files:
            file_path = base_path / file_name
            if file_path.exists():
                found_files.append(file_name)
            else:
                missing_files.append(file_name)
                
        duration = (time.time() - start_time) * 1000
        
        if not missing_files:
            return PreflightTestResult(
                test_id=test_config.test_id,
                test_type=PreflightTestType.FILE_MANIFEST,
                result=PreflightResult.PASS,
                description=test_config.description,
                duration_ms=duration,
                details={"found": found_files, "total": len(test_config.required_files)},
            )
        else:
            return PreflightTestResult(
                test_id=test_config.test_id,
                test_type=PreflightTestType.FILE_MANIFEST,
                result=PreflightResult.FAIL,
                description=test_config.description,
                duration_ms=duration,
                details={"found": found_files, "missing": missing_files},
                error_message=f"Missing files: {', '.join(missing_files)}",
            )
    
    def _run_dependency_test(self) -> PreflightTestResult:
        """Test that required packages are installed."""
        import time
        start_time = time.time()
        
        test_config = self.config.dependency_test
        missing_packages = []
        found_packages = []
        version_mismatches = []
        
        for package in test_config.required_packages:
            try:
                module = importlib.import_module(package.replace('-', '_'))
                found_packages.append(package)
                
                # Check version if specified
                if package in test_config.version_constraints:
                    expected_version = test_config.version_constraints[package]
                    actual_version = getattr(module, '__version__', 'unknown')
                    if not self._version_satisfies(actual_version, expected_version):
                        version_mismatches.append({
                            "package": package,
                            "expected": expected_version,
                            "actual": actual_version,
                        })
            except ImportError:
                missing_packages.append(package)
                
        duration = (time.time() - start_time) * 1000
        
        if not missing_packages and not version_mismatches:
            return PreflightTestResult(
                test_id=test_config.test_id,
                test_type=PreflightTestType.DEPENDENCY,
                result=PreflightResult.PASS,
                description=test_config.description,
                duration_ms=duration,
                details={"found": found_packages},
            )
        else:
            return PreflightTestResult(
                test_id=test_config.test_id,
                test_type=PreflightTestType.DEPENDENCY,
                result=PreflightResult.FAIL,
                description=test_config.description,
                duration_ms=duration,
                details={
                    "found": found_packages,
                    "missing": missing_packages,
                    "version_mismatches": version_mismatches,
                },
                error_message=f"Missing: {missing_packages}, Version issues: {version_mismatches}",
            )
    
    def _run_schema_version_test(self) -> PreflightTestResult:
        """Test that schema files match expected versions."""
        import time
        import json
        start_time = time.time()
        
        test_config = self.config.schema_version_test
        mismatches = []
        matches = []
        
        for file_name, expected_version in test_config.version_pins.items():
            try:
                # Try to load the file and check version
                file_path = Path(file_name)
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        actual_version = data.get('version', data.get('schema_version', 'unknown'))
                        
                        if actual_version == expected_version:
                            matches.append(file_name)
                        else:
                            mismatches.append({
                                "file": file_name,
                                "expected": expected_version,
                                "actual": actual_version,
                            })
                else:
                    mismatches.append({
                        "file": file_name,
                        "expected": expected_version,
                        "actual": "FILE_NOT_FOUND",
                    })
            except Exception as e:
                mismatches.append({
                    "file": file_name,
                    "expected": expected_version,
                    "actual": f"ERROR: {str(e)}",
                })
                
        duration = (time.time() - start_time) * 1000
        
        if not mismatches:
            return PreflightTestResult(
                test_id=test_config.test_id,
                test_type=PreflightTestType.SCHEMA_VERSION,
                result=PreflightResult.PASS,
                description=test_config.description,
                duration_ms=duration,
                details={"verified": matches},
            )
        else:
            return PreflightTestResult(
                test_id=test_config.test_id,
                test_type=PreflightTestType.SCHEMA_VERSION,
                result=PreflightResult.FAIL,
                description=test_config.description,
                duration_ms=duration,
                details={"verified": matches, "mismatches": mismatches},
                error_message=f"Version mismatches: {len(mismatches)}",
            )
    
    def _run_environment_test(self) -> PreflightTestResult:
        """Test environment configuration."""
        import time
        start_time = time.time()
        
        issues = []
        checks_passed = []
        
        # Check Python version
        current_version = sys.version_info[:2]
        min_version = self.config.min_python_version
        
        if current_version >= min_version:
            checks_passed.append(f"Python {current_version[0]}.{current_version[1]}")
        else:
            issues.append(f"Python version {current_version} < required {min_version}")
            
        # Check required environment variables
        for env_var in self.config.required_env_vars:
            if os.environ.get(env_var):
                checks_passed.append(f"ENV:{env_var}")
            else:
                issues.append(f"Missing environment variable: {env_var}")
                
        duration = (time.time() - start_time) * 1000
        
        if not issues:
            return PreflightTestResult(
                test_id="VALIDATE_ENVIRONMENT",
                test_type=PreflightTestType.ENVIRONMENT,
                result=PreflightResult.PASS,
                description="Verifies environment configuration",
                duration_ms=duration,
                details={"passed": checks_passed},
            )
        else:
            return PreflightTestResult(
                test_id="VALIDATE_ENVIRONMENT",
                test_type=PreflightTestType.ENVIRONMENT,
                result=PreflightResult.FAIL,
                description="Verifies environment configuration",
                duration_ms=duration,
                details={"passed": checks_passed, "issues": issues},
                error_message="; ".join(issues),
            )
    
    def _version_satisfies(self, actual: str, constraint: str) -> bool:
        """Check if actual version satisfies constraint."""
        # Simple version comparison - could be enhanced with packaging.version
        try:
            if constraint.startswith('>='):
                return actual >= constraint[2:]
            elif constraint.startswith('<='):
                return actual <= constraint[2:]
            elif constraint.startswith('=='):
                return actual == constraint[2:]
            elif constraint.startswith('>'):
                return actual > constraint[1:]
            elif constraint.startswith('<'):
                return actual < constraint[1:]
            else:
                return actual == constraint
        except Exception:
            return False
    
    def _create_report(
        self,
        results: List[PreflightTestResult],
        start_time: float,
        halt_reason: Optional[str],
    ) -> PreflightReport:
        """Create a pre-flight report from results."""
        import time
        
        passed = sum(1 for r in results if r.result == PreflightResult.PASS)
        failed = sum(1 for r in results if r.result == PreflightResult.FAIL)
        skipped = sum(1 for r in results if r.result == PreflightResult.SKIP)
        
        return PreflightReport(
            success=failed == 0 and halt_reason is None,
            tests_run=len(results),
            tests_passed=passed,
            tests_failed=failed,
            tests_skipped=skipped,
            results=results,
            total_duration_ms=(time.time() - start_time) * 1000,
            halt_reason=halt_reason,
        )


# =============================================================================
# CAPABILITY TESTS
# =============================================================================

class CapabilityTest:
    """Test for specific engine capabilities."""
    
    @staticmethod
    def test_json_parsing() -> PreflightTestResult:
        """Test JSON parsing capability."""
        import time
        import json
        start_time = time.time()
        
        test_json = '{"key": "value", "nested": {"array": [1, 2, 3]}}'
        
        try:
            parsed = json.loads(test_json)
            if parsed.get("key") == "value" and parsed.get("nested", {}).get("array") == [1, 2, 3]:
                return PreflightTestResult(
                    test_id="CAPABILITY_JSON_PARSING",
                    test_type=PreflightTestType.CAPABILITY,
                    result=PreflightResult.PASS,
                    description="Test JSON parsing capability",
                    duration_ms=(time.time() - start_time) * 1000,
                )
        except Exception as e:
            return PreflightTestResult(
                test_id="CAPABILITY_JSON_PARSING",
                test_type=PreflightTestType.CAPABILITY,
                result=PreflightResult.FAIL,
                description="Test JSON parsing capability",
                duration_ms=(time.time() - start_time) * 1000,
                error_message=str(e),
            )
            
        return PreflightTestResult(
            test_id="CAPABILITY_JSON_PARSING",
            test_type=PreflightTestType.CAPABILITY,
            result=PreflightResult.FAIL,
            description="Test JSON parsing capability",
            duration_ms=(time.time() - start_time) * 1000,
            error_message="JSON parsing produced unexpected result",
        )
    
    @staticmethod
    def test_regex_support() -> PreflightTestResult:
        """Test regex capability."""
        import time
        import re
        start_time = time.time()
        
        try:
            pattern = r'\d+%|\$[\d,]+[MBK]?'
            test_string = "Achieved 25% growth and $5M revenue"
            matches = re.findall(pattern, test_string)
            
            if matches == ['25%', '$5M']:
                return PreflightTestResult(
                    test_id="CAPABILITY_REGEX",
                    test_type=PreflightTestType.CAPABILITY,
                    result=PreflightResult.PASS,
                    description="Test regex capability",
                    duration_ms=(time.time() - start_time) * 1000,
                    details={"matches": matches},
                )
        except Exception as e:
            return PreflightTestResult(
                test_id="CAPABILITY_REGEX",
                test_type=PreflightTestType.CAPABILITY,
                result=PreflightResult.FAIL,
                description="Test regex capability",
                duration_ms=(time.time() - start_time) * 1000,
                error_message=str(e),
            )
            
        return PreflightTestResult(
            test_id="CAPABILITY_REGEX",
            test_type=PreflightTestType.CAPABILITY,
            result=PreflightResult.FAIL,
            description="Test regex capability",
            duration_ms=(time.time() - start_time) * 1000,
            error_message="Regex produced unexpected result",
        )
    
    @staticmethod
    def test_dataclass_support() -> PreflightTestResult:
        """Test dataclass capability."""
        import time
        from dataclasses import dataclass as dc, field as f
        start_time = time.time()
        
        try:
            @dc
            class TestClass:
                """TestClass implementation."""
                name: str
                values: List[int] = f(default_factory=list)
                
            obj = TestClass(name="test", values=[1, 2, 3])
            
            if obj.name == "test" and obj.values == [1, 2, 3]:
                return PreflightTestResult(
                    test_id="CAPABILITY_DATACLASS",
                    test_type=PreflightTestType.CAPABILITY,
                    result=PreflightResult.PASS,
                    description="Test dataclass capability",
                    duration_ms=(time.time() - start_time) * 1000,
                )
        except Exception as e:
            return PreflightTestResult(
                test_id="CAPABILITY_DATACLASS",
                test_type=PreflightTestType.CAPABILITY,
                result=PreflightResult.FAIL,
                description="Test dataclass capability",
                duration_ms=(time.time() - start_time) * 1000,
                error_message=str(e),
            )
            
        return PreflightTestResult(
            test_id="CAPABILITY_DATACLASS",
            test_type=PreflightTestType.CAPABILITY,
            result=PreflightResult.FAIL,
            description="Test dataclass capability",
            duration_ms=(time.time() - start_time) * 1000,
            error_message="Dataclass produced unexpected result",
        )


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_default_validator() -> PreflightValidator:
    """Create a validator with default configuration."""
    return PreflightValidator()


def create_strict_validator() -> PreflightValidator:
    """Create a validator with strict configuration."""
    config = PreflightConfig(
        on_failure=PreflightAction.HALT_WITH_ENGINE_COMPLIANCE_ERROR,
        run_iteration_test=True,
        run_structural_test=True,
        run_file_manifest_test=True,
        run_dependency_test=True,
        run_schema_version_test=True,
        run_environment_test=True,
    )
    validator = PreflightValidator(config=config)
    
    # Add capability tests
    validator.add_custom_test(CapabilityTest.test_json_parsing)
    validator.add_custom_test(CapabilityTest.test_regex_support)
    validator.add_custom_test(CapabilityTest.test_dataclass_support)
    
    return validator


def create_minimal_validator() -> PreflightValidator:
    """Create a validator with minimal tests."""
    config = PreflightConfig(
        on_failure=PreflightAction.WARN_AND_CONTINUE,
        run_iteration_test=True,
        run_structural_test=False,
        run_file_manifest_test=False,
        run_dependency_test=False,
        run_schema_version_test=False,
        run_environment_test=True,
    )
    return PreflightValidator(config=config)


def run_preflight_checks(
    required_files: Optional[List[str]] = None,
    required_packages: Optional[List[str]] = None,
    version_pins: Optional[Dict[str, str]] = None,
    required_env_vars: Optional[List[str]] = None,
) -> PreflightReport:
    """
    Convenience function to run pre-flight checks.
    
    Args:
        required_files: List of required file paths
        required_packages: List of required Python packages
        version_pins: Dict of schema file -> expected version
        required_env_vars: List of required environment variables
        
    Returns:
        PreflightReport with all test results
    """
    config = PreflightConfig()
    
    if required_files:
        config.file_manifest_test.required_files = required_files
        
    if required_packages:
        config.dependency_test.required_packages = required_packages
        
    if version_pins:
        config.schema_version_test.version_pins = version_pins
        
    if required_env_vars:
        config.required_env_vars = required_env_vars
        
    validator = PreflightValidator(config=config)
    return validator.run_all()
