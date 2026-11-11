import json
import unittest
from pathlib import Path

from routing import load_graph, fastest_route
from road_conditions import estimate_graph
from traffic import forecast, adjust_for_traffic


class TrafficTests(unittest.TestCase):
    folder = Path(__file__).parent / "Scenarios" / "Scenario2"
    model = json.loads((folder / "traffic_probabilities.json").read_text())

    def test_empty_history(self):
        self.assertEqual(forecast(self.model, []), self.model["initial"])

    def test_two_readings_against_hidden_path_enumeration(self):
        model = self.model
        totals = {}
        for dest in model["initial"]:
            totals[dest] = sum(
                pa * model["emission"][a]["High"] * model["transition"][a][b]
                * model["emission"][b]["Low"] * model["transition"][b][dest]
                for a, pa in model["initial"].items() for b in model["initial"]
            )
        actual = forecast(model, ["High", "Low"])
        for state, weight in totals.items():
            self.assertAlmostEqual(actual[state], weight / sum(totals.values()))

    def test_forecast_changes_scenario_two_route(self):
        roads = estimate_graph(self.folder, load_graph(self.folder))
        traffic = adjust_for_traffic(self.folder, roads)
        self.assertEqual(fastest_route(roads, "H2", "N9")[0], ["H2", "N8", "N9"])
        path, seconds = fastest_route(traffic, "H2", "N9")
        self.assertEqual(path, ["H2", "N7", "N9"])
        self.assertAlmostEqual(seconds, 54.5501666667)
