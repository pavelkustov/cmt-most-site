/* Общие части страниц: иконки, шапка, подвал, мелкие помощники.
   Пути иконок взяты из экспортированных SVG макета (assets/icons), цвет через currentColor. */

const ICONS = {
  arrowUpRight: '<svg viewBox="0 0 82 82" fill="none" aria-hidden="true"><path d="M56.97 24.6H24.6M56.17 26.05 24.82 57.4M57.4 56.96V24.6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
  arrowUpRightSmall: '<svg viewBox="0 0 22 22" fill="none" aria-hidden="true"><path d="M19.07 2.76H2.75M18.67 3.48 2.86 19.29M19.29 19.07V2.75" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
  arrowRight: '<svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M5 10h10.98M10.5 15.5 15.98 10 10.5 4.5" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  sliderArrow: '<svg viewBox="0 0 82 82" fill="none" aria-hidden="true"><path d="M63.88 40.69 41 17.81M62.3 41.15H17.96M41.31 63.88 64.19 41" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
  chevronDown: '<svg viewBox="0 0 20 16" fill="none" aria-hidden="true"><path d="M15.67 6.67a1 1 0 0 1 .09 1.41l-5 5.72a1 1 0 0 1-1.5 0L.25 3.52a1 1 0 0 1 1.5-1.32l8.25 9.42 4.26-4.86a1 1 0 0 1 1.41-.09Zm3.99-4.56a1 1 0 0 1 .09 1.41l-2.32 2.65a1 1 0 1 1-1.5-1.32l2.32-2.65a1 1 0 0 1 1.41-.09Z" fill="currentColor"/></svg>',
  chat: '<svg viewBox="0 0 30 26.15" fill="none" aria-hidden="true"><path d="M26.47 1A2.53 2.53 0 0 1 29 3.53v13.61a2.53 2.53 0 0 1-2.53 2.53H13.67l-7.6 5.32a.9.9 0 0 1-1.4-.8l.36-4.52h-1.5A2.53 2.53 0 0 1 1 17.14V3.53A2.53 2.53 0 0 1 3.53 1H21.9" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="10.15" cy="10.65" r="1.17" fill="currentColor"/><circle cx="15.11" cy="10.65" r="1.17" fill="currentColor"/><circle cx="20.07" cy="10.65" r="1.17" fill="currentColor"/></svg>',
  back: '<svg viewBox="0 0 21 21" fill="none" aria-hidden="true"><path d="M5 10.49h10.98M10.49 15.98l5.49-5.49L10.49 5" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  backTop: '<svg viewBox="0 0 82 82" fill="none" aria-hidden="true"><path d="M24.14 40.76h35.23M22.88 41.12l18.18 18.19M40.81 22.69 22.63 40.88" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
  download: '<svg viewBox="0 0 16.22 18.89" fill="none" aria-hidden="true"><path d="M15.1 16.89a1 1 0 1 1 0 2H1.04a1 1 0 1 1 0-2H15.1ZM8.02 0a1 1 0 0 1 1 1v11.86l5.5-5.48a1 1 0 1 1 1.41 1.42l-7.07 7.04a1 1 0 0 1-1.5.1L.29 8.89a1 1 0 0 1 1.41-1.41l5.32 5.29V1a1 1 0 0 1 1-1Z" fill="currentColor"/></svg>',
  chevronPoint: '<svg viewBox="0 0 32.38 44.38" fill="none" aria-hidden="true"><path d="M15.16 15.31a.56.56 0 0 1 .8.02l6.26 6.47a.56.56 0 0 1 0 .78l-11.25 11.63a.56.56 0 1 1-.81-.79l10.87-11.23-5.88-6.08a.56.56 0 0 1 .01-.8Zm-4.99-5.15a.56.56 0 0 1 .8.01l2.9 3a.56.56 0 1 1-.81.79l-2.9-3a.56.56 0 0 1 .01-.8Z" fill="currentColor"/></svg>',
  list: '<svg viewBox="0 0 18 18" fill="none" aria-hidden="true"><path d="M1.86 14.28a1.86 1.86 0 1 1 0 3.72 1.86 1.86 0 0 1 0-3.72Zm14.28 0a1.86 1.86 0 0 1 0 3.72H7.45a1.86 1.86 0 0 1 0-3.72h8.69ZM1.86 7.14a1.86 1.86 0 1 1 0 3.72 1.86 1.86 0 0 1 0-3.72Zm14.28 0a1.86 1.86 0 0 1 0 3.72H7.45a1.86 1.86 0 0 1 0-3.72h8.69ZM1.86 0a1.86 1.86 0 1 1 0 3.72 1.86 1.86 0 0 1 0-3.72Zm14.28 0a1.86 1.86 0 0 1 0 3.72H7.45a1.86 1.86 0 0 1 0-3.72h8.69Z" fill="currentColor"/></svg>',
  grid: '<svg viewBox="0 0 18 18" fill="none" aria-hidden="true"><path d="M5.5 10A2.5 2.5 0 0 1 8 12.5v3A2.5 2.5 0 0 1 5.5 18h-3A2.5 2.5 0 0 1 0 15.5v-3A2.5 2.5 0 0 1 2.5 10h3Zm10 0a2.5 2.5 0 0 1 2.5 2.5v3a2.5 2.5 0 0 1-2.5 2.5h-3a2.5 2.5 0 0 1-2.5-2.5v-3a2.5 2.5 0 0 1 2.5-2.5h3ZM5.5 0A2.5 2.5 0 0 1 8 2.5v3A2.5 2.5 0 0 1 5.5 8h-3A2.5 2.5 0 0 1 0 5.5v-3A2.5 2.5 0 0 1 2.5 0h3Zm10 0A2.5 2.5 0 0 1 18 2.5v3A2.5 2.5 0 0 1 15.5 8h-3A2.5 2.5 0 0 1 10 5.5v-3A2.5 2.5 0 0 1 12.5 0h3Z" fill="currentColor"/></svg>',
  search: '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="10.5" cy="10.5" r="7" stroke="currentColor" stroke-width="2"/><path d="m16 16 5.5 5.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
  close: '<svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="m4 4 12 12M16 4 4 16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
  burger: '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
};

