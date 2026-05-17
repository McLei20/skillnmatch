# Guided Journey UX Polish — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current 3-tab Streamlit UI with a guided 3-step journey (Discover → Match → Plan), redesign skill input as a hybrid search/category picker, refresh visual styling to dark + teal. No changes to the recommender algorithm or data pipeline.

**Architecture:** Single-page Streamlit app routed by `st.session_state.step`. Three view modules in `src/ui/` (`discover.py`, `match.py`, `plan.py`) plus shared components (`stepper.py`, `theme.py`, `skill_categories.py`). Recommender functions in `src/recommender.py` are reused unchanged.

**Tech Stack:** Python 3.11, Streamlit 1.55, pandas, mlxtend, plotly. Tests use stdlib `unittest` (no new dependencies).

**Spec:** `docs/superpowers/specs/2026-05-17-guided-journey-ux-polish-design.md`

**Deliberate simplification vs. spec:** The spec lists `cached_matches` in session state with an invalidation rule. The plan drops the cache entirely — `recommend_careers` is fast enough (ms-level) that caching adds complexity without measurable benefit, and removing it eliminates a subtle invalidation bug when skills change via chip toggles. Behaviorally indistinguishable.

---

## Pre-flight

This project has no git repo today. Initialize one before starting so the commit steps work:

```bash
cd C:/Users/admin/Desktop/skillnmatch
git init
git add -A
git commit -m "chore: snapshot pre-refactor state"
```

If git is intentionally not used, skip every `git commit` step in this plan.

Verify the Streamlit app runs as-is before changing anything:

```bash
streamlit run app.py
```

Open the browser, confirm all three tabs render and produce results. Close when done.

---

## Task 1: Theme config and CSS scaffold

Establish the dark + teal baseline. The app should look slightly different after this task (background color, primary button color) but still behave identically.

**Files:**
- Create: `.streamlit/config.toml`
- Create: `src/__init__.py`
- Create: `src/ui/__init__.py`
- Create: `src/ui/theme.py`
- Modify: `app.py` (one line: import + call `inject_css()`)

- [ ] **Step 1.1: Create the theme config**

Create `.streamlit/config.toml`:

```toml
[theme]
base = "dark"
primaryColor = "#14b8a6"
backgroundColor = "#0f1419"
secondaryBackgroundColor = "#1a2333"
textColor = "#e8edf2"
font = "sans serif"
```

- [ ] **Step 1.2: Create the package init files**

Create `src/__init__.py` (empty file — makes `src` an importable package):

```python
```

Create `src/ui/__init__.py` (empty file):

```python
```

- [ ] **Step 1.3: Create the theme module**

Create `src/ui/theme.py`:

```python
import streamlit as st

_CSS = """
<style>
/* Stepper */
.snm-stepper {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 0;
    margin-bottom: 24px;
    position: sticky;
    top: 0;
    background: #0f1419;
    z-index: 100;
    border-bottom: 1px solid #1a2333;
}
.snm-step {
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 600;
    border: 1px solid #2a3a4f;
    color: #8a9aab;
    background: transparent;
}
.snm-step--active {
    background: #14b8a6;
    color: #0f1419;
    border-color: #14b8a6;
}
.snm-step--past {
    border-color: #14b8a6;
    color: #14b8a6;
}
.snm-step--locked {
    color: #4a5a6b;
}
.snm-step-divider {
    flex: 0 0 24px;
    height: 1px;
    background: #2a3a4f;
}

/* Chips */
.snm-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin: 8px 0;
}
.snm-chip {
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    background: #2a3a4f;
    color: #e8edf2;
    border: 1px solid transparent;
}
.snm-chip--selected {
    background: #14b8a6;
    color: #0f1419;
    font-weight: 600;
}
.snm-chip--soft {
    background: #1a2333;
    color: #e8edf2;
    border-color: #2a3a4f;
}

/* Match cards */
.snm-card {
    background: #1a2333;
    border-radius: 6px;
    padding: 14px 16px;
    margin-bottom: 10px;
    border-left: 3px solid #2a3a4f;
}
.snm-card--great { border-left-color: #10b981; }
.snm-card--good { border-left-color: #3b82f6; }
.snm-card--fair { border-left-color: #f59e0b; }
.snm-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}
.snm-card-title {
    font-size: 16px;
    font-weight: 600;
    color: #e8edf2;
}
.snm-badge {
    padding: 2px 8px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
}
.snm-badge--great { background: #10b981; color: #0f1419; }
.snm-badge--good { background: #3b82f6; color: #fff; }
.snm-badge--fair { background: #f59e0b; color: #0f1419; }
.snm-card-meta {
    font-size: 11px;
    color: #8a9aab;
    margin-bottom: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Section labels */
.snm-section-label {
    font-size: 11px;
    color: #8a9aab;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 8px 0 4px 0;
}
</style>
"""

def inject_css() -> None:
    """Inject SkillNMatch CSS into the Streamlit page. Call once near app start."""
    st.markdown(_CSS, unsafe_allow_html=True)
```

