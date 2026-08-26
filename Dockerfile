# python:3.13-slim — стабильный, хорошо документированный образ.
# Не берём полный python:3.13 (там куча лишнего: компиляторы и т.д.),
# и не берём alpine — там другая libc (musl), из-за которой иногда
# ломаются бинарные зависимости; для личного проекта slim — золотая середина.
FROM python:3.13-slim

WORKDIR /app

# Сначала копируем ТОЛЬКО requirements.txt и ставим зависимости.
# Это осознанный порядок: Docker кэширует слои по содержимому файлов,
# и пока requirements.txt не меняется, шаг pip install не будет
# перевыполняться при каждой пересборке после правки кода — сборка быстрее.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Теперь копируем остальной код.
COPY . .

# Отдельная папка под файл SQLite — на неё будет примонтирован volume
# в docker-compose.yml, чтобы прогресс не терялся при пересборке образа.
RUN mkdir -p /app/db

# Запуск от root внутри контейнера — плохая практика (лишние права,
# если вдруг найдут уязвимость в приложении). Создаём отдельного юзера.
RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

ENV DB_PATH=/app/db/progress.db

EXPOSE 5000

# Docker будет сам проверять, жив ли сервис, дергая /healthz каждые 30 сек.
# Используем urllib из стандартной библиотеки Python, чтобы не тянуть
# в образ curl только ради healthcheck.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/healthz', timeout=2)" || exit 1

# gunicorn, а не встроенный flask-сервер: тот однопоточный и не
# предназначен для постоянной работы (см. предупреждение при "flask run").
# 2 воркера с запасом хватит на личный сайт при 3 ГБ RAM.
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
