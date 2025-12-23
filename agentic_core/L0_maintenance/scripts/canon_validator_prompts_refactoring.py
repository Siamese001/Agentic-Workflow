"""
Refactoring and import resolution few-shot patterns.
Used by ArchitectureGovernor, DependencySentinel, StructuralEngineer.
"""

FEW_SHOT_GLOBAL_REFACTOR = """
FEW-SHOT REFACTORING PATTERNS (Follow exactly for subatomic compliance):

EXAMPLE 1: Monolith Function → Atomic Split
BAD (violates Atomicity Law):
def handle_order(order):
    # 250 lines: validate, charge, inventory, email...

GOOD (compliant):
# Split into:
# apps_rg/orders/validate.py
# apps_rg/orders/charge.py
# apps_rg/orders/notify.py
# Each file <180 lines, single responsibility

EXAMPLE 2: Incorrect Depth → Correct Depth
BAD: apps/payment/helpers.py (depth 3)
GOOD: Move to apps_shared/payments/domain/charge_service.py (depth 5)

EXAMPLE 3: Duplicated Validation Logic
BAD: Same Pydantic model in lic.py and rg.py
GOOD: Single source in schemas/payment.py, imported with:
from schemas.payment import PaymentSchema

EXAMPLE 4: Root Directory Noise
BAD: debug_tool.py in root
GOOD: Move to scripts/debug_tool.py or delete

Prioritize minimal changes. Always preserve behavior.
"""

FEW_SHOT_IMPORT_FIXES = """
FEW-SHOT IMPORT RESOLUTION (DependencySentinel):

EXAMPLE 1: Relative Import Wrong Depth
BAD: from utils.validation import validate
GOOD: from apps_shared.validation.common import validate

EXAMPLE 2: Missing Schema
BAD: ImportError: cannot import name 'OrderSchema'
GOOD: from schemas.order import OrderSchema

EXAMPLE 3: Circular Dependency
BAD: orders/service.py imports payments/utils.py
      payments/utils.py imports orders/models.py
GOOD: Extract shared types to schemas/shared.py
      Both import from schemas/shared.py

EXAMPLE 4: Unused Import
GOOD: Remove line entirely — do not replace
"""