- [ ] **Step 1.4: Wire inject_css into app.py**

Modify `app.py` — add a new import for `inject_css` and call it once before any other Streamlit calls.

Replace the import block at the top of `app.py` with:

```python
import streamlit as st
import plotly.express as px
import pandas as pd
import ast
import sys
sys.path.append('src')
from recommender import load_rules, load_frequencies, load_soft_rules, recommend_skills, recommend_soft_skills, get_skills_from_rules, get_all_skills, recommend_careers
from src.ui.theme import inject_css
```

Then add `inject_css()` as a new line just before `# Title` (which precedes `st.title("SkillNMatch")`). The block becomes:

```python
# Load data and rules
df = pd.read_csv('data/cleaned_jobs.csv')
df['IT Skills'] = df['IT Skills'].apply(ast.literal_eval)
all_rules = load_rules()
all_freq = load_frequencies()
all_soft_rules = load_soft_rules()

inject_css()

# Title
st.title("SkillNMatch")
```

Note: `from src.ui.theme import inject_css` works because Python's CWD when running `streamlit run app.py` is the project root, which contains the `src/` package. `sys.path.append('src')` is kept so the existing `from recommender import ...` line continues to work.

- [ ] **Step 1.5: Smoke-check the theme**

Run:

```bash
streamlit run app.py
```

Expected: app opens, background is dark navy (`#0f1419`), buttons appear teal when clicked. The 3 tabs still work as before — no behavioral change yet.

Close the browser when done.

- [ ] **Step 1.6: Commit**

```bash
git add .streamlit/config.toml src/__init__.py src/ui/__init__.py src/ui/theme.py app.py
git commit -m "feat(ui): add dark teal theme config and CSS scaffold"
```

---

## Task 2: Skill categorization module (TDD)

Build the hand-curated skill → category mapping. The mapping is incomplete by design: starter entries cover the most common skills; everything else falls to `"Other"`. Tests verify the contract (no orphans crash the app, helpers behave correctly).

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_skill_categories.py`
- Create: `src/ui/skill_categories.py`
- Create: `scripts/dump_uncategorized.py` (one-off helper for the engineer)

- [ ] **Step 2.1: Create tests directory**

Create `tests/__init__.py` (empty file):

```python
```

- [ ] **Step 2.2: Write the failing tests**

Create `tests/test_skill_categories.py`:

```python
import unittest
from src.ui.skill_categories import (
    SKILL_CATEGORIES,
    CATEGORY_ORDER,
    get_skills_by_category,
    get_uncategorized_skills,
    categorize,
)


