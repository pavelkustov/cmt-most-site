/* Логика страниц. Какая страница, определяем по <body data-page="..."> */

const img = (file) => `assets/img/${file}`;
// незаполненные метрики пропускаем: лучше показать меньше цифр, чем выдуманные
const statsHTML = (items) => items.filter(([value]) => value).map(([value, label]) =>
  `<div class="stat"><p class="stat__value">${esc(value)}</p><p class="stat__label">${esc(label)}</p></div>`).join("");
const tagsHTML = (tags) => `<div class="tags">${tags.map((t) => `<span class="tag">${esc(t)}</span>`).join("")}</div>`;

/* ---------- новости ---------- */

/* В заголовке новости владелец сам решает, где сломать строку: пишет <br> прямо в тексте.
   Все остальное экранируем, наружу пропускаем только сам перенос. */
function newsTitleHTML(title) {
  return esc(title)
    .replace(/&lt;\/?br\s*\/?&gt;/gi, "<br>")
    // названия вроде FLAMN-25 и LUMOS-2026 браузер рвет по дефису, а это одно слово
    .replace(/([A-Za-zА-Яа-я]{2,})-(\d+)/g, '<span class="nb">$1-$2</span>');
}

const newsPhoto = (n) => (n.image ? `<img src="${img(n.image)}" alt="" loading="lazy">` : "");

/* Окно новости живет и на странице новостей, и на главной: с главной карточка открывается
   здесь же, а не уводит на другую страницу. Разметка окна есть в обоих файлах. */
