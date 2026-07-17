import unittest

from cyberdyne.governor import evaluate, halted

POLICY = {
    "max_steps": 3,
    "max_seconds": 100,
    "heartbeat_timeout": 30,
    "require_approval_for": ["delete"],
}


def run(events, policy=POLICY):
    return evaluate(policy, events)


class GovernorTests(unittest.TestCase):
    def test_clean_run_ok(self):
        ev = [{"t": 0, "kind": "heartbeat"}, {"t": 1, "kind": "action", "action": "read"}]
        self.assertFalse(halted(run(ev)))

    def test_step_budget_halts(self):
        ev = [{"t": i, "kind": "action", "action": "x"} for i in range(5)]
        d = run(ev)
        self.assertTrue(halted(d))
        self.assertEqual(d["reason"], "step-budget-exceeded")

    def test_time_budget_halts(self):
        ev = [{"t": 0, "kind": "action", "action": "x"}, {"t": 200, "kind": "action", "action": "y"}]
        d = run(ev)
        self.assertTrue(halted(d))
        self.assertEqual(d["reason"], "time-budget-exceeded")

    def test_heartbeat_lost_halts(self):
        ev = [{"t": 0, "kind": "heartbeat"}, {"t": 100, "kind": "action", "action": "x"}]
        d = run(ev)
        self.assertTrue(halted(d))
        self.assertEqual(d["reason"], "heartbeat-lost")

    def test_unapproved_required_action_halts(self):
        d = run([{"t": 0, "kind": "action", "action": "delete"}])
        self.assertTrue(halted(d))
        self.assertEqual(d["reason"], "unapproved-action")

    def test_approved_action_passes(self):
        d = run([{"t": 0, "kind": "action", "action": "delete", "approved": True}])
        self.assertFalse(halted(d))

    def test_forbidden_action_halts_even_when_approved(self):
        pol = dict(POLICY, forbidden_actions=["rm_rf"])
        d = evaluate(pol, [{"t": 0, "kind": "action", "action": "rm_rf", "approved": True}])
        self.assertTrue(halted(d))
        self.assertEqual(d["reason"], "forbidden-action")

    def test_forbidden_beats_the_approval_gate(self):
        # "delete" both requires approval AND is forbidden — forbidden must win.
        pol = dict(POLICY, forbidden_actions=["delete"])
        d = evaluate(pol, [{"t": 0, "kind": "action", "action": "delete", "approved": True}])
        self.assertEqual(d["reason"], "forbidden-action")

    def test_non_forbidden_action_unaffected(self):
        pol = dict(POLICY, forbidden_actions=["rm_rf"])
        self.assertFalse(halted(evaluate(pol, [{"t": 0, "kind": "action", "action": "read"}])))


if __name__ == "__main__":
    unittest.main()