class TestSkillCategories(unittest.TestCase):

    def test_category_order_contains_other(self):
        """'Other' must always be in the category list as a fallback."""
        self.assertIn("Other", CATEGORY_ORDER)

    def test_category_order_no_duplicates(self):
        self.assertEqual(len(CATEGORY_ORDER), len(set(CATEGORY_ORDER)))

    def test_all_mapped_categories_are_in_order(self):
        """Every category used in SKILL_CATEGORIES must appear in CATEGORY_ORDER."""
        mapped_cats = set(SKILL_CATEGORIES.values())
        for cat in mapped_cats:
            self.assertIn(cat, CATEGORY_ORDER, f"Category '{cat}' not in CATEGORY_ORDER")

    def test_categorize_known_skill(self):
        # Python is a starter entry — must be Languages.
        self.assertEqual(categorize("python"), "Languages")

    def test_categorize_unknown_skill_falls_to_other(self):
        self.assertEqual(categorize("zzz_invented_skill_xyz"), "Other")

    def test_get_skills_by_category_returns_sorted_list(self):
        all_skills = ["python", "sql", "java", "aws", "zzz_invented_skill_xyz"]
        langs = get_skills_by_category("Languages", all_skills)
        self.assertEqual(langs, sorted(langs))
        self.assertIn("python", langs)
        self.assertIn("java", langs)
        self.assertNotIn("aws", langs)
        self.assertNotIn("zzz_invented_skill_xyz", langs)

    def test_get_skills_by_category_other_captures_unknowns(self):
        all_skills = ["python", "zzz_invented_skill_xyz"]
        other = get_skills_by_category("Other", all_skills)
        self.assertIn("zzz_invented_skill_xyz", other)
        self.assertNotIn("python", other)

    def test_get_uncategorized_skills_returns_only_other(self):
        all_skills = ["python", "sql", "zzz_invented_skill_xyz", "another_unknown_abc"]
        uncat = get_uncategorized_skills(all_skills)
        self.assertIn("zzz_invented_skill_xyz", uncat)
        self.assertIn("another_unknown_abc", uncat)
        self.assertNotIn("python", uncat)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2.3: Run tests to verify they fail**

Run:

```bash
python -m unittest tests.test_skill_categories -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'src.ui.skill_categories'` (or similar).

- [ ] **Step 2.4: Implement the skill_categories module**

Create `src/ui/skill_categories.py`:

```python
"""Skill → category mapping for the Discover step's category filter.

Mapping is hand-curated. Any skill not present here falls through to 'Other'
so the UI never breaks on a new or unseen skill.
"""

# Display order of categories in the UI.
CATEGORY_ORDER = [
    "Languages",
    "Data & ML",
    "Cloud & DevOps",
    "Web",
    "Databases",
    "Tools",
    "Other",
]

# Starter mapping — covers the most common ~60 skills. The engineer should
# extend this after running scripts/dump_uncategorized.py against the real
# rules dataset (see Step 2.7).
SKILL_CATEGORIES: dict[str, str] = {
    # Languages
    "python": "Languages",
    "java": "Languages",
    "javascript": "Languages",
    "typescript": "Languages",
    "c++": "Languages",
    "c#": "Languages",
    "c": "Languages",
    "r": "Languages",
    "scala": "Languages",
    "go": "Languages",
    "ruby": "Languages",
    "php": "Languages",
    "swift": "Languages",
    "kotlin": "Languages",
    "rust": "Languages",

    # Data & ML
    "machine learning": "Data & ML",
    "deep learning": "Data & ML",
    "artificial intelligence": "Data & ML",
    "natural language processing": "Data & ML",
    "computer vision": "Data & ML",
    "tensorflow": "Data & ML",
    "pytorch": "Data & ML",
    "keras": "Data & ML",
    "scikit-learn": "Data & ML",
    "pandas": "Data & ML",
    "numpy": "Data & ML",
    "statistics": "Data & ML",
    "data analysis": "Data & ML",
    "data visualization": "Data & ML",
    "spark": "Data & ML",
    "hadoop": "Data & ML",

    # Cloud & DevOps
    "aws": "Cloud & DevOps",
    "azure": "Cloud & DevOps",
    "gcp": "Cloud & DevOps",
    "docker": "Cloud & DevOps",
    "kubernetes": "Cloud & DevOps",
    "terraform": "Cloud & DevOps",
    "jenkins": "Cloud & DevOps",
    "ci/cd": "Cloud & DevOps",
    "linux": "Cloud & DevOps",

    # Web
    "html": "Web",
    "css": "Web",
    "react": "Web",
    "angular": "Web",
    "vue": "Web",
    "node.js": "Web",
    "express": "Web",
    "django": "Web",
    "flask": "Web",
    "rest": "Web",
    "graphql": "Web",
    "application programming interface": "Web",

    # Databases
    "sql": "Databases",
    "mysql": "Databases",
    "postgresql": "Databases",
    "mongodb": "Databases",
    "redis": "Databases",
    "oracle": "Databases",
    "nosql": "Databases",
    "database": "Databases",

    # Tools
    "git": "Tools",
    "github": "Tools",
    "jira": "Tools",
    "tableau": "Tools",
    "power bi": "Tools",
    "excel": "Tools",
    "vs code": "Tools",
    "agile": "Tools",
    "scrum": "Tools",
}


def categorize(skill: str) -> str:
    """Return the category for a skill, defaulting to 'Other' if unmapped."""
    return SKILL_CATEGORIES.get(skill, "Other")


def get_skills_by_category(category: str, all_skills: list[str]) -> list[str]:
    """Return the subset of `all_skills` that fall under `category`, sorted."""
    return sorted(s for s in all_skills if categorize(s) == category)


def get_uncategorized_skills(all_skills: list[str]) -> list[str]:
    """Return the subset of `all_skills` that fall into 'Other'. Useful for
    extending SKILL_CATEGORIES — run scripts/dump_uncategorized.py to see them."""
    return sorted(s for s in all_skills if categorize(s) == "Other")
```

