# SkillNMatch — Guided Journey UX Polish

**Date:** 2026-05-17
**Status:** Approved design, ready for implementation planning
**Scope:** Replace the current 3-tab Streamlit UI with a guided 3-step journey, redesign skill input, refresh visual styling. No changes to the recommender algorithm, data pipeline, or data files.

---

## Background

SkillNMatch is a Streamlit app that uses FP-Growth association rule mining on 3,000 IT job postings to recommend careers, skills, and soft skills. Today it presents three independent tabs:

1. **Career Fit** — user picks skills from a flat 124-item multiselect, gets ranked career matches.
2. **Skill Recommendations** — user picks a career and current skills, gets recommended IT skills + soft skills.
3. **Skill Demand** — user picks a career, sees the top 10 most in-demand skills.

The recommender layer works well, but the UI has four UX problems that show up across all three tabs:

- **Lack of guidance** — users don't know where to start or how to interpret results.
- **Visual clutter / weak hierarchy** — too much competing information per tab.
- **Boring / not engaging** — functional but bland, no narrative.
- **Tedious inputs** — flat 124-skill multiselect is painful to scan.

The target audience is mixed: job seekers exploring IT careers, IT students figuring out what to learn, and academic/portfolio reviewers evaluating the project. Polish must serve all three.

## Goals

- Reduce cognitive load by giving users a single linear path through the recommender's capabilities.
- Replace the flat skill multiselect with an input that supports both search and browsing.
- Refresh the visual styling so the app feels like a modern data tool, not a default Streamlit demo.
- Keep the recommender algorithm, data pipeline, and `requirements.txt` unchanged.

## Non-goals

- Changing the recommendation algorithm, scoring formula, or ARM parameters.
- Persisting user state across browser sessions (no login, no cookies).
- Adding new features beyond the three current ones — just reorganizing what's there.
- Reintroducing the `skill_network.html` visualization (intentionally removed; not user-friendly).
- Mobile-first redesign (default Streamlit responsive behavior is acceptable).
- Adding new Python dependencies.

## Design

### Overall structure: Guided Journey

The 3-tab layout is replaced with a 3-step linear journey:

1. **Discover** — user enters their current skills.
2. **Match** — user sees ranked career matches and picks one.
3. **Plan** — user sees skills to learn, soft skills, and market demand for the chosen career, all on one screen.

A clickable stepper at the top of the page shows progress and allows backward jumps freely. Forward jumps are only allowed if the requirements for the destination step are already met. Per-step requirements:

- **Discover**: no prerequisite.
- **Match**: requires ≥1 skill in `selected_skills`.
- **Plan**: requires `selected_career` to be set (which implies Match was completed).

### Step 1: Discover — Hybrid skill input

Replaces the flat 124-item multiselect with a hybrid input:

- **Search bar** at the top — typeahead matching against all 124 skill names. Selecting a result adds it to the selection.
- **Selected chips** appear in a row beneath the search bar, each removable with a ✕.
- **Category filter pills** below selected chips — `Languages`, `Data & ML`, `Cloud & DevOps`, `Web`, `Databases`, `Tools`, `Other`. Clicking a category filters the chip grid below.
- **Chip grid** of all skills in the active category, click to toggle on/off. Selected chips highlight teal.
- **"Continue →"** button at the bottom, disabled until ≥1 skill is selected (with hint copy when disabled).

This serves all three audiences: students/experienced users search, career-curious browse by category.

### Step 2: Match — Ranked cards (all equal)

Top 5 careers from `recommend_careers()` rendered as equal-weight vertical cards:

- Each card is a full-width row with a colored left border indicating match strength:
  - Green (3px left border) — Great Match (score ≥ 0.35)
  - Blue — Good Match (score ≥ 0.25)
  - Amber — Fair Match (score < 0.25)
