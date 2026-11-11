import unittest
from routing import fastest_route


class RoutingTests(unittest.TestCase):
    graph = {"A": [("C", 9), ("B", 2)], "B": [("C", 3)], "C": []}

    def test_indirect_route_saves_time(self):
        self.assertEqual(fastest_route(self.graph, "A", "C"), (["A", "B", "C"], 5))

    def test_one_way_roads(self):
        self.assertIsNone(fastest_route(self.graph, "C", "A"))

    def test_already_at_destination(self):
        self.assertEqual(fastest_route(self.graph, "B", "B"), (["B"], 0))
