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

// ---- сворачивающийся список фаз -------------------------------------------
// Ссылок на фазы тринадцать, и в липкой шапке они занимают до трёх строк.
// Поэтому ряд прячется сам: вниз по странице — свернулся, вверх — вернулся.
// Ручной режим это поведение перебивает целиком.
//
// Режим хранится в data-nav-mode на <html> и в localStorage["phase-nav"]:
//   auto   — по прокрутке (значение по умолчанию, в хранилище его нет);
//   shown  — всегда показан;
//   hidden — всегда скрыт.
// Свёрнут ли ряд прямо сейчас — это отдельный атрибут data-nav-collapsed.
// Оба выставляет ещё скрипт в <head>: ряд меняет высоту шапки, и делай мы это
// отсюда, при каждой загрузке страница дёргалась бы вверх (та же причина,
// по которой там же выставляется тема).

var NAV_MODES = ["auto", "shown", "hidden"];
var NAV_TITLES = {
  auto: "Список фаз: прячется при прокрутке вниз",
  shown: "Список фаз: всегда показан",
  hidden: "Список фаз: всегда скрыт",
};

// Порог в пикселях: мелкое дрожание прокрутки (тачпад, инерция телефона)
// не должно дёргать шапку туда-сюда.
var NAV_STEP = 10;

var navLastScrollY = 0;
var navTicking = false;
var navSuppressUntil = 0;   // пока идёт прыжок по якорю — прокрутку не слушаем

function getNavMode() {
  var mode = document.documentElement.getAttribute("data-nav-mode");
  return NAV_MODES.indexOf(mode) === -1 ? "auto" : mode;
}

function syncNavToggleUi() {
  var button = document.getElementById("nav-toggle");
  if (!button) return;

  var title = NAV_TITLES[getNavMode()];
  button.title = title;
  button.setAttribute("aria-label", title);
  button.setAttribute(
    "aria-expanded",
    document.documentElement.hasAttribute("data-nav-collapsed") ? "false" : "true"
  );
}

function setNavCollapsed(collapsed) {
  var root = document.documentElement;
  if (collapsed === root.hasAttribute("data-nav-collapsed")) return;

  if (collapsed) root.setAttribute("data-nav-collapsed", "");
  else root.removeAttribute("data-nav-collapsed");

  syncNavToggleUi();

  // Шапка стоит в обычном потоке, поэтому свернувшийся ряд укорачивает всю
  // страницу — а браузер на это может подвинуть прокрутку. Обработчик принял
  // бы такой сдвиг за движение пальца вверх и тут же развернул ряд обратно,
  // так что на время перехода перестаём слушать прокрутку.
  navSuppressUntil = Date.now() + 250;

  // Высота шапки поехала, а на ней держится scroll-margin-top у фаз. Точное
  // значение известно только после перехода — там его и меряем (см.
  // setupPhaseNav), здесь же обновляем на случай отключённых анимаций.
  syncHeaderOffset();
}

// Развернуть немедленно, без анимации: сразу после этого меряют высоту шапки,
// а в середине перехода она ещё старая. Отключение перехода нужно и тогда,
// когда ряд уже развёрнут: если анимация ещё идёт, transition: none обрывает
// её и высота сразу становится конечной — иначе замер попадёт в середину.
function expandNavInstantly() {
  var root = document.documentElement;

  root.setAttribute("data-nav-instant", "");
  root.removeAttribute("data-nav-collapsed");
  void document.body.offsetHeight; // заставляем браузер применить новую высоту
  root.removeAttribute("data-nav-instant");

  syncNavToggleUi();
}

function applyNavMode(mode, remember) {
  document.documentElement.setAttribute("data-nav-mode", mode);

  if (remember) {
    try {
      localStorage.setItem("phase-nav", mode);
    } catch (e) {
      // приватный режим: режим переключится, но не переживёт перезагрузку
    }
  }

  // При возврате в "авто" показываем ряд — дальше им управляет прокрутка.
  setNavCollapsed(mode === "hidden");
  navLastScrollY = window.pageYOffset;

  syncNavToggleUi();
}

function onNavScroll() {
  var y = window.pageYOffset;

  if (Date.now() < navSuppressUntil || getNavMode() !== "auto") {
    navLastScrollY = y;
    return;
  }

  // У самого верха страницы ряд всегда виден: прятать его там не от чего.
  if (y <= NAV_STEP) {
    setNavCollapsed(false);
    navLastScrollY = y;
    return;
  }

  var delta = y - navLastScrollY;
  // Точку отсчёта не двигаем, пока не набралось порога: так несколько мелких
  // шагов в одну сторону всё-таки сработают, а дрожание на месте — нет.
  if (Math.abs(delta) < NAV_STEP) return;

  setNavCollapsed(delta > 0);
  navLastScrollY = y;
}

function setupPhaseNav() {
  navLastScrollY = window.pageYOffset;
  syncNavToggleUi();

  var wrap = document.querySelector(".phase-nav-wrap");
  if (wrap) {
    wrap.addEventListener("transitionend", function (event) {
      if (event.propertyName === "grid-template-rows") syncHeaderOffset();
    });
  }

  var button = document.getElementById("nav-toggle");
  if (!button) return;

  // Одна кнопка на три состояния: авто -> всегда показан -> всегда скрыт.
  button.addEventListener("click", function () {
    var next = NAV_MODES[(NAV_MODES.indexOf(getNavMode()) + 1) % NAV_MODES.length];
    applyNavMode(next, true);
    // Переход длится --t; transitionend его и поймает, но при отключённых
    // анимациях события не будет — подстраховываемся таймером.
    setTimeout(syncHeaderOffset, 220);
  });
}

document.addEventListener("DOMContentLoaded", setupPhaseNav);

