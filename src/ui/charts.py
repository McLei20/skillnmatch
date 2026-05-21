"""Pure data helpers for the Plan-step charts.

Streamlit- and Plotly-free so they can be unit-tested in isolation. The
rendering code in plan.py builds Plotly figures from the dataframes these
helpers return.
"""
from __future__ import annotations

from typing import Optional

import pandas as pd


def soft_skill_radar_data(
    soft_rules_df: Optional[pd.DataFrame], top_n: int = 8
) -> tuple[list[str], list[float]]:
    """Return ordered (axes, values) for the soft-skill radar chart.

    Axes = up to ``top_n`` title-cased soft skills, sorted by lift descending
    (deduped: each skill appears at most once via its best rule). Value =
    ``consequent support`` of the chosen rule (falls back to ``support`` if the
    column is missing).
    """
    if (
        soft_rules_df is None
        or len(soft_rules_df) == 0
        or "consequents" not in soft_rules_df.columns
        or "lift" not in soft_rules_df.columns
    ):
        return [], []

    df = soft_rules_df.copy()
    df = df[df["consequents"].apply(lambda x: len(x) == 1)]
    if len(df) == 0:
        return [], []
    df["skill"] = df["consequents"].apply(lambda x: list(x)[0])

    support_col = (
        "consequent support" if "consequent support" in df.columns else "support"
    )

    df = df.sort_values("lift", ascending=False)
    df = df.drop_duplicates("skill", keep="first")
    df = df.head(top_n)

    axes = [str(s).title() for s in df["skill"]]
    values = [float(v) for v in df[support_col]]
    return axes, values