/* ---------- язык ----------
   Английские страницы лежат в en/ и собираются из русских скриптом tools/build.py.
   Язык берем из <html lang>. Строки интерфейса переводит t() по словарю EN.ui, переводы
   направлений, новостей и людей лежат там же (assets/js/en.js грузится только на английских
   страницах). Русские данные не подменяем: по ним считаются порядок команды и цифры центра.
   Английская страница лежит на уровень глубже, поэтому к картинкам из скриптов добавляется ROOT. */
/* Страница «не найдено» одна на обе версии: сервер отдает ее на любой несуществующий адрес,
   в том числе внутри en/. Корень сайта задает ее тег base, от него и смотрим, в какой версии адрес */
if (document.body.dataset.page === "404" && location.pathname.startsWith(new URL("en/", document.baseURI).pathname)) {
  document.documentElement.lang = "en";
}
const LANG = document.documentElement.lang === "en" ? "en" : "ru";
const ROOT = LANG === "en" ? "../" : "";
const t = (s) => (LANG === "en" && window.EN?.ui?.[s]) || s;
// перевод записи данных: поля из EN[kind][key] поверх русских, чего нет в переводе, остается по-русски
const tr = (kind, key, obj) => (LANG === "en" && window.EN?.[kind]?.[key] ? { ...obj, ...window.EN[kind][key] } : obj);

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const MONTHS_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
// по-английски 07.09.2026 читается двояко (7 сентября или 9 июля), поэтому месяц словом.
// День впереди и без запятой, 7 Sep 2026: так дата короче и ближе к русской (владелец: «даты большие»)
const formatDate = (iso) => {
  if (LANG !== "en") return iso.split("-").reverse().join(".");
  const [y, m, d] = iso.split("-").map(Number);
  return `${d} ${MONTHS_EN[m - 1]} ${y}`;
};
const plural = (n, one, few, many) => {
  const m10 = n % 10, m100 = n % 100;
  if (m10 === 1 && m100 !== 11) return one;
  if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return few;
  return many;
};
// число со словом на языке страницы: nWord(5, ["статья", "статьи", "статей"], ["paper", "papers"])
const nWord = (n, ru, en) => `${n} ${LANG === "en" ? en[n === 1 ? 0 : 1] : plural(n, ...ru)}`;

