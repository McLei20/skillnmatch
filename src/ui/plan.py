"""Step 3 of the guided journey: combined learning plan for a selected career."""
from html import escape

import plotly.express as px
import streamlit as st


def _learn_tier(lift: float) -> str:
    """Return the label for a skill-recommendation lift score."""
    if lift >= 2.0:
        return "★★★ Highly Recommended"
    if lift >= 1.5:
        return "★★ Recommended"
    return "★ Consider Learning"


def _soft_tier(lift: float) -> str:
    if lift >= 2.0:
        return "★★★ Highly Expected"
    if lift >= 1.5:
        return "★★ Commonly Expected"
    return "★ Good to Have"


def render_plan(
    recommend_skills_fn,
    recommend_soft_skills_fn,
    all_rules: dict,
    all_soft_rules: dict,
    all_freq: dict,
) -> None:
    """Render the Plan step.

    Args:
      recommend_skills_fn: src.recommender.recommend_skills
      recommend_soft_skills_fn: src.recommender.recommend_soft_skills
      all_rules: loaded ARM rules dict
      all_soft_rules: loaded soft-skill rules dict
      all_freq: loaded skill-frequency dict

    Reads:
      - st.session_state.selected_skills
      - st.session_state.selected_career
    """
    career = st.session_state.selected_career
    user_skills = sorted(st.session_state.selected_skills)

    st.markdown('<div class="snm-section-label">Step 3 of 3</div>', unsafe_allow_html=True)
    st.markdown(f"## Your plan for **{career}**")
    st.caption(f"Based on: {', '.join(user_skills)}")

    left, right = st.columns([3, 2])

    # --- Left: Skills to learn ---
    with left:
        st.markdown("### ⭐ Skills to learn")
        if career not in all_rules:
            st.info(f"No skill recommendations available for *{career}* yet.")
        else:
            recs = recommend_skills_fn(user_skills, career, all_rules, top_n=10)
            if not recs:
                st.caption("You already have most of the recommended skills for this career!")
            else:
                for r in recs:
                    label = _learn_tier(r["lift"])
                    skill = r["skill"].title()
                    st.markdown(
                        f'<div class="snm-chip snm-chip--selected" style="display:inline-block;margin:4px 4px 4px 0">{escape(skill)} &nbsp;·&nbsp; {label}</div>',
                        unsafe_allow_html=True,
                    )

    # --- Right: In-demand chart ---
    with right:
        st.markdown("### 📊 In demand")
        if career not in all_freq:
            st.info("No frequency data for this career.")
        else:
            top = all_freq[career].head(10).copy()
            top["support"] = top["support"].round(3)
            plot_data = top.sort_values("support", ascending=True)
            fig = px.bar(
                plot_data, x="support", y="skill", orientation="h",
                color="support", color_continuous_scale="teal",
            )
            fig.update_layout(
                xaxis_title="% of postings", yaxis_title="",
                coloraxis_showscale=False,
                template="plotly_dark",
                margin=dict(l=0, r=10, t=10, b=30),
                height=max(280, len(plot_data) * 32),
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # --- Bottom band: Soft skills ---
    st.markdown("### 🤝 Soft skills employers want")
    soft = recommend_soft_skills_fn(career, all_soft_rules, top_n=5)
    if not soft:
        st.caption("No soft skill data available for this career.")
    else:
        for s in soft:
            label = _soft_tier(s["lift"])
            st.markdown(
                f'<div class="snm-chip snm-chip--selected" style="display:inline-block;margin:4px 4px 4px 0">{escape(s["skill"])} &nbsp;·&nbsp; {label}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")
    col_a, col_b = st.columns(2)
    if col_a.button("← Pick a different career"):
        st.session_state.step = "match"
        st.rerun()
    if col_b.button("← Edit your skills"):
        st.session_state.step = "discover"
        st.rerun()
