"""Dataset loading, exclusion filtering, and train/val splitting."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.preprocessing import LabelEncoder

from .constants import (
    FEATURE_ORDER,
    MAX_RETRY_COUNT,
    OOD_BUDGET_SENTINEL,
    REPAIR_OUTCOME_CLASSES,
    UNKNOWN_CLASS_INDEX,
)

# ---------------------------------------------------------------------------
# Exclusion rules — order matters: first match wins, rest skipped for that row
# ---------------------------------------------------------------------------
_EXCLUSION_RULES: list[tuple[str, Callable[[pd.DataFrame], pd.Series]]] = [
    (
        "ood_flag",
        lambda df: df["ood_flag"].astype(bool),
    ),
    (
        "heuristic_fallback_no_divergence",
        lambda df: (df["source"] == "HEURISTIC_FALLBACK") & (~df["divergence_flag"].astype(bool)),
    ),
    (
        "unknown_failure_class",
        lambda df: df["failure_class"] == UNKNOWN_CLASS_INDEX,
    ),
    (
        "budget_sentinel",
        lambda df: df["budget_remaining"] == OOD_BUDGET_SENTINEL,
    ),
    (
        "missing_outcome",
        lambda df: df["repair_outcome"].isna(),
    ),
    (
        "excessive_retries",
        lambda df: df["retry_count"] > MAX_RETRY_COUNT,
    ),
    (
        "stale_excluded_flag",
        lambda df: df["excluded"].astype(bool) if "excluded" in df.columns else pd.Series(False, index=df.index),
    ),
]


@dataclass
class SplitDataset:
    X_train: np.ndarray
    y_train: np.ndarray
    X_calib: np.ndarray
    y_calib: np.ndarray
    X_val: np.ndarray
    y_val: np.ndarray
    failure_class_train: np.ndarray
    failure_class_val: np.ndarray
    train_meta: pd.DataFrame
    val_meta: pd.DataFrame
    label_encoder: LabelEncoder
    excluded_df: pd.DataFrame


def load_dataset(path: str) -> pd.DataFrame:
    """Load dataset from CSV or Parquet."""
    if path.endswith(".parquet"):
        return pd.read_parquet(path)
    return pd.read_csv(path, encoding="utf-8")


def apply_exclusions(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (included_df, excluded_df) with exclusion_reason column on excluded."""
    excluded_mask = pd.Series(False, index=df.index)
    exclusion_reasons = pd.Series("", index=df.index, dtype=str)

    for reason, rule_fn in _EXCLUSION_RULES:
        newly_excluded = rule_fn(df) & ~excluded_mask
        exclusion_reasons[newly_excluded] = reason
        excluded_mask |= newly_excluded

    excluded = df[excluded_mask].copy()
    excluded["exclusion_reason"] = exclusion_reasons[excluded_mask]
    included = df[~excluded_mask].copy()
    return included, excluded


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """Keep first occurrence of each (run_id, signal_hash) pair."""
    sort_col = "run_clock" if "run_clock" in df.columns else "run_id"
    return df.sort_values(sort_col).drop_duplicates(
        subset=["run_id", "signal_hash"], keep="first"
    )


def encode_features(df: pd.DataFrame) -> np.ndarray:
    """Extract features in FEATURE_ORDER as float64 array."""
    return df[FEATURE_ORDER].astype(float).to_numpy()  # type: ignore[return-value]


def make_label_encoder() -> LabelEncoder:
    le = LabelEncoder()
    le.fit(REPAIR_OUTCOME_CLASSES)
    return le


def make_split(
    df: pd.DataFrame,
    temporal_val_fraction: float = 0.20,
    calib_fraction: float = 0.10,
    random_state: int = 42,
) -> SplitDataset:
    """Temporal outer split + stratified inner calibration split.

    Temporal split is the primary evaluation strategy: last
    temporal_val_fraction of events (by run_clock) form the holdout set.
    The remaining pool is further split to carve out a calibration fold.
    """
    # Filter to valid outcomes only
    df = df[df["repair_outcome"].isin(REPAIR_OUTCOME_CLASSES)].copy()

    # Sort by run_clock for temporal integrity; fall back to row order
    if "run_clock" in df.columns:
        df = df.sort_values("run_clock").reset_index(drop=True)

    n = len(df)
    n_val = max(1, int(n * temporal_val_fraction))
    train_pool = df.iloc[: n - n_val].copy()
    val_df = df.iloc[n - n_val :].copy()

    le = make_label_encoder()
    y_pool = le.transform(train_pool["repair_outcome"])

    n_calib = max(1, int(len(train_pool) * calib_fraction))
    sss = StratifiedShuffleSplit(
        n_splits=1, test_size=n_calib, random_state=random_state
    )

    for train_idx, calib_idx in sss.split(np.zeros(len(train_pool)), y_pool):
        train_df = train_pool.iloc[train_idx].copy()
        calib_df = train_pool.iloc[calib_idx].copy()

        return SplitDataset(
            X_train=encode_features(train_df),
            y_train=le.transform(train_df["repair_outcome"]),
            X_calib=encode_features(calib_df),
            y_calib=le.transform(calib_df["repair_outcome"]),
            X_val=encode_features(val_df),
            y_val=le.transform(val_df["repair_outcome"]),
            failure_class_train=train_df["failure_class"].to_numpy(),
            failure_class_val=val_df["failure_class"].to_numpy(),
            train_meta=train_df,
            val_meta=val_df,
            label_encoder=le,
            excluded_df=pd.DataFrame(),
        )

    raise RuntimeError("StratifiedShuffleSplit produced no splits")  # unreachable
