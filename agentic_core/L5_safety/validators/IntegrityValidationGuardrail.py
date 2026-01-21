"""
Integrity Validation Guardrail - Consolidated Integrity Checks

Merges:
- L5IntegrityGateExecutor
- GravityEnforcer

Composable Rules:
- integrity_checks: Data integrity validation
- gravity_compliance: Gravity enforcement
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class IntegrityViolation:
    """Integrity violation record."""
    rule: str
    severity: str  # "warning", "error", "critical"
    description: str
    expected: Any = None
    actual: Any = None
    location: str | None = None


@dataclass
class IntegrityResult:
    """Result of integrity validation."""
    valid: bool
    violations: list[IntegrityViolation] = field(default_factory=list)
    checksum: str | None = None
    validation_time_ms: float = 0.0


class IntegrityValidationGuardrail:
    """
    Consolidated Integrity Validation Guardrail.

    Provides unified integrity checks with:
    - Data integrity validation (checksums, signatures)
    - Gravity compliance (import structure enforcement)
    - State consistency checks
    """

    def __init__(self):
        """Initialize integrity validation guardrail."""
        self.enabled_rules: list[str] = [
            "integrity_checks",
            "gravity_compliance",
        ]

        # Gravity rules (layer import restrictions)
        self.gravity_rules = {
            "L0": [],  # L0 can't import anything
            "L1": ["L0"],
            "L2": ["L0", "L1"],
            "L3": ["L0", "L1", "L2"],
            "L4": ["L0", "L1", "L2", "L3"],
            "L5": ["L0", "L1", "L2", "L3", "L4"],
        }

        # Checksum registry
        self.checksums: dict[str, str] = {}

        # Statistics
        self.validations_performed = 0
        self.violations_found = 0
        self.gravity_violations = 0

    async def validate_integrity(
        self,
        data: Any,
        expected_checksum: str | None = None,
        data_id: str | None = None
    ) -> IntegrityResult:
        """
        Validate data integrity.

        Args:
            data: Data to validate
            expected_checksum: Expected checksum (optional)
            data_id: Data identifier for tracking

        Returns:
            IntegrityResult
        """
        start_time = time.time()
        self.validations_performed += 1
        violations = []

        # Calculate checksum
        data_str = str(data)
        actual_checksum = hashlib.sha256(data_str.encode()).hexdigest()

        # Check against expected if provided
        if "integrity_checks" in self.enabled_rules:
            if expected_checksum and actual_checksum != expected_checksum:
                violations.append(IntegrityViolation(
                    rule="integrity_checks",
                    severity="error",
                    description="Checksum mismatch - data may be corrupted",
                    expected=expected_checksum,
                    actual=actual_checksum
                ))

            # Check against stored checksum
            if data_id and data_id in self.checksums:
                if self.checksums[data_id] != actual_checksum:
                    violations.append(IntegrityViolation(
                        rule="integrity_checks",
                        severity="warning",
                        description="Data has changed since last validation",
                        expected=self.checksums[data_id],
                        actual=actual_checksum
                    ))

        # Store checksum
        if data_id:
            self.checksums[data_id] = actual_checksum

        self.violations_found += len(violations)

        return IntegrityResult(
            valid=len(violations) == 0,
            violations=violations,
            checksum=actual_checksum,
            validation_time_ms=(time.time() - start_time) * 1000
        )

    async def validate_gravity(
        self,
        source_layer: str,
        imported_layers: list[str],
        file_path: str | None = None
    ) -> IntegrityResult:
        """
        Validate gravity compliance (layer import rules).

        Args:
            source_layer: Layer making imports (e.g., "L3")
            imported_layers: List of layers being imported
            file_path: Optional file path for context

        Returns:
            IntegrityResult
        """
        start_time = time.time()
        self.validations_performed += 1
        violations = []

        if "gravity_compliance" not in self.enabled_rules:
            return IntegrityResult(
                valid=True,
                violations=[],
                validation_time_ms=(time.time() - start_time) * 1000
            )

        allowed_imports = self.gravity_rules.get(source_layer, [])

        for imported in imported_layers:
            if imported not in allowed_imports and imported != source_layer:
                violations.append(IntegrityViolation(
                    rule="gravity_compliance",
                    severity="error",
                    description=f"Gravity violation: {source_layer} cannot import from {imported}",
                    expected=f"Allowed: {allowed_imports}",
                    actual=imported,
                    location=file_path
                ))
                self.gravity_violations += 1

        self.violations_found += len(violations)

        return IntegrityResult(
            valid=len(violations) == 0,
            violations=violations,
            validation_time_ms=(time.time() - start_time) * 1000
        )

    def register_checksum(self, data_id: str, checksum: str) -> None:
        """Register expected checksum for data."""
        self.checksums[data_id] = checksum

    def calculate_checksum(self, data: Any) -> str:
        """Calculate SHA256 checksum for data."""
        data_str = str(data)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def verify_checksum(self, data: Any, expected: str) -> bool:
        """Verify data matches expected checksum."""
        actual = self.calculate_checksum(data)
        return actual == expected

    def get_statistics(self) -> dict[str, Any]:
        """Get integrity validation statistics."""
        return {
            "validations_performed": self.validations_performed,
            "violations_found": self.violations_found,
            "gravity_violations": self.gravity_violations,
            "registered_checksums": len(self.checksums),
            "enabled_rules": self.enabled_rules
        }
