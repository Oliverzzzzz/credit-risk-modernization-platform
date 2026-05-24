from __future__ import annotations

import pandas as pd
import numpy as np


def population_stability_index(reference: pd.Series, current: pd.Series, buckets: int = 10) -> float:
    quantiles = reference.quantile([i / buckets for i in range(1, buckets)]).drop_duplicates().to_list()
    reference_bins = pd.cut(reference, bins=[-float("inf"), *quantiles, float("inf")])
    current_bins = pd.cut(current, bins=[-float("inf"), *quantiles, float("inf")])
    ref_dist = reference_bins.value_counts(normalize=True).sort_index().replace(0, 0.0001)
    cur_dist = current_bins.value_counts(normalize=True).sort_index().replace(0, 0.0001)
    return float(((cur_dist - ref_dist) * np.log(cur_dist / ref_dist)).sum())


def drift_summary(reference: pd.DataFrame, current: pd.DataFrame, columns: list[str]) -> dict[str, float]:
    summary: dict[str, float] = {}
    for column in columns:
        if column in reference.columns and column in current.columns:
            summary[column] = population_stability_index(reference[column], current[column])
    return summary
