"""Composable mandatory-output closeout helpers."""

from .seal import (
    CLOSEOUT_MANDATORY_OUTPUT_PROFILE,
    MANDATORY_OUTPUT_COMMIT_MANIFEST,
    PRODUCT_MANDATORY_OUTPUT_PROFILE,
    begin_mandatory_output_transaction,
    seal_mandatory_output_bundle,
    validate_mandatory_output_seal,
)
from .terminal import apply_mandatory_closeout_state

__all__ = [
    "CLOSEOUT_MANDATORY_OUTPUT_PROFILE",
    "MANDATORY_OUTPUT_COMMIT_MANIFEST",
    "PRODUCT_MANDATORY_OUTPUT_PROFILE",
    "apply_mandatory_closeout_state",
    "begin_mandatory_output_transaction",
    "seal_mandatory_output_bundle",
    "validate_mandatory_output_seal",
]
