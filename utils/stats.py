"""Statistical and comparison helpers."""

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency


def gap_table(frame: pd.DataFrame, group: str) -> pd.DataFrame:
    """Aggregate volume, actual pass rate, expected rate, and percentage-point gap."""
    result = frame.groupby(group, observed=True).agg(
        exams=("exam_id", "size"),
        pass_rate=("passed", "mean"),
        expected=("expected_pass_rate", "mean"),
    ).reset_index()
    result["gap"] = (result["pass_rate"] - result["expected"]) * 100
    return result.sort_values("gap", ascending=False)


def covid_test(frame: pd.DataFrame) -> dict[str, float]:
    """Return chi-square and Cramer's V for period versus observed pass/fail."""
    valid = frame.dropna(subset=["passed", "period"])
    table = pd.crosstab(valid["period"], valid["passed"])
    if table.shape[0] < 2 or table.shape[1] < 2:
        return {"chi2": np.nan, "p_value": np.nan, "cramers_v": np.nan, "n": len(valid)}
    chi2, p_value, _, _ = chi2_contingency(table)
    n = table.values.sum()
    v = np.sqrt(chi2 / (n * min(table.shape[0] - 1, table.shape[1] - 1)))
    return {"chi2": chi2, "p_value": p_value, "cramers_v": v, "n": int(n)}
