import unittest
from typing import Dict, List

from src.graph import build_dependency_graph
from src.visualizer import to_d2


class TestDependencyTool(unittest.TestCase):
    def setUp(self) -> None:
        self.repo: Dict[str, List[str]] = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["A"],
            "D": [],
        }

    def _provider(self, pkg: str, depth: int) -> List[str]:
        return self.repo.get(pkg, [])

    def test_bfs_graph_and_cycles(self) -> None:
        graph = build_dependency_graph("A", 2, "", self._provider)
        self.assertEqual(graph, {"A": ["B", "C"], "B": ["D"], "C": ["A"]})

    def test_filter_substring(self) -> None:
        graph = build_dependency_graph("A", 2, "C", self._provider)
        self.assertEqual(graph, {"A": ["B"], "B": ["D"]})

    def test_to_d2(self) -> None:
        d2_output = to_d2({"A": ["B"], "B": []})
        self.assertEqual(d2_output, '"A" -> "B"\n"B"')


if __name__ == "__main__":
    unittest.main()