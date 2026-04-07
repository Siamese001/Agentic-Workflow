"""Opportunity 5: Advanced Security & Compliance Framework

Implements unified security, data classification, access control, privacy controls,
and comprehensive audit logging for the 4-layer retrieval pattern.
"""

import asyncio
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from .implementation_plan import LayerType, QueryRequest, SecurityContext

logger = logging.getLogger(__name__)


class DataClassification(Enum):
    """Data classification levels."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    SENSITIVE_PII = "sensitive_pii"


class ComplianceFramework(Enum):
    """Compliance frameworks."""

    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    CCPA = "ccpa"


class AccessLevel(Enum):
    """Access levels for permissions."""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    AUDIT = "audit"


class SecurityAction(Enum):
    """Security actions for auditing."""

    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    DATA_ACCESSED = "data_accessed"
    DATA_MODIFIED = "data_modified"
    DATA_DELETED = "data_deleted"
    PRIVACY_VIOLATION = "privacy_violation"
    COMPLIANCE_BREACH = "compliance_breach"
    SECURITY_INCIDENT = "security_incident"


@dataclass
class SecurityPolicy:
    """Security policy definition."""

    policy_id: str
    name: str
    description: str
    data_classification: DataClassification
    compliance_frameworks: list[ComplianceFramework]
    access_rules: dict[str, list[str]]  # role -> permissions
    retention_days: int
    encryption_required: bool
    audit_required: bool
    data_masking_rules: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class AuditLogEntry:
    """Audit log entry."""

    entry_id: str
    timestamp: datetime
    user_id: str
    action: SecurityAction
    resource_type: str
    resource_id: str
    layer_type: LayerType
    ip_address: str
    user_agent: str
    success: bool
    details: dict[str, Any] = field(default_factory=dict)
    compliance_tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "action": self.action.value,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "layer_type": self.layer_type.value,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "success": self.success,
            "details": self.details,
            "compliance_tags": self.compliance_tags,
        }


@dataclass
class ComplianceReport:
    """Compliance report."""

    report_id: str
    framework: ComplianceFramework
    period_start: datetime
    period_end: datetime
    total_access_requests: int
    granted_access: int
    denied_access: int
    privacy_violations: int
    compliance_breaches: int
    data_retention_violations: int
    audit_entries: list[AuditLogEntry]
    generated_at: datetime = field(default_factory=datetime.now)


class DataClassifier:
    """Classifies data based on content and context."""

    def __init__(self):
        self.classification_rank = {
            DataClassification.PUBLIC: 0,
            DataClassification.INTERNAL: 1,
            DataClassification.CONFIDENTIAL: 2,
            DataClassification.RESTRICTED: 3,
            DataClassification.SENSITIVE_PII: 4,
        }

        self.classification_rules = {
            DataClassification.PUBLIC: ["public", "general", "announcement", "news"],
            DataClassification.INTERNAL: ["internal", "company", "employee", "internal_use"],
            DataClassification.CONFIDENTIAL: ["confidential", "proprietary", "trade_secret", "business_plan"],
            DataClassification.RESTRICTED: ["restricted", "classified", "top_secret", "executive"],
            DataClassification.SENSITIVE_PII: [
                "ssn",
                "social_security",
                "credit_card",
                "bank_account",
                "personal",
                "private",
                "contact_info",
                "medical",
            ],
        }

        self.pii_patterns = [
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN pattern
            r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",  # Credit card pattern
            r"\b\d{9}\b",  # Generic 9-digit number
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email pattern
        ]

    def classify_text(self, text: str, context: dict[str, Any] | None = None) -> DataClassification:
        """Classify text based on content."""
        text_lower = text.lower()

        # Check for PII patterns first (highest priority)
        import re

        for pattern in self.pii_patterns:
            if re.search(pattern, text):
                return DataClassification.SENSITIVE_PII

        # Check classification keywords
        classification_scores = {}

        for classification, keywords in self.classification_rules.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            classification_scores[classification] = score

        # Consider context if provided
        if context:
            if context.get("contains_pii", False):
                return DataClassification.SENSITIVE_PII
            if context.get("financial_data", False):
                return DataClassification.RESTRICTED
            if context.get("employee_data", False):
                return DataClassification.CONFIDENTIAL

        # Return classification with highest score
        if classification_scores:
            return max(classification_scores, key=classification_scores.get)

        return DataClassification.INTERNAL  # Default classification

    def classify_cache_entry(self, key: str, value: Any, layer_type: LayerType) -> DataClassification:
        """Classify cache entry."""
        # Classify based on key pattern
        key_classification = self.classify_text(key)

        # Classify based on value if it's text
        if isinstance(value, str):
            value_classification = self.classify_text(value)
            # Return higher classification
            if self.classification_rank[value_classification] > self.classification_rank[key_classification]:
                return value_classification

        # Layer-specific classification rules
        layer_classifications = {
            LayerType.REDIS_EXACT_MATCH: DataClassification.INTERNAL,
            LayerType.SEMANTIC_CACHE: DataClassification.INTERNAL,
            LayerType.RAG_RETRIEVAL: DataClassification.CONFIDENTIAL,
            LayerType.AGENTIC_ACTION: DataClassification.RESTRICTED,
        }

        layer_classification = layer_classifications.get(layer_type, DataClassification.INTERNAL)

        # Return highest classification
        classifications = [key_classification, layer_classification]
        if isinstance(value, str):
            classifications.append(self.classify_text(value))

        return max(classifications, key=lambda c: self.classification_rank[c])


class AccessController:
    """Controls access based on roles and permissions."""

    def __init__(self):
        self.role_permissions: dict[str, set[AccessLevel]] = {}
        self.user_roles: dict[str, set[str]] = {}
        self.resource_permissions: dict[str, dict[str, set[AccessLevel]]] = defaultdict(dict)
        self._lock = asyncio.Lock()

    def add_role(self, role: str, permissions: list[AccessLevel]):
        """Add role with permissions."""
        self.role_permissions[role] = set(permissions)
        logger.info(f"Added role {role} with permissions {[p.value for p in permissions]}")

    def assign_user_role(self, user_id: str, role: str):
        """Assign role to user."""
        if user_id not in self.user_roles:
            self.user_roles[user_id] = set()
        self.user_roles[user_id].add(role)
        logger.info(f"Assigned role {role} to user {user_id}")

    def set_resource_permissions(
        self, resource_type: str, resource_id: str, role_permissions: dict[str, list[AccessLevel]]
    ):
        """Set permissions for specific resource."""
        self.resource_permissions[resource_type][resource_id] = {
            role: set(permissions) for role, permissions in role_permissions.items()
        }

    async def check_access(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        access_level: AccessLevel,
        layer_type: LayerType,
    ) -> bool:
        """Check if user has access to resource."""
        async with self._lock:
            # Get user's roles
            user_roles = self.user_roles.get(user_id, set())
            if not user_roles:
                return False

            # Check resource-specific permissions first
            resource_perms = self.resource_permissions.get(resource_type, {})
            if resource_id in resource_perms:
                for role in user_roles:
                    if role in resource_perms[resource_id]:
                        if access_level in resource_perms[resource_id][role]:
                            return True

            # Check general role permissions
            for role in user_roles:
                role_perms = self.role_permissions.get(role, set())
                if access_level in role_perms:
                    return True

            return False

    def get_user_permissions(self, user_id: str) -> dict[str, list[str]]:
        """Get all permissions for user."""
        user_roles = self.user_roles.get(user_id, set())
        permissions = set()

        for role in user_roles:
            role_perms = self.role_permissions.get(role, set())
            permissions.update(role_perms)

        return {"roles": list(user_roles), "permissions": [p.value for p in permissions]}


class PrivacyEngine:
    """Handles data privacy and masking."""

    def __init__(self):
        self.masking_rules = {
            DataClassification.SENSITIVE_PII: {
                "email": lambda x: x[:2] + "***@" + x.split("@")[1] if "@" in x else "***",
                "phone": lambda x: "***-" + x[-4:] if len(x) > 7 else "***",
                "ssn": lambda x: "***-**-" + x[-4:] if len(x) > 4 else "***",
                "credit_card": lambda x: "****-****-****-" + x[-4:] if len(x) > 4 else "***",
                "default": lambda x: "***",
            },
            DataClassification.RESTRICTED: {
                "default": lambda x: x[:2] + "***" + x[-2:] if len(x) > 4 else "***"
            },
            DataClassification.CONFIDENTIAL: {
                "default": lambda x: x[:4] + "***" + x[-4:] if len(x) > 8 else "***"
            },
        }

    def mask_data(
        self, data: Any, classification: DataClassification, context: dict[str, Any] | None = None
    ) -> Any:
        """Mask data based on classification."""
        if classification == DataClassification.PUBLIC:
            return data

        if isinstance(data, str):
            return self._mask_text(data, classification)
        elif isinstance(data, dict):
            return self._mask_dict(data, classification)
        elif isinstance(data, list):
            return [self.mask_data(item, classification, context) for item in data]
        else:
            # For other types, return masked placeholder
            return "***"

    def _mask_text(self, text: str, classification: DataClassification) -> str:
        """Mask text data."""
        rules = self.masking_rules.get(classification, {})

        # Check for specific patterns
        import re

        # Email masking
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        if re.search(email_pattern, text):
            email_mask = rules.get("email", rules.get("default", lambda x: "***"))
            return re.sub(email_pattern, lambda m: email_mask(m.group()), text)

        # Phone masking
        phone_pattern = r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"
        if re.search(phone_pattern, text):
            phone_mask = rules.get("phone", rules.get("default", lambda x: "***"))
            return re.sub(phone_pattern, lambda m: phone_mask(m.group()), text)

        # SSN masking
        ssn_pattern = r"\b\d{3}-\d{2}-\d{4}\b"
        if re.search(ssn_pattern, text):
            ssn_mask = rules.get("ssn", rules.get("default", lambda x: "***"))
            return re.sub(ssn_pattern, lambda m: ssn_mask(m.group()), text)

        # Credit card masking
        cc_pattern = r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"
        if re.search(cc_pattern, text):
            cc_mask = rules.get("credit_card", rules.get("default", lambda x: "***"))
            return re.sub(cc_pattern, lambda m: cc_mask(m.group()), text)

        # Default masking
        default_mask = rules.get("default", lambda x: "***")
        return default_mask(text)

    def _mask_dict(self, data: dict[str, Any], classification: DataClassification) -> dict[str, Any]:
        """Mask dictionary data."""
        masked_dict = {}

        for key, value in data.items():
            # Check if key indicates sensitive data
            key_lower = key.lower()
            if any(keyword in key_lower for keyword in ["password", "secret", "token", "key", "credential"]):
                masked_dict[key] = "***"
            else:
                masked_dict[key] = self.mask_data(value, classification)

        return masked_dict


class AuditLogger:
    """Comprehensive audit logging system."""

    def __init__(self, retention_days: int = 2555):  # 7 years default
        self.retention_days = retention_days
        self.audit_logs: deque = deque(maxlen=100000)  # Store last 100k entries
        self.compliance_reports: dict[ComplianceFramework, list[ComplianceReport]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def log_access(
        self,
        user_id: str,
        action: SecurityAction,
        resource_type: str,
        resource_id: str,
        layer_type: LayerType,
        success: bool,
        ip_address: str,
        user_agent: str,
        details: dict[str, Any] | None = None,
        compliance_tags: list[str] | None = None,
    ):
        """Log access event."""
        entry = AuditLogEntry(
            entry_id=f"audit_{int(time.time() * 1000000)}_{hash(user_id)}",
            timestamp=datetime.now(),
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            layer_type=layer_type,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            details=details or {},
            compliance_tags=compliance_tags or [],
        )

        async with self._lock:
            self.audit_logs.append(entry)

        # Log to external system (in real implementation)
        logger.info(
            f"Audit log: {user_id} {action.value} {resource_type}/{resource_id} - {'SUCCESS' if success else 'DENIED'}"
        )

    async def log_security_incident(
        self,
        incident_type: str,
        severity: str,
        description: str,
        affected_resources: list[str],
        user_id: str | None = None,
        compliance_tags: list[str] | None = None,
    ):
        """Log security incident."""
        await self.log_access(
            user_id=user_id or "system",
            action=SecurityAction.SECURITY_INCIDENT,
            resource_type="security_incident",
            resource_id=incident_type,
            layer_type=LayerType.REDIS_EXACT_MATCH,  # Default layer
            success=False,
            ip_address="system",
            user_agent="security_monitor",
            details={
                "incident_type": incident_type,
                "severity": severity,
                "description": description,
                "affected_resources": affected_resources,
            },
            compliance_tags=["security", "incident", *(compliance_tags or [])],
        )

    async def generate_compliance_report(
        self, framework: ComplianceFramework, period_start: datetime, period_end: datetime
    ) -> ComplianceReport:
        """Generate compliance report."""
        async with self._lock:
            # Filter audit logs for the period
            period_logs = [log for log in self.audit_logs if period_start <= log.timestamp <= period_end]

        # Calculate statistics
        total_requests = len(period_logs)
        granted_access = len([log for log in period_logs if log.success])
        denied_access = total_requests - granted_access

        privacy_violations = len(
            [log for log in period_logs if log.action == SecurityAction.PRIVACY_VIOLATION]
        )

        compliance_breaches = len(
            [log for log in period_logs if log.action == SecurityAction.COMPLIANCE_BREACH]
        )

        data_retention_violations = len(
            [log for log in period_logs if "retention_violation" in log.compliance_tags]
        )

        report = ComplianceReport(
            report_id=f"report_{framework.value}_{int(time.time())}",
            framework=framework,
            period_start=period_start,
            period_end=period_end,
            total_access_requests=total_requests,
            granted_access=granted_access,
            denied_access=denied_access,
            privacy_violations=privacy_violations,
            compliance_breaches=compliance_breaches,
            data_retention_violations=data_retention_violations,
            audit_entries=period_logs,
        )

        self.compliance_reports[framework].append(report)

        logger.info(
            f"Generated {framework.value} compliance report: {total_requests} requests, {privacy_violations} violations"
        )

        return report

    async def cleanup_old_logs(self):
        """Clean up old audit logs."""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)

        async with self._lock:
            original_size = len(self.audit_logs)
            self.audit_logs = deque(
                [log for log in self.audit_logs if log.timestamp >= cutoff_date], maxlen=100000
            )
            removed = original_size - len(self.audit_logs)

        if removed > 0:
            logger.info(f"Cleaned up {removed} old audit logs (older than {self.retention_days} days)")

        return removed

    def get_audit_summary(self, period_days: int = 30) -> dict[str, Any]:
        """Get audit summary for period."""
        cutoff_date = datetime.now() - timedelta(days=period_days)

        recent_logs = [log for log in self.audit_logs if log.timestamp >= cutoff_date]

        action_counts = defaultdict(int)
        layer_counts = defaultdict(int)
        success_rate = 0.0

        if recent_logs:
            for log in recent_logs:
                action_counts[log.action.value] += 1
                layer_counts[log.layer_type.value] += 1

            success_rate = sum(1 for log in recent_logs if log.success) / len(recent_logs)

        return {
            "period_days": period_days,
            "total_entries": len(recent_logs),
            "success_rate": success_rate,
            "action_counts": dict(action_counts),
            "layer_counts": dict(layer_counts),
            "retention_days": self.retention_days,
            "total_stored": len(self.audit_logs),
        }


class SecurityGateway:
    """Main security gateway for unified security controls."""

    def __init__(self):
        self.data_classifier = DataClassifier()
        self.access_controller = AccessController()
        self.privacy_engine = PrivacyEngine()
        self.audit_logger = AuditLogger()
        self.security_policies: dict[str, SecurityPolicy] = {}

        # Initialize default roles and permissions
        self._initialize_default_roles()

        # Background tasks
        self._cleanup_task = None
        self._running = False

    def _initialize_default_roles(self):
        """Initialize default security roles."""
        self.access_controller.add_role(
            "admin",
            [AccessLevel.READ, AccessLevel.WRITE, AccessLevel.DELETE, AccessLevel.ADMIN, AccessLevel.AUDIT],
        )

        self.access_controller.add_role("user", [AccessLevel.READ, AccessLevel.WRITE])

        self.access_controller.add_role("viewer", [AccessLevel.READ])

        self.access_controller.add_role("auditor", [AccessLevel.READ, AccessLevel.AUDIT])

        logger.info("Initialized default security roles")

    async def start(self):
        """Start security gateway services."""
        self._running = True
        self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
        logger.info("Started security gateway")

    async def stop(self):
        """Stop security gateway services."""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
        logger.info("Stopped security gateway")

    async def _periodic_cleanup(self):
        """Periodic cleanup of old audit logs."""
        while self._running:
            try:
                await asyncio.sleep(86400)  # Run daily
                await self.audit_logger.cleanup_old_logs()
            except asyncio.CancelledError:
                break
            except Exception as e:  # guardian: allow-log-and-swallow -- teardown/cleanup context -- swallow is conventional in resource-release paths
                logger.error(f"Error in periodic cleanup: {e}")

    async def authenticate_request(self, request: QueryRequest, security_context: SecurityContext) -> bool:
        """Authenticate incoming request."""
        for role in security_context.roles:
            if role in self.access_controller.role_permissions:
                self.access_controller.assign_user_role(security_context.user_id, role)

        # Check if user has basic access
        has_access = await self.access_controller.check_access(
            security_context.user_id,
            "query",
            request.query_id,
            AccessLevel.READ,
            LayerType.REDIS_EXACT_MATCH,  # Default to lowest layer
        )

        await self.audit_logger.log_access(
            user_id=security_context.user_id,
            action=SecurityAction.ACCESS_GRANTED if has_access else SecurityAction.ACCESS_DENIED,
            resource_type="query",
            resource_id=request.query_id,
            layer_type=LayerType.REDIS_EXACT_MATCH,
            success=has_access,
            ip_address=security_context.access_permissions.get("ip_address", "unknown"),
            user_agent=security_context.access_permissions.get("user_agent", "unknown"),
            details={"query_length": len(request.user_query)},
            compliance_tags=security_context.compliance_requirements,
        )

        return has_access

    async def filter_response_data(
        self, layer_type: LayerType, data: Any, security_context: SecurityContext
    ) -> Any:
        """Filter and mask response data based on security policies."""
        # Classify data
        if isinstance(data, dict) and "key" in data:
            classification = self.data_classifier.classify_cache_entry(
                data["key"], data.get("value"), layer_type
            )
        else:
            classification = self.data_classifier.classify_text(str(data))

        # Check if user has access to this classification
        if classification in [DataClassification.RESTRICTED, DataClassification.SENSITIVE_PII]:
            has_clearance = await self.access_controller.check_access(
                security_context.user_id,
                "classified_data",
                classification.value,
                AccessLevel.READ,
                layer_type,
            )

            if not has_clearance:
                await self.audit_logger.log_access(
                    user_id=security_context.user_id,
                    action=SecurityAction.ACCESS_DENIED,
                    resource_type="classified_data",
                    resource_id=classification.value,
                    layer_type=layer_type,
                    success=False,
                    ip_address=security_context.access_permissions.get("ip_address", "unknown"),
                    user_agent=security_context.access_permissions.get("user_agent", "unknown"),
                    details={"classification": classification.value},
                    compliance_tags=security_context.compliance_requirements,
                )

                return None  # Deny access to classified data

        # Apply privacy masking
        masked_data = self.privacy_engine.mask_data(data, classification)

        # Log data access
        await self.audit_logger.log_access(
            user_id=security_context.user_id,
            action=SecurityAction.DATA_ACCESSED,
            resource_type="layer_data",
            resource_id=layer_type.value,
            layer_type=layer_type,
            success=True,
            ip_address=security_context.access_permissions.get("ip_address", "unknown"),
            user_agent=security_context.access_permissions.get("user_agent", "unknown"),
            details={
                "classification": classification.value,
                "masked": classification != DataClassification.PUBLIC,
            },
            compliance_tags=security_context.compliance_requirements,
        )

        return masked_data

    async def validate_compliance(
        self, framework: ComplianceFramework, security_context: SecurityContext
    ) -> bool:
        """Validate compliance with framework requirements."""
        framework_requirements = {
            ComplianceFramework.GDPR: ["data_minimization", "consent_management", "right_to_be_forgotten"],
            ComplianceFramework.HIPAA: ["phi_protection", "access_controls", "audit_logging"],
            ComplianceFramework.SOX: ["financial_controls", "segregation_of_duties", "audit_trails"],
            ComplianceFramework.PCI_DSS: ["cardholder_data", "encryption", "access_control"],
            ComplianceFramework.CCPA: ["privacy_rights", "data_sale_optout", "access_transparency"],
        }

        required_controls = framework_requirements.get(framework, [])
        user_permissions = security_context.access_permissions

        # Check if user has required compliance controls
        for control in required_controls:
            if not user_permissions.get(control, False):
                await self.audit_logger.log_security_incident(
                    incident_type="compliance_violation",
                    severity="medium",
                    description=f"Missing compliance control: {control}",
                    affected_resources=[framework.value],
                    user_id=security_context.user_id,
                )

                return False

        return True

    def add_security_policy(self, policy: SecurityPolicy):
        """Add security policy."""
        self.security_policies[policy.policy_id] = policy
        logger.info(f"Added security policy: {policy.name}")

    async def enforce_data_retention(self, layer_type: LayerType, data_age_days: int) -> bool:
        """Enforce data retention policies."""
        # Get applicable policies for layer
        applicable_policies = [
            policy
            for policy in self.security_policies.values()
            if layer_type.value in policy.data_masking_rules.get("applicable_layers", [layer_type.value])
        ]

        if not applicable_policies:
            return True  # No retention policies apply

        for policy in applicable_policies:
            if data_age_days > policy.retention_days:
                await self.audit_logger.log_security_incident(
                    incident_type="retention_violation",
                    severity="low",
                    description=f"Data exceeds retention policy: {policy.name}",
                    affected_resources=[f"{layer_type.value}_data"],
                    compliance_tags=["retention", policy.policy_id],
                )

                return False  # Violation detected

        return True

    def get_security_status(self) -> dict[str, Any]:
        """Get overall security status."""
        return {
            "policies_count": len(self.security_policies),
            "users_count": len(self.access_controller.user_roles),
            "roles_count": len(self.access_controller.role_permissions),
            "audit_summary": self.audit_logger.get_audit_summary(),
            "compliance_reports": {
                framework.value: len(reports)
                for framework, reports in self.audit_logger.compliance_reports.items()
            },
        }