function writeButton(extraClass = "") {
  // без JS ссылка откроет почту, со скриптом покажет окно с адресом (см. mountLayout)
  return `<a class="btn btn--light ${extraClass}" href="mailto:${SITE.email}" data-write>${t("написать")}<span class="btn__icon">${ICONS.chat}</span></a>`;
}

/* Переключатель языка ведет на ту же страницу другого языка: русская лежит в корне, английская в en/.
   Адрес собираем в момент нажатия: окно новости меняет ?open= в адресе уже после загрузки */
function otherLangHref() {
  const file = location.pathname.split("/").pop() || "index.html";
  return `${LANG === "en" ? "../" : "en/"}${file}${location.search}${location.hash}`;
}

const LOGO = LANG === "en"
  ? { src: "logo-en.png", alt: "ITMO, Interdisciplinary Technologies Center «Bridge»", w: 1018, h: 340 }
  : { src: "logo.png", alt: "ИТМО, Центр междисциплинарных технологий «Мост»", w: 1225, h: 269 };
const logoImg = (lazy = false) =>
  `<img src="${ROOT}assets/img/${LOGO.src}" alt="${LOGO.alt}" width="${LOGO.w}" height="${LOGO.h}"${lazy ? ' loading="lazy"' : ""}>`;

function renderHeader(active) {
  const item = (key, href, label) =>
    `<a class="nav__item${active === key ? " is-active" : ""}" href="${href}"${active === key ? ' aria-current="page"' : ""}>${label}</a>`;
  return `
  <header class="site-header">
    <a class="site-header__logo" href="index.html" aria-label="${t("ЦМТ «Мост», на главную")}">${logoImg()}</a>
    <button class="burger" type="button" aria-expanded="false" aria-controls="site-menu" aria-label="${t("Меню")}">${ICONS.burger}${ICONS.close}</button>
    <div class="site-header__right" id="site-menu">
      <nav class="nav" aria-label="${t("Основное меню")}">
        <div class="nav__bar">
          ${item("home", "index.html", t("Главная"))}
          <button class="nav__item${active === "science" ? " is-active" : ""}" type="button" aria-expanded="false" aria-controls="nav-science">${t("наука")} ${ICONS.chevronDown}</button>
          ${item("industry", "index.html#industry", t("индустрия"))}
          ${item("education", "index.html#education", t("образование"))}
          ${item("news", "news.html", t("Новости"))}
        </div>
        <div class="nav__dropdown" id="nav-science" hidden>
          <a class="nav__card" href="index.html#science">${t("Научные <br>направления")}<span class="square-btn card-arrow">${ICONS.arrowUpRight}</span></a>
          <a class="nav__card" href="publications.html">${t("Публикации")}<span class="square-btn card-arrow">${ICONS.arrowUpRight}</span></a>
        </div>
      </nav>
      <div class="lang">
        <div class="lang__inner">
          ${LANG === "ru"
            ? `<span class="lang__btn is-active" aria-current="true">Ру</span>
          <span class="lang__divider" aria-hidden="true"></span>
          <a class="lang__btn" href="${esc(otherLangHref())}" hreflang="en" lang="en" data-lang-switch>EN</a>`
            : `<a class="lang__btn" href="${esc(otherLangHref())}" hreflang="ru" lang="ru" data-lang-switch>Ру</a>
          <span class="lang__divider" aria-hidden="true"></span>
          <span class="lang__btn is-active" aria-current="true">EN</span>`}
        </div>
      </div>
    </div>
  </header>`;
}