- [ ] **Step 2.5: Run tests to verify they pass**

Run:

```bash
python -m unittest tests.test_skill_categories -v
```

Expected: PASS — all 8 tests green.

- [ ] **Step 2.6: Create the dump-uncategorized helper script**

Create `scripts/dump_uncategorized.py`:

```python
"""Print all skills from the live ARM rules that are not yet categorized.

Run from project root:
    python scripts/dump_uncategorized.py

Use the output to extend SKILL_CATEGORIES in src/ui/skill_categories.py.
"""
import sys
sys.path.insert(0, "src")

from recommender import load_rules, get_all_skills
from ui.skill_categories import get_uncategorized_skills


def main() -> None:
    all_rules = load_rules()
    all_skills = get_all_skills(all_rules)
    uncategorized = get_uncategorized_skills(all_skills)
    print(f"Total skills: {len(all_skills)}")
    print(f"Uncategorized (falls to 'Other'): {len(uncategorized)}")
    for s in uncategorized:
        print(f"  {s}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2.7: Extend the categorization for real-world skills**

Run:

```bash
python scripts/dump_uncategorized.py
```

This prints all skills currently falling to `"Other"`. Open `src/ui/skill_categories.py` and add entries to `SKILL_CATEGORIES` for ones that obviously fit a category. Leave genuinely ambiguous ones (e.g., "sas" — language or tool?) in `"Other"` — that's the safe fallback.

Aim to get the `"Other"` list down to fewer than 25% of total skills. Re-run the dump script as you go.

After extending, re-run the tests:

```bash
python -m unittest tests.test_skill_categories -v
```

Expected: PASS — the contract didn't change, only the mapping grew.

- [ ] **Step 2.8: Commit**

```bash
git add tests/ src/ui/skill_categories.py scripts/dump_uncategorized.py
git commit -m "feat(ui): add skill categorization module with starter mapping"
```

---

## Task 3: Session state and navigation helpers (TDD)

Pure functions for session state init and navigation logic. These are the only state-management primitives that need unit tests — view rendering doesn't.

**Files:**
- Create: `tests/test_state_transitions.py`
- Create: `src/ui/state.py`

- [ ] **Step 3.1: Write the failing tests**

Create `tests/test_state_transitions.py`:

```python
import unittest
from src.ui.state import can_advance, default_state, STEPS


class TestStateTransitions(unittest.TestCase):

    def test_steps_constant(self):
        self.assertEqual(STEPS, ["discover", "match", "plan"])

    def test_default_state_shape(self):
        s = default_state()
        self.assertEqual(s["step"], "discover")
        self.assertEqual(s["selected_skills"], set())
        self.assertIsNone(s["selected_career"])

    def test_can_advance_to_discover_always_true(self):
        # No prerequisite for going back to step 1.
        self.assertTrue(can_advance("discover", default_state()))

    def test_can_advance_to_match_requires_skills(self):
        s = default_state()
        self.assertFalse(can_advance("match", s))
        s["selected_skills"] = {"python"}
        self.assertTrue(can_advance("match", s))

    def test_can_advance_to_plan_requires_career(self):
        s = default_state()
        s["selected_skills"] = {"python"}
        self.assertFalse(can_advance("plan", s))
        s["selected_career"] = "Data Scientist"
        self.assertTrue(can_advance("plan", s))

    def test_can_advance_unknown_step_false(self):
        self.assertFalse(can_advance("nonsense", default_state()))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3.2: Run tests to verify they fail**

Run:

```bash
python -m unittest tests.test_state_transitions -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'src.ui.state'`.

