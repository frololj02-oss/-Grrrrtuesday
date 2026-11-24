# Инструмент визуализации графа зависимостей (Вариант №33)

## 1. Общее описание
CLI-приложение на Python (используется исключительно стандартная библиотека) для анализа и визуализации графа зависимостей пакетов Rust (Cargo). Инструмент считывает параметры из INI-файла, запрашивает метаданные пакетов напрямую из официального sparse-индекса `crates.io` (или из локального тестового репозитория), строит граф зависимостей методом рекурсивного поиска в ширину (BFS) с учётом глубины, фильтрации и защиты от циклов, а также визуализирует результат в формате Graphviz (DOT) и ASCII-дерева.

### Структура проекта
* `src/config.py` — загрузка и валидация конфигурации из INI-файла (Этап 1).
* `src/fetcher.py` — получение прямых зависимостей из sparse-индекса Cargo по HTTP и загрузка тестового репозитория (Этап 2).
* `src/graph.py` — построение графа зависимостей с помощью рекурсивного BFS, фильтрация и обработка циклов (Этап 3).
* `src/visualizer.py` — генерация представления графа в формате Graphviz DOT и ASCII-дерева (Этап 5).
* `src/main.py` — точка входа CLI и управление этапами выполнения.
* `config.ini` — файл конфигурации.
* `run.bat` / `run.sh` — скрипты запуска для Windows и Linux/macOS.
* `tests/` — директория для тестов.

## 2. Описание функций и настроек
Параметры задаются в файле `config.ini` в секции `[settings]`:
* `package_name` — имя анализируемого пакета (например, `serde`).
* `repo_url` — URL индекса репозитория (`https://index.crates.io`) или путь к файлу тестового репозитория.
* `test_mode` — режим работы с тестовым репозиторием (`true` или `false`).
* `package_version` — целевая версия корневого пакета (например, `1.0.210`).
* `max_depth` — максимальная глубина анализа графа (целое положительное число).
* `filter_substring` — подстрока для исключения пакетов из графа (если пусто — фильтрация отключена).

### Реализованные этапы (`--stage`)
* `1` — вывод всех параметров конфигурации в формате «ключ — значение».
* `2` — сбор и вывод списка прямых зависимостей указанной версии пакета.
* `3` — построение полного графа зависимостей (рекурсивный BFS) с учётом максимальной глубины, фильтра и защиты от зацикливаний.
* `5` — визуализация построенного графа в виде кода Graphviz (DOT) и ASCII-дерева.

## 3. Команды для запуска
Запуск выполняется из корневой директории проекта с указанием нужного этапа (`1`, `2`, `3` или `5`):

* **Windows (PowerShell / CMD):**
  ```cmd
  .\run.bat --stage 5
  ```
* **Linux / macOS:**
  ```bash
  ./run.sh --stage 5
  ```
* **Напрямую через Python:**
  ```bash
  python -m src.main config.ini --stage 1
  python -m src.main config.ini --stage 2
  python -m src.main config.ini --stage 3
  python -m src.main config.ini --stage 5
  ```

## 4. Примеры использования

### Этап 2 — прямые зависимости (`--stage 2`)
```text
Прямые зависимости пакета serde:
- serde_derive
```

### Этап 3 — построение графа (`--stage 3`, `max_depth = 3`)
```text
Граф зависимостей пакета serde:
serde -> serde_derive
serde_derive -> proc-macro2, quote, syn
proc-macro2 -> unicode-ident
quote -> proc-macro2
syn -> proc-macro2, quote, unicode-ident
```

### Этап 5 — визуализация (`--stage 5`, `max_depth = 3`)
```text
Graphviz DOT:
digraph Dependencies {
    "serde" -> "serde_derive";
    "serde_derive" -> "proc-macro2";
    "serde_derive" -> "quote";
    "serde_derive" -> "syn";
    "proc-macro2" -> "unicode-ident";
    "quote" -> "proc-macro2";
    "syn" -> "proc-macro2";
    "syn" -> "quote";
    "syn" -> "unicode-ident";
}

ASCII-дерево:
serde
└── serde_derive
    ├── proc-macro2
    │   └── unicode-ident
    ├── quote
    │   └── proc-macro2
    │       └── unicode-ident
    └── syn
        ├── proc-macro2
        │   └── unicode-ident
        ├── quote
        │   └── proc-macro2
        │       └── unicode-ident
        └── unicode-ident
```