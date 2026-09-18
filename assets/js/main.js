/* Логика страниц. Какая страница, определяем по <body data-page="..."> */

const img = (file) => `assets/img/${file}`;
// незаполненные метрики пропускаем: лучше показать меньше цифр, чем выдуманные
const statsHTML = (items) => items.filter(([value]) => value).map(([value, label]) =>
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

/* Библиографические данные: из citations.js (Crossref), а если публикации там нет, из data.js */
function refOf(p) {
  // у статей в российских журналах DOI бывает не присвоен, цитата тогда собирается из data.js
  const doi = (p.doi || "").replace(/^https?:\/\/doi\.org\//, "");
  const c = doi && window.CITATIONS?.[doi];
  if (c) return { ...c, doi };
  return {
    type: "journal-article", doi, title: p.title, container: p.journal, year: Number(p.date.slice(0, 4)),
    authors: p.authors.split(/,\s*/).map((name) => {
      const parts = name.trim().split(/\s+/);
      // «Kustov P.» — фамилия первой, «Pavel Kustov» — последней
      return /\.$/.test(parts[parts.length - 1]) ? [parts[0], parts.slice(1).join(" ")] : [parts.pop(), parts.join(" ")];
    }),
  };
}

const initials = (given, sep = " ") => given.split(/[\s.]+/).filter(Boolean)
  .map((g) => g.split("-").map((x) => `${x[0]}.`).join("-")).join(sep);
const isConf = (r) => r.type === "proceedings-article";

/* Форматы как в Google Scholar. Возвращают HTML, поэтому получают данные с уже экранированными строками */
const CITE_STYLES = {
  "ГОСТ": (r) => {
    const a = r.authors;
    const who = a.length > 3
      ? `${a[0][0]} ${initials(a[0][1])} et al.`
      : a.map(([f, g]) => `${f} ${initials(g)}`).join(", ");
    const pages = r.page ? ` – С. ${r.page}.` : "";
    return isConf(r)
      ? `${who} ${r.title} //${r.container}. – ${r.publisher ? `${r.publisher}, ` : ""}${r.year}.${pages}`
      : `${who} ${r.title} //${r.container}. – ${r.year}.${r.volume ? ` – Т. ${r.volume}.` : ""}${r.issue ? ` – №. ${r.issue}.` : ""}${pages}`;
  },
  MLA: (r) => {
    const a = r.authors;
    const first = `${a[0][0]}, ${a[0][1]}`;
    const who = a.length === 1 ? first : a.length === 2 ? `${first}, and ${a[1][1]} ${a[1][0]}` : `${first}, et al`;
    const ends = (s) => (/[.?!]$/.test(s) ? s : `${s}.`);
    return isConf(r)
      ? `${ends(who)} "${ends(r.title)}" <i>${r.container}</i>. ${r.publisher ? `${r.publisher}, ` : ""}${r.year}.`
      : `${ends(who)} "${ends(r.title)}" <i>${r.container}</i>${r.volume ? ` ${r.volume}${r.issue ? `.${r.issue}` : ""}` : ""} (${r.year})${r.page ? `: ${r.page}` : ""}.`;
  },
  APA: (r) => {
    const names = r.authors.map(([f, g]) => `${f}, ${initials(g)}`);
    const who = names.length === 1 ? names[0]
      : names.length <= 7 ? `${names.slice(0, -1).join(", ")}, & ${names[names.length - 1]}`
      : `${names.slice(0, 6).join(", ")}, ... & ${names[names.length - 1]}`;
    return isConf(r)
      ? `${who} (${r.year}). ${r.title}. In <i>${r.container}</i>${r.page ? ` (pp. ${r.page})` : ""}.${r.publisher ? ` ${r.publisher}.` : ""}`
      : `${who} (${r.year}). ${r.title}. <i>${r.container}</i>${r.volume ? `, <i>${r.volume}</i>${r.issue ? `(${r.issue})` : ""}` : ""}${r.page ? `, ${r.page}` : ""}.`;
  },
};

/* Файлы для менеджеров библиографии */
const pageSplit = (page = "") => page.split("-");
const citeKey = (r) => `${(r.authors[0]?.[0] || "ref").replace(/[^A-Za-z]/g, "")}${r.year}${(r.title.match(/[A-Za-z]{4,}/) || ["paper"])[0].toLowerCase()}`;
const CITE_EXPORTS = {
  BibTeX: { ext: "bib", type: "application/x-bibtex", build: (r) => {
    const f = [
      ["title", r.title], ["author", r.authors.map(([f, g]) => `${f}, ${g}`).join(" and ")],
      [isConf(r) ? "booktitle" : "journal", r.container], ["volume", r.volume], ["number", r.issue],
      ["pages", r.page && r.page.replace("-", "--")], ["year", r.year], ["publisher", r.publisher], ["doi", r.doi],
    ].filter(([, v]) => v);
    return `@${isConf(r) ? "inproceedings" : "article"}{${citeKey(r)},\n${f.map(([k, v]) => `  ${k}={${v}}`).join(",\n")}\n}\n`;
  } },
  EndNote: { ext: "enw", type: "application/x-endnote-refer", build: (r) => [
    `%0 ${isConf(r) ? "Conference Proceedings" : "Journal Article"}`, `%T ${r.title}`,
    ...r.authors.map(([f, g]) => `%A ${f}, ${g}`), `%${isConf(r) ? "B" : "J"} ${r.container}`,
    r.volume && `%V ${r.volume}`, r.issue && `%N ${r.issue}`, r.page && `%P ${r.page}`,
    `%D ${r.year}`, r.publisher && `%I ${r.publisher}`, `%R ${r.doi}`,
  ].filter(Boolean).join("\n") + "\n" },
  RefMan: { ext: "ris", type: "application/x-research-info-systems", build: (r) => {
    const [sp, ep] = pageSplit(r.page);
    return [
      `TY  - ${isConf(r) ? "CONF" : "JOUR"}`, `TI  - ${r.title}`, ...r.authors.map(([f, g]) => `AU  - ${f}, ${g}`),
      `T2  - ${r.container}`, r.volume && `VL  - ${r.volume}`, r.issue && `IS  - ${r.issue}`,
      sp && `SP  - ${sp}`, ep && `EP  - ${ep}`, `PY  - ${r.year}`, r.publisher && `PB  - ${r.publisher}`,
      `DO  - ${r.doi}`, "ER  - ",
    ].filter(Boolean).join("\r\n") + "\r\n";
  } },
  RefWorks: { ext: "txt", type: "text/plain", build: (r) => {
    const [sp, ep] = pageSplit(r.page);
    return [
      `RT ${isConf(r) ? "Conference Proceedings" : "Journal Article"}`, ...r.authors.map(([f, g]) => `A1 ${f}, ${g}`),
      `T1 ${r.title}`, `${isConf(r) ? "T2" : "JF"} ${r.container}`, r.volume && `VO ${r.volume}`, r.issue && `IS ${r.issue}`,
      sp && `SP ${sp}`, ep && `OP ${ep}`, `YR ${r.year}`, r.publisher && `PB ${r.publisher}`, `DO ${r.doi}`,
    ].filter(Boolean).join("\n") + "\n";
  } },
};

function downloadFile(name, type, text) {
  const url = URL.createObjectURL(new Blob([text], { type: `${type};charset=utf-8` }));
  const a = Object.assign(document.createElement("a"), { href: url, download: name });
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function openCiteSheet(p) {
  const r = refOf(p);
  const safe = { ...r, title: esc(r.title), container: esc(r.container), publisher: esc(r.publisher),
    authors: r.authors.map(([f, g]) => [esc(f), esc(g)]) };
  const rows = Object.entries(CITE_STYLES).map(([name, fmt]) => `
    <div class="cite__row">
      <p class="cite__style">${name}</p>
      <p class="cite__text">${fmt(safe)}</p>
      <button class="cite__copy" type="button" data-copy-style="${name}" aria-label="Скопировать ${name}"><span class="copy-label">копировать</span></button>
    </div>`).join("");
  const exports = Object.keys(CITE_EXPORTS).map((k) => `<button class="cite__export" type="button" data-export="${k}">${k}</button>`).join("");
  const dlg = openSheet("Цитировать", `<div class="cite__rows">${rows}</div><div class="cite__exports">${exports}</div>`, "sheet--cite");
  dlg.querySelector(".sheet__body").onclick = (e) => {
    const copy = e.target.closest("[data-copy-style]");
    // неразрывные пробелы от типографики сайта в скопированную цитату не нужны
    if (copy) copyText(copy.closest(".cite__row").querySelector(".cite__text").textContent.replace(/ /g, " "), copy);
    const exp = e.target.closest("[data-export]");
    if (exp) {
      const x = CITE_EXPORTS[exp.dataset.export];
      downloadFile(`${citeKey(r)}.${x.ext}`, x.type, x.build(r));
    }
  };
}

// одна работа может относиться сразу к нескольким направлениям, поэтому direction бывает и списком
const pubDirs = (p) => (Array.isArray(p.direction) ? p.direction : p.direction ? [p.direction] : []);

function pubHTML(p, index) {
  const dirs = pubDirs(p).map((id) => DIRECTIONS.find((d) => d.id === id)).filter(Boolean);
  const image = p.image
    ? `<img src="${img(p.image)}" alt="" loading="lazy">`
    : `<span class="pub__img-placeholder">${esc(p.journal)}</span>`;
  // у статей в российских журналах DOI бывает не присвоен, тогда ссылок нет
  const title = p.doi
    ? `<a href="${esc(p.doi)}" target="_blank" rel="noopener">${esc(p.title)}</a>`
    : esc(p.title);
  return `
  <article class="pub">
    <div class="pub__meta">
      <div class="pub__meta-left">
        <time class="pub__date" datetime="${p.date}">${formatDate(p.date)}</time>
        <span>${esc(p.journal)}</span>
        ${p.quartile ? `<span class="tag tag--outline">${esc(p.quartile)}</span>` : ""}
        ${dirs.map((d) => `<a href="direction.html?id=${d.id}">${esc(d.title)}</a>`).join("")}
      </div>
      <button class="pub__cite" type="button" data-cite="${index}" aria-haspopup="dialog"><span>Цитировать</span>${ICONS.download}</button>
    </div>
    <div class="pub__main">
      <div class="pub__body">
        <div>
          <h3 class="pub__title">${title}</h3>
          <p class="pub__authors">${esc(p.authors)}</p>
        </div>
        ${p.desc ? `<div class="pub__desc">${ICONS.chevronPoint}<p>${esc(p.desc)}</p></div>` : ""}
        ${p.tags && p.tags.length ? `<div>
          <p class="pub__tags-title">Ключевые теги</p>
          ${tagsHTML(p.tags)}
        </div>` : ""}
      </div>
      <div class="pub__img${p.image ? "" : " is-empty"}">
        ${image}
        ${p.doi ? `<a class="pub__img-link" href="${esc(p.doi)}" target="_blank" rel="noopener">подробнее ${ICONS.arrowRight}</a>` : ""}
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

  list.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-cite]");
    if (btn) openCiteSheet(items[Number(btn.dataset.cite)]);
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

/* ---------- горизонтальные ленты (направления на главной, команда направления) ---------- */

/* Стрелки листают ленту на одну карточку, гаснут на краях и прячутся, если всё помещается в экран */
function mountSlider(track, arrows, itemSel) {
  const [prev, next] = arrows.querySelectorAll(".square-btn");
  const step = () => {
    const [a, b] = track.querySelectorAll(itemSel);
    return b ? b.getBoundingClientRect().left - a.getBoundingClientRect().left : track.clientWidth;
  };
  const update = () => {
    arrows.hidden = track.scrollWidth <= track.clientWidth + 4;
    prev.disabled = track.scrollLeft < 4;
    next.disabled = track.scrollLeft + track.clientWidth >= track.scrollWidth - 4;
  };
  prev.addEventListener("click", () => track.scrollBy({ left: -step(), behavior: "smooth" }));
  next.addEventListener("click", () => track.scrollBy({ left: step(), behavior: "smooth" }));
  track.addEventListener("scroll", update, { passive: true });
  window.addEventListener("resize", update);
  update();
}

/* Перетаскивание ленты мышью (на телефоне и тачпаде прокрутка и так работает) */
function enableDragScroll(track) {
  let startX = 0, startLeft = 0, dragging = false, moved = false;
  track.addEventListener("pointerdown", (e) => {
    if (e.pointerType !== "mouse" || e.button !== 0) return;
    dragging = true; moved = false; startX = e.clientX; startLeft = track.scrollLeft;
    track.classList.add("is-dragging");
    track.setPointerCapture(e.pointerId);
  });
  track.addEventListener("pointermove", (e) => {
    if (!dragging) return;
    const dx = e.clientX - startX;
    if (Math.abs(dx) > 4) moved = true;
    track.scrollLeft = startLeft - dx;
  });
  const stop = () => {
    if (!dragging) return;
    dragging = false;
    track.classList.remove("is-dragging");
  };
  track.addEventListener("pointerup", stop);
  track.addEventListener("pointercancel", stop);
  // после перетаскивания не срабатывает клик по карточке
  track.addEventListener("click", (e) => { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
  track.addEventListener("dragstart", (e) => e.preventDefault());
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
      <div class="dir-card__img${d.image ? "" : " is-empty"}">${d.image ? `<img src="${img(d.image)}" alt="" loading="lazy" style="object-position:${d.imagePos || "center"}">` : ""}</div>
    </a>`).join("");

  mountSlider(carousel, document.querySelector(".science .slider-arrows"), ".dir-card");

  document.querySelector(".news__grid").innerHTML = NEWS.filter((n) => !n.featured).slice(0, 3).map(newsCardHTML).join("");
}

/* ---------- направление ---------- */

/* Порядок команды на странице направления: доктора наук, кандидаты наук, аспиранты,
   магистры, студенты, бакалавры. Внутри ступени раньше идет тот, кто старше по курсу
   (аспирант 4-го года выше аспиранта 1-го). Сортировка живет здесь, а не в data.js,
   чтобы правило соблюдалось само при любой правке состава. */
const STAGES = [[/доктор/i, 10], [/кандидат/i, 20], [/аспирант/i, 30], [/магистр/i, 40], [/студент/i, 50], [/бакалавр/i, 60]];

function personRank(degree = "") {
  const stage = STAGES.find(([re]) => re.test(degree));
  if (!stage) return 90;
  const year = Number((degree.match(/(\d)-го года/) || [])[1]);
  // курс старше — выше в списке; если курс не указан, ставим в конец своей ступени
  return stage[1] + (year ? 5 - year : 5);
}

function teamOf(d) {
  return d.people
    .map((name) => ({ name, ...(window.PEOPLE?.[name] || {}) }))
    .map((p) => ({ ...p, role: [p.degree, p.post].filter(Boolean).join(", ") }))
    .sort((a, b) => personRank(a.degree) - personRank(b.degree));
}

function initDirection() {
  const id = new URLSearchParams(location.search).get("id");
  const d = DIRECTIONS.find((x) => x.id === id) || DIRECTIONS.find((x) => x.id === "puf");
  document.title = `${d.title} · ЦМТ «Мост»`;

  // фон первого экрана: своя обложка из макета, иначе фото с карточки направления
  // у направлений без своей картинки фоном идет общий первый экран сайта
  document.querySelector(".hero__bg img").src = img(d.hero || d.image || "hero-home.webp");
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
  // тема письма из карточки-приглашения: сразу видно, по какому направлению запрос
  about.querySelector(".dir-cta__btn").dataset.writeSubject = `Совместная работа: ${d.title}`;
  about.querySelector(".dir-stats").innerHTML = statsHTML(stats);
  about.querySelector(".dir-about__tags").innerHTML = d.tags ? tagsHTML(d.tags) : "";

  const people = document.querySelector(".people");
  if (d.people) {
    // фотография есть не у всех: без нее карточка остается плашкой фирменного цвета
    people.innerHTML = teamOf(d).map((p) => `
      <figure class="person${p.photo ? "" : " person--plain"}">
        ${p.photo ? `<img src="${img(p.photo)}" alt="${esc(p.name)}" loading="lazy" style="object-position:${p.pos || "center"}">` : ""}
        <figcaption class="person__text"><p class="person__name">${esc(p.name)}</p>${p.role ? `<p class="person__role">${esc(p.role)}</p>` : ""}</figcaption>
      </figure>`).join("");
    mountSlider(people, document.querySelector(".people-head .slider-arrows"), ".person");
    enableDragScroll(people);
  } else {
    people.remove();
    document.querySelector(".people-head").remove();
  }

  const pubsSection = document.querySelector(".pubs");
  const pubs = PUBLICATIONS.filter((p) => pubDirs(p).includes(d.id)).sort((a, b) => b.date.localeCompare(a.date));
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

  const usedDirs = new Set(PUBLICATIONS.flatMap(pubDirs));
  DIRECTIONS.filter((d) => usedDirs.has(d.id))
    .forEach((d) => dirSel.insertAdjacentHTML("beforeend", `<option value="${d.id}">${esc(d.title)}</option>`));
  [...new Set(PUBLICATIONS.map((p) => p.date.slice(0, 4)))].sort().reverse()
    .forEach((y) => yearSel.insertAdjacentHTML("beforeend", `<option value="${y}">${y}</option>`));

  const section = document.querySelector(".pubs");
  section.querySelector(".view-toggle-slot").outerHTML = viewToggleHTML();

  const getItems = () => {
    const term = q.value.trim().toLowerCase();
    const items = PUBLICATIONS.filter((p) =>
      (!term || `${p.title} ${p.authors} ${p.journal} ${(p.tags || []).join(" ")}`.toLowerCase().includes(term)) &&
      (!dirSel.value || pubDirs(p).includes(dirSel.value)) &&
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
