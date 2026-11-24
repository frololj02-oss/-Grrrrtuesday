from typing import Dict, List


def to_d2(graph: Dict[str, List[str]]) -> str:
    lines: List[str] = []
    for pkg, deps in graph.items():
        if not deps:
            lines.append(f'"{pkg}"')
        for dep in deps:
            lines.append(f'"{pkg}" -> "{dep}"')
    return "\n".join(lines)