/* Логика страниц. Какая страница, определяем по <body data-page="..."> */

const img = (file) => `assets/img/${file}`;
const statsHTML = (items) => items.map(([value, label]) =>
  `<div class="stat"><p class="stat__value">${esc(value)}</p><p class="stat__label">${esc(label)}</p></div>`).join("");
const tagsHTML = (tags) => `<div class="tags">${tags.map((t) => `<span class="tag">${esc(t)}</span>`).join("")}</div>`;

/* ---------- новости ---------- */

function newsCardHTML(n) {
  return `
  <article class="news-card">
    <div class="news-card__img"><img src="${img(n.image || "news-1.webp")}" alt="" loading="lazy"></div>
    <div class="news-card__body">
      <div class="news-meta"><span class="tag">${esc(n.tag)}</span><time class="news-meta__date" datetime="${n.date}">${formatDate(n.date)}</time></div>
      <div>
        <h3 class="news-card__title">${esc(n.title)}</h3>
        <p class="news-card__text">${esc(n.text)}</p>
      </div>
      <a class="link-arrow" href="news.html?open=${encodeURIComponent(n.id)}" data-open-news="${esc(n.id)}">Читать ${ICONS.arrowRight}</a>
    </div>
  </article>`;
}

/* ---------- публикации ---------- */

function citation(p) {
  const year = p.date.slice(0, 4);
  return `${p.authors}. ${p.title}. ${p.journal}, ${year}. ${p.doi}`;
}

function pubHTML(p, index) {
  const dir = DIRECTIONS.find((d) => d.id === p.direction);
  const image = p.image
    ? `<img src="${img(p.image)}" alt="" loading="lazy">`
    : `<span class="pub__img-placeholder">${esc(p.journal)}</span>`;
  return `
  <article class="pub">
    <div class="pub__meta">
      <div class="pub__meta-left">
        <time class="pub__date" datetime="${p.date}">${formatDate(p.date)}</time>
        <span>${esc(p.journal)}</span>
        ${p.quartile ? `<span class="tag tag--outline">${esc(p.quartile)}</span>` : ""}
        ${dir ? `<a href="direction.html?id=${dir.id}">${esc(dir.title)}</a>` : ""}
      </div>
      <button class="pub__cite" type="button" data-cite="${index}">Цитировать ${ICONS.download}</button>
    </div>
    <div class="pub__main">
      <div class="pub__body">
        <div>
          <h3 class="pub__title"><a href="${esc(p.doi)}" target="_blank" rel="noopener">${esc(p.title)}</a></h3>
          <p class="pub__authors">${esc(p.authors)}</p>
        </div>
        <div class="pub__desc">${ICONS.chevronPoint}<p>${esc(p.desc)}</p></div>
        <div>
          <p class="pub__tags-title">Ключевые теги</p>
          ${tagsHTML(p.tags)}
        </div>
      </div>
      <div class="pub__img${p.image ? "" : " is-empty"}">
        ${image}
        <a class="pub__img-link" href="${esc(p.doi)}" target="_blank" rel="noopener">подробнее ${ICONS.arrowRight}</a>
      </div>
    </div>
  </article>`;
}

/* Список публикаций с переключателем «карточки / список» и кнопкой «показать еще» */
function mountPubList(root, getItems, { pageSize = Infinity } = {}) {
  const list = root.querySelector(".pub-list");
  const more = root.querySelector(".more");
  const toggle = root.querySelectorAll(".view-toggle__btn");
  let shown = pageSize;
  let items = [];

  let view = "cards";
  try { view = localStorage.getItem("pubView") || "cards"; } catch (e) { /* хранилище недоступно */ }
  const applyView = () => {
    list.classList.toggle("is-list", view === "list");
    toggle.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.view === view)));
  };
  toggle.forEach((b) => b.addEventListener("click", () => {
    view = b.dataset.view;
    try { localStorage.setItem("pubView", view); } catch (e) { /* ничего */ }
    applyView();
  }));
  applyView();

  list.addEventListener("click", async (e) => {
    const btn = e.target.closest("[data-cite]");
    if (!btn) return;
    const text = citation(items[Number(btn.dataset.cite)]);
    try {
      await navigator.clipboard.writeText(text);
      toast("Ссылка на статью скопирована");
    } catch (err) {
      window.prompt("Скопируйте ссылку на статью", text);
    }
  });

  const render = () => {
    items = getItems();
    const visible = items.slice(0, shown);
    list.innerHTML = visible.length
      ? visible.map(pubHTML).join("")
      : `<p class="empty">Ничего не найдено. Попробуйте изменить фильтры.</p>`;
    if (more) {
      more.hidden = items.length <= pageSize;
      more.querySelector(".more__count").textContent = `Показано ${visible.length} из ${items.length}`;
      more.querySelector("button").hidden = visible.length >= items.length;
    }
    return items;
  };
  more?.querySelector("button").addEventListener("click", () => { shown += pageSize; render(); });
  return {
    render,
    reset: () => { shown = pageSize; return render(); },
  };
}

