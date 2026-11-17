import configparser
import os
from dataclasses import dataclass

MIN_DEPTH = 0
REQUIRED_SECTION = "settings"
REQUIRED_KEYS = (
    "package_name",
    "repo_url",
    "test_mode",
    "package_version",
    "max_depth",
    "filter_substring",
)


class ConfigError(Exception):
    pass


@dataclass
class AppConfig:
    package_name: str
    repo_url: str
    test_mode: bool
    package_version: str
    max_depth: int
    filter_substring: str


def _validate_keys(section: configparser.SectionProxy) -> None:
    for key in REQUIRED_KEYS:
        if key not in section:
            raise ConfigError(f"Отсутствует обязательный параметр: {key}")


def _parse_bool(value: str, key_name: str) -> bool:
    normalized = value.strip().lower()
    if normalized in ("true", "yes", "1"):
        return True
    if normalized in ("false", "no", "0"):
        return False
    raise ConfigError(f"Некорректное булево значение в '{key_name}': {value}")


def _parse_depth(value: str) -> int:
    try:
        depth = int(value.strip())
    except ValueError as err:
        raise ConfigError(
            f"Глубина должна быть целым числом: {value}"
        ) from err
    if depth < MIN_DEPTH:
        raise ConfigError("Максимальная глубина не может быть отрицательной")
    return depth


def _validate_strings(
    pkg: str, url: str, ver: str, test_mode: bool
) -> None:
    if not pkg:
        raise ConfigError("Имя пакета не может быть пустым")
    if not url:
        raise ConfigError("URL или путь к репозиторию не может быть пустым")
    if not ver and not test_mode:
        raise ConfigError("Версия пакета обязательна в режиме репозитория")
    if test_mode and not os.path.isfile(url):
        raise ConfigError(f"Файл тестового репозитория не найден: {url}")


def load_config(file_path: str) -> AppConfig:
    if not os.path.isfile(file_path):
        raise ConfigError(f"Конфигурационный файл не найден: {file_path}")

    parser = configparser.ConfigParser()
    try:
        parser.read(file_path, encoding="utf-8")
    except configparser.Error as err:
        raise ConfigError(f"Ошибка синтаксиса INI-файла: {err}") from err

    if REQUIRED_SECTION not in parser:
        raise ConfigError(f"Отсутствует секция [{REQUIRED_SECTION}]")

    sec = parser[REQUIRED_SECTION]
    _validate_keys(sec)

    pkg = sec["package_name"].strip()
    url = sec["repo_url"].strip()
    test_mode = _parse_bool(sec["test_mode"], "test_mode")
    ver = sec["package_version"].strip()
    depth = _parse_depth(sec["max_depth"])
    flt = sec["filter_substring"].strip()

    _validate_strings(pkg, url, ver, test_mode)
    return AppConfig(pkg, url, test_mode, ver, depth, flt)


def format_config_kv(config: AppConfig) -> str:
    lines = [
        f"package_name={config.package_name}",
        f"repo_url={config.repo_url}",
        f"test_mode={config.test_mode}",
        f"package_version={config.package_version}",
        f"max_depth={config.max_depth}",
        f"filter_substring={config.filter_substring}",
    ]
    return "\n".join(lines)