- [ ] **Step 3.3: Implement the state module**

Create `src/ui/state.py`:

```python
"""Session state shape and navigation guards for the guided journey."""
from typing import TypedDict, Any


STEPS = ["discover", "match", "plan"]


class JourneyState(TypedDict):
    step: str
    selected_skills: set[str]
    selected_career: str | None


def default_state() -> dict[str, Any]:
    """Initial session state for a fresh user."""
    return {
        "step": "discover",
        "selected_skills": set(),
        "selected_career": None,
    }


def can_advance(target_step: str, state: dict[str, Any]) -> bool:
    """Return True if the user is allowed to navigate to `target_step` given current state.

    - discover: no prerequisite.
    - match: requires >=1 skill in selected_skills.
    - plan: requires selected_career to be set.
    """
    if target_step == "discover":
        return True
    if target_step == "match":
        return len(state.get("selected_skills", set())) >= 1
    if target_step == "plan":
        return state.get("selected_career") is not None
    return False
```

- [ ] **Step 3.4: Run tests to verify they pass**

Run:

```bash
python -m unittest tests.test_state_transitions -v
```

Expected: PASS — all 6 tests green.

- [ ] **Step 3.5: Run all tests together to confirm nothing broke**

Run:

```bash
python -m unittest discover tests -v
```

Expected: PASS — all tests from Task 2 and Task 3 green.

- [ ] **Step 3.6: Commit**

```bash
git add tests/test_state_transitions.py src/ui/state.py
git commit -m "feat(ui): add session state and navigation guard helpers"
```

---

## Task 4: Stepper component

The 3-step navigation bar at the top of every page. Renders three pills based on `st.session_state.step`; clicks update the step (with `can_advance` enforcing forward locks).

**Files:**
- Create: `src/ui/stepper.py`

- [ ] **Step 4.1: Implement the stepper**

Create `src/ui/stepper.py`:

```python
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
```

- [ ] **Step 4.2: Smoke-check the stepper in isolation**

Create a temporary `scratch_stepper.py` at project root:

```python
import streamlit as st
import sys
sys.path.append('.')
from src.ui.theme import inject_css
from src.ui.stepper import render_stepper
from src.ui.state import default_state

# Initialize state
for k, v in default_state().items():
    if k not in st.session_state:
        st.session_state[k] = v

inject_css()
render_stepper()

st.write(f"Current step: `{st.session_state.step}`")
st.write(f"Selected skills: {st.session_state.selected_skills}")

# Buttons to fake state changes
col1, col2 = st.columns(2)
if col1.button("Add 'python' to skills"):
    st.session_state.selected_skills.add("python")
    st.rerun()
if col2.button("Set career to 'Data Scientist'"):
    st.session_state.selected_career = "Data Scientist"
    st.rerun()
```

Run:

```bash
streamlit run scratch_stepper.py
```

Expected:
- Initially: "Discover" is active (●), "Match" and "Plan" are 🔒 locked.
- Click "Add 'python' to skills" → "Match" unlocks.
- Click "Set career to 'Data Scientist'" → "Plan" unlocks.
- Click "Match" → navigates, "Discover" becomes ✓ past, "Match" becomes ● active.
- Click "✓ Discover" → goes back.

Close the browser. Delete the scratch file:

```bash
rm scratch_stepper.py
```

- [ ] **Step 4.3: Commit**

```bash
git add src/ui/stepper.py
git commit -m "feat(ui): add clickable 3-step stepper component"
```

---

## Task 5: Discover view (Step 1)

The skill-input screen: search bar + selected chips + category filter + chip grid + Continue button.

**Files:**
- Create: `src/ui/discover.py`

- [ ] **Step 5.1: Implement the Discover view**

Create `src/ui/discover.py`:

```python
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

    # --- Category filter pills ---
    st.markdown('<div class="snm-section-label">Browse by category</div>', unsafe_allow_html=True)
    cat_cols = st.columns(len(CATEGORY_ORDER))
    for i, cat in enumerate(CATEGORY_ORDER):
        is_active = cat == st.session_state.active_category
        label = f"● {cat}" if is_active else cat
        if cat_cols[i].button(label, key=f"cat_{cat}", use_container_width=True):
            st.session_state.active_category = cat
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
```