function viewToggleHTML() {
  return `
  <div class="view-toggle" role="group" aria-label="Вид списка">
    <button class="view-toggle__btn" type="button" data-view="cards" aria-pressed="true">${ICONS.grid} Карточки</button>
    <button class="view-toggle__btn" type="button" data-view="list" aria-pressed="false">${ICONS.list} Список</button>
  </div>`;
}

/* ---------- главная ---------- */

function initHome() {
  const carousel = document.querySelector(".carousel");
  carousel.innerHTML = DIRECTIONS.map((d) => `
    <a class="dir-card" href="direction.html?id=${d.id}">
      <div class="dir-card__top">
        <h3 class="dir-card__title">${esc(d.title)}</h3>
        <div class="dir-card__row">
          <div class="dir-card__stats">${statsHTML([[d.team, "человек в команде"], [d.pubs, "публикаций"]])}</div>
          <span class="square-btn" aria-hidden="true">${ICONS.arrowUpRight}</span>
        </div>
      </div>
      <div class="dir-card__img"><img src="${img(d.image)}" alt="" loading="lazy" style="object-position:${d.imagePos || "center"}"></div>
    </a>`).join("");

  const [prev, next] = document.querySelectorAll(".slider-arrows .square-btn");
  const step = () => carousel.querySelector(".dir-card").getBoundingClientRect().width + 14;
  const update = () => {
    prev.disabled = carousel.scrollLeft < 4;
    next.disabled = carousel.scrollLeft + carousel.clientWidth >= carousel.scrollWidth - 4;
  };
  prev.addEventListener("click", () => carousel.scrollBy({ left: -step(), behavior: "smooth" }));
  next.addEventListener("click", () => carousel.scrollBy({ left: step(), behavior: "smooth" }));
  carousel.addEventListener("scroll", update, { passive: true });
  window.addEventListener("resize", update);
  update();

  document.querySelector(".news__grid").innerHTML = NEWS.filter((n) => !n.featured).slice(0, 3).map(newsCardHTML).join("");
}

/* ---------- направление ---------- */

function initDirection() {
  const id = new URLSearchParams(location.search).get("id");
  const d = DIRECTIONS.find((x) => x.id === id) || DIRECTIONS.find((x) => x.id === "puf");
  document.title = `${d.title} · ЦМТ «Мост»`;

  // фон первого экрана: своя обложка из макета, иначе фото с карточки направления
  document.querySelector(".hero__bg img").src = img(d.hero || d.image);
  document.querySelector(".hero__title").innerHTML = d.heroTitle || esc(d.title);
  document.querySelector(".hero__subtitle").textContent = d.subtitle || "Научное направление ЦМТ «Мост»";

  const about = document.querySelector(".dir-about");
  const text = d.about
    ? d.about.map((p) => `<p>${esc(p)}</p>`).join("")
    : `<p>Описание направления готовится. Пока можно написать нам, и мы расскажем о проектах команды.</p>`;
  const stats = [[d.team, plural(d.team, "человек", "человека", "человек") + " в команде"], [d.pubs, "публикаций"]];
  if (d.awards) stats.push([d.awards, "наград"]);
  if (d.conferences) stats.push([d.conferences, "конференций"]);
  about.querySelector(".dir-about__text").innerHTML = text;
  about.querySelector(".dir-stats").innerHTML = statsHTML(stats);
  about.querySelector(".dir-about__tags").innerHTML = d.tags ? tagsHTML(d.tags) : "";

  const people = document.querySelector(".people");
  if (d.people) {
    people.innerHTML = d.people.map((p) => `
      <figure class="person">
        <img src="${img(p.photo)}" alt="${esc(p.name)}" loading="lazy" style="object-position:${p.pos || "center"}">
        <figcaption class="person__text"><p class="person__name">${esc(p.name)}</p><p class="person__role">${esc(p.role)}</p></figcaption>
      </figure>`).join("");
  } else {
    people.remove();
  }

  const pubsSection = document.querySelector(".pubs");
  const pubs = PUBLICATIONS.filter((p) => p.direction === d.id).sort((a, b) => b.date.localeCompare(a.date));
  if (!pubs.length) { pubsSection.remove(); return; }
  pubsSection.querySelector(".view-toggle-slot").outerHTML = viewToggleHTML();
  mountPubList(pubsSection, () => pubs, { pageSize: 6 }).render();
}

/* ---------- все публикации ---------- */

