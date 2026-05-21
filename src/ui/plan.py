"""Step 3 of the guided journey: combined learning plan for a selected career."""
from typing import Optional

import plotly.graph_objects as go
import streamlit as st

from src.ui.charts import soft_skill_radar_data


def _build_skills_to_learn_fig(recs: list[dict]) -> go.Figure:
    """Horizontal bar chart of recommended skills, ranked by learning priority.

    Priority = lift / max(lift in recs), so the top pick is always 100% and the
    rest are scaled relative to it.
    """
    max_lift = max(r["lift"] for r in recs)
    # Ascending so the highest priority lands at the top of the chart.
    ordered = sorted(recs, key=lambda r: r["lift"])

    skills = [r["skill"].title() for r in ordered]
    priorities = [(r["lift"] / max_lift) if max_lift > 0 else 0.0 for r in ordered]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=priorities,
        y=skills,
        orientation="h",
        marker=dict(color="#14b8a6"),
        text=[f"{p * 100:.0f}%" for p in priorities],
        textposition="outside",
        cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>Learning Priority: %{x:.0%}<extra></extra>",
    ))

    fig.update_layout(
        xaxis=dict(
            title="Learning Priority",
            tickformat=".0%",
            range=[0, 1.12],
        ),
        yaxis_title="",
        template="plotly_dark",
        margin=dict(l=0, r=60, t=20, b=40),
        height=max(320, len(recs) * 42),
        showlegend=False,
        bargap=0.3,
    )
    return fig


def _build_radar_fig(soft_rules_df) -> Optional[go.Figure]:
    """Radar of the top soft skills for the selected career.

    Returns None when there is no soft-skill data so the caller can show a
    fallback message instead of an empty chart.
    """
    axes, values = soft_skill_radar_data(soft_rules_df, top_n=8)
    if not axes:
        return None

    axes_closed = axes + [axes[0]]
    values_closed = values + [values[0]]

    max_val = max(values) if max(values) > 0 else 1.0
    upper = max_val * 1.15

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=axes_closed,
        fill="toself",
        line=dict(color="#14b8a6", width=2),
        fillcolor="rgba(20, 184, 166, 0.25)",
        name="Demand",
        hovertemplate="<b>%{theta}</b><br>Demand: %{r:.0%}<extra></extra>",
    ))

    fig.update_layout(
        polar=dict(
            bgcolor="#1a2333",
            radialaxis=dict(
                visible=True,
                range=[0, upper],
                tickformat=".0%",
                gridcolor="#2a3a4f",
                tickfont=dict(size=10, color="#8a9aab"),
            ),
            angularaxis=dict(
                gridcolor="#2a3a4f",
                tickfont=dict(size=11, color="#e8edf2"),
            ),
        ),
        template="plotly_dark",
        showlegend=False,
        margin=dict(l=60, r=60, t=40, b=40),
        height=480,
    )
    return fig


def render_plan(
    recommend_role_skills_fn,
    all_rules: dict,
    all_soft_rules: dict,
) -> None:
    """Render the Plan step.

    Args:
      recommend_role_skills_fn: src.recommender.recommend_role_skills -- ranks
        skills by what the role needs (max lift over the career's rules),
        independent of the user's antecedent matches.
      all_rules: loaded ARM rules dict
      all_soft_rules: loaded soft-skill rules dict (used by the radar)

    Reads:
      - st.session_state.selected_skills
      - st.session_state.selected_career
    """
    career = st.session_state.selected_career
    user_skills_sorted = sorted(st.session_state.selected_skills)

    st.markdown('<div class="snm-section-label">Step 3 of 3</div>', unsafe_allow_html=True)
    st.markdown(f"## Your plan for **{career}**")
    st.caption(f"Based on: {', '.join(user_skills_sorted)}")

    plotly_config = {"displayModeBar": False}

    # --- Skills to learn — horizontal bar chart ---
    st.markdown("### ⭐ Skills to learn")
    st.caption("Recommended next steps based on your current skills.")
    if career not in all_rules:
        st.info(f"No skill recommendations available for *{career}* yet.")
    else:
        recs = recommend_role_skills_fn(career, user_skills_sorted, all_rules, top_n=10)
        if not recs:
            st.caption("You already have all of the strongly-associated skills for this career!")
        else:
            st.plotly_chart(
                _build_skills_to_learn_fig(recs),
                use_container_width=True,
                config=plotly_config,
            )

    st.markdown("---")

    # --- Radar: soft skills emphasis (centered) ---
    st.markdown("### 🤝 Soft skills employers want")
    st.caption("Top soft skills for this career, weighted by how often employers ask for them.")
    pad_l, radar_col, pad_r = st.columns([1, 2, 1])
    with radar_col:
        fig = _build_radar_fig(all_soft_rules.get(career))
        if fig is None:
            st.info("No soft-skill data available for this career.")
        else:
            st.plotly_chart(fig, use_container_width=True, config=plotly_config)

    st.markdown("---")
    col_a, col_b = st.columns(2)
    if col_a.button("← Pick a different career"):
        st.session_state.step = "match"
        st.rerun()
    if col_b.button("← Edit your skills"):
        st.session_state.step = "discover"
        st.rerun()