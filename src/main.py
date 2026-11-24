import argparse
import sys
from typing import Callable, Dict, List

from src.config import AppConfig, ConfigError, format_config_kv, load_config
from src.fetcher import (
    FetchError,
    fetch_cargo_dependencies,
    load_test_repository,
)
from src.graph import build_dependency_graph
from src.visualizer import to_d2

EXIT_ERROR_CODE = 1
STAGE_CONFIG = 1
STAGE_DIRECT = 2
STAGE_GRAPH = 3
STAGE_VISUALIZE = 5


def _make_deps_provider(
    cfg: AppConfig, test_repo: Dict[str, List[str]]
) -> Callable[[str, int], List[str]]:
    def _provider(pkg: str, depth: int) -> List[str]:
        if cfg.test_mode:
            return test_repo.get(pkg, [])
        version = cfg.package_version if depth == 0 else ""
        return fetch_cargo_dependencies(cfg.repo_url, pkg, version)

    return _provider


def _run_stage_two(cfg: AppConfig, test_repo: Dict[str, List[str]]) -> None:
    if cfg.test_mode:
        deps = test_repo.get(cfg.package_name, [])
    else:
        deps = fetch_cargo_dependencies(
            cfg.repo_url, cfg.package_name, cfg.package_version
        )
    print(f"Прямые зависимости пакета {cfg.package_name}:")
    for dep in deps:
        print(f"- {dep}")


def _run_stage_three(cfg: AppConfig, test_repo: Dict[str, List[str]]) -> None:
    provider = _make_deps_provider(cfg, test_repo)
    graph = build_dependency_graph(
        cfg.package_name, cfg.max_depth, cfg.filter_substring, provider
    )
    print(f"Граф зависимостей пакета {cfg.package_name}:")
    for pkg, deps in graph.items():
        deps_str = ", ".join(deps) if deps else "нет"
        print(f"{pkg} -> {deps_str}")


def _run_stage_five(cfg: AppConfig, test_repo: Dict[str, List[str]]) -> None:
    provider = _make_deps_provider(cfg, test_repo)
    graph = build_dependency_graph(
        cfg.package_name, cfg.max_depth, cfg.filter_substring, provider
    )
    print(to_d2(graph))


def execute_stage(cfg: AppConfig, stage: int) -> None:
    if stage == STAGE_CONFIG:
        print(format_config_kv(cfg))
        return

    test_repo = load_test_repository(cfg.repo_url) if cfg.test_mode else {}
    if stage == STAGE_DIRECT:
        _run_stage_two(cfg, test_repo)
        return
    if stage == STAGE_GRAPH:
        _run_stage_three(cfg, test_repo)
        return
    if stage == STAGE_VISUALIZE:
        _run_stage_five(cfg, test_repo)
        return


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Визуализатор графа зависимостей (Вариант 33)"
    )
    parser.add_argument("config", help="Путь к INI-файлу конфигурации")
    parser.add_argument(
        "--stage",
        type=int,
        choices=[1, 2, 3, 5],
        default=STAGE_VISUALIZE,
        help="Номер этапа (1, 2, 3 или 5)",
    )
    args = parser.parse_args()

    try:
        cfg = load_config(args.config)
        execute_stage(cfg, args.stage)
    except (ConfigError, FetchError, OSError) as err:
        print(f"Ошибка: {err}", file=sys.stderr)
        sys.exit(EXIT_ERROR_CODE)


if __name__ == "__main__":
    main()