function mountNewsModal(fallbackId = "") {
  const modal = document.querySelector(".modal");
  if (!modal) return;
  const body = modal.querySelector(".modal__body");
  const wrap = modal.querySelector(".modal__scroll");
  // на широком экране прокручивается колонка текста, на планшете и телефоне вся новость вместе с фото
  const scroller = () => (wrap && getComputedStyle(wrap).overflowY !== "visible" ? wrap : body);
  let lastFocus = null;

  // вступление и заключение приходят абзацами: в анкете их пишут в несколько строк.
  // В интервью абзац с вопросом выделяется, иначе разговор читается сплошняком
  const paras = (text, cls = "", ask = false) => (Array.isArray(text) ? text : [text])
    .filter(Boolean)
    .map((p, i) => {
      // в интервью первый абзац это вводка, дальше вопрос и ответ чередуются
      const kind = !ask ? cls
        : i === 0 ? `${cls} intro`.trim()
        : /\?\s*$/.test(p) ? `${cls} q`.trim()
        : `${cls} a`.trim();
      return `<p${kind ? ` class="${kind}"` : ""}>${esc(p)}</p>`;
    }).join("");
  // длинный текст прокручивается внутри окна: подсказка внизу гаснет, когда текст дочитан
  const atEnd = () => {
    const s = scroller();
    modal.querySelector(".modal__dialog").classList.toggle("at-end", s.scrollTop + s.clientHeight >= s.scrollHeight - 4);
  };
  body.addEventListener("scroll", atEnd);
  wrap?.addEventListener("scroll", atEnd);

  const open = (id) => {
    const n = NEWS.find((x) => x.id === id);
    if (!n) return;
    const b = n.body;
    // у окна на широком экране, на планшете и телефоне в альбомной почти квадратная колонка под фото (свой кадр
    // popupImage), на планшете и телефоне в книжной фото идет во всю ширину над текстом, туда подходит кадр 3:2
    modal.querySelector(".modal__img").innerHTML = n.image
      ? `<picture>${n.popupImage ? `<source media="(min-width: 1101px), (min-width: 761px) and (orientation: landscape), (max-height: 500px) and (orientation: landscape)" srcset="${img(n.popupImage)}">` : ""}<img src="${img(n.image)}" alt=""></picture>`
      : "";
    modal.querySelector(".modal__dialog").classList.toggle("no-image", !n.image);
    modal.querySelector(".modal__meta").innerHTML = `<span class="tag">${esc(n.tag)}</span><time class="news-meta__date" datetime="${n.date}">${formatDate(n.date)}</time>`;
    // в окне колонка другая, поэтому перенос из карточки там скрыт стилями
    modal.querySelector(".modal__title").innerHTML = newsTitleHTML(n.title);
    const talk = (n.tag || "").toLowerCase() === "интервью";
    modal.querySelector(".modal__text").innerHTML = b
      ? `${paras(b.lead, "", talk)}
         ${b.quote ? `<blockquote>${paras(b.quote)}</blockquote>` : ""}
         ${paras(b.note, "note")}`
      : `<p>${esc(n.text)}</p>`;
    lastFocus = document.activeElement;
    modal.hidden = false;
    document.body.style.overflow = "hidden";
    body.scrollTop = 0;
    if (wrap) wrap.scrollTop = 0;
    atEnd();
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
  if (requested) open(NEWS.some((n) => n.id === requested) ? requested : fallbackId);
}

function newsCardHTML(n) {
  return `
  <article class="news-card">
    <div class="news-card__img${n.image ? "" : " is-empty"}">${n.image ? `<img src="${img(n.image)}" alt="" loading="lazy">` : ""}</div>
    <div class="news-card__body">
      <div class="news-meta"><span class="tag">${esc(n.tag)}</span><time class="news-meta__date" datetime="${n.date}">${formatDate(n.date)}</time></div>
      <div>
        <h3 class="news-card__title">${newsTitleHTML(n.title)}</h3>
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

const SPLIT = /\n{2,}/;  // абзацы абстракта

/* Абстракт берется из assets/js/abstracts.js по DOI и показывается как есть, на языке
   статьи. Если абстракта нет, показываем короткое описание из данных, когда оно написано. */
function abstractOf(p) {
  const doi = (p.doi || "").replace("https://doi.org/", "").toLowerCase();
  const full = doi && window.ABSTRACTS ? window.ABSTRACTS[doi] : "";
  return full || p.desc || "";
}

/* Название публикации выводится заглавными, а химическую формулу это портит:
   MAPbI3 превращается в MAPBI3, c-Si в C-SI. Такие куски оставляем как в оригинале. */
const FORMULA = /^(?:[A-Z][a-z]?[0-9]*)+$/;          // TiO2, CsPbBr3, ZnO, HeLa
const PREFIX = /^[a-z]{1,2}-[A-Z]/;                  // c-Si, fs-Laser, a-SiC
const LOWUP = /^[a-z][A-Z]/;                         // pH, mRNA
const ABBR = /^[A-Z]{2,}[a-z]+[0-9]*$/;              // MOFs, DNAzyme

function keepsCase(word) {
  const core = word.replace(/^[^0-9A-Za-z]+|[^0-9A-Za-z+]+$/g, "");
  if (core.length < 2 || !/[a-z]/.test(core) || !/[A-Z]/.test(core)) return false;
  if (PREFIX.test(core) || LOWUP.test(core) || ABBR.test(core)) return true;
  // формула может быть склеена через дробь или дефис: Ag/TiO2, ZnO-based
  return core.split(/[/:-]/).some((part) => {
    if (!FORMULA.test(part)) return false;
    const elements = part.match(/[A-Z][a-z]?[0-9]*/g) || [];
    return elements.length > 1 || /[0-9]/.test(part);
  });
}

// разбиваем по пробелам, чтобы не трогать остальной текст названия
const titleHTML = (title) => title.split(/(\s+)/)
  .map((part) => (keepsCase(part) ? `<span class="keep-case">${esc(part)}</span>` : esc(part)))
  .join("");

function pubHTML(p, index) {
  const image = p.image
    ? `<img src="${img(p.image)}" alt="" loading="lazy">`
    : `<span class="pub__img-placeholder">${esc(p.journal)}</span>`;
  // у статей в российских журналах DOI бывает не присвоен: тогда ведем на страницу издателя,
  // ссылку владелец находит руками, она лежит в поле url
  const link = p.doi || p.url || "";
  const title = link
    ? `<a href="${esc(link)}" target="_blank" rel="noopener">${titleHTML(p.title)}</a>`
    : titleHTML(p.title);
  const text = abstractOf(p);
  return `
  <article class="pub">
    <div class="pub__meta">
      <div class="pub__meta-left">
        <time class="pub__date" datetime="${p.date}">${formatDate(p.date)}</time>
        ${p.quartile ? `<span class="tag tag--outline">${esc(p.quartile)}</span>` : ""}
        <span>${esc(p.journal)}</span>
      </div>
      <button class="pub__cite" type="button" data-cite="${index}" aria-haspopup="dialog"><span>Цитировать</span>${ICONS.download}</button>
    </div>
    <div class="pub__main">
      <div class="pub__body">
        <div>
          <h3 class="pub__title">${title}</h3>
          <p class="pub__authors">${esc(p.authors)}</p>
        </div>
        ${text ? `<div class="pub__desc">
          <button class="pub__desc-btn" type="button" aria-expanded="false" title="Показать абстракт целиком">${ICONS.chevronPoint}</button>
          <div class="pub__desc-text">${text.split(SPLIT).map((part) => `<p>${esc(part)}</p>`).join("")}</div>
        </div>
        <button class="pub__desc-toggle" type="button" aria-expanded="false"><span class="pub__desc-more">весь абстракт</span><span class="pub__desc-less">свернуть</span>${ICONS.chevronDown}</button>` : ""}
        ${p.tags && p.tags.length ? `<div class="pub__tags">
          <p class="pub__tags-title">Ключевые теги</p>
          ${tagsHTML(p.tags)}
        </div>` : ""}
      </div>
      <div class="pub__img${p.image ? "" : " is-empty"}">
        ${image}
        ${link ? `<a class="pub__img-link" href="${esc(link)}" target="_blank" rel="noopener">подробнее ${ICONS.arrowRight}</a>` : ""}
      </div>
    </div>
    <!-- на телефоне «Цитировать» стоит внизу карточки, а в строке с датой скрыт -->
    <div class="pub__foot">
      <button class="pub__cite" type="button" data-cite="${index}" aria-haspopup="dialog"><span>Цитировать</span>${ICONS.download}</button>
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

  // абстракт свернут до высоты карточки, по клику раскрывается целиком
  // на телефоне под абстрактом отдельная кнопка «весь абстракт», стрелка слева там скрыта
  list.addEventListener("click", (e) => {
    const toggle = e.target.closest(".pub__desc-toggle");
    const desc = toggle ? toggle.previousElementSibling : e.target.closest(".pub__desc");
    if (!desc || e.target.closest("a")) return;
    const open = desc.classList.toggle("is-open");
    const btn = desc.querySelector(".pub__desc-btn");
    if (btn) {
      btn.setAttribute("aria-expanded", String(open));
      btn.title = open ? "Свернуть абстракт" : "Показать абстракт целиком";
    }
    desc.nextElementSibling?.matches(".pub__desc-toggle") && desc.nextElementSibling.setAttribute("aria-expanded", String(open));
  });
  // короткий абстракт виден целиком, кнопка «весь абстракт» ему не нужна
  const markShort = () => list.querySelectorAll(".pub__desc:not(.is-open)").forEach((d) =>
    d.classList.toggle("is-short", d.scrollHeight <= d.clientHeight + 2));

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
    markShort();
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
  autoSlide(track, arrows, step);
}

/* Лента сама листается на карточку, как будто нажали стрелку «вперед»: первый раз через
   SLIDE_FIRST после того, как лента появилась на экране (иначе кажется, что блок застыл),
   дальше раз в SLIDE_EVERY. В самый конец не заходит: там после последней карточки пустое
   поле, и лента стояла бы в нем целый интервал. Как только следующий шаг упер бы ленту
   в конец, она вместо него плавно уезжает к началу.
   Листает, только когда лента на экране и вкладка открыта. Пока над лентой мышь или в ней
   фокус, стоит. После касания, прокрутки или стрелки отсчет начинается заново, чтобы лента
   не уехала из-под руки. При «уменьшить движение» не листает */
const SLIDE_FIRST = 2200;
const SLIDE_EVERY = 3000;

function autoSlide(track, arrows, step) {
  if (matchMedia("(prefers-reduced-motion: reduce)").matches || !("IntersectionObserver" in window)) return;
  let timer = null, visible = false, held = false;
  const plan = (delay = SLIDE_EVERY) => {
    clearTimeout(timer);
    if (visible && !held && !document.hidden && !arrows.hidden) timer = setTimeout(move, delay);
  };
  const move = () => {
    const d = step();
    const room = track.scrollWidth - track.clientWidth - track.scrollLeft;
    if (room > d + 4) track.scrollBy({ left: d, behavior: "smooth" });
    // лента длиннее экрана меньше чем на две карточки: из начала все-таки показываем остаток
    else if (track.scrollLeft < 4) track.scrollTo({ left: track.scrollWidth, behavior: "smooth" });
    else track.scrollTo({ left: 0, behavior: "smooth" });
    plan();
  };
  const again = () => plan();
  const hold = (on) => (e) => {
    // касание на сенсорном экране тоже шлет «наведение», но без ухода: иначе лента застыла бы
    if (e.pointerType && e.pointerType !== "mouse") return;
    held = on; plan();
  };
  track.addEventListener("pointerenter", hold(true));
  track.addEventListener("pointerleave", hold(false));
  track.addEventListener("focusin", hold(true));
  track.addEventListener("focusout", hold(false));
  ["pointerdown", "wheel", "touchstart"].forEach((type) => track.addEventListener(type, again, { passive: true }));
  arrows.addEventListener("click", again);
  document.addEventListener("visibilitychange", () => plan(SLIDE_FIRST));
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; plan(SLIDE_FIRST); }, { threshold: 0.3 }).observe(track);
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

