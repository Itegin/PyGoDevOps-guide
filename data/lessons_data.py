# -*- coding: utf-8 -*-
"""
Содержимое гайда: фазы и уроки.

Это ОБЫЧНЫЕ Python-структуры (списки словарей), а не база данных.
Идея разделения: контент (что показывать) живёт тут, в коде,
а состояние (что уже отмечено) — в SQLite (см. app.py).
Так удобно редактировать текст гайда, не трогая логику приложения.

Каждый урок обязан иметь уникальный "id" — по нему в БД хранится
галочка "выполнено / не выполнено". Если добавляешь новый урок —
придумай новый уникальный id и просто добавь его в список ниже.
"""

PHASES = [
    {
        "code": "p0",
        "track": "py",  # py / go / project — используется для цвета в CSS
        "title": "Окружение и инструменты",
        "meta": "Неделя 0 · ~4 ч",
        "why": "",
        "lessons": [
            {
                "id": "p0-1",
                "title": "SSH и VS Code Remote-SSH к домашнему серверу",
                "text": "Генерируешь ключ (ssh-keygen -ed25519), кладёшь публичный на Debian, "
                        "настраиваешь ~/.ssh/config. Дальше весь код пишешь локально, "
                        "а выполняешь на сервере.",
                "task": "Практика: подключиться без пароля, открыть терминал сервера прямо в VS Code",
            },
            {
                "id": "p0-2",
                "title": "Git и GitHub с нуля до PR",
                "text": "init, add, commit, .gitignore, ветки, push, первый Pull Request сам себе.",
                "task": "Практика: создать репозиторий learning-log, коммитить туда заметки по каждому уроку",
            },
            {
                "id": "p0-3",
                "title": "Установка Python 3.14 и Go 1.26 на Debian",
                "text": "apt в Debian stable почти всегда отстаёт по версиям, поэтому Python — через pyenv, "
                        "а Go — официальным tar.gz с go.dev.",
                "task": "Практика: python3 --version и go version показывают актуальные версии",
            },
        ],
    },
    {
        "code": "p1",
        "track": "py",
        "title": "Python: основы языка",
        "meta": "Недели 1–3 · ~18 ч",
        "why": "Цель фазы — уверенно читать и писать код без гугления синтаксиса на каждой строке.",
        "lessons": [
            {"id": "p1-1", "title": "Переменные, типы, операторы, ввод/вывод",
             "text": "", "task": "Скрипт-конвертер единиц измерения (МБ↔ГБ, часы↔сек)"},
            {"id": "p1-2", "title": "Условия и циклы (if/for/while)",
             "text": "", "task": "Скрипт, проверяющий диапазон портов на «занятость» по номеру"},
            {"id": "p1-3", "title": "Функции, аргументы, области видимости",
             "text": "", "task": "Функция форматирования байт в человекочитаемый вид (1024 → 1.0 KB)"},
            {"id": "p1-4", "title": "Структуры данных: list, dict, tuple, set",
             "text": "Это то, чем ты будешь оперировать 90% времени в DevOps-скриптах.",
             "task": "Распарсить вывод df -h (как текст) в список словарей"},
            {"id": "p1-5", "title": "Обработка ошибок: try/except, свои исключения",
             "text": "", "task": "Обернуть скрипт с диском так, чтобы он не падал, если путь не существует"},
            {"id": "p1-6", "title": "Модули, пакеты, virtualenv/venv",
             "text": "Почему нельзя ставить всё через pip install глобально на сервере — сломает системный Python.",
             "task": "Создать venv, поставить requests, зафиксировать зависимости в requirements.txt"},
            {"id": "p1-7", "title": "Файлы, JSON, YAML",
             "text": "", "task": "Скрипт, читающий config.yaml с настройками (пороги алертов) и валидирующий его"},
            {"id": "p1-8", "title": "Минимальный ООП: классы, атрибуты, методы, dataclass",
             "text": "Ровно столько, чтобы понимать модели Pydantic в FastAPI.",
             "task": "Класс ServerMetric(cpu, ram, disk, timestamp) через @dataclass"},
        ],
    },
    {
        "code": "p2",
        "track": "py",
        "title": "Python для автоматизации / DevOps",
        "meta": "Недели 4–6 · ~18 ч",
        "why": "Здесь Python превращается из «языка программирования» в инструмент сисадмина.",
        "lessons": [
            {"id": "p2-1", "title": "subprocess: запуск shell-команд из Python",
             "text": "С обработкой кода возврата и таймаутов — иначе скрипт зависнет намертво.",
             "task": "Обёртка вокруг systemctl status <service>, возвращающая True/False"},
            {"id": "p2-2", "title": "os / shutil / pathlib: файлы, права, диски",
             "text": "", "task": "Скрипт очистки старых логов (по возрасту файла) с dry-run режимом"},
            {"id": "p2-3", "title": "argparse: превращаем скрипт в нормальный CLI",
             "text": "", "task": "Добавить флаги --dry-run, --path, --days к скрипту очистки логов"},
            {"id": "p2-4", "title": "logging вместо print()",
             "text": "Почему в проде это критично: уровни INFO/WARNING/ERROR, запись в файл, ротация.",
             "task": "Заменить все print в предыдущих скриптах на logging"},
            {"id": "p2-5", "title": "requests: работа с REST API",
             "text": "", "task": "Написать функцию отправки сообщения в Telegram через Bot API"},
            {"id": "p2-6", "title": "psutil: метрики системы (CPU/RAM/диск/сеть)",
             "text": "", "task": "Скрипт, печатающий текущую нагрузку каждые 5 секунд"},
            {"id": "p2-7", "title": "docker SDK для Python (docker-py)",
             "text": "", "task": "Скрипт, находящий контейнеры в статусе unhealthy"},
            {"id": "p2-8", "title": "systemd unit + timer вместо cron",
             "text": "Разница: timer логируется в journalctl, легче дебажить, есть зависимости между юнитами.",
             "task": "Обернуть скрипт метрик в systemd service + timer, запускающийся раз в минуту"},
        ],
    },
    {
        "code": "p3",
        "track": "py",
        "title": "БД, API, подготовка к проекту",
        "meta": "Недели 7–8 · ~12 ч",
        "why": "",
        "lessons": [
            {"id": "p3-1", "title": "SQL-минимум + SQLite из Python (sqlite3)",
             "text": "SQLite выбран сознательно: файл на диске, ноль настройки, хватает с запасом при твоей нагрузке.",
             "task": "Таблица metrics(ts, cpu, ram, disk), запись и выборка за период"},
            {"id": "p3-2", "title": "SQLAlchemy (ORM) — по желанию",
             "text": "Либо остаёшься на чистом SQL.", "task": ""},
            {"id": "p3-3", "title": "FastAPI: первые роуты, Pydantic-модели, /docs",
             "text": "", "task": "GET /health, возвращающий {\"status\": \"ok\"}"},
            {"id": "p3-4", "title": "CRUD-эндпоинты + async basics",
             "text": "", "task": "GET /metrics?from=&to= с фильтрацией по датам из SQLite"},
            {"id": "p3-5", "title": "Dockerfile для Python-приложения + docker-compose",
             "text": "Multi-stage build, чтобы образ был лёгкий — важно при 1 ТБ и медленном 7200rpm диске.",
             "task": "Собрать образ FastAPI-приложения, поднять через docker-compose"},
        ],
    },
    {
        "code": "pr1",
        "track": "project",
        "title": "★ Проект 1 — Homelab Monitoring & Alerting API",
        "meta": "Недели 9–11 · ~20 ч",
        "why": "Итог: сервис на FastAPI, который сам собирает метрики CPU/RAM/диска и статус "
               "Docker-контейнеров твоего сервера, копит историю в SQLite, отдаёт по API "
               "и шлёт алерты в Telegram при превышении порогов.",
        "lessons": [
            {"id": "pr1-1", "title": "Milestone 1 — collector.py",
             "text": "Сбор метрик системы (psutil) и контейнеров (docker-py), запись в SQLite по расписанию.", "task": ""},
            {"id": "pr1-2", "title": "Milestone 2 — API-слой",
             "text": "FastAPI-эндпоинты для текущих и исторических метрик.", "task": ""},
            {"id": "pr1-3", "title": "Milestone 3 — пороги и алерты",
             "text": "Конфиг с порогами (disk > 90%, RAM > 90%), проверка при сборе, Telegram с антиспам-задержкой.", "task": ""},
            {"id": "pr1-4", "title": "Milestone 4 — мини-дашборд",
             "text": "Простая HTML/Chart.js страница либо Grafana поверх SQLite.", "task": ""},
            {"id": "pr1-5", "title": "Milestone 5 — упаковка и деплой",
             "text": "docker-compose (app + опционально nginx), деплой на Debian-сервер, автозапуск.", "task": ""},
            {"id": "pr1-6", "title": "Milestone 6 — README для портфолио",
             "text": "Схема архитектуры, скриншот дашборда, «как запустить локально».", "task": ""},
        ],
    },
    {
        "code": "g1",
        "track": "go",
        "title": "Go: основы языка",
        "meta": "Недели 12–14 · ~18 ч",
        "why": "Go учат не «потому что модно» — Docker, containerd, Kubernetes, Terraform, Prometheus "
               "и большинство CLI-инструментов DevOps написаны на нём.",
        "lessons": [
            {"id": "g1-1", "title": "go.mod, структура проекта, go run/build",
             "text": "", "task": "hello-world как отдельный модуль с go.mod"},
            {"id": "g1-2", "title": "Базовые типы, переменные, константы, приведение типов", "text": "", "task": ""},
            {"id": "g1-3", "title": "Срезы (slices) и карты (maps)",
             "text": "Аналоги list/dict из Python, но со своими нюансами (capacity, nil map).",
             "task": "Переписать парсер df -h из P1 на Go"},
            {"id": "g1-4", "title": "Функции, множественный возврат значений", "text": "", "task": ""},
            {"id": "g1-5", "title": "Структуры (struct) и методы", "text": "", "task": ""},
            {"id": "g1-6", "title": "Интерфейсы: маленькие интерфейсы, много реализаций", "text": "", "task": ""},
            {"id": "g1-7", "title": "Обработка ошибок в Go-стиле (if err != nil), пакет errors",
             "text": "Непривычно после try/except, но это стандарт индустрии для Go.", "task": ""},
        ],
    },
    {
        "code": "g2",
        "track": "go",
        "title": "Go: конкурентность, сеть, CLI",
        "meta": "Недели 15–17 · ~18 ч",
        "why": "",
        "lessons": [
            {"id": "g2-1", "title": "Goroutines и channels — конкурентность без потоков ОС",
             "text": "", "task": "Параллельно опросить 10 URL и собрать время ответа"},
            {"id": "g2-2", "title": "sync.WaitGroup, sync.Mutex — синхронизация горутин", "text": "", "task": ""},
            {"id": "g2-3", "title": "net/http: пишем HTTP-сервер с нуля",
             "text": "", "task": "/health и /version эндпоинты"},
            {"id": "g2-4", "title": "Кодирование JSON и текстовых форматов ответа", "text": "", "task": ""},
            {"id": "g2-5", "title": "CLI-утилиты: flag или cobra, конфиг через флаги/env",
             "text": "Так устроены kubectl, terraform, docker cli.",
             "task": "CLI с флагами --port, --interval"},
            {"id": "g2-6", "title": "Базовое тестирование: пакет testing, table-driven tests",
             "text": "Наличие тестов — весомый плюс в портфолио.", "task": ""},
        ],
    },
    {
        "code": "pr2",
        "track": "project",
        "title": "★ Проект 2 — Metrics Exporter + Health-check CLI",
        "meta": "Недели 18–21 · ~22 ч",
        "why": "Ты своими руками пересобираешь упрощённые версии node_exporter + blackbox_exporter — "
               "инструментов, которые реально стоят в проде у DevOps-команд.",
        "lessons": [
            {"id": "pr2-1", "title": "Milestone 1",
             "text": "HTTP-сервер на net/http, отдающий /metrics в формате экспозиции Prometheus.", "task": ""},
            {"id": "pr2-2", "title": "Milestone 2",
             "text": "Сбор системных метрик (CPU/RAM/диск) через /proc на Linux, без внешних зависимостей.", "task": ""},
            {"id": "pr2-3", "title": "Milestone 3",
             "text": "Health-check модуль — параллельные (goroutines) проверки списка URL/портов из конфига.", "task": ""},
            {"id": "pr2-4", "title": "Milestone 4",
             "text": "CLI-конфигурация (флаги/YAML), нормальное логирование, graceful shutdown по SIGTERM.", "task": ""},
            {"id": "pr2-5", "title": "Milestone 5 (stretch)",
             "text": "Через Docker Engine API — автоматический restart контейнера, если он unhealthy дольше N минут.", "task": ""},
            {"id": "pr2-6", "title": "Milestone 6",
             "text": "Связка с VictoriaMetrics (лёгкая замена Prometheus) + Grafana через docker-compose.", "task": ""},
            {"id": "pr2-7", "title": "Milestone 7",
             "text": "README с архитектурной схемой и объяснением, зачем писать самому при наличии готового node_exporter.", "task": ""},
        ],
    },
    {
        "code": "p6",
        "track": "project",
        "title": "CI/CD и упаковка портфолио",
        "meta": "Недели 22–24 · ~13 ч",
        "why": "",
        "lessons": [
            {"id": "p6-1", "title": "Git-гигиена: осмысленные коммиты, .gitignore, ветки feature/*", "text": "", "task": ""},
            {"id": "p6-2", "title": "GitHub Actions: lint + тесты Python-проекта при каждом push", "text": "", "task": ""},
            {"id": "p6-3", "title": "GitHub Actions: build + go test для Go-проекта", "text": "", "task": ""},
            {"id": "p6-4", "title": "Сборка и публикация Docker-образов в GHCR", "text": "", "task": ""},
            {"id": "p6-5", "title": "Автодеплой на домашний сервер по SSH-ключу деплоя при пуше в main", "text": "", "task": ""},
            {"id": "p6-6", "title": "Финальные README обоих проектов + описание для резюме", "text": "", "task": ""},
        ],
    },
]


def all_lesson_ids():
    """Плоский список всех id уроков — нужен, чтобы засеять таблицу progress в БД."""
    ids = []
    for phase in PHASES:
        for lesson in phase["lessons"]:
            ids.append(lesson["id"])
    return ids
