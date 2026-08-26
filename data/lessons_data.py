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

Поле "links" — необязательное: список {"title": ..., "url": ...}.
Все ссылки ниже проверены и ведут либо на официальную документацию,
либо на конкретные проверенные статьи/туториалы по теме урока.
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
                        "настраиваешь ~/.ssh/config. Дальше весь код пишешь локально в VS Code, "
                        "а выполняется он на сервере — файлы физически лежат там, редактор лишь "
                        "подключается по SSH и работает с ними напрямую.",
                "task": "Практика: подключиться без пароля, открыть терминал сервера прямо в VS Code",
                "links": [
                    {"title": "VS Code Remote-SSH — офиц. документация",
                     "url": "https://code.visualstudio.com/docs/remote/ssh"},
                ],
            },
            {
                "id": "p0-2",
                "title": "Git и GitHub с нуля до PR",
                "text": "init, add, commit, .gitignore, ветки, push, первый Pull Request сам себе. "
                        "Пока это кажется формальностью, но именно так будут выглядеть оба твоих "
                        "будущих проекта — отдельные репозитории с историей коммитов, которую "
                        "смотрят на собеседованиях.",
                "task": "Практика: создать репозиторий learning-log, коммитить туда заметки по каждому уроку",
                "links": [
                    {"title": "Pro Git — бесплатная книга целиком", "url": "https://git-scm.com/book/en/v2"},
                ],
            },
            {
                "id": "p0-3",
                "title": "Установка Python 3.14 и Go 1.26 на Debian",
                "text": "apt в Debian stable почти всегда отстаёт по версиям, поэтому Python ставим "
                        "через pyenv (менеджер версий, можно держать сразу несколько), а Go — "
                        "официальным tar.gz с go.dev, распаковав в /usr/local/go.",
                "task": "Практика: python3 --version и go version показывают актуальные версии",
                "links": [
                    {"title": "pyenv — официальный репозиторий и установка", "url": "https://github.com/pyenv/pyenv"},
                    {"title": "Go — страница загрузок (актуальные версии)", "url": "https://go.dev/dl/"},
                ],
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
             "text": "Числа, строки, булевы значения, приведение типов (int() / str() / float()), "
                     "input()/print(). Скучно, но без автоматизма здесь дальше будет тяжело.",
             "task": "Скрипт-конвертер единиц измерения (МБ↔ГБ, часы↔сек)",
             "links": [{"title": "The Python Tutorial — официальный учебник", "url": "https://docs.python.org/3/tutorial/introduction.html"}]},
            {"id": "p1-2", "title": "Условия и циклы (if/for/while)",
             "text": "if/elif/else, for по спискам и range(), while, break/continue. Это то, из чего "
                     "состоит логика почти любого скрипта.",
             "task": "Скрипт, проверяющий диапазон портов на «занятость» по номеру",
             "links": [{"title": "Control Flow — официальный туториал", "url": "https://docs.python.org/3/tutorial/controlflow.html"}]},
            {"id": "p1-3", "title": "Функции, аргументы, области видимости",
             "text": "def, позиционные/именованные аргументы, значения по умолчанию, return. "
                     "Плюс — что такое локальная и глобальная область видимости и почему это важно.",
             "task": "Функция форматирования байт в человекочитаемый вид (1024 → 1.0 KB)",
             "links": [{"title": "Defining Functions — официальный туториал", "url": "https://docs.python.org/3/tutorial/controlflow.html#defining-functions"}]},
            {"id": "p1-4", "title": "Структуры данных: list, dict, tuple, set",
             "text": "Это то, чем ты будешь оперировать 90% времени в DevOps-скриптах: списки серверов, "
                     "словари конфигов, множества уникальных IP.",
             "task": "Распарсить вывод df -h (как текст) в список словарей",
             "links": [{"title": "Data Structures — официальный туториал", "url": "https://docs.python.org/3/tutorial/datastructures.html"}]},
            {"id": "p1-5", "title": "Обработка ошибок: try/except, свои исключения",
             "text": "try/except/else/finally, конкретные типы исключений (не голый except:), "
                     "raise и создание собственных классов исключений.",
             "task": "Обернуть скрипт с диском так, чтобы он не падал, если путь не существует",
             "links": [{"title": "Errors and Exceptions — официальный туториал", "url": "https://docs.python.org/3/tutorial/errors.html"}]},
            {"id": "p1-6", "title": "Модули, пакеты, virtualenv/venv",
             "text": "Почему нельзя ставить всё через pip install глобально на сервере — сломает системный "
                     "Python (в Debian он используется системными утилитами). venv создаёт изолированную "
                     "копию интерпретатора для каждого проекта.",
             "task": "Создать venv, поставить requests, зафиксировать зависимости в requirements.txt",
             "links": [{"title": "venv — официальный туториал", "url": "https://docs.python.org/3/tutorial/venv.html"}]},
            {"id": "p1-7", "title": "Файлы, JSON, YAML",
             "text": "Чтение/запись файлов через with open(...), сериализация в JSON стандартным модулем "
                     "json, и YAML через сторонний пакет PyYAML (в стандартной библиотеке его нет).",
             "task": "Скрипт, читающий config.yaml с настройками (пороги алертов) и валидирующий его",
             "links": [
                 {"title": "json — официальная документация", "url": "https://docs.python.org/3/library/json.html"},
                 {"title": "PyYAML — Quick start", "url": "https://pyyaml.org/wiki/PyYAMLDocumentation"},
             ]},
            {"id": "p1-8", "title": "Минимальный ООП: классы, атрибуты, методы, dataclass",
             "text": "Ровно столько, чтобы понимать модели Pydantic в FastAPI: class, __init__, self, "
                     "и декоратор @dataclass, который сам генерирует __init__ по объявленным полям.",
             "task": "Класс ServerMetric(cpu, ram, disk, timestamp) через @dataclass",
             "links": [{"title": "dataclasses — официальная документация", "url": "https://docs.python.org/3/library/dataclasses.html"}]},
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
             "text": "subprocess.run() — рекомендованный способ вызвать внешнюю команду. Обязательно "
                     "с таймаутом (timeout=...) и без shell=True на непроверенных данных — иначе "
                     "это дыра для shell injection.",
             "task": "Обёртка вокруг systemctl status <service>, возвращающая True/False",
             "links": [
                 {"title": "subprocess — официальная документация", "url": "https://docs.python.org/3/library/subprocess.html"},
                 {"title": "Real Python: The subprocess Module", "url": "https://realpython.com/python-subprocess/"},
             ]},
            {"id": "p2-2", "title": "os / shutil / pathlib: файлы, права, диски",
             "text": "pathlib.Path — современный способ работать с путями (вместо os.path). "
                     "shutil.disk_usage() для места на диске, os.stat() для прав доступа.",
             "task": "Скрипт очистки старых логов (по возрасту файла) с dry-run режимом", "links": []},
            {"id": "p2-3", "title": "argparse: превращаем скрипт в нормальный CLI",
             "text": "add_argument(), позиционные и опциональные флаги, автоматический --help. "
                     "Это то, что отличает «скрипт для себя» от инструмента, которым может пользоваться кто-то ещё.",
             "task": "Добавить флаги --dry-run, --path, --days к скрипту очистки логов",
             "links": [{"title": "argparse — официальный туториал (HOWTO)", "url": "https://docs.python.org/3/howto/argparse.html"}]},
            {"id": "p2-4", "title": "logging вместо print()",
             "text": "Почему в проде это критично: уровни INFO/WARNING/ERROR, запись в файл, ротация, "
                     "возможность включить подробный DEBUG без правки кода.",
             "task": "Заменить все print в предыдущих скриптах на logging",
             "links": [{"title": "Logging HOWTO — официальная документация", "url": "https://docs.python.org/3/howto/logging.html"}]},
            {"id": "p2-5", "title": "requests: работа с REST API",
             "text": "GET/POST, заголовки, JSON в теле запроса, обработка кодов ответа и таймаутов "
                     "(requests без timeout может зависнуть навсегда).",
             "task": "Написать функцию отправки сообщения в Telegram через Bot API",
             "links": [
                 {"title": "requests — официальная документация", "url": "https://requests.readthedocs.io/en/latest/"},
                 {"title": "Telegram Bot API — метод sendMessage", "url": "https://core.telegram.org/bots/api#sendmessage"},
             ]},
            {"id": "p2-6", "title": "psutil: метрики системы (CPU/RAM/диск/сеть)",
             "text": "psutil.cpu_percent(), psutil.virtual_memory(), psutil.disk_usage() — кроссплатформенная "
                     "библиотека, которая читает те же /proc-данные, что и утилиты top/df, но отдаёт их питоновскими объектами.",
             "task": "Скрипт, печатающий текущую нагрузку каждые 5 секунд",
             "links": [{"title": "psutil — документация", "url": "https://psutil.readthedocs.io/en/latest/"}]},
            {"id": "p2-7", "title": "docker SDK для Python (docker-py)",
             "text": "docker.from_env(), client.containers.list(), чтение статуса health каждого контейнера "
                     "— то же самое, что делает docker ps, но программно.",
             "task": "Скрипт, находящий контейнеры в статусе unhealthy",
             "links": [{"title": "docker-py — документация", "url": "https://docker-py.readthedocs.io/en/stable/"}]},
            {"id": "p2-8", "title": "systemd unit + timer вместо cron",
             "text": "Разница: timer логируется в journalctl (journalctl -u имя.service), легче дебажить, "
                     "есть явные зависимости между юнитами (After=, Requires=) — то, чего у cron просто нет.",
             "task": "Обернуть скрипт метрик в systemd service + timer, запускающийся раз в минуту",
             "links": [{"title": "systemd/Timers — ArchWiki", "url": "https://wiki.archlinux.org/title/Systemd/Timers"}]},
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
             "text": "SQLite выбран сознательно: файл на диске, ноль настройки (не нужен отдельный "
                     "сервер БД), хватает с большим запасом при твоей нагрузке. sqlite3 — в стандартной "
                     "библиотеке Python, ничего доустанавливать не нужно.",
             "task": "Таблица metrics(ts, cpu, ram, disk), запись и выборка за период",
             "links": [{"title": "sqlite3 — официальная документация", "url": "https://docs.python.org/3/library/sqlite3.html"}]},
            {"id": "p3-2", "title": "SQLAlchemy (ORM) — по желанию",
             "text": "Либо остаёшься на чистом SQL — для проекта такого размера это абсолютно нормальный выбор.",
             "task": "", "links": []},
            {"id": "p3-3", "title": "FastAPI: первые роуты, Pydantic-модели, /docs",
             "text": "@app.get(...), автоматическая валидация входных данных через Pydantic-модели, "
                     "и бесплатная интерактивная документация на /docs, которую FastAPI строит сам.",
             "task": "GET /health, возвращающий {\"status\": \"ok\"}",
             "links": [{"title": "FastAPI — First Steps (офиц. туториал)", "url": "https://fastapi.tiangolo.com/tutorial/first-steps/"}]},
            {"id": "p3-4", "title": "CRUD-эндпоинты + async basics",
             "text": "async def и await — зачем это нужно веб-серверу (не блокировать один запрос, "
                     "пока ждём ответ от БД или другого сервиса).",
             "task": "GET /metrics?from=&to= с фильтрацией по датам из SQLite", "links": []},
            {"id": "p3-5", "title": "Dockerfile для Python-приложения + docker-compose",
             "text": "Multi-stage build, чтобы образ был лёгкий — важно при 1 ТБ и медленном 7200rpm диске: "
                     "меньше слоёв, меньше данных гонять при каждой пересборке.",
             "task": "Собрать образ FastAPI-приложения, поднять через docker-compose",
             "links": [{"title": "Docker — Best practices для Dockerfile", "url": "https://docs.docker.com/build/building/best-practices/"}]},
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
             "text": "Сбор метрик системы (psutil) и контейнеров (docker-py), запись в SQLite по расписанию "
                     "(тот самый systemd timer из фазы P2). Отдельный скрипт, независимый от веб-сервера.",
             "task": "", "links": []},
            {"id": "pr1-2", "title": "Milestone 2 — API-слой",
             "text": "FastAPI-эндпоинты для текущих и исторических метрик: GET /metrics/latest, "
                     "GET /metrics?from=&to=.",
             "task": "", "links": []},
            {"id": "pr1-3", "title": "Milestone 3 — пороги и алерты",
             "text": "Конфиг с порогами (disk > 90%, RAM > 90%), проверка при каждом сборе, Telegram "
                     "с антиспам-задержкой — иначе при затянувшейся проблеме бот будет слать сообщение каждую минуту.",
             "task": "",
             "links": [{"title": "Telegram Bot API — метод sendMessage", "url": "https://core.telegram.org/bots/api#sendmessage"}]},
            {"id": "pr1-4", "title": "Milestone 4 — мини-дашборд",
             "text": "Простая HTML/Chart.js страница, отдаваемая тем же FastAPI, либо Grafana поверх SQLite "
                     "(через community-плагин для SQLite-датасорса).",
             "task": "", "links": []},
            {"id": "pr1-5", "title": "Milestone 5 — упаковка и деплой",
             "text": "docker-compose (app + опционально nginx), деплой на Debian-сервер, автозапуск — "
                     "тот же паттерн, что ты уже проходил на трекере уроков.",
             "task": "", "links": []},
            {"id": "pr1-6", "title": "Milestone 6 — README для портфолио",
             "text": "Схема архитектуры, скриншот дашборда, «как запустить локально» — это то, что реально "
                     "читают на собеседовании, а не только сам код.",
             "task": "", "links": []},
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
             "text": "go mod init задаёт имя модуля, go.sum фиксирует версии зависимостей (аналог "
                     "requirements.txt, но с хэшами). go run для разработки, go build для готового бинарника.",
             "task": "hello-world как отдельный модуль с go.mod",
             "links": [{"title": "A Tour of Go — интерактивный туториал", "url": "https://go.dev/tour/welcome/1"}]},
            {"id": "g1-2", "title": "Базовые типы, переменные, константы, приведение типов",
             "text": "int/float64/string/bool, var и короткое объявление :=, const, явное приведение "
                     "типов (в Go оно всегда явное — неявных преобразований нет).",
             "task": "", "links": []},
            {"id": "g1-3", "title": "Срезы (slices) и карты (maps)",
             "text": "Аналоги list/dict из Python, но со своими нюансами: у среза есть length и capacity, "
                     "а обращение к несуществующему ключу карты не падает, а возвращает нулевое значение.",
             "task": "Переписать парсер df -h из P1 на Go",
             "links": [
                 {"title": "Go by Example: Slices", "url": "https://gobyexample.com/slices"},
                 {"title": "Go by Example: Maps", "url": "https://gobyexample.com/maps"},
             ]},
            {"id": "g1-4", "title": "Функции, множественный возврат значений",
             "text": "func f() (int, error) — идиома Go: функция почти всегда возвращает и результат, "
                     "и ошибку отдельным значением, а не бросает исключение.",
             "task": "", "links": []},
            {"id": "g1-5", "title": "Структуры (struct) и методы",
             "text": "struct — аналог класса без наследования; методы объявляются отдельно от структуры "
                     "через receiver: func (s *Server) IsHealthy() bool.",
             "task": "", "links": []},
            {"id": "g1-6", "title": "Интерфейсы: маленькие интерфейсы, много реализаций",
             "text": "В Go интерфейсы реализуются неявно — достаточно, чтобы у типа были нужные методы. "
                     "Идиоматично держать интерфейсы маленькими (1-2 метода).",
             "task": "",
             "links": [{"title": "Effective Go — интерфейсы", "url": "https://go.dev/doc/effective_go#interfaces"}]},
            {"id": "g1-7", "title": "Обработка ошибок в Go-стиле (if err != nil), пакет errors",
             "text": "Непривычно после try/except, но это стандарт индустрии для Go: ошибка — обычное "
                     "значение, которое явно проверяется сразу после вызова функции.",
             "task": "",
             "links": [{"title": "Effective Go — обработка ошибок", "url": "https://go.dev/doc/effective_go#errors"}]},
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
             "text": "go func() запускает горутину — лёгкий поток, управляемый рантаймом Go (их можно "
                     "запускать тысячами). channel — способ горутинам безопасно обмениваться данными.",
             "task": "Параллельно опросить 10 URL и собрать время ответа",
             "links": [
                 {"title": "Go by Example: Goroutines", "url": "https://gobyexample.com/goroutines"},
                 {"title": "Go by Example: Channels", "url": "https://gobyexample.com/channels"},
             ]},
            {"id": "g2-2", "title": "sync.WaitGroup, sync.Mutex — синхронизация горутин",
             "text": "WaitGroup — дождаться завершения группы горутин. Mutex — защитить общие данные "
                     "от одновременной записи из разных горутин (data race).",
             "task": "", "links": []},
            {"id": "g2-3", "title": "net/http: пишем HTTP-сервер с нуля",
             "text": "http.HandleFunc() и http.ListenAndServe() — полноценный веб-сервер в 10 строк "
                     "стандартной библиотеки, без единого внешнего пакета.",
             "task": "/health и /version эндпоинты",
             "links": [{"title": "net/http — официальная документация пакета", "url": "https://pkg.go.dev/net/http"}]},
            {"id": "g2-4", "title": "Кодирование JSON и текстовых форматов ответа",
             "text": "encoding/json — Marshal/Unmarshal, теги полей структуры (`json:\"name\"`), "
                     "которые определяют, как поле называется в итоговом JSON.",
             "task": "", "links": []},
            {"id": "g2-5", "title": "CLI-утилиты: flag или cobra, конфиг через флаги/env",
             "text": "Стандартного пакета flag хватает для простых утилит; cobra — то, на чём "
                     "построены kubectl, terraform, docker cli, если нужны подкоманды (app server, app fetch).",
             "task": "CLI с флагами --port, --interval",
             "links": [{"title": "Cobra — библиотека для CLI на Go", "url": "https://github.com/spf13/cobra"}]},
            {"id": "g2-6", "title": "Базовое тестирование: пакет testing, table-driven tests",
             "text": "Файлы *_test.go, функции TestXxx(t *testing.T), и идиома «табличных тестов» — "
                     "один тест-кейс проверяет сразу набор входных/ожидаемых значений в цикле. "
                     "Наличие тестов — весомый плюс в портфолио.",
             "task": "",
             "links": [{"title": "testing — официальная документация пакета", "url": "https://pkg.go.dev/testing"}]},
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
             "text": "HTTP-сервер на net/http, отдающий /metrics в текстовом формате экспозиции Prometheus "
                     "(это просто строки вида metric_name{label=\"value\"} 123 — никакой магии).",
             "task": "",
             "links": [{"title": "Prometheus — форматы экспозиции метрик", "url": "https://prometheus.io/docs/instrumenting/exposition_formats/"}]},
            {"id": "pr2-2", "title": "Milestone 2",
             "text": "Сбор системных метрик (CPU/RAM/диск) через чтение /proc на Linux напрямую, без внешних "
                     "зависимостей — /proc/stat, /proc/meminfo — это и есть источник данных для top/free.",
             "task": "", "links": []},
            {"id": "pr2-3", "title": "Milestone 3",
             "text": "Health-check модуль — параллельные (goroutines) проверки списка URL/портов из конфига, "
                     "с общим таймаутом и сбором результатов через channel.",
             "task": "", "links": []},
            {"id": "pr2-4", "title": "Milestone 4",
             "text": "CLI-конфигурация (флаги/YAML), нормальное логирование, graceful shutdown по SIGTERM — "
                     "чтобы docker stop не убивал процесс мгновенно, а давал время корректно закрыть соединения.",
             "task": "", "links": []},
            {"id": "pr2-5", "title": "Milestone 5 (stretch)",
             "text": "Через Docker Engine API — автоматический restart контейнера, если он unhealthy дольше "
                     "N минут. Тот же API, которым пользуется сам docker CLI.",
             "task": "",
             "links": [{"title": "Docker Engine API — Go client (pkg.go.dev)", "url": "https://pkg.go.dev/github.com/docker/docker/client"}]},
            {"id": "pr2-6", "title": "Milestone 6",
             "text": "Связка с VictoriaMetrics (лёгкая замена Prometheus, меньше требований к RAM) + Grafana "
                     "через docker-compose — тот же паттерн деплоя, что уже был в Проекте 1.",
             "task": "",
             "links": [{"title": "VictoriaMetrics — Quick Start", "url": "https://docs.victoriametrics.com/quick-start/"}]},
            {"id": "pr2-7", "title": "Milestone 7",
             "text": "README с архитектурной схемой и объяснением, зачем писать самому при наличии готового "
                     "node_exporter — ответ для собеседования: показать понимание internals, а не просто «умею запускать чужой бинарник».",
             "task": "", "links": []},
        ],
    },
    {
        "code": "p6",
        "track": "project",
        "title": "CI/CD и упаковка портфолио",
        "meta": "Недели 22–24 · ~13 ч",
        "why": "",
        "lessons": [
            {"id": "p6-1", "title": "Git-гигиена: осмысленные коммиты, .gitignore, ветки feature/*",
             "text": "Один коммит — одно логическое изменение, понятное сообщение (что и зачем, "
                     "а не «fix»). Это то, что смотрят при код-ревью на работе.",
             "task": "", "links": []},
            {"id": "p6-2", "title": "GitHub Actions: lint + тесты Python-проекта при каждом push",
             "text": "Workflow-файл в .github/workflows/*.yml, который автоматически запускает "
                     "flake8/pytest на каждый push — без ручного «а давай я перед пушем проверю».",
             "task": "",
             "links": [{"title": "Quickstart for GitHub Actions", "url": "https://docs.github.com/en/actions/get-started/quickstart"}]},
            {"id": "p6-3", "title": "GitHub Actions: build + go test для Go-проекта",
             "text": "Тот же принцип, что и для Python-workflow, но с actions/setup-go и go test ./... .",
             "task": "", "links": []},
            {"id": "p6-4", "title": "Сборка и публикация Docker-образов в GHCR",
             "text": "GitHub Container Registry (ghcr.io) — бесплатный реестр образов, привязанный "
                     "к твоему GitHub-аккаунту, логин через встроенный GITHUB_TOKEN без своих секретов.",
             "task": "",
             "links": [{"title": "GitHub Docs — Publishing Docker images", "url": "https://docs.github.com/actions/guides/publishing-docker-images"}]},
            {"id": "p6-5", "title": "Автодеплой на домашний сервер по SSH-ключу деплоя при пуше в main",
             "text": "Отдельный SSH-ключ только для деплоя (не твой личный), с ограниченными правами — "
                     "если ключ утечёт, урон ограничен.",
             "task": "", "links": []},
            {"id": "p6-6", "title": "Финальные README обоих проектов + описание для резюме",
             "text": "Что сделано, какой стек, какая проблема решена — 3-4 абзаца, которые можно "
                     "почти дословно перенести в резюме или сопроводительное письмо.",
             "task": "", "links": []},
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
