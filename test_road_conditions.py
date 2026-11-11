import json
import unittest
from pathlib import Path

from road_conditions import estimate_graph, posterior
from routing import fastest_route, load_graph

SCENARIO = Path(__file__).parent / "Scenarios" / "Scenario1"


class RoadConditionTests(unittest.TestCase):
    tables = json.loads((SCENARIO / "road_probabilities.json").read_text())

    def test_no_evidence_uses_marginal_prior(self):
        result = posterior(self.tables, [])
        self.assertAlmostEqual(result["Open"], 0.685)
        self.assertAlmostEqual(sum(result.values()), 1)

    def test_conflicting_reports(self):
        reports = [
            {"weather": "Rain", "source": source, "reported_status": status}
            for source, status in [("Citizen", "Blocked"), ("Police", "Blocked"),
                                   ("Sensor", "Congested")]
        ]
        # Independent calculation in state order open, congested, blocked.
        weights = [0.60 * 0.10 * 0.02 * 0.10, 0.30 * 0.20 * 0.08 * 0.80,
                   0.10 * 0.70 * 0.90 * 0.07]
        self.assertAlmostEqual(posterior(self.tables, reports)["Blocked"],
                               weights[2] / sum(weights))

    def test_directional_cost_and_detour(self):
        base = load_graph(SCENARIO)
        graph = estimate_graph(SCENARIO, base)
        self.assertNotIn("N2", dict(graph["N1"]))
        self.assertAlmostEqual(dict(graph["N2"])["N1"], 1.5 * 775 / 15)
        path, seconds = fastest_route(graph, "N1", "N2")
        self.assertEqual(path, ["N1", "H1", "N2"])
        self.assertAlmostEqual(seconds, 78.6)
