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
