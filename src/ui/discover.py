"""Step 1 of the guided journey: skill input via search + category chips."""
import streamlit as st
from src.ui.skill_categories import CATEGORY_ORDER, get_skills_by_category


def render_discover(all_skills: list[str]) -> None:
    """Render the Discover step.

    Reads/writes:
      - st.session_state.selected_skills (set[str])
      - st.session_state.step  (set to 'match' on Continue)
      - st.session_state.active_category (local UI state, str)
    """
    st.markdown('<div class="snm-section-label">Step 1 of 3</div>', unsafe_allow_html=True)
    st.markdown("## What skills do you have?")
    st.caption("Add skills you've worked with — even at a beginner level counts.")

    # Initialize local UI state for the category filter.
    if "active_category" not in st.session_state:
        st.session_state.active_category = CATEGORY_ORDER[0]

    # --- Search bar ---
    query = st.text_input(
        "Search skills",
        key="discover_search",
        placeholder="e.g. python, aws, machine learning",
        label_visibility="collapsed",
    )
    if query:
        q = query.strip().lower()
        matches = [s for s in all_skills if q in s.lower()][:10]
        if matches:
            st.caption(f"Matches for '{query}':")
            cols = st.columns(min(len(matches), 5))
            for i, skill in enumerate(matches):
                col = cols[i % len(cols)]
                already = skill in st.session_state.selected_skills
                if col.button(
                    ("✓ " if already else "+ ") + skill,
                    key=f"search_add_{skill}",
                    disabled=already,
                ):
                    st.session_state.selected_skills.add(skill)
                    st.rerun()
        else:
            st.caption(f"No skills match '{query}'.")

    # --- Selected chips ---
    st.markdown('<div class="snm-section-label">Your selections</div>', unsafe_allow_html=True)
    selected = sorted(st.session_state.selected_skills)
    if not selected:
        st.caption("Nothing selected yet. Search above or pick from a category below.")
    else:
        # Render each selected skill as a "remove" button (chip-styled by CSS).
        chip_cols = st.columns(min(len(selected), 6))
        for i, skill in enumerate(selected):
            col = chip_cols[i % len(chip_cols)]
            if col.button(f"{skill} ✕", key=f"remove_{skill}"):
                st.session_state.selected_skills.discard(skill)
                st.rerun()

    st.markdown("---")

    # --- Category filter ---
    st.markdown('<div class="snm-section-label">Browse by category</div>', unsafe_allow_html=True)
    picked = st.radio(
        "Category",
        CATEGORY_ORDER,
        index=CATEGORY_ORDER.index(st.session_state.active_category),
        horizontal=True,
        label_visibility="collapsed",
        key="discover_category_radio",
    )
    if picked != st.session_state.active_category:
        st.session_state.active_category = picked
        st.rerun()

    # --- Chip grid for active category ---
    cat_skills = get_skills_by_category(st.session_state.active_category, all_skills)
    if not cat_skills:
        st.caption(f"No skills in '{st.session_state.active_category}'.")
    else:
        grid_cols = st.columns(4)
        for i, skill in enumerate(cat_skills):
            col = grid_cols[i % 4]
            already = skill in st.session_state.selected_skills
            label = f"✓ {skill}" if already else f"+ {skill}"
            if col.button(label, key=f"grid_{skill}", use_container_width=True):
                if already:
                    st.session_state.selected_skills.discard(skill)
                else:
                    st.session_state.selected_skills.add(skill)
                st.rerun()

    st.markdown("---")

    # --- Continue button ---
    n = len(st.session_state.selected_skills)
    if n == 0:
        st.button("Continue →", disabled=True, help="Pick at least one skill to begin")
    else:
        if st.button(f"Continue → ({n} skill{'s' if n != 1 else ''} selected)", type="primary"):
            st.session_state.step = "match"
            st.rerun()
