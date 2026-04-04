"""
Types module for apps_underwriting_ai.

Exports all domain type contracts for credit underwriting.
"""

# Underwriting request types
from .underwriting_request_types import (
    UnderwritingRequest,
    RequestedStructure,
    ExternalSignals,
    ProductType,
    DecisionType,
    InterestType,
    DecisionState,
)

# Borrower profile types
from .borrower_profile_types import (
    BorrowerProfile,
    OwnerInfo,
    EntityType,
)

# Financial package types
from .financial_package_types import (
    FinancialPackage,
    FinancialPeriod,
    CalculatedMetrics,
    FiscalType,
)

# Collateral package types
from .collateral_package_types import (
    CollateralPackage,
    CollateralType,
    LienPosition,
)

# Credit package types
from .credit_package_types import (
    CreditPackage,
)

# Banking package types
from .banking_package_types import (
    BankingPackage,
    DepositTrend,
)

# Document package types
from .document_package_types import (
    DocumentPackage,
    DocumentRef,
)

# Policy context types
from .policy_context_types import (
    PolicyContext,
    CollateralRules,
)

# Relationship context types
from .relationship_context_types import (
    RelationshipContext,
)

# Decision constraints types
from .decision_constraints_types import (
    DecisionConstraints,
)

# Risk feature types
from .risk_feature_types import (
    RiskFeatures,
    CapacityFeatures,
    LiquidityFeatures,
    CollateralFeatures,
    CreditFeatures,
    OperatingRiskFeatures,
    RelationshipFeatures,
    DocumentationFeatures,
    PolicyFeatures,
    CompositeFeatures,
    RiskGrade,
)

# Decision memo types
from .decision_memo_types import (
    DecisionMemo,
    EvidenceItem,
)

# Evidence register types
from .evidence_register_types import (
    EvidenceRegister,
    EvidenceEntry,
)

# Decision packet types
from .decision_packet_types import (
    DecisionPacket,
    AuditTrace,
)

__all__ = [
    # Request types
    "UnderwritingRequest",
    "RequestedStructure",
    "ExternalSignals",
    "ProductType",
    "DecisionType",
    "InterestType",
    "DecisionState",

    # Borrower types
    "BorrowerProfile",
    "OwnerInfo",
    "EntityType",

    # Financial types
    "FinancialPackage",
    "FinancialPeriod",
    "CalculatedMetrics",
    "FiscalType",

    # Collateral types
    "CollateralPackage",
    "CollateralType",
    "LienPosition",

    # Credit types
    "CreditPackage",

    # Banking types
    "BankingPackage",
    "DepositTrend",

    # Document types
    "DocumentPackage",
    "DocumentRef",

    # Policy types
    "PolicyContext",
    "CollateralRules",

    # Relationship types
    "RelationshipContext",

    # Constraints types
    "DecisionConstraints",

    # Risk feature types
    "RiskFeatures",
    "CapacityFeatures",
    "LiquidityFeatures",
    "CollateralFeatures",
    "CreditFeatures",
    "OperatingRiskFeatures",
    "RelationshipFeatures",
    "DocumentationFeatures",
    "PolicyFeatures",
    "CompositeFeatures",
    "RiskGrade",

    # Output types
    "DecisionMemo",
    "EvidenceItem",
    "EvidenceRegister",
    "EvidenceEntry",
    "DecisionPacket",
    "AuditTrace",
]