- [ ] **Step 5.2: Smoke-check Discover in isolation**

Create `scratch_discover.py`:

```python
import streamlit as st
import sys
sys.path.append('.')
sys.path.append('src')
from recommender import load_rules, get_all_skills
from src.ui.theme import inject_css
from src.ui.stepper import render_stepper
from src.ui.discover import render_discover
from src.ui.state import default_state

for k, v in default_state().items():
    if k not in st.session_state:
        st.session_state[k] = v

all_rules = load_rules()
all_skills = get_all_skills(all_rules)

inject_css()
render_stepper()

if st.session_state.step == "discover":
    render_discover(all_skills)
else:
    st.write(f"Advanced to: `{st.session_state.step}`")
    st.write(f"With skills: {sorted(st.session_state.selected_skills)}")
```

Run:

```bash
streamlit run scratch_discover.py
```

Expected:
- Search "python" → "+ python" appears, click it → moves to selections.
- Click "Languages" category → shows language chips. Click some → they appear in selections.
- Click "✕" on a selected chip → removes it.
- "Continue →" is disabled with 0 skills, enabled with ≥1.
- Clicking Continue advances to "match" step (text replaces the form).

Close browser, delete scratch file:

```bash
rm scratch_discover.py
```

- [ ] **Step 5.3: Commit**

```bash
git add src/ui/discover.py
git commit -m "feat(ui): add Discover view with hybrid search/category skill input"
```

---

## Task 6: Match view (Step 2)

Top 5 career matches as ranked cards. Each card shows rank, career, match badge, and matched skills. Click "Plan this career →" to advance.

**Files:**
- Create: `src/ui/match.py`

- [ ] **Step 6.1: Implement the Match view**

Create `src/ui/match.py`:

```python
"""Step 2 of the guided journey: ranked career matches."""
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
                f'<span class="snm-chip snm-chip--soft">{s}</span>' for s in shown
            )
            if extra > 0:
                chips_html += f'<span class="snm-chip snm-chip--soft">+{extra} more</span>'
            chips_html += "</div>"

        st.markdown(
            f"""
            <div class="snm-card {card_cls}">
              <div class="snm-card-header">
                <div class="snm-card-title">{medal} &nbsp; {career}</div>
                <span class="snm-badge {badge_cls}">{badge_text}</span>
              </div>
              <div class="snm-card-meta">Your matching skills</div>
              {chips_html if chips_html else '<div class="snm-card-meta" style="color:#5a6a7b">none yet</div>'}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(f"See plan for {career} →", key=f"plan_{career}"):
            st.session_state.selected_career = career
            st.session_state.step = "plan"
            st.rerun()

    st.markdown("---")
    if st.button("← Back to Discover"):
        st.session_state.step = "discover"
        st.rerun()
```

- [ ] **Step 6.2: Smoke-check Match in isolation**

Create `scratch_match.py`:

```python
import streamlit as st
import sys
sys.path.append('.')
sys.path.append('src')
from recommender import load_rules, recommend_careers, get_skills_from_rules
from src.ui.theme import inject_css
from src.ui.stepper import render_stepper
from src.ui.match import render_match
from src.ui.state import default_state

for k, v in default_state().items():
    if k not in st.session_state:
        st.session_state[k] = v

# Pre-load some test skills so we land on Match directly.
if not st.session_state.selected_skills:
    st.session_state.selected_skills = {"python", "sql", "machine learning"}
    st.session_state.step = "match"

all_rules = load_rules()
inject_css()
render_stepper()

if st.session_state.step == "match":
    render_match(recommend_careers, get_skills_from_rules, all_rules)
else:
    st.write(f"Current step: `{st.session_state.step}`")
    st.write(f"Career: {st.session_state.selected_career}")
```

Run:

```bash
streamlit run scratch_match.py
```

Expected:
- 5 cards render with medals 🥇–5️⃣.
- Each card has a colored left border (green/blue/amber) and a matching badge.
- "Your matching skills" shows chips for skills like python/sql/ml that appear in each career's rules.
- "See plan for X →" button advances to the plan step.
- "← Back to Discover" works.

Close browser, delete scratch file:

```bash
rm scratch_match.py
```

- [ ] **Step 6.3: Commit**

```bash
git add src/ui/match.py
git commit -m "feat(ui): add Match view with ranked career cards"
```

