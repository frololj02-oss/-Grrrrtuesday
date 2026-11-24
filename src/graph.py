from typing import Callable, Dict, List, Set


def _bfs_recursive(
    level: List[str],
    depth: int,
    max_depth: int,
    filter_substring: str,
    visited: Set[str],
    graph: Dict[str, List[str]],
    get_deps: Callable[[str, int], List[str]],
) -> None:
    if not level or depth >= max_depth:
        return

    next_level: List[str] = []
    for pkg in level:
        raw_deps = get_deps(pkg, depth)
        filtered_deps: List[str] = []
        for dep in raw_deps:
            if filter_substring and filter_substring in dep:
                continue
            if dep not in filtered_deps:
                filtered_deps.append(dep)
            if dep not in visited:
                visited.add(dep)
                next_level.append(dep)
        graph[pkg] = filtered_deps

    _bfs_recursive(
        next_level,
        depth + 1,
        max_depth,
        filter_substring,
        visited,
        graph,
        get_deps,
    )


def build_dependency_graph(
    root: str,
    max_depth: int,
    filter_substring: str,
    get_deps: Callable[[str, int], List[str]],
) -> Dict[str, List[str]]:
    if filter_substring and filter_substring in root:
        return {}

    graph: Dict[str, List[str]] = {}
    visited: Set[str] = {root}
    _bfs_recursive(
        [root],
        0,
        max_depth,
        filter_substring,
        visited,
        graph,
        get_deps,
    )
    return graph