/* Цифры в блоке «ЦМТ Мост» считаются по данным сайта, а не пишутся в разметке руками:
   иначе они устаревают с каждой новой работой. В разметке стоят те же числа, чтобы
   страница была правдива и до выполнения скрипта.

   Мест в блоке три, а цифр девять: у каждого места своя тройка, она сменяется по кругу.
   Иконка у места одна и та же, меняются только число и подпись. */
const START_YEAR = 2015;
const METRIC_SHOW = 6000;    // сколько держится одна цифра
const METRIC_FIRST = 2200;   // первая смена быстрее: иначе кажется, что блок застыл
const METRIC_FADE = 500;     // столько длится затухание, столько же стоит в CSS
const METRIC_STEP = 1200;    // на столько сдвинуты соседние места, чтобы не мигали разом

const ORDINAL = { 2: "вторая", 3: "третья", 4: "четвертая", 5: "пятая", 6: "шестая", 7: "седьмая" };

/* «каждая четвертая работа»: если доля не дотягивает до круглой, пишем «почти» */
function everyNth(total, part) {
  const share = total / (part || 1);
  const nth = Math.round(share);
  return (share > nth ? "почти каждая " : "каждая ") + (ORDINAL[nth] || `${nth}-я`);
}

function homeMetricSets() {
  const count = (n, one, few, many) => `${n} ${plural(n, one, few, many)}`;
  const people = Object.values(window.PEOPLE || {});
  const withDegree = (re) => people.filter((p) => re.test(p.degree || "")).length;
  const cited = PUBLICATIONS.reduce((sum, p) => sum + (p.cited || 0), 0);
  const ranked = PUBLICATIONS.map((p) => p.cited || 0).sort((a, b) => b - a);
  const h = ranked.filter((c, i) => c >= i + 1).length;
  const known = PUBLICATIONS.filter((p) => p.quartile);
  const top = known.filter((p) => p.quartile === "Q1" || p.quartile === "Q2");
  const since = new Date().getFullYear() - 2;
  const recent = PUBLICATIONS.filter((p) => Number(p.date.slice(0, 4)) >= since).length;
  const cands = withDegree(/кандидат/);
  const doctors = withDegree(/доктор/);
  const postgrads = withDegree(/аспирант/);
  return {
    people: [
      [count(people.length, "человек", "человека", "человек"),
       "работает над наукой, образованием и технологиями центра"],
      [`${count(cands, "кандидат", "кандидата", "кандидатов")} наук`,
       (doctors ? `и ${count(doctors, "доктор", "доктора", "докторов")} наук ` : "")
       + "ведут проекты центра и научное руководство"],
      [count(postgrads, "аспирант", "аспиранта", "аспирантов"),
       "ведут исследования в центре вместе со студентами и магистрами"],
    ],
    works: [
      [count(PUBLICATIONS.length, "публикация", "публикации", "публикаций"),
       "опубликовано сотрудниками центра в высокорейтинговых журналах"],
      [`${Math.round((top.length / (known.length || 1)) * 100)}% в Q1 и Q2`,
       "столько работ с известным квартилем вышло в лучших журналах"],
      [count(recent, "статья", "статьи", "статей"),
       `вышло за три последних года, это ${everyNth(PUBLICATIONS.length, recent)} работа центра`],
    ],
    impact: [
      [count(new Date().getFullYear() - START_YEAR, "год", "года", "лет"),
       "ведется научно-образовательная деятельность центра (с 2015 года)"],
      [count(cited, "цитирование", "цитирования", "цитирований"),
       "собрали работы сотрудников центра у коллег по всему миру"],
      // «одним единственным» связано неразрывным пробелом: так строка ломается после
      // «будь он» и обе половины выходят примерно одной длины
      [`индекс Хирша ${h}`, "столько было бы у центра, будь он одним единственным ученым"],
    ],
  };
}

