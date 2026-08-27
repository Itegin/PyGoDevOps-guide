# -*- coding: utf-8 -*-
"""
roadmap-site — личный сайт-трекер для гайда Python+Go -> DevOps.

Стек: Flask + SQLite. Никакого фронтенд-фреймворка — рендерим HTML
на сервере через Jinja2, и это осознанный выбор для личного проекта:
меньше движущихся частей, меньше что может сломаться на слабом сервере.

Как это работает:
1. Контент гайда (фазы/уроки) лежит в data/lessons_data.py — обычный Python.
2. Состояние "отмечено / не отмечено" лежит в SQLite (файл progress.db).
3. При каждом запросе на "/" мы читаем контент из lessons_data.py,
   подмешиваем к нему состояние из БД и считаем проценты выполнения.
"""

import os
import sqlite3
from datetime import datetime, timezone

import markdown as md
from flask import Flask, render_template, redirect, url_for, request, jsonify

from data.lessons_data import PHASES, all_lesson_ids
from data.lesson_content import CONTENT

app = Flask(__name__)

# Путь к файлу БД можно переопределить переменной окружения — это нужно,
# чтобы в Docker её можно было держать на смонтированном volume
# (иначе прогресс будет теряться при пересборке контейнера).
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "progress.db"))


def get_db():
    """Одно соединение с SQLite на запрос. check_same_thread=False нужен,
    потому что gunicorn/flask могут дёргать это из разных потоков."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # позволяет обращаться к колонкам по имени: row["done"]
    return conn


def init_db():
    """Создаёт таблицу, если её ещё нет, и добавляет строки для новых уроков
    (тех, что появились в lessons_data.py, но которых ещё нет в БД).
    INSERT OR IGNORE — безопасно вызывать при каждом старте приложения."""
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS progress (
            lesson_id  TEXT PRIMARY KEY,
            done       INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT
        )
        """
    )
    conn.executemany(
        "INSERT OR IGNORE INTO progress (lesson_id, done) VALUES (?, 0)",
        [(lid,) for lid in all_lesson_ids()],
    )
    conn.commit()
    conn.close()


def get_progress_map():
    """Возвращает {lesson_id: True/False} — статус выполнения каждого урока."""
    conn = get_db()
    rows = conn.execute("SELECT lesson_id, done FROM progress").fetchall()
    conn.close()
    return {row["lesson_id"]: bool(row["done"]) for row in rows}


def build_phases_with_progress():
    """Собирает данные для шаблона: фазы + уроки + флаг done у каждого урока
    + счётчики (сделано/всего) на каждую фазу."""
    progress = get_progress_map()
    phases = []
    total_done, total_all = 0, 0

    for phase in PHASES:
        lessons = []
        phase_done = 0
        for lesson in phase["lessons"]:
            done = progress.get(lesson["id"], False)
            lessons.append({**lesson, "done": done})
            if done:
                phase_done += 1
        phases.append({
            **phase,
            "lessons": lessons,
            "phase_done": phase_done,
            "phase_total": len(lessons),
        })
        total_done += phase_done
        total_all += len(lessons)

    return phases, total_done, total_all


# Плоский список уроков в порядке прохождения курса — считаем один раз при
# старте (PHASES не меняется во время работы процесса), нужен для кнопок
# "← предыдущий / следующий →" на странице урока, как в курсах на Stepik.
def _build_flat_lessons():
    flat = []
    for phase in PHASES:
        for lesson in phase["lessons"]:
            flat.append({"phase": phase, "lesson": lesson})
    return flat


FLAT_LESSONS = _build_flat_lessons()


def find_lesson(lesson_id):
    """Возвращает (phase, lesson, prev_entry, next_entry) или (None, None, None, None)."""
    for i, entry in enumerate(FLAT_LESSONS):
        if entry["lesson"]["id"] == lesson_id:
            prev_entry = FLAT_LESSONS[i - 1] if i > 0 else None
            next_entry = FLAT_LESSONS[i + 1] if i < len(FLAT_LESSONS) - 1 else None
            return entry["phase"], entry["lesson"], prev_entry, next_entry
    return None, None, None, None


@app.route("/lesson/<lesson_id>")
def lesson_detail(lesson_id):
    phase, lesson, prev_entry, next_entry = find_lesson(lesson_id)
    if lesson is None:
        return "Урок не найден", 404

    done = get_progress_map().get(lesson_id, False)

    # extensions: fenced_code — блоки ```python ... ```; tables — таблицы;
    # sane_lists — списки ведут себя предсказуемо (частая боль ванильного markdown).
    content_md = CONTENT.get(lesson_id, "")
    content_html = md.markdown(
        content_md, extensions=["fenced_code", "tables", "sane_lists"]
    ) if content_md else ""

    return render_template(
        "lesson_detail.html",
        phase=phase,
        lesson={**lesson, "done": done},
        content_html=content_html,
        prev_entry=prev_entry,
        next_entry=next_entry,
    )


@app.route("/")
def index():
    phases, total_done, total_all = build_phases_with_progress()
    percent = round((total_done / total_all) * 100) if total_all else 0
    return render_template(
        "index.html",
        phases=phases,
        total_done=total_done,
        total_all=total_all,
        percent=percent,
    )


@app.route("/toggle/<lesson_id>", methods=["POST"])
def toggle(lesson_id):
    """Переключает урок done <-> не done.
    Отвечает JSON, если запрос пришёл через fetch() из нашего JS
    (см. static/app.js), иначе просто редиректит обратно на страницу —
    так форма работает и с выключенным JS."""
    conn = get_db()
    row = conn.execute("SELECT done FROM progress WHERE lesson_id = ?", (lesson_id,)).fetchone()
    if row is None:
        conn.close()
        return jsonify({"error": "unknown lesson_id"}), 404

    new_done = 0 if row["done"] else 1
    conn.execute(
        "UPDATE progress SET done = ?, updated_at = ? WHERE lesson_id = ?",
        (new_done, datetime.now(timezone.utc).isoformat(), lesson_id),
    )
    conn.commit()
    conn.close()

    if request.headers.get("X-Requested-With") == "fetch":
        _, total_done, total_all = build_phases_with_progress()
        percent = round((total_done / total_all) * 100) if total_all else 0
        return jsonify({
            "lesson_id": lesson_id,
            "done": bool(new_done),
            "total_done": total_done,
            "total_all": total_all,
            "percent": percent,
        })

    return redirect(request.referrer or url_for("index"))


@app.route("/reset", methods=["POST"])
def reset():
    """Сбрасывает весь прогресс. Отдельная кнопка в шаблоне спрашивает
    подтверждение через confirm() на стороне браузера перед отправкой."""
    conn = get_db()
    conn.execute("UPDATE progress SET done = 0, updated_at = NULL")
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/healthz")
def healthz():
    """Простой health-check эндпоинт — пригодится и для Docker healthcheck,
    и это ровно тот паттерн, который встретится в проекте 1 из гайда."""
    return jsonify({"status": "ok"})


# init_db() должен отработать один раз при старте процесса — что при
# локальном "flask run", что под gunicorn в контейнере.
init_db()

if __name__ == "__main__":
    # Используется только для локальной разработки (flask run / python app.py).
    # В Docker-образе процесс запускается через gunicorn (см. Dockerfile).
    app.run(host="0.0.0.0", port=5000, debug=True)
