import unittest
from pathlib import Path
from allocation import Incident, Responder, read_inputs, simulate
from routing import load_graph
from traffic import adjust_for_traffic
from road_conditions import estimate_graph


class AllocationTests(unittest.TestCase):
    def test_specialist_leaves_flexible_responder_for_other_incident(self):
        responders = [Responder("both", "A", {"x", "y"}, 0), Responder("x", "A", {"x"}, 0)]
        incidents = [Incident(skill, "A", "High", 0, skill, 0, 1) for skill in ("x", "y")]
        plan, _ = simulate({"A": []}, responders, incidents)
        self.assertEqual({(a["responder_id"], a["incident_id"]) for a in plan},
                         {("both", "y"), ("x", "x")})

    def test_future_critical_incident_cannot_influence_earlier_dispatch(self):
        r = Responder("r", "A", {"x"}, 0)
        incidents = [Incident("early", "A", "Low", 5, "x", 0, 10),
                     Incident("later", "A", "Critical", 3, "x", 1, 1)]
        plan, _ = simulate({"A": []}, [r], incidents)
        self.assertEqual([a["incident_id"] for a in plan], ["early"])

    def test_replay_scenario_plans(self):
        for folder in sorted((Path(__file__).parent / "Scenarios").glob("Scenario*")):
            with self.subTest(scenario=folder.name):
                graph = adjust_for_traffic(folder, estimate_graph(folder, load_graph(folder)))
                responders, incidents = read_inputs(folder)
                plan, delays = simulate(graph, responders, incidents)
                fresh, _ = read_inputs(folder)
                units = {r.id: r for r in fresh}
                calls = {i.id: i for i in incidents}
                self.assertTrue(plan)
                for assignment, delay in zip(plan, delays):
                    i = calls.pop(assignment["incident_id"])
                    r = units[assignment["responder_id"]]
                    t, path = assignment["time"], assignment["path"]
                    self.assertGreaterEqual(t, max(i.release, r.ready))
                    self.assertIn(i.skill, r.skills)
                    self.assertEqual((path[0], path[-1]), (r.location, i.location))
                    arrival = t + sum(dict(graph[a])[b] for a, b in zip(path, path[1:]))
                    self.assertLessEqual(arrival, i.deadline)
                    self.assertAlmostEqual(delay, arrival - i.release)
                    r.location, r.ready = i.location, arrival + i.duration