- Card body: rank emoji (🥇🥈🥉4️⃣5️⃣) + career name + match badge + a small chip list of the user's matched skills for that career — defined as `selected_skills ∩ get_skills_from_rules(career, all_rules)`. Shows up to 5 chips with a "+N more" suffix if exceeded.
- Whole card is clickable. Click sets `selected_career` and advances to Step 3.

Equal weight (vs. a hero-style #1 card) is intentional: the scoring formula often produces close scores, and over-promoting the #1 result would misrepresent that.

### Step 3: Plan — Two-column + soft skills below

Three pieces from today's app (skill recs, soft skills, demand chart) combined on one screen:

- **Top row** — `st.columns([3, 2])`:
  - **Left column (wider): "⭐ Skills to learn"** — recommended skills from `recommend_skills()` displayed as chips, each labeled by tier:
    - ★★★ Highly Recommended (lift ≥ 2.0)
    - ★★ Recommended (lift ≥ 1.5)
    - ★ Consider Learning (lift < 1.5)
  - **Right column (narrower): "📊 In demand"** — top 10 frequent skills from `arm_freq` as the existing Plotly horizontal bar chart (already dark-themed).
- **Bottom band (full width): "🤝 Soft skills employers want"** — chip-style display from `recommend_soft_skills()` with labels:
  - ★★★ Highly Expected (lift ≥ 2.0)
  - ★★ Commonly Expected (lift ≥ 1.5)
  - ★ Good to Have (lift < 1.5)

Cross-referencing is the design's unique value: a user can visually see that a recommended skill (left) also appears in the in-demand list (right).

### Stepper navigation

- Always visible at top of page, sticky on scroll.
- Three pill-shaped steps connected by a thin line: `Discover` — `Match` — `Plan`.
- Active step: solid teal background, dark text.
- Past steps: outlined teal, clickable.
- Future steps: muted gray; clickable only if their requirements are met (else click is a no-op with a small hint).
- Clicking a past step keeps prior selections intact (user can edit and re-advance).

### Visual styling

Builds on the existing dark + teal palette to keep visual coherence with the Plotly charts.

**`.streamlit/config.toml`** (new file):
```toml
[theme]
base = "dark"
primaryColor = "#14b8a6"               # teal
backgroundColor = "#0f1419"            # deep navy
secondaryBackgroundColor = "#1a2333"   # card surfaces
textColor = "#e8edf2"
font = "sans serif"
```

**Custom CSS** (injected once via `theme.inject_css()`):
- Skill chips — pill-shaped, ~22px tall, teal when selected, ✕ remove icon.
- Match cards — full-width with colored left border, subtle hover lift.
- Stepper — pill steps with connecting line, sticky top.

**Copy tone:** short, direct, second person ("Pick your skills," not "Please select your skills"). Step titles set context. Empty/error states friendly but not chatty.

**Out of scope visually (YAGNI):**
- No custom Streamlit components or React/HTML embeds.
- No illustrations or icons beyond emoji.
- No animations beyond CSS hover transitions.
- No mobile-specific layout.

## Architecture

### Component structure

```
app.py                          # entry point: load data, init session state, route by step
.streamlit/config.toml          # NEW: theme config
src/
  recommender.py                # UNCHANGED
  arm.py                        # UNCHANGED
  preprocessing.py              # UNCHANGED
  ui/                           # NEW directory
    __init__.py
    stepper.py                  # render_stepper(current_step) -> None
    discover.py                 # render_discover() -> None
    match.py                    # render_match() -> None
    plan.py                     # render_plan() -> None
    skill_categories.py         # SKILL_CATEGORIES dict + helpers
    theme.py                    # inject_css() -> None
data/                           # UNCHANGED
tests/                          # NEW directory
  test_skill_categories.py
  test_state_transitions.py
docs/superpowers/specs/         # this spec lives here
```

Each `render_*` function reads from `st.session_state` and writes back on user interaction. Loaded data (`all_rules`, `all_freq`, `all_soft`) is passed in as arguments rather than imported globally, so components are testable in isolation.

### Session state

Initialized in `app.py` on first load:

```python
st.session_state.step             = "discover"   # one of: discover | match | plan
st.session_state.selected_skills  = set()        # user-chosen skill strings
st.session_state.selected_career  = None         # career string or None
st.session_state.cached_matches   = None         # list[(career, score)] or None
```

### Data flow per step

- **Discover** writes `selected_skills` on chip toggles. "Continue →" sets `step = "match"` and clears `cached_matches`.
- **Match** computes once per visit: `cached_matches = recommend_careers(selected_skills, all_rules)` if `cached_matches is None`. Cards render from that. Click sets `selected_career` and `step = "plan"`.
- **Plan** computes on every render (cheap): `recommend_skills(...)`, `recommend_soft_skills(...)`, `all_freq[selected_career].head(10)`.

### Invalidation rules

- Changing `selected_skills` → set `cached_matches = None`.
- Changing `selected_career` → no cache to invalidate; Plan recomputes per render.
- Jumping back via stepper → preserves state; user can edit and re-advance.

### Skill categorization

A new hand-curated dict in `src/ui/skill_categories.py` maps each of the 124 skills to one of ~7 categories: `Languages`, `Data & ML`, `Cloud & DevOps`, `Web`, `Databases`, `Tools`, `Other`. Unmapped skills fall back to `Other` so nothing breaks if a skill is missed.

Helpers:
- `get_skills_by_category(category: str) -> list[str]`
- `get_uncategorized_skills(all_skills: list[str]) -> list[str]` (for diagnostics)

## Edge cases

- **0 skills on Discover** — "Continue →" disabled with hint: "Pick at least one skill to begin."
- **No matches from `recommend_careers`** — empty state on Match: "We couldn't find strong matches — try adding more skills." Includes "Back to Discover" button.
- **Selected career has no rules** (3 of 25 careers lack rules in `arm_rules`) — Plan hides the "Skills to learn" section with a small note; Soft Skills and Demand still render.
- **Selected career has no frequency data** — Plan hides the "In demand" chart with a small note.
- **Selected career still selected but skills changed** — preserved; user can re-run Match to get new ranks.

## Testing

- **`tests/test_skill_categories.py`** — verify every skill returned by `get_all_skills(all_rules)` maps to a category (no orphans except those intentionally falling to `Other`); category names are stable strings.
- **`tests/test_state_transitions.py`** — pure-function tests for any extracted state logic (e.g., `can_advance(step, state) -> bool`).
- **Manual smoke checklist** for the UI (no automated visual tests):
  - Each step renders cleanly.
  - Stepper navigates forward and backward correctly.
  - Empty states trigger on 0 skills, 0 matches.
  - Plan renders correctly for all 22 careers with rules and the 3 without.
  - Two-column layout collapses cleanly on narrow viewports.

## Risks

1. **Skill categorization completeness.** 124 hand-mapped skills, likely 5–10 ambiguous (e.g., "sas"). Mitigation: `Other` category as fallback; iterate after first review.
2. **Stepper UX in Streamlit.** Streamlit re-renders the whole page per click. Stepper needs `st.rerun()` after state changes to feel snappy. Mitigation: prototype stepper in isolation first.
3. **Card click handlers.** Streamlit doesn't natively support "click anywhere on a card." Likely need `st.button` styled as a card via CSS. Fallback: a "Plan this career →" button below each card.
4. **Two-column layout on narrow screens.** Streamlit columns collapse to stacked automatically; needs a manual check at ~768px.

## Migration

- `app.py` is replaced wholesale, not refactored incrementally. The current `st.tabs(...)` structure doesn't map cleanly to the new step flow.
- Entry point stays `streamlit run app.py`.
- No changes to data files, recommender, preprocessing, or ARM pipeline.
- No new Python dependencies.
