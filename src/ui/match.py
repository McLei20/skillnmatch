"""Step 2 of the guided journey: ranked career matches."""
from html import escape

import streamlit as st


_MEDALS = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]


def _label_and_class(score: float) -> tuple[str, str, str]:
    """Return (badge_text, card_modifier, badge_modifier) for a match score."""
    if score >= 0.35:
        return "Great Match", "snm-card--great", "snm-badge--great"
    if score >= 0.25:
        return "Good Match", "snm-card--good", "snm-badge--good"
    return "Fair Match", "snm-card--fair", "snm-badge--fair"


def render_match(
    recommend_careers_fn,
    get_skills_from_rules_fn,
    all_rules: dict,
) -> None:
    """Render the Match step.

    Args:
      recommend_careers_fn: src.recommender.recommend_careers
      get_skills_from_rules_fn: src.recommender.get_skills_from_rules
      all_rules: loaded ARM rules dict

    Reads/writes:
      - st.session_state.selected_skills
      - st.session_state.selected_career  (set on card click)
      - st.session_state.step  (set to 'plan' on card click)
    """
    st.markdown('<div class="snm-section-label">Step 2 of 3</div>', unsafe_allow_html=True)
    st.markdown("## Your best career matches")

    user_skills = sorted(st.session_state.selected_skills)
    st.caption(f"Based on: {', '.join(user_skills)}")

    matches = recommend_careers_fn(user_skills, all_rules)

    if not matches:
        st.warning("We couldn't find strong matches with those skills.")
        st.caption("Try adding more skills — at least 2-3 usually produces good matches.")
        if st.button("← Back to Discover"):
            st.session_state.step = "discover"
            st.rerun()
        return

    for i, (career, score) in enumerate(matches):
        badge_text, card_cls, badge_cls = _label_and_class(score)
        medal = _MEDALS[i] if i < len(_MEDALS) else f"{i+1}."

        # Matched skills: intersection of user's skills with this career's rule-skills.
        career_skills = set(get_skills_from_rules_fn(career, all_rules))
        matched = sorted(st.session_state.selected_skills & career_skills)

        # Card visual
        chips_html = ""
        if matched:
            shown = matched[:5]
            extra = len(matched) - len(shown)
            chips_html = '<div class="snm-chips">' + "".join(
                f'<span class="snm-chip snm-chip--soft">{escape(s)}</span>' for s in shown
            )
            if extra > 0:
                chips_html += f'<span class="snm-chip snm-chip--soft">+{extra} more</span>'
            chips_html += "</div>"

        st.markdown(
            f"""
            <div class="snm-card {card_cls}">
              <div class="snm-card-header">
                <div class="snm-card-title">{medal} &nbsp; {escape(career)}</div>
                <span class="snm-badge {badge_cls}">{badge_text}</span>
              </div>
              <div class="snm-card-meta">Your matching skills</div>
              {chips_html if chips_html else '<div class="snm-card-meta" style="color:#5a6a7b">none yet</div>'}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(f"See plan for {career} →", key=f"plan_{i}_{career}"):
            st.session_state.selected_career = career
            st.session_state.step = "plan"
            st.rerun()

    st.markdown("---")
    if st.button("← Back to Discover"):
        st.session_state.step = "discover"
        st.rerun()