function renderFooter() {
  return `
  <footer class="site-footer" id="contacts">
    <div class="site-footer__bg" aria-hidden="true"><img src="${ROOT}assets/img/hero-home.webp" alt="" loading="lazy"></div>
    <div class="site-footer__inner">
      <div class="site-footer__top">
        <a class="site-footer__logo" href="index.html">${logoImg(true)}</a>
        <button class="back-top" type="button" aria-label="${t("Наверх")}">${ICONS.backTop}</button>
      </div>
      <div class="site-footer__cols">
        <div class="f-col">
          <p class="f-col__title">${t("Меню")}</p>
          <ul>
            <li><a href="index.html#about">${t("О нас")}</a></li>
            <li><a href="index.html#science">${t("Наука")}</a></li>
            <li><a href="index.html#industry">${t("Индустрия")}</a></li>
            <li><a href="index.html#education">${t("Образование")}</a></li>
            <li><a href="news.html">${t("Новости")}</a></li>
          </ul>
        </div>
        <div class="f-col">
          <p class="f-col__title">${t("Документы")}</p>
          <ul>
            <li><a href="${SITE.links.privacy}" target="_blank" rel="noopener">${t("Политика по обработке<br>персональных данных")}</a></li>
            <li><a href="${SITE.links.orgInfo}" target="_blank" rel="noopener">${t("Информация об организации")}</a></li>
          </ul>
        </div>
        <div class="f-col">
          <a class="f-ext" href="${LANG === "en" ? SITE.links.physicsEn || SITE.links.physics : SITE.links.physics}" target="_blank" rel="noopener">${t("Сайт нового физтеха")} ${ICONS.arrowUpRightSmall}</a>
          <a class="f-ext" href="${LANG === "en" ? SITE.links.itmoEn || SITE.links.itmo : SITE.links.itmo}" target="_blank" rel="noopener">${t("Сайт ИТМО")} ${ICONS.arrowUpRightSmall}</a>
        </div>
        <div class="f-col f-contacts">
          <div class="f-col">
            <p class="f-col__title">${t("Контакты")}</p>
            <ul>
              <li><a class="f-tel" href="tel:${SITE.phone.replace(/\s/g, "")}">${SITE.phone}</a></li>
              <li><a href="mailto:${SITE.email}">${SITE.email}</a></li>
            </ul>
          </div>
          ${writeButton()}
        </div>
      </div>
      <div class="site-footer__bottom">
        <p>${t("© Все права защищены")}</p>
        <p>${t("ЦМТ «Мост» · Университет ИТМО")}</p>
      </div>
    </div>
  </footer>`;
}

function toast(message) {
  let el = document.querySelector(".toast");
  if (!el) {
    el = document.createElement("div");
    el.className = "toast";
    el.setAttribute("role", "status");
    document.body.append(el);
  }
  el.textContent = message;
  el.classList.add("is-shown");
  clearTimeout(el._t);
  el._t = setTimeout(() => el.classList.remove("is-shown"), 2400);
}

/* ---------- всплывающее окно (написать нам, цитирование) ----------
   Нативный <dialog>: фокус, Esc и затемнение фона браузер делает сам. Клик по фону закрывает. */
function openSheet(title, bodyHTML, extraClass = "") {
  let dlg = document.querySelector(".sheet");
  if (!dlg) {
    dlg = document.createElement("dialog");
    dlg.className = "sheet";
    dlg.setAttribute("aria-labelledby", "sheet-title");
    dlg.innerHTML = `
      <div class="sheet__head">
        <h2 class="sheet__title" id="sheet-title"></h2>
        <button class="sheet__close" type="button" aria-label="${t("Закрыть")}">${ICONS.close}</button>
      </div>
      <div class="sheet__body"></div>`;
    document.body.append(dlg);
    dlg.querySelector(".sheet__close").addEventListener("click", () => dlg.close());
    dlg.addEventListener("click", (e) => { if (e.target === dlg) dlg.close(); });
    dlg.addEventListener("close", () => { document.body.style.overflow = ""; });
  }
  dlg.className = `sheet ${extraClass}`.trim();
  dlg.querySelector(".sheet__title").textContent = title;
  dlg.querySelector(".sheet__body").innerHTML = bodyHTML;
  document.body.style.overflow = "hidden";
  dlg.showModal();
  return dlg;
}

