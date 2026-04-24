"""Labeled calibration fixtures (W0.P1).

One JSON file per path. Each fixture is a list of records; each record is a dict
with ``score`` (float in [0,1]) and ``label`` (bool — True means "threshold should
fire / is positive"). Paths R1B/R3 also carry optional ``namespace`` for
per-namespace calibration (W2.P1 future use).
"""
