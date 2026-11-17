import json
import urllib.error
import urllib.request
from typing import Dict, List

LEN_ONE = 1
LEN_TWO = 2
LEN_THREE = 3
PREFIX_STEP = 2
SECOND_SLICE_END = 4
HTTP_TIMEOUT = 10
NORMAL_DEP_KIND = "normal"


class FetchError(Exception):
    pass


def get_cargo_index_url(base_url: str, pkg_name: str) -> str:
    base = base_url.rstrip("/")
    name = pkg_name.lower()
    length = len(name)

    if length == LEN_ONE:
        return f"{base}/1/{name}"
    if length == LEN_TWO:
        return f"{base}/2/{name}"
    if length == LEN_THREE:
        return f"{base}/3/{name[0]}/{name}"

    p1 = name[:PREFIX_STEP]
    p2 = name[PREFIX_STEP:SECOND_SLICE_END]
    return f"{base}/{p1}/{p2}/{name}"


def _extract_normal_deps(deps_list: List[dict]) -> List[str]:
    result: List[str] = []
    for dep in deps_list:
        kind = dep.get("kind", NORMAL_DEP_KIND)
        if kind is None or kind == NORMAL_DEP_KIND:
            dep_name = dep.get("package") or dep.get("name")
            if dep_name and dep_name not in result:
                result.append(dep_name)
    return result


def _parse_cargo_index_lines(
    raw_text: str, pkg_name: str, version: str
) -> List[str]:
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    if not lines:
        raise FetchError(f"Пустой индекс для пакета {pkg_name}")

    target_record = None
    for line in lines:
        record = json.loads(line)
        if not version or version == "latest":
            if not record.get("yanked", False):
                target_record = record
        elif record.get("vers") == version:
            target_record = record
            break

    if target_record is None:
        raise FetchError(
            f"Версия '{version}' для пакета '{pkg_name}' не найдена"
        )
    return _extract_normal_deps(target_record.get("deps", []))


def fetch_cargo_dependencies(
    base_url: str, pkg_name: str, version: str
) -> List[str]:
    url = get_cargo_index_url(base_url, pkg_name)
    req = urllib.request.Request(
        url, headers={"User-Agent": "DepVisualizer-MIREA/1.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as response:
            text = response.read().decode("utf-8")
    except urllib.error.URLError as err:
        raise FetchError(
            f"Не удалось получить пакет '{pkg_name}' по {url}: {err}"
        ) from err

    return _parse_cargo_index_lines(text, pkg_name, version)


def load_test_repository(file_path: str) -> Dict[str, List[str]]:
    repo: Dict[str, List[str]] = {}
    with open(file_path, "r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line or ":" not in line:
                continue
            pkg, deps_part = line.split(":", maxsplit=1)
            pkg_clean = pkg.strip()
            deps = [d.strip() for d in deps_part.split() if d.strip()]
            repo[pkg_clean] = deps
    return repo