function initHomeMetrics() {
  const sets = homeMetricSets();
  const slots = [...document.querySelectorAll(".metric[data-slot]")]
    .map((slot) => ({ slot, rows: sets[slot.dataset.slot] || [], at: 0 }))
    .filter((s) => s.rows.length);

  const draw = ({ slot, rows, at }) => {
    const [value, text] = rows[at];
    slot.querySelector(".metric__title").textContent = value;
    slot.querySelector(".metric__text").textContent = text;
  };
  slots.forEach(draw);

  /* Цифры и подписи разной длины, и при смене блок дергался бы по высоте. Меряем самую
     высокую тройку места на текущей ширине и держим место под нее. */
  const reserve = () => slots.forEach(({ slot, rows, at }) => {
    const body = slot.querySelector(".metric__body");
    const title = slot.querySelector(".metric__title");
    const text = slot.querySelector(".metric__text");
    let tallest = 0;
    body.style.minHeight = "";
    rows.forEach(([value, label]) => {
      title.textContent = value;
      text.textContent = label;
      tallest = Math.max(tallest, body.getBoundingClientRect().height);
    });
    title.textContent = rows[at][0];
    text.textContent = rows[at][1];
    body.style.minHeight = `${Math.ceil(tallest)}px`;
  });
  reserve();
  if (document.fonts) document.fonts.ready.then(reserve);   // шрифт приезжает позже разметки
  let resized;
  window.addEventListener("resize", () => { clearTimeout(resized); resized = setTimeout(reserve, 200); });

  // цифры тикают, только когда блок на экране: незачем менять их в пустоту
  const quiet = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const box = document.querySelector(".metrics");
  if (quiet || !box || !("IntersectionObserver" in window) || slots.length < 2) return;
  let timers = [], running = false, turn = 0;
  const stop = () => { running = false; turn += 1; timers.forEach(clearInterval); timers = []; };
  const swap = (s) => {
    const body = s.slot.querySelector(".metric__body");
    body.classList.add("is-out");
    setTimeout(() => {
      s.at = (s.at + 1) % s.rows.length;
      draw(s);
      body.classList.remove("is-out");
    }, METRIC_FADE);
  };
  const start = () => {
    if (running) return;
    running = true;
    const mine = (turn += 1);
    // соседние места стартуют со сдвигом, поэтому мигают по очереди, а не разом
    slots.forEach((s, i) => setTimeout(() => {
      if (mine !== turn) return;
      swap(s);
      timers.push(setInterval(() => swap(s), METRIC_SHOW));
    }, METRIC_FIRST + i * METRIC_STEP));
  };
  new IntersectionObserver((entries) => entries.forEach((e) => (e.isIntersecting ? start() : stop())))
    .observe(box);
}