---

## Task 7: Plan view (Step 3)

Two-column layout: Skills to Learn (left) + In Demand chart (right). Soft Skills band below. Reuses the existing Plotly chart from the old Tab 3 unchanged.

**Files:**
- Create: `src/ui/plan.py`

- [ ] **Step 7.1: Implement the Plan view**

Create `src/ui/plan.py`:

```python
"""Step 3 of the guided journey: combined learning plan for a selected career."""
import pandas as pd
import plotly.express as px
import streamlit as st


def _learn_tier(lift: float) -> tuple[str, str]:
    """Return (label, css_class_suffix) for a skill-recommendation lift score."""
    if lift >= 2.0:
        return "★★★ Highly Recommended", "snm-chip--selected"
    if lift >= 1.5:
        return "★★ Recommended", "snm-chip--selected"
    return "★ Consider Learning", "snm-chip--soft"


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
                    label, _ = _learn_tier(r["lift"])
                    skill = r["skill"].title()
                    st.markdown(
                        f'<div class="snm-chip snm-chip--selected" style="display:inline-block;margin:4px 4px 4px 0">{skill} &nbsp;·&nbsp; {label}</div>',
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
                f'<div class="snm-chip snm-chip--selected" style="display:inline-block;margin:4px 4px 4px 0">{s["skill"]} &nbsp;·&nbsp; {label}</div>',
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
```

- [ ] **Step 7.2: Smoke-check Plan in isolation**

Create `scratch_plan.py`:

```python
import streamlit as st
import sys
sys.path.append('.')
sys.path.append('src')
from recommender import (
    load_rules, load_soft_rules, load_frequencies,
    recommend_skills, recommend_soft_skills,
)
from src.ui.theme import inject_css
from src.ui.stepper import render_stepper
from src.ui.plan import render_plan
from src.ui.state import default_state

for k, v in default_state().items():
    if k not in st.session_state:
        st.session_state[k] = v

if not st.session_state.selected_skills:
    st.session_state.selected_skills = {"python", "sql"}
    st.session_state.selected_career = "Data Scientist"
    st.session_state.step = "plan"

all_rules = load_rules()
all_soft_rules = load_soft_rules()
all_freq = load_frequencies()

inject_css()
render_stepper()

if st.session_state.step == "plan":
    render_plan(recommend_skills, recommend_soft_skills, all_rules, all_soft_rules, all_freq)
else:
    st.write(f"Step: `{st.session_state.step}`")
```

Run:

```bash
streamlit run scratch_plan.py
```

Expected:
- Two-column layout: "⭐ Skills to learn" on left with chip-style recommendations, "📊 In demand" Plotly chart on right.
- "🤝 Soft skills employers want" appears as a band below.
- Both back buttons work.
- Try changing `selected_career` to a career without rules (check `arm.py` output — there are 3 of 25) to verify graceful empty states.

Close browser, delete scratch file:

```bash
rm scratch_plan.py
```

- [ ] **Step 7.3: Commit**

```bash
git add src/ui/plan.py
git commit -m "feat(ui): add Plan view with two-column layout and soft skills"
```

---

## Task 8: Wire it all together in app.py

Replace `app.py` wholesale. New `app.py` is just session state init + router.

**Files:**
- Modify: `app.py` (wholesale replace)

- [ ] **Step 8.1: Back up the old app.py**

```bash
cp app.py app.py.bak
```