function initPublications() {
  const form = document.querySelector(".filters");
  const q = form.querySelector("[name=q]");
  const dirSel = form.querySelector("[name=direction]");
  const yearSel = form.querySelector("[name=year]");
  const sortSel = form.querySelector("[name=sort]");
  const found = document.querySelector(".pubs__sub");

  const usedDirs = new Set(PUBLICATIONS.map((p) => p.direction));
  DIRECTIONS.filter((d) => usedDirs.has(d.id))
    .forEach((d) => dirSel.insertAdjacentHTML("beforeend", `<option value="${d.id}">${esc(d.title)}</option>`));
  [...new Set(PUBLICATIONS.map((p) => p.date.slice(0, 4)))].sort().reverse()
    .forEach((y) => yearSel.insertAdjacentHTML("beforeend", `<option value="${y}">${y}</option>`));

  const section = document.querySelector(".pubs");
  section.querySelector(".view-toggle-slot").outerHTML = viewToggleHTML();

  const getItems = () => {
    const term = q.value.trim().toLowerCase();
    const items = PUBLICATIONS.filter((p) =>
      (!term || `${p.title} ${p.authors} ${p.journal} ${p.tags.join(" ")}`.toLowerCase().includes(term)) &&
      (!dirSel.value || p.direction === dirSel.value) &&
      (!yearSel.value || p.date.startsWith(yearSel.value)));
    items.sort((a, b) => sortSel.value === "old" ? a.date.localeCompare(b.date) : b.date.localeCompare(a.date));
    return items;
  };
  const list = mountPubList(section, getItems, { pageSize: 6 });
  const update = () => {
    const n = list.reset().length;
    found.textContent = `Найдено ${n} ${plural(n, "работа", "работы", "работ")}`;
  };
  form.addEventListener("input", update);
  form.addEventListener("submit", (e) => e.preventDefault());
  form.querySelector(".filters__reset").addEventListener("click", () => { form.reset(); update(); });
  update();
}

/* ---------- новости ---------- */

function initNews() {
  const featured = NEWS.find((n) => n.featured);
  const rest = NEWS.filter((n) => !n.featured);
  const modal = document.querySelector(".modal");
  let lastFocus = null;

  const photo = (n) => n.image
    ? `<img src="${img(n.image)}" alt="" loading="lazy">`
    : "";

  if (featured) {
    document.querySelector(".featured__slot").outerHTML = `
      <button class="featured__card${featured.image ? "" : " no-image"}" type="button" data-open-news="${featured.id}">
        ${featured.image ? `<span class="featured__img">${photo(featured)}</span>` : ""}
        <span class="featured__body">
          <span class="news-meta"><span class="tag">${esc(featured.tag)}</span><time class="news-meta__date" datetime="${featured.date}">${formatDate(featured.date)}</time></span>
          <span class="featured__main">
            <span class="featured__title">${esc(featured.title)}</span>
            <span class="featured__text">${esc(featured.text)}</span>
          </span>
          <span class="link-arrow">Читать ${ICONS.arrowRight}</span>
        </span>
      </button>`;
  } else {
    document.querySelector(".featured").remove();
  }

  const grid = document.querySelector(".news-all .news__grid");
  const more = document.querySelector(".news-all .more");
  const total = document.querySelector(".news-all .pubs__sub");
  const pageSize = 6;
  let shown = pageSize;
  total.textContent = `Всего ${NEWS.length} ${plural(NEWS.length, "новость", "новости", "новостей")}`;
  const render = () => {
    grid.innerHTML = rest.slice(0, shown).map(newsCardHTML).join("");
    const visible = Math.min(shown, rest.length) + (featured ? 1 : 0);
    more.querySelector(".more__count").textContent = `Показано ${visible} из ${NEWS.length}`;
    more.querySelector("button").hidden = shown >= rest.length;
  };
  more.querySelector("button").addEventListener("click", () => { shown += pageSize; render(); });
  render();

  const open = (id) => {
    const n = NEWS.find((x) => x.id === id);
    if (!n) return;
    const b = n.body;
    modal.querySelector(".modal__img").innerHTML = photo({ image: n.popupImage || n.image });
    modal.querySelector(".modal__dialog").classList.toggle("no-image", !n.image);
    modal.querySelector(".modal__meta").innerHTML = `<span class="tag">${esc(n.tag)}</span><time class="news-meta__date" datetime="${n.date}">${formatDate(n.date)}</time>`;
    modal.querySelector(".modal__title").textContent = n.title;
    modal.querySelector(".modal__text").innerHTML = b
      ? `<p>${esc(b.lead)}</p>
         ${b.quote ? `<blockquote>${b.quote.map((q) => `<p>${esc(q)}</p>`).join("")}</blockquote>` : ""}
         ${b.note ? `<p class="note">${esc(b.note)}</p>` : ""}`
      : `<p>${esc(n.text)}</p>`;
    lastFocus = document.activeElement;
    modal.hidden = false;
    document.body.style.overflow = "hidden";
    modal.querySelector(".modal__close").focus();
    history.replaceState(null, "", `?open=${encodeURIComponent(id)}`);
  };
  const close = () => {
    modal.hidden = true;
    document.body.style.overflow = "";
    history.replaceState(null, "", location.pathname);
    lastFocus?.focus();
  };

  document.addEventListener("click", (e) => {
    const trigger = e.target.closest("[data-open-news]");
    if (trigger) { e.preventDefault(); open(trigger.dataset.openNews); }
  });
  modal.querySelector(".modal__close").addEventListener("click", close);
  modal.querySelector(".modal__backdrop").addEventListener("click", close);
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !modal.hidden) close(); });

  const requested = new URLSearchParams(location.search).get("open");
  if (requested) open(NEWS.some((n) => n.id === requested) ? requested : featured?.id);
}

document.addEventListener("DOMContentLoaded", () => {
  ({ home: initHome, direction: initDirection, publications: initPublications, news: initNews })[document.body.dataset.page]?.();
});
