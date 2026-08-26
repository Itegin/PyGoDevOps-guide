// Без этого файла сайт всё равно будет работать: каждый чекбокс лежит
// в обычной <form method="post">, так что при выключенном JS страница
// просто перезагрузится после клика. Этот скрипт — "улучшение поверх
// базовой версии": перехватывает отправку формы и обновляет страницу
// точечно, без мигания и потери прокрутки.

document.addEventListener("submit", function (event) {
  const form = event.target;
  if (!form.classList.contains("toggle-form")) return;

  event.preventDefault(); // не даём браузеру перезагрузить страницу

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

      // 2) обновляем общий прогресс-бар и счётчик в шапке
      document.getElementById("bar").style.width = data.percent + "%";
      document.getElementById("pct").textContent = data.percent + "%";
      document.getElementById("counts").textContent = data.total_done + "/" + data.total_all;

      // 3) обновляем счётчик конкретной фазы (X/Y рядом с её заголовком)
      const phaseDetails = li ? li.closest("details.phase") : null;
      if (phaseDetails) {
        const doneInPhase = phaseDetails.querySelectorAll("ul.lessons li.done").length;
        const totalInPhase = phaseDetails.querySelectorAll("ul.lessons li").length;
        const badge = phaseDetails.querySelector(".ph-progress");
        if (badge) badge.textContent = doneInPhase + "/" + totalInPhase;
      }
    })
    .catch(() => {
      // Если сеть/сервер подвели — просто отправляем форму как обычно (без AJAX).
      form.submit();
    });
});
