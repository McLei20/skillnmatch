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
