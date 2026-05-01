"""Per-route-shape evidence extractors for runtime certification (Phase C.3+).

Houses bounded, read-only helpers that consume ``NormalizedTraceRow`` rows
(from Phase C.2) and produce structured evidence reports — one extractor per
route shape. No extractor certifies any app; ``runtime_certification_status``
remains ``NOT_CERTIFIED`` throughout.

Extractors by route shape
--------------------------
- ``r3_evidence.py`` — R3_grounded_read 8-contract evidence (Phase C.3)
- ``btc_evidence.py`` — build_time_compiler 3-contract evidence (Phase C.4, future)
- ``formal_exception_evidence.py`` — formal-exception evidence (Phase C.5, future)
"""
