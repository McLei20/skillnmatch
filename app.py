import streamlit as st
import sys
sys.path.append('src')

from src.recommender import (
    load_rules, load_soft_rules,
    recommend_skills, recommend_careers,
    get_all_skills,
)


def get_skills_from_rules(career, all_rules):
    """All skills appearing in a career's rules (antecedents + consequents)."""
    if career not in all_rules:
        return []
    skills = set()
    for _, row in all_rules[career].iterrows():
        skills.update(row['antecedents'])
        skills.update(row['consequents'])
    return sorted(skills)


from src.ui.theme import inject_css
from src.ui.state import default_state
from src.ui.stepper import render_stepper
from src.ui.discover import render_discover
from src.ui.match import render_match
from src.ui.plan import render_plan


st.set_page_config(page_title="SkillNMatch", page_icon="🎯", layout="wide")

# --- Load data once ---
all_rules = load_rules()
all_soft_rules = load_soft_rules()
all_skills = get_all_skills(all_rules)

# --- Initialize session state on first run ---
for key, value in default_state().items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- Render page ---
inject_css()
st.title("SkillNMatch")
render_stepper()

step = st.session_state.step
if step == "discover":
    render_discover(all_skills)
elif step == "match":
    render_match(recommend_careers, get_skills_from_rules, all_rules)
elif step == "plan":
    render_plan(recommend_skills, all_rules, all_soft_rules)
else:
    # Defensive: unknown step — reset to discover.
    st.session_state.step = "discover"
    st.rerun()
