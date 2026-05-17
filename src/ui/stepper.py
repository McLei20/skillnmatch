"""Top-of-page stepper for the guided journey."""
import streamlit as st
from src.ui.state import can_advance, STEPS


_STEP_LABELS = {
    "discover": "1. Discover",
    "match": "2. Match",
    "plan": "3. Plan",
}


def render_stepper() -> None:
    """Render the 3-step stepper. Reads/writes st.session_state.step."""
    current = st.session_state.step
    cols = st.columns([1, 1, 1, 1, 1])  # 3 pills + 2 spacers

    # Pill columns are 0, 2, 4; spacers are 1 and 3.
    pill_cols = [cols[0], cols[2], cols[4]]
    for i, step in enumerate(STEPS):
        col = pill_cols[i]
        is_active = step == current
        is_past = STEPS.index(step) < STEPS.index(current)
        is_locked = not is_active and not is_past and not can_advance(step, st.session_state)

        label = _STEP_LABELS[step]
        if is_active:
            label = f"● {label}"
        elif is_past:
            label = f"✓ {label}"
        elif is_locked:
            label = f"🔒 {label}"

        # Use Streamlit button for clickability; CSS styles it as a pill.
        clicked = col.button(label, key=f"stepper_{step}", use_container_width=True, disabled=is_locked or is_active)
        if clicked and can_advance(step, st.session_state):
            st.session_state.step = step
            st.rerun()

    # Spacer columns contain visual dividers
    cols[1].markdown('<div class="snm-step-divider"></div>', unsafe_allow_html=True)
    cols[3].markdown('<div class="snm-step-divider"></div>', unsafe_allow_html=True)

    st.markdown("---")