(This is just a safety net — we'll delete it after smoke-testing.)

- [ ] **Step 8.2: Replace app.py with the new router**

Replace the entire contents of `app.py` with:

```python
import streamlit as st
import sys
sys.path.append('src')

from recommender import (
    load_rules, load_frequencies, load_soft_rules,
    recommend_skills, recommend_soft_skills, recommend_careers,
    get_skills_from_rules, get_all_skills,
)
from src.ui.theme import inject_css
from src.ui.state import default_state
from src.ui.stepper import render_stepper
from src.ui.discover import render_discover
from src.ui.match import render_match
from src.ui.plan import render_plan


st.set_page_config(page_title="SkillNMatch", page_icon="🎯", layout="centered")

# --- Load data once ---
all_rules = load_rules()
all_freq = load_frequencies()
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
    render_plan(recommend_skills, recommend_soft_skills, all_rules, all_soft_rules, all_freq)
else:
    # Defensive: unknown step — reset to discover.
    st.session_state.step = "discover"
    st.rerun()
```

- [ ] **Step 8.3: Run the full app and walk the journey**

Run:

```bash
streamlit run app.py
```

Walk through the full happy path:
1. Land on Discover. Search "python", add it. Browse "Languages" category, add "sql".
2. Click "Continue → (2 skills selected)".
3. Match shows 5 career cards. Click "See plan for Data Scientist →".
4. Plan renders with two columns + soft skills band.
5. Click "✓ Discover" in the stepper — should go back, skills preserved.
6. Click "Match" in the stepper — should go back to Match (cards still cached).
7. Try removing all skills on Discover — "Continue →" should disable. Stepper should lock "Match" and "Plan".

- [ ] **Step 8.4: Delete the backup**

If everything works:

```bash
rm app.py.bak
```

If something doesn't work, debug — don't restore the backup. Fix forward.

- [ ] **Step 8.5: Commit**

```bash
git add app.py
git commit -m "feat(app): replace tabs with guided 3-step journey"
```

---

## Task 9: Manual smoke checklist + edge cases

Walk the spec's edge cases and capture any bugs. Each item is a yes/no — fix anything that fails before moving on.

- [ ] **Step 9.1: Edge — 0 skills selected**

Open the app, do not add any skills. Verify:
- "Continue →" button is disabled with hover hint "Pick at least one skill to begin".
- Stepper "Match" pill shows 🔒 and is unclickable.
- Stepper "Plan" pill shows 🔒 and is unclickable.

- [ ] **Step 9.2: Edge — no matches found**

Add a single obscure skill that's unlikely to produce matches (try uncategorized ones from `scripts/dump_uncategorized.py`). Click Continue. Verify:
- Match view shows the warning copy: "We couldn't find strong matches..."
- "← Back to Discover" button is present and works.

- [ ] **Step 9.3: Edge — career without rules**

Manually find a career in `all_soft_rules` keys that is NOT in `all_rules` keys. (Run `python -c "from src.recommender import load_rules, load_soft_rules; print(set(load_soft_rules()) - set(load_rules()))"` to list them.) Add skills, advance to Match, then click that career on Match → it will probably not appear since recommend_careers skips careers with < 20 rules. Instead, fake it by setting `st.session_state.selected_career` to one of those careers via the URL bar after entering some skills:

Actually simpler: pick any career from the Match list normally, then in the Plan view, check what happens for a career with sparse data. If you can't trigger this organically, set `selected_career` programmatically via a temporary scratch script.

Verify:
- "Skills to learn" shows "No skill recommendations available for *X* yet." instead of crashing.
- "In demand" shows "No frequency data for this career." instead of crashing.
- Soft skills section still renders.

- [ ] **Step 9.4: Edge — narrow window**

Resize the browser to ~768px wide. Verify:
- Stepper still renders in a usable row.
- Plan's two columns stack vertically (Streamlit default behavior).
- Chip grids wrap rather than overflow.

- [ ] **Step 9.5: Edge — navigation preserves state**

With skills picked and a career selected, jump backward to Discover via the stepper. Verify:
- Selected skills are still there.
- Selected career persists in state.
- Re-advancing to Match shows cached results (or re-runs cleanly).

Match recomputes on every visit (no caching), so changes always reflect.

- [ ] **Step 9.6: Run all tests one more time**

```bash
python -m unittest discover tests -v
```

Expected: all tests pass.

- [ ] **Step 9.7: Final commit**

If any of Steps 9.1–9.5 surfaced a bug you fixed, commit those fixes:

```bash
git add -A
git commit -m "fix(ui): address edge cases from smoke test"
```

Otherwise, skip this commit.

---

## Done

The app should now:
- Open on a Discover step with a search + category skill picker.
- Advance to Match showing 5 ranked cards.
- Advance to Plan with two columns + soft skills.
- Allow free backward navigation via a sticky stepper.
- Look dark-and-teal-styled throughout.

Recommender logic, data files, and `requirements.txt` are unchanged. Test files cover the only two units with non-trivial logic (categorization + state guards); UI behavior was verified manually.

If a follow-up feels needed (e.g., more skill categorization, an info "How this works" disclosure for academic reviewers), capture it as a separate spec.