/* Копирует текст; подпись кнопки на пару секунд меняется на «Скопировано» (тост под окном не виден) */
async function copyText(text, button) {
  try {
    await navigator.clipboard.writeText(text);
  } catch (err) {
    window.prompt(t("Скопируйте вручную"), text);
    return;
  }
  if (!button) return;
  const label = button.querySelector(".copy-label") || button;
  clearTimeout(button._t);
  button._label ??= label.textContent;
  label.textContent = t("Скопировано");
  button.classList.add("is-done");
  button._t = setTimeout(() => { label.textContent = button._label; button.classList.remove("is-done"); }, 1800);
}

// subject: тема письма, например «Совместная работа: <направление>» (кнопка с data-write-subject)
function openWriteSheet(subject = "") {
  const mailto = `mailto:${SITE.email}${subject ? `?subject=${encodeURIComponent(subject)}` : ""}`;
  const dlg = openSheet(t("Написать нам"), `
    <p class="write__lead">${t("Мы открыты к сотрудничеству и рады любым вопросам. Расскажите о своей задаче или идее, и мы подскажем, чем можем помочь.")}</p>
    <p class="write__mail"><a href="${esc(mailto)}">${SITE.email}</a></p>
    <div class="write__actions">
      <a class="btn btn--dark" href="${esc(mailto)}">${t("открыть почту")}<span class="btn__icon">${ICONS.chat}</span></a>
      <button class="btn btn--ghost" type="button" data-copy-mail><span class="copy-label">${t("скопировать адрес")}</span></button>
    </div>`, "sheet--write");
  dlg.querySelector("[data-copy-mail]").addEventListener("click", (e) => copyText(SITE.email, e.currentTarget));
}

/* ---------- типографика: предлоги и короткие союзы не висят в конце строки (и в английском тоже) ----------
   Пробел после них заменяем неразрывным, слово уходит на следующую строку вместе с предлогом.
   Работает по всем текстовым узлам страницы, включая то, что дорисовывается скриптами позже. */
const HANGING_RU = "в|во|без|до|из|изо|к|ко|на|над|надо|о|об|обо|от|ото|по|под|подо|при|про|с|со|у|через|для|за|перед|между|и|а|но|да|или|ни|не";
// в английском так же не оставляют в конце строки артикли, короткие предлоги и союзы
const HANGING_EN = "a|an|the|of|in|on|at|to|for|by|with|from|as|and|or|but|nor|since|into|onto|via|per|than|its|our|we|is|are|be";
const HANGING = LANG === "en" ? HANGING_EN : HANGING_RU;
const HANGING_RE = new RegExp(`(?<![\\p{L}\\p{N}])(${HANGING}) (?=\\S)`, "giu");
const SKIP_TAGS = new Set(["SCRIPT", "STYLE", "TEXTAREA", "INPUT", "CODE", "PRE"]);

function fixHanging(root) {
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode: (n) => (n.parentElement && SKIP_TAGS.has(n.parentElement.tagName) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT),
  });
  for (let n = root.nodeType === Node.TEXT_NODE ? root : walker.nextNode(); n; n = walker.nextNode()) {
    const fixed = n.data.replace(HANGING_RE, "$1 ");
    if (fixed !== n.data) n.data = fixed;
    if (root.nodeType === Node.TEXT_NODE) break;
  }
}

function watchTypography() {
  fixHanging(document.body);
  new MutationObserver((records) => {
    for (const r of records) r.addedNodes.forEach((n) => {
      if (n.nodeType === Node.TEXT_NODE ? !SKIP_TAGS.has(n.parentElement?.tagName) : n.nodeType === Node.ELEMENT_NODE) fixHanging(n);
    });
  }).observe(document.body, { childList: true, subtree: true });
}

