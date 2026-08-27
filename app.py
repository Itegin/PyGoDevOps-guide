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
    """Создаёт таблицы, если их ещё нет, и добавляет строки для новых уроков
    (тех, что появились в lessons_data.py, но которых ещё нет в БД).
    INSERT OR IGNORE — безопасно вызывать при каждом старте приложения.

    CREATE TABLE IF NOT EXISTS отрабатывает и на уже развёрнутом progress.db:
    таблица notes просто добавляется рядом, ничего не переписывая."""
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
    # Личные заметки к урокам. В отличие от progress эту таблицу НЕ засеиваем
    # пустыми строками на все 56 уроков: отсутствие строки и есть "заметки нет",
    # так что 56 пустых записей были бы чистым мусором.
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (
            lesson_id  TEXT PRIMARY KEY,
            content    TEXT NOT NULL DEFAULT '',
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


def get_note(lesson_id):
    """Текст заметки к уроку. Нет строки в таблице — значит, заметки нет,
    возвращаем пустую строку (шаблону всё равно, а textarea будет пустой)."""
    conn = get_db()
    row = conn.execute("SELECT content FROM notes WHERE lesson_id = ?", (lesson_id,)).fetchone()
    conn.close()
    return row["content"] if row else ""


def get_noted_ids():
    """Множество id уроков, у которых есть непустая заметка — из него на
    главной рисуется пометка "✎" рядом с названием урока.
    Заметку из одних пробелов и переводов строк значком не помечаем; голый
    TRIM() в SQLite срезает только пробелы, поэтому список символов задан явно."""
    conn = get_db()
    rows = conn.execute(
        "SELECT lesson_id FROM notes "
        "WHERE TRIM(content, char(32) || char(9) || char(10) || char(13)) != ''"
    ).fetchall()
    conn.close()
    return {row["lesson_id"] for row in rows}


def get_progress_map():
    """Возвращает {lesson_id: True/False} — статус выполнения каждого урока."""
    conn = get_db()
    rows = conn.execute("SELECT lesson_id, done FROM progress").fetchall()
    conn.close()
    return {row["lesson_id"]: bool(row["done"]) for row in rows}


def build_phases_with_progress(progress=None):
    """Собирает данные для шаблона: фазы + уроки + флаг done у каждого урока
    + счётчики (сделано/всего) на каждую фазу.

    progress можно передать снаружи, если карта прогресса уже прочитана, —
    так страница урока обходится одним чтением БД вместо двух."""
    if progress is None:
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


def calc_percent(total_done, total_all):
    """Процент выполнения курса — то, что видно в шапке рядом с прогресс-баром."""
    return round((total_done / total_all) * 100) if total_all else 0


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


def find_continue_lesson(progress):
    """Первый по порядку курса урок, который ещё не отмечен пройденным —
    именно на него ведёт кнопка "Продолжить" на главной.
    Возвращает элемент FLAT_LESSONS или None, если пройдено вообще всё."""
    for entry in FLAT_LESSONS:
        if not progress.get(entry["lesson"]["id"], False):
            return entry
    return None


@app.route("/lesson/<lesson_id>")
def lesson_detail(lesson_id):
    phase, lesson, prev_entry, next_entry = find_lesson(lesson_id)
    if lesson is None:
        return "Урок не найден", 404

    progress = get_progress_map()
    done = progress.get(lesson_id, False)

    # Шапка (прогресс-бар, счётчики, навигация по фазам) живёт в base.html и
    # рисуется на каждой странице — значит, её данные нужны и здесь, иначе на
    # странице урока бар остаётся пустым, а список фаз — вообще не выводится.
    phases, total_done, total_all = build_phases_with_progress(progress)

    # extensions: fenced_code — блоки ```python ... ```; tables — таблицы;
    # sane_lists — списки ведут себя предсказуемо (частая боль ванильного markdown).
    content_md = CONTENT.get(lesson_id, "")
    content_html = md.markdown(
        content_md, extensions=["fenced_code", "tables", "sane_lists"]
    ) if content_md else ""

    return render_template(
        "lesson_detail.html",
        phases=phases,
        note_content=get_note(lesson_id),
        total_done=total_done,
        total_all=total_all,
        percent=calc_percent(total_done, total_all),
        phase=phase,
        lesson={**lesson, "done": done},
        content_html=content_html,
        prev_entry=prev_entry,
        next_entry=next_entry,
    )


@app.route("/")
def index():
    progress = get_progress_map()
    phases, total_done, total_all = build_phases_with_progress(progress)
    continue_entry = find_continue_lesson(progress)
    return render_template(
        "index.html",
        phases=phases,
        total_done=total_done,
        total_all=total_all,
        percent=calc_percent(total_done, total_all),
        continue_entry=continue_entry,
        noted_ids=get_noted_ids(),
        # Раскрытой по умолчанию оставляем только ту фазу, в которой лежит
        # следующий незакрытый урок: остальные свёрнуты, чтобы список не
        # растягивался на несколько экранов.
        open_phase=continue_entry["phase"]["code"] if continue_entry else None,
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


@app.route("/notes/<lesson_id>", methods=["POST"])
def save_note(lesson_id):
    """Сохраняет личную заметку к уроку (upsert: строка появляется в момент
    первого сохранения). Как и /toggle, работает в двух режимах: JSON для
    автосохранения из static/notes.js и обычная форма с редиректом —
    чтобы заметки можно было писать и с выключенным JS."""
    _, lesson, _, _ = find_lesson(lesson_id)
    if lesson is None:
        return jsonify({"error": "unknown lesson_id"}), 404

    is_fetch = request.headers.get("X-Requested-With") == "fetch"

    # silent=True — чтобы кривой/не-JSON body не превращался в 400 от Flask;
    # form-вариант нужен для отправки обычной формой без JS.
    data = request.get_json(silent=True) or {}
    content = data.get("content") if "content" in data else request.form.get("content")
    content = str(content or "")  # None недопустим: колонка NOT NULL

    now = datetime.now(timezone.utc).isoformat()
    conn = get_db()
    conn.execute(
        """
        INSERT INTO notes (lesson_id, content, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(lesson_id) DO UPDATE SET
            content = excluded.content,
            updated_at = excluded.updated_at
        """,
        (lesson_id, content, now),
    )
    conn.commit()
    conn.close()

    if is_fetch:
        return jsonify({"saved": True, "updated_at": now})

    return redirect(request.referrer or url_for("lesson_detail", lesson_id=lesson_id))


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
