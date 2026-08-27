// Без этого файла сайт всё равно будет работать: каждый чекбокс лежит
// в обычной <form method="post">, так что при выключенном JS страница
// просто перезагрузится после клика. Этот скрипт — "улучшение поверх
// базовой версии": перехватывает отправку формы и обновляет страницу
// точечно, без мигания и потери прокрутки.

// Пересобирает карточку "Продолжить" на главной. Порядок <li> в DOM совпадает
// с порядком уроков в курсе (и то, и другое строится из PHASES), поэтому
// первый неотмеченный урок в документе — это ровно то же, что вернул бы
// find_continue_lesson() на сервере.
function refreshContinueCard() {
  const link = document.getElementById("continue-link");
  const doneCard = document.getElementById("continue-done");
  if (!link || !doneCard) return; // не главная страница — нечего обновлять

  const nextLi = document.querySelector("ul.lessons li[data-lesson-li]:not(.done)");
  if (!nextLi) {
    link.hidden = true;
    doneCard.hidden = false;
    return;
  }

  const titleLink = nextLi.querySelector(".lesson-title-link");
  if (!titleLink) return;

  link.href = titleLink.getAttribute("href");
  document.getElementById("continue-title").textContent = titleLink.textContent.trim();

  // цвет карточки — по треку той фазы, в которой лежит следующий урок
  const details = nextLi.closest("details.phase");
  const track = details ? (details.className.match(/track-[a-z]+/) || [])[0] : null;
  link.className = "continue-card" + (track ? " " + track : "");

  link.hidden = false;
  doneCard.hidden = true;
}

// Ссылки на фазы (шапка, хлебные крошки, кнопка "Список" на странице урока)
// ведут на якорь вида /#p1. Тут две проблемы, и обе решаются здесь:
// 1) по умолчанию сервер оставляет раскрытой только одну фазу — ту, где лежит
//    следующий урок, — так что переход по такой ссылке упирался бы в свёрнутый
//    блок;
// 2) шапка липкая, и штатный прыжок по якорю прячет заголовок фазы под ней.
//    Высоту шапки знает только браузер (она зависит от ширины экрана), поэтому
//    отдаём её в CSS переменной, а scroll-margin-top в style.css её подхватывает.
function syncHeaderOffset() {
  const header = document.querySelector(".topbar");
  if (!header) return;
  const offset = Math.round(header.getBoundingClientRect().height) + 10;
  document.documentElement.style.setProperty("--header-h", offset + "px");
}

function openPhaseFromHash() {
  syncHeaderOffset();

  const id = decodeURIComponent(location.hash.slice(1));
  if (!id) return;

  const details = document.getElementById(id);
  if (!details || details.tagName !== "DETAILS") return;

  details.open = true;
  details.scrollIntoView(); // учитывает scroll-margin-top, т.е. высоту шапки
}

document.addEventListener("DOMContentLoaded", openPhaseFromHash);
window.addEventListener("hashchange", openPhaseFromHash);
window.addEventListener("resize", syncHeaderOffset);

// Шаг урока (практика / пункт проверки). Отдельный обработчик, потому что
// ответ у /step другой: на общий прогресс курса эти галочки не влияют,
// обновлять шапку и счётчики фаз тут нечего.
function submitStepForm(form) {
  fetch(form.action, {
    method: "POST",
    headers: { "X-Requested-With": "fetch" },
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.error) return;

      const label = form.querySelector(".done-toggle span");
      if (label) label.textContent = data.done ? "Практика выполнена" : "Отметить практику";

      const li = form.closest("li[data-step-li]");
      if (li) li.classList.toggle("done", data.done);
    })
    .catch(() => {
      form.submit(); // сеть подвела — отправляем форму обычным способом
    });
}

document.addEventListener("submit", function (event) {
  const form = event.target;
  if (!form.classList.contains("toggle-form")) return;

  event.preventDefault(); // не даём браузеру перезагрузить страницу

  if (form.classList.contains("step-form")) {
    submitStepForm(form);
    return;
  }

  fetch(form.action, {
    method: "POST",
    // Этот заголовок Flask (см. app.py) использует, чтобы понять:
    // отвечать JSON-ом для JS, а не HTML-редиректом.
    headers: { "X-Requested-With": "fetch" },
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.error) return;

      // 1) визуально помечаем строку урока как выполненную/невыполненную
      const li = document.querySelector('[data-lesson-li="' + data.lesson_id + '"]');
      if (li) li.classList.toggle("done", data.done);

      // 2) обновляем шапку: общую цифру и полоску каждого трека
      document.getElementById("pct").textContent = data.percent + "%";
      document.getElementById("counts").textContent = data.total_done + "/" + data.total_all;
      (data.tracks || []).forEach(function (t) {
        const row = document.querySelector('.track-row[data-track="' + t.track + '"]');
        if (!row) return;
        row.querySelector(".bar-inner").style.width = t.percent + "%";
        row.querySelector(".track-count").textContent = t.done + "/" + t.total;
      });

      // 3) обновляем счётчик конкретной фазы (X/Y рядом с её заголовком)
      const phaseDetails = li ? li.closest("details.phase") : null;
      if (phaseDetails) {
        const doneInPhase = phaseDetails.querySelectorAll("ul.lessons li.done").length;
        const totalInPhase = phaseDetails.querySelectorAll("ul.lessons li").length;
        const badge = phaseDetails.querySelector(".ph-progress");
        if (badge) badge.textContent = doneInPhase + "/" + totalInPhase;
      }

      // 4) подпись у переключателя на странице урока
      const label = form.querySelector(".done-toggle span");
      if (label) label.textContent = data.done ? "Пройдено" : "Отметить пройденным";

      // 5) карточка "Продолжить" на главной не должна вести на только что
      //    закрытый урок
      refreshContinueCard();
    })
    .catch(() => {
      // Если сеть/сервер подвели — просто отправляем форму как обычно (без AJAX).
      form.submit();
    });
});
