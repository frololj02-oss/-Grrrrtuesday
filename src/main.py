import argparse
import sys
from typing import Dict, List

from src.config import AppConfig, ConfigError, format_config_kv, load_config
from src.fetcher import (
    FetchError,
    fetch_cargo_dependencies,
    load_test_repository,
)

EXIT_ERROR_CODE = 1
STAGE_CONFIG = 1
STAGE_DIRECT = 2


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


def execute_stage(cfg: AppConfig, stage: int) -> None:
    if stage == STAGE_CONFIG:
        print(format_config_kv(cfg))
        return

    test_repo = load_test_repository(cfg.repo_url) if cfg.test_mode else {}
    if stage == STAGE_DIRECT:
        _run_stage_two(cfg, test_repo)
        return


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Визуализатор графа зависимостей (Вариант 33)"
    )
    parser.add_argument("config", help="Путь к INI-файлу конфигурации")
    parser.add_argument(
        "--stage",
        type=int,
        choices=[1, 2],
        default=STAGE_DIRECT,
        help="Номер этапа (1 или 2)",
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