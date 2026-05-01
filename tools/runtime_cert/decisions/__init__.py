"""Phase D runtime-certification decision schema package.

Phase D.1 lands here as schema-only code per ADR-080 §0:
- ``cert_decision_record.py`` — frozen ``CertificationDecisionRecord``
  dataclass + ``compute_decision_id()`` deterministic hash helper.

No evaluator logic, no ledger writer, no scanner changes. ADR-080 §11
gates D.2 / D.3 / D.4 / D.5 each on their own Author-Gate.
"""
