"""ADG Prompt Assembly — retrieval adapters (C0 side).

These adapters fetch raw data from canonical ADG sources and return
typed EvidenceItem/EvidenceBundle objects. Prompt assembly NEVER
calls SQLite/JSON/graph DB directly — only through these adapters.
"""