window.addEventListener(
  "scroll",
  function () {
    if (navTicking) return;
    navTicking = true;
    window.requestAnimationFrame(function () {
      navTicking = false;
      onNavScroll();
    });
  },
  { passive: true }
);

function openPhaseFromHash() {
  // Прыжок по якорю мы отмеряем от высоты шапки, поэтому она не должна
  // меняться прямо в этот момент: в режиме "авто" разворачиваем ряд фаз
  // мгновенно и на несколько сотен миллисекунд глушим реакцию на прокрутку
  // (сам scrollIntoView её тоже вызовет). Закреплённый вручную режим не
  // трогаем — там высота и так постоянная.
  navSuppressUntil = Date.now() + 400;
  if (getNavMode() === "auto") expandNavInstantly();

  syncHeaderOffset();

  const id = decodeURIComponent(location.hash.slice(1));
  if (!id) return;

  const details = document.getElementById(id);
  if (!details || details.tagName !== "DETAILS") return;

  details.open = true;
  details.scrollIntoView(); // учитывает scroll-margin-top, т.е. высоту шапки
  navLastScrollY = window.pageYOffset;
}

document.addEventListener("DOMContentLoaded", openPhaseFromHash);
window.addEventListener("hashchange", openPhaseFromHash);
window.addEventListener("resize", syncHeaderOffset);

// Переключатель "тёмная / светлая". Саму тему на <html> выставляет короткий
// скрипт в <head> (чтобы страница не моргала чужими цветами при загрузке),
// здесь остаётся только сам клик: перевернуть атрибут, запомнить выбор
// и подменить файл темы highlight.js.
//
// Записываем в localStorage только отсюда: пока пользователь не нажал кнопку,
// сайт должен следовать за настройкой ОС, а не за тем, какой она была
// в первый визит.
function setupThemeToggle() {
  var button = document.getElementById("theme-toggle");
  if (!button) return;

  button.addEventListener("click", function () {
    var next = document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", next);

    try {
      localStorage.setItem("theme", next);
    } catch (e) {
      // приватный режим или запрет на хранилище: тема переключится,
      // но не переживёт перезагрузку — это лучше, чем ошибка в консоли
    }

    var hl = document.getElementById("hl-theme");
    if (hl) hl.href = hl.getAttribute("data-" + next);
  });
}

document.addEventListener("DOMContentLoaded", setupThemeToggle);

// ---- кнопка «Копировать» у блоков кода ------------------------------------
// Конспекты — это в основном команды, которые нужно перенести в терминал,
// поэтому у каждого <pre><code> появляется своя кнопка. В разметке её нет:
// HTML конспекта приходит из Markdown, добавлять её туда пришлось бы на
// стороне сервера, разбирая готовый HTML.
//
// Каждый <pre> заворачивается в .code-block, и кнопка кладётся рядом с ним,
// а не внутрь: highlight.js переписывает содержимое <code> целиком и стёр бы
// всё, что лежит внутри, а <pre> к тому же прокручивается вбок — кнопка внутри
// него уезжала бы вместе с длинной строкой.
//
// Порядок с highlight.js неважен (он трогает только <code>), но на всякий
// случай есть и защита от повторного запуска: уже завёрнутый <pre> пропускаем,
// второй кнопки не появится.

// Кладёт текст в буфер обмена. navigator.clipboard есть только в защищённом
// контексте — то есть по https или на localhost. Сайт же чаще всего открыт
// в домашней сети по http://<ip>:8080, где этого API просто нет, поэтому
// запасной путь через execCommand("copy") здесь не перестраховка, а рабочий
// вариант для реального развёртывания.
function copyText(text) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    return navigator.clipboard.writeText(text);
  }

  return new Promise(function (resolve, reject) {
    var area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    // прячем поле за пределами экрана: оно нужно ровно на один вызов
    area.style.position = "fixed";
    area.style.top = "-1000px";
    document.body.appendChild(area);
    area.select();

    var ok = false;
    try { ok = document.execCommand("copy"); } catch (e) { ok = false; }

    document.body.removeChild(area);
    ok ? resolve() : reject(new Error("copy failed"));
  });
}

// Подпись кнопки возвращается к исходной через полторы секунды. Таймер живёт
// на самой кнопке: без этого частые клики оставили бы подпись висеть или,
// наоборот, сбросили бы её раньше времени.
function flashCopyLabel(button, label, isError) {
  button.textContent = label;
  button.classList.toggle("copied", !isError);

  clearTimeout(button._copyTimer);
  button._copyTimer = setTimeout(function () {
    button.textContent = "Копировать";
    button.classList.remove("copied");
  }, 1500);
}

function setupCodeCopy() {
  document.querySelectorAll(".lesson-content pre").forEach(function (pre) {
    if (pre.parentElement && pre.parentElement.classList.contains("code-block")) return;

    var wrap = document.createElement("div");
    wrap.className = "code-block";
    pre.parentNode.insertBefore(wrap, pre);
    wrap.appendChild(pre);

    var button = document.createElement("button");
    button.type = "button";
    button.className = "code-copy";
    button.textContent = "Копировать";
    button.setAttribute("aria-label", "Скопировать код в буфер обмена");
    wrap.appendChild(button);

    button.addEventListener("click", function () {
      // текст берём в момент клика, а не при создании кнопки: к этому времени
      // highlight.js уже перебрал <code>, да и разметка могла поменяться
      var code = pre.querySelector("code");
      var text = (code || pre).textContent;

      copyText(text)
        .then(function () { flashCopyLabel(button, "Скопировано!", false); })
        .catch(function () { flashCopyLabel(button, "Не удалось", true); });
    });
  });
}

document.addEventListener("DOMContentLoaded", setupCodeCopy);

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