function initHome() {
  initHomeMetrics();
  const carousel = document.querySelector(".carousel");
  carousel.innerHTML = DIRECTIONS.map((d) => `
    <a class="dir-card" href="direction.html?id=${d.id}">
      <div class="dir-card__top">
        <h3 class="dir-card__title">${esc(d.title)}</h3>
        <div class="dir-card__row">
          <div class="dir-card__stats">${statsHTML([[d.team, "человек в команде"], [PUBLICATIONS.filter((p) => pubDirs(p).includes(d.id)).length, "публикаций"]])}</div>
          <span class="square-btn" aria-hidden="true">${ICONS.arrowUpRight}</span>
        </div>
      </div>
      <div class="dir-card__img${d.image ? "" : " is-empty"}">${d.image ? `<img src="${img(d.image)}" alt="" loading="lazy" style="object-position:${d.imagePos || "center"}">` : ""}</div>
    </a>`).join("");

  mountSlider(carousel, document.querySelector(".science .slider-arrows"), ".dir-card");

  // на главной три самые свежие новости, новость месяца в том числе: отдельного места
  // под нее здесь нет, и без этого самая свежая новость с главной просто пропадала
  document.querySelector(".news__grid").innerHTML = NEWS.slice(0, 3).map(newsCardHTML).join("");
  mountNewsModal();
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

/* Метрики направления считаются по его же публикациям, а не берутся из анкет:
   цитирования и квартили приходят из базы работ (tools/enrich_publications.py). */
function pubMetrics(pubs) {
  const cites = pubs.reduce((sum, p) => sum + (p.cited || 0), 0);
  const ranked = [...pubs].map((p) => p.cited || 0).sort((a, b) => b - a);
  const h = ranked.filter((c, i) => c >= i + 1).length;
  const known = pubs.filter((p) => p.quartile);
  const top = known.filter((p) => p.quartile === "Q1" || p.quartile === "Q2");
  const since = new Date().getFullYear() - 2;
  const recent = pubs.filter((p) => Number(p.date.slice(0, 4)) >= since).length;
  return {
    cites, h, recent, since,
    topShare: known.length >= 3 ? Math.round((top.length / known.length) * 100) : 0,
  };
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
  // в подзаголовке разрешен только перенос строки: где делить фразу, решает владелец
  document.querySelector(".hero__subtitle").innerHTML =
    (d.subtitle || "Научное направление ЦМТ «Мост»").split("<br>").map(esc).join("<br>");

  const about = document.querySelector(".dir-about");
  const text = d.about
    ? d.about.map((p) => `<p>${esc(p)}</p>`).join("")
    : `<p>Описание направления готовится. Пока можно написать нам, и мы расскажем о проектах команды.</p>`;
  const dirPubs = PUBLICATIONS.filter((p) => pubDirs(p).includes(d.id)).sort((a, b) => b.date.localeCompare(a.date));
  const m = pubMetrics(dirPubs);
  const stats = [
    [d.team, plural(d.team, "человек", "человека", "человек") + " в команде"],
    [dirPubs.length, "публикаций"],
    [m.cites, "цитирований"],
    [m.h, "индекс Хирша"],
    [m.topShare ? m.topShare + "%" : 0, "статей в Q1 и Q2"],
    [m.recent, "статей с " + m.since + " года"],
  ];
  const textBox = about.querySelector(".dir-about__text");
  textBox.innerHTML = text;
  // на телефоне виден первый абзац, остальные открываются кнопкой (на компьютере кнопка скрыта)
  if (textBox.children.length > 1) {
    textBox.insertAdjacentHTML("afterend",
      `<button class="dir-about__more" type="button" aria-expanded="false"><span class="dir-about__more-open">читать полностью</span><span class="dir-about__more-close">свернуть</span>${ICONS.chevronDown}</button>`);
    const more = textBox.nextElementSibling;
    more.addEventListener("click", () => {
      const open = textBox.classList.toggle("is-open");
      more.setAttribute("aria-expanded", String(open));
    });
  }
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
  const pubs = dirPubs;
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

  if (featured) {
    document.querySelector(".featured__slot").outerHTML = `
      <button class="featured__card${featured.image ? "" : " no-image"}" type="button" data-open-news="${featured.id}">
        ${featured.image ? `<span class="featured__img">${newsPhoto(featured)}</span>` : ""}
        <span class="featured__body">
          <span class="news-meta"><span class="tag">${esc(featured.tag)}</span><time class="news-meta__date" datetime="${featured.date}">${formatDate(featured.date)}</time></span>
          <span class="featured__main">
            <span class="featured__title">${newsTitleHTML(featured.title)}</span>
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

  // неизвестный адрес ?open= на этой странице открывает новость месяца, а не пустоту
  mountNewsModal(featured?.id);
}

document.addEventListener("DOMContentLoaded", () => {
  ({ home: initHome, direction: initDirection, publications: initPublications, news: initNews })[document.body.dataset.page]?.();
});