/* ---------- анимации при прокрутке ----------
   Блоки ниже первого экрана мягко появляются один раз, когда до них докрутили.
   Прячем только то, что на момент загрузки ниже экрана (переход по якорю не мигает).
   После появления служебные классы снимаются, у элементов снова обычные стили и эффекты наведения.
   При системной настройке «уменьшить движение» ничего не делаем. */
const MOTION_GROUPS = [          // контейнер, его элементы, шаг задержки между ними
  [".metrics", ".metric", 120],
  [".carousel", ".dir-card", 90],
  [".ind-grid", ":scope > *", 90],
  [".facts", ".fact", 110],
  [".news__grid", ".news-card", 90],
  [".people", ".person", 80],
  [".dir-stats", ".stat", 80],
];
const MOTION_SINGLES = [
  "main .section-head", "main .section-head--row", ".featured .h2", ".featured__card", ".news-all > .h2",
  ".dir-about .h2", ".dir-about__text", ".dir-cta", ".dir-about__tags", ".people-head", ".education__photo", ".education__text", ".education .btn",
];

function initMotion() {
  if (matchMedia("(prefers-reduced-motion: reduce)").matches || !("IntersectionObserver" in window)) return;
  const below = (el) => el.getBoundingClientRect().top > innerHeight;
  const show = (el) => {
    el.classList.add("is-in");
    const delay = parseFloat(el.style.getPropertyValue("--d")) || 0;
    setTimeout(() => { el.classList.remove("reveal", "is-in"); el.style.removeProperty("--d"); }, delay + 900);
  };
  const io = new IntersectionObserver((entries) => entries.forEach((e) => {
    if (!e.isIntersecting) return;
    io.unobserve(e.target);
    const t = e.target;
    if (t._items) {
      t._items.forEach(show);
    } else if (t.matches(".timeline")) {
      t.classList.replace("is-pending", "is-drawn");
    } else {
      show(t);
    }
  }), { rootMargin: "0px 0px -12% 0px" });

  MOTION_GROUPS.forEach(([groupSel, itemSel, step]) => document.querySelectorAll(groupSel).forEach((group) => {
    if (!below(group)) return;
    group._items = [...group.querySelectorAll(itemSel)];
    group._items.forEach((el, i) => { el.classList.add("reveal"); el.style.setProperty("--d", `${Math.min(i, 4) * step}ms`); });
    io.observe(group);
  }));
  document.querySelectorAll(MOTION_SINGLES.join(",")).forEach((el) => {
    if (!below(el) || el.classList.contains("reveal")) return;
    el.classList.add("reveal");
    io.observe(el);
  });
  document.querySelectorAll(".timeline").forEach((el) => {
    if (!below(el)) return;
    el.classList.add("is-pending");
    io.observe(el);
  });
}

/* ---------- оптическое выравнивание крупных заголовков ----------
   У буквы в шрифте есть свое пустое поле слева, на крупном кегле оно заметно: «О» в «О направлении»
   стоит на 2 px правее текста под ней на телефоне и на 4 px на компьютере, «Т» в заголовке первого
   экрана до 8 px. Меряем первую букву заголовка и сдвигаем его влево ровно на это поле.
   Сдвиг в em, поэтому он верен на любой ширине окна. Меряем после загрузки шрифта, иначе
   получим поле запасного шрифта. Заголовки, которые дорисовывает main.js, к этому моменту уже есть. */
const OPTICAL = ".h2, .hero__title";

