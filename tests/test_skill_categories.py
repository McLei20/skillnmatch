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
