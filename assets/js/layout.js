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

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const formatDate = (iso) => iso.split("-").reverse().join(".");
const plural = (n, one, few, many) => {
  const m10 = n % 10, m100 = n % 100;
  if (m10 === 1 && m100 !== 11) return one;
  if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return few;
  return many;
};

function writeButton(extraClass = "") {
  // без JS ссылка откроет почту, со скриптом покажет окно с адресом (см. mountLayout)
  return `<a class="btn btn--light ${extraClass}" href="mailto:${SITE.email}" data-write>написать<span class="btn__icon">${ICONS.chat}</span></a>`;
}

function renderHeader(active) {
  const item = (key, href, label) =>
    `<a class="nav__item${active === key ? " is-active" : ""}" href="${href}"${active === key ? ' aria-current="page"' : ""}>${label}</a>`;
  return `
  <header class="site-header">
    <a class="site-header__logo" href="index.html" aria-label="ЦМТ «Мост», на главную"><img src="assets/img/logo.png" alt="ИТМО, Центр междисциплинарных технологий «Мост»" width="364" height="80"></a>
    <button class="burger" type="button" aria-expanded="false" aria-controls="site-menu" aria-label="Меню">${ICONS.burger}</button>
    <div class="site-header__right" id="site-menu">
      <nav class="nav" aria-label="Основное меню">
        <div class="nav__bar">
          ${item("home", "index.html", "Главная")}
          <button class="nav__item${active === "science" ? " is-active" : ""}" type="button" aria-expanded="false" aria-controls="nav-science">наука ${ICONS.chevronDown}</button>
          ${item("industry", "index.html#industry", "индустрия")}
          ${item("education", "index.html#education", "образование")}
          ${item("news", "news.html", "Новости")}
        </div>
        <div class="nav__dropdown" id="nav-science" hidden>
          <a class="nav__card" href="index.html#science">Научные<br>направления<span class="square-btn card-arrow">${ICONS.arrowUpRight}</span></a>
          <a class="nav__card" href="publications.html">Публикации<span class="square-btn card-arrow">${ICONS.arrowUpRight}</span></a>
        </div>
      </nav>
      <div class="lang">
        <div class="lang__inner">
          <span class="lang__btn is-active" aria-current="true">Ру</span>
          <span class="lang__divider" aria-hidden="true"></span>
          <a class="lang__btn" aria-disabled="true" title="Английская версия готовится">EN</a>
        </div>
      </div>
    </div>
  </header>`;
}

function renderFooter() {
  return `
  <footer class="site-footer" id="contacts">
    <div class="site-footer__bg" aria-hidden="true"><img src="assets/img/hero-home.webp" alt="" loading="lazy"></div>
    <div class="site-footer__inner">
      <div class="site-footer__top">
        <a class="site-footer__logo" href="index.html"><img src="assets/img/logo.png" alt="ИТМО, Центр междисциплинарных технологий «Мост»" width="400" height="88" loading="lazy"></a>
        <button class="back-top" type="button" aria-label="Наверх">${ICONS.backTop}</button>
      </div>
      <div class="site-footer__cols">
        <div class="f-col">
          <p class="f-col__title">Меню</p>
          <ul>
            <li><a href="index.html#about">О нас</a></li>
            <li><a href="index.html#science">Наука</a></li>
            <li><a href="index.html#industry">Индустрия</a></li>
            <li><a href="index.html#education">Образование</a></li>
            <li><a href="news.html">Новости</a></li>
          </ul>
        </div>
        <div class="f-col">
          <p class="f-col__title">Документы</p>
          <ul>
            <li><a href="#">Политика по обработке персональных данных</a></li>
            <li><a href="#">Информация об организации</a></li>
          </ul>
        </div>
        <div class="f-col">
          <a class="f-ext" href="${SITE.links.physics}" target="_blank" rel="noopener">Сайт нового физтеха ${ICONS.arrowUpRightSmall}</a>
          <a class="f-ext" href="${SITE.links.itmo}" target="_blank" rel="noopener">Сайт ИТМО ${ICONS.arrowUpRightSmall}</a>
        </div>
        <div class="f-col f-contacts">
          <div class="f-col">
            <p class="f-col__title">Контакты</p>
            <ul>
              <li><a href="tel:${SITE.phone.replace(/\s/g, "")}" style="text-decoration:none">${SITE.phone}</a></li>
              <li><a href="mailto:${SITE.email}">${SITE.email}</a></li>
            </ul>
          </div>
          ${writeButton()}
        </div>
      </div>
      <div class="site-footer__bottom">
        <p>© Все права защищены</p>
        <p>ЦМТ «Мост» · Университет ИТМО</p>
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
        <button class="sheet__close" type="button" aria-label="Закрыть">${ICONS.close}</button>
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
    window.prompt("Скопируйте вручную", text);
    return;
  }
  if (!button) return;
  const label = button.querySelector(".copy-label") || button;
  clearTimeout(button._t);
  button._label ??= label.textContent;
  label.textContent = "Скопировано";
  button.classList.add("is-done");
  button._t = setTimeout(() => { label.textContent = button._label; button.classList.remove("is-done"); }, 1800);
}

function openWriteSheet() {
  const dlg = openSheet("Написать нам", `
    <p class="write__lead">Мы открыты к сотрудничеству и рады любым вопросам. Расскажите о своей задаче или идее, и мы подскажем, чем можем помочь.</p>
    <p class="write__mail"><a href="mailto:${SITE.email}">${SITE.email}</a></p>
    <div class="write__actions">
      <a class="btn btn--dark" href="mailto:${SITE.email}">открыть почту<span class="btn__icon">${ICONS.chat}</span></a>
      <button class="btn btn--ghost" type="button" data-copy-mail><span class="copy-label">скопировать адрес</span></button>
    </div>`, "sheet--write");
  dlg.querySelector("[data-copy-mail]").addEventListener("click", (e) => copyText(SITE.email, e.currentTarget));
}

/* ---------- типографика: предлоги и короткие союзы не висят в конце строки ----------
   Пробел после них заменяем неразрывным, слово уходит на следующую строку вместе с предлогом.
   Работает по всем текстовым узлам страницы, включая то, что дорисовывается скриптами позже. */
const HANGING = "в|во|без|до|из|изо|к|ко|на|над|надо|о|об|обо|от|ото|по|под|подо|при|про|с|со|у|через|для|за|перед|между|и|а|но|да|или|ни|не";
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

function mountLayout() {
  watchTypography();
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
    if (!e.target.closest("[data-write]")) return;
    e.preventDefault();
    openWriteSheet();
  });
}

document.addEventListener("DOMContentLoaded", mountLayout);