function alignOptical() {
  const ctx = document.createElement("canvas").getContext("2d");
  document.querySelectorAll(OPTICAL).forEach((el) => {
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    let n = walker.nextNode();
    while (n && !n.data.trim()) n = walker.nextNode();
    if (!n) return;
    const s = getComputedStyle(n.parentElement);
    const font = `${s.fontStyle} ${s.fontWeight} ${s.fontSize} ${s.fontFamily}`;
    const ch = n.data.trim()[0];
    // ждем именно это начертание: общий document.fonts.ready бывает готов раньше, чем курсив заголовка
    const measure = () => {
      ctx.font = font;
      const bearing = -ctx.measureText(ch).actualBoundingBoxLeft;
      // em у отступа считается от кегля самого заголовка, а первая буква может сидеть в <em> со своим кеглем
      el.style.marginLeft = bearing > 0.3 ? `${(-bearing / parseFloat(getComputedStyle(el).fontSize)).toFixed(3)}em` : "";
    };
    if (document.fonts) document.fonts.load(font, ch).then(measure, measure);
    else measure();
  });
}

/* Английский текст страницы «не найдено»: ссылки ведут на английские страницы, логотип английский */
function translateNotFound() {
  const q = (s) => document.querySelector(s);
  document.title = "Page not found · ITC «Bridge»";
  q(".oops__logo").setAttribute("aria-label", "ITC «Bridge», home page");
  q(".oops__logo").href = "en/index.html";
  q(".oops__logo img").src = "assets/img/logo-en.png";
  q(".oops__logo img").alt = "ITMO, Interdisciplinary Technologies Center «Bridge»";
  q(".oops__title").innerHTML = "This bridge<br>is not finished yet";
  q(".oops__text").innerHTML = "There is no page at this address.<br>It has moved, or the link has a typo.";
  const [news, pubs] = document.querySelectorAll(".oops__link");
  news.textContent = "to news";
  news.href = "en/news.html";
  pubs.textContent = "to publications";
  pubs.href = "en/publications.html";
  const home = q(".oops__home");
  home.firstChild.textContent = "home";
  home.href = "en/index.html";
  q(".oops__foot").textContent = "ITC «Bridge» · ITMO University";
}

function mountLayout() {
  if (document.body.dataset.page === "404" && LANG === "en") translateNotFound();
  watchTypography();
  // заголовки, которые дорисовывает main.js, появляются в том же DOMContentLoaded, поэтому через setTimeout
  setTimeout(alignOptical);
  // страница 404 идет без шапки и подвала, ей нужна только типографика
  if (document.body.dataset.layout === "off") return;
  // карточки и списки дорисовывает main.js в своем обработчике DOMContentLoaded, анимации настраиваем после него
  setTimeout(initMotion);
  const page = document.querySelector(".page");
  const active = document.body.dataset.nav;
  page.insertAdjacentHTML("afterbegin", renderHeader(active));
  page.insertAdjacentHTML("beforeend", renderFooter());

  const header = page.querySelector(".site-header");
  const scienceBtn = header.querySelector('[aria-controls="nav-science"]');
  const dropdown = header.querySelector("#nav-science");
  const setDropdown = (open) => {
    scienceBtn.setAttribute("aria-expanded", String(open));
    dropdown.hidden = !open;
  };
  scienceBtn.addEventListener("click", () => setDropdown(dropdown.hidden));
  document.addEventListener("click", (e) => { if (!header.querySelector(".nav").contains(e.target)) setDropdown(false); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") setDropdown(false); });

  const burger = header.querySelector(".burger");
  burger.addEventListener("click", () => {
    const open = !header.classList.contains("is-open");
    header.classList.toggle("is-open", open);
    burger.setAttribute("aria-expanded", String(open));
  });
  header.querySelectorAll(".site-header__right a[href]").forEach((a) =>
    a.addEventListener("click", () => { header.classList.remove("is-open"); setDropdown(false); }));

  page.querySelector(".back-top").addEventListener("click", () => window.scrollTo({ top: 0 }));

  document.addEventListener("click", (e) => {
    const trigger = e.target.closest("[data-write]");
    if (!trigger) return;
    e.preventDefault();
    openWriteSheet(trigger.dataset.writeSubject);
  });

  // переключатель языка: адрес собираем в момент нажатия (окно новости могло поменять ?open=)
  header.querySelector("[data-lang-switch]")?.addEventListener("click", (e) => { e.currentTarget.href = otherLangHref(); });
}

document.addEventListener("DOMContentLoaded", mountLayout);
