"""
Types module for apps_underwriting_ai.

Exports all domain type contracts for credit underwriting.
"""

# Underwriting request types
# Banking package types
from .banking_package_types import (
    BankingPackage,
    DepositTrend,
)

# Borrower profile types
from .borrower_profile_types import (
    BorrowerProfile,
    EntityType,
    OwnerInfo,
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

# Decision constraints types
from .decision_constraints_types import (
    DecisionConstraints,
)

# Decision memo types
from .decision_memo_types import (
    DecisionMemo,
    EvidenceItem,
)

# Decision packet types
from .decision_packet_types import (
    AuditTrace,
    DecisionPacket,
)

# Document package types
from .document_package_types import (
    DocumentPackage,
    DocumentRef,
)

# Evidence register types
from .evidence_register_types import (
    EvidenceEntry,
    EvidenceRegister,
)

# Financial package types
from .financial_package_types import (
    CalculatedMetrics,
    FinancialPackage,
    FinancialPeriod,
    FiscalType,
)

# Policy context types
from .policy_context_types import (
    CollateralRules,
    PolicyContext,
)

# Relationship context types
from .relationship_context_types import (
    RelationshipContext,
)

# Risk feature types
from .risk_feature_types import (
    CapacityFeatures,
    CollateralFeatures,
    CompositeFeatures,
    CreditFeatures,
    DocumentationFeatures,
    LiquidityFeatures,
    OperatingRiskFeatures,
    PolicyFeatures,
    RelationshipFeatures,
    RiskFeatures,
    RiskGrade,
)
from .underwriting_request_types import (
    DecisionState,
    DecisionType,
    ExternalSignals,
    InterestType,
    ProductType,
    RequestedStructure,
    UnderwritingRequest,
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
