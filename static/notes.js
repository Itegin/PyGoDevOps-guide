// Автосохранение личной заметки к уроку (страница /lesson/<id>).
//
// Как и app.js, это "улучшение поверх базовой версии": сама заметка лежит
// в обычной <form method="post" action="/notes/<id>">, так что с выключенным
// JS кнопка "Сохранить" просто отправит форму и страница перезагрузится.
// Здесь мы перехватываем отправку и добавляем сохранение по ходу набора.

(function () {
  var area = document.getElementById("note-area");
  var status = document.getElementById("note-status");
  if (!area || !status) return; // не страница урока — выходим

  var form = area.form;
  var timer = null;
  // Текст, который заведомо лежит в БД. Нужен, чтобы не слать запрос, если
  // пользователь потыкал в textarea, но ничего не изменил.
  var savedValue = area.value;
  var DELAY = 800; // мс тишины после последнего нажатия клавиши

  function setStatus(text, cls) {
    status.textContent = text;
    status.className = "note-status" + (cls ? " " + cls : "");
  }

  function save() {
    // Отменяем отложенное сохранение: то, что мы отправляем сейчас, свежее.
    clearTimeout(timer);
    timer = null;

    var value = area.value;
    setStatus("Сохранение…");

    return fetch(form.action, {
      method: "POST",
      headers: {
        // Тот же заголовок, что и у чекбоксов: по нему Flask понимает,
        // что отвечать надо JSON-ом, а не редиректом (см. app.py).
        "X-Requested-With": "fetch",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ content: value }),
    })
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
      })
      .then(function (data) {
        if (!data.saved) throw new Error("not saved");
        savedValue = value;
        setStatus("Сохранено", "ok");
      })
      .catch(function () {
        // Молча терять заметку нельзя — она набита руками и нигде больше
        // не существует. Явно говорим, что текст остался только в браузере.
        setStatus("Не сохранено — нажмите «Сохранить»", "err");
      });
  }

  area.addEventListener("input", function () {
    if (area.value === savedValue) {
      // Вернулись к уже сохранённому тексту (например, Ctrl+Z) — запрос не нужен.
      clearTimeout(timer);
      timer = null;
      setStatus("Сохранено", "ok");
      return;
    }
    setStatus("Изменено…");
    clearTimeout(timer);
    timer = setTimeout(save, DELAY);
  });

  // Кнопка "Сохранить" — для тех, кто автосохранению не доверяет:
  // сохраняем сразу, не дожидаясь паузы в наборе.
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    save();
  });

  // Уход со страницы (в том числе по стрелкам "предыдущий/следующий")
  // не должен съедать текст, который ещё ждёт своей отправки.
  window.addEventListener("pagehide", function () {
    if (timer === null || area.value === savedValue) return;
    clearTimeout(timer);
    // fetch с keepalive переживает выгрузку страницы, в отличие от обычного.
    fetch(form.action, {
      method: "POST",
      headers: { "X-Requested-With": "fetch", "Content-Type": "application/json" },
      body: JSON.stringify({ content: area.value }),
      keepalive: true,
    }).catch(function () {});
  });
})();
