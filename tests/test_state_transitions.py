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
