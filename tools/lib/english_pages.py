"""Английские страницы en/*.html из русских, часть сборки (tools/build.py).

Английские страницы руками не правим: текст в них заменяется по списку пар ниже
(русский фрагмент HTML → английский), пути к файлам уходят на уровень выше (../assets),
<html lang="en">, подключаются словарь assets/js/en.js и переводы данных en-content.js. Строки, которые рисуют скрипты
(шапка, подвал, карточки, подписи), переводятся в en.js, данные направлений и новостей тоже там.

Заодно в русские и английские страницы вписываются ссылки hreflang друг на друга, чтобы
поисковики знали о второй версии. Если после замены на английской странице осталась
кириллица (поменяли русский текст, а пару не обновили), сборка падает и показывает где.
"""
import re
PAGES = ["index.html", "direction.html", "news.html", "publications.html"]
NAME = "ITC «Bridge»"
FULL = "Interdisciplinary Technologies Center «Bridge»"

# общие для всех страниц: заголовки вкладок, соцсети, кнопки
COMMON = [
    ("ЦМТ «Мост» · Университет ИТМО", f"{NAME} · ITMO University"),
    ('aria-label="Закрыть"', 'aria-label="Close"'),
    (">написать<span", ">contact us<span"),
    ("назад</a>", "back</a>"),
    (">Показать еще<", ">Show more<"),
]

PAIRS = {
    "index.html": [
        ("Центр междисциплинарных технологий «Мост» физического факультета Университета ИТМО. Соединяем образование, науку и индустрию.",
         f"{FULL} of the ITMO University Faculty of Physics. Connecting education, science and industry."),
        ("Соединяем образование, науку и индустрию", "Connecting education, science and industry"),
        ('"name": "Центр междисциплинарных технологий «Мост»"', f'"name": "{FULL}"'),
        ('"alternateName": "ЦМТ «Мост»"', f'"alternateName": "{NAME}"'),
        ('"name": "Университет ИТМО"', '"name": "ITMO University"'),
        ('"addressLocality": "Санкт-Петербург"', '"addressLocality": "Saint Petersburg"'),
        ("assets/img/logo.png", "assets/img/logo-en.png"),
        ("<em>Соединяем</em><br>образование,<br>науку и индустрию", "<em>Connecting</em><br>education,<br>science and industry"),
        ("ЦМТ «Мост» — центр междисциплинарных технологий физического факультета Университета ИТМО",
         f"{NAME} is the Interdisciplinary Technologies Center of the ITMO University Faculty of Physics"),
        ('<h2 class="h2">ЦМТ «Мост»</h2>', f'<h2 class="h2">{NAME}</h2>'),
        ("центр, где научные идеи доводятся до практических<br>R&amp;D-решений и интегрируются в образование",
         "a center where research ideas grow into practical<br class=\"br-desk\">R&amp;D solutions and become part of education"),
        # цифры в разметке те же, что посчитает скрипт: меняются вместе с данными, поэтому по шаблону
        (re.compile(r'<p class="metric__title">(\d+) человек\w*</p>'), r'<p class="metric__title">\1 people</p>'),
        (re.compile(r'<p class="metric__title">(\d+) публикац\w*</p>'), r'<p class="metric__title">\1 publications</p>'),
        (re.compile(r'<p class="metric__title">(\d+) (?:лет|год\w*)</p>'), r'<p class="metric__title">\1 years</p>'),
        ("работает над наукой, образованием и технологиями центра", "work on the center’s research, education and technology"),
        ("опубликовано сотрудниками центра в высокорейтинговых журналах", "by the center’s researchers in high-impact journals"),
        ("ведется научно&#8209;образовательная деятельность центра (с 2015&nbsp;года)", "of research and teaching at the center (since 2015)"),
        ("работаем на стыке фундаментальной и прикладной направленности", "working where fundamental and applied research meet"),
        ('aria-label="Предыдущие направления"', 'aria-label="Previous research areas"'),
        ('aria-label="Следующие направления"', 'aria-label="Next research areas"'),
        ('aria-label="Научные направления"', 'aria-label="Research areas"'),
        ("от технического задания до готового продукта: реверс-инжиниринг, разработка технологий и производство микро- и наноструктур",
         "from technical specification to finished product: reverse engineering, technology development and fabrication of micro- and nanostructures"),
        ("Проработка <br>технического задания", "Working out <br>the specification"),
        ("Изготовление <br>макетов", "Building <br>prototypes"),
        ("Проведение <br>испытаний", "Running <br>tests"),
        ("Финальная упаковка <br>продукта", "Final product <br>packaging"),
        ("Реверс-инжиниринг оптического оборудования", "Reverse engineering of optical equipment"),
        ("Входное тестирование и деконструирование", "Incoming testing and teardown"),
        ("Анализ материалов и свойств", "Analysis of materials and their properties"),
        ("Построение CAD-моделей и цифровых двойников", "CAD models and digital twins"),
        ("Реверс оптомеханики, электроники и ПО", "Reverse engineering of optomechanics, electronics and software"),
        ("Разработка технологий<br>и оборудования", "Development of technologies<br>and equipment"),
        ("Лазерные технологии и устройства", "Laser technologies and devices"),
        ("Оптические системы и приборы", "Optical systems and instruments"),
        ("Тонкопленочные покрытия", "Thin-film coatings"),
        ("Малотоннажная химия", "Fine chemical synthesis"),
        ("Микрофлюидные устройства", "Microfluidic devices"),
        ('<h3 class="ind-photo__title">Оборудование</h3>', '<h3 class="ind-photo__title">Equipment</h3>'),
        (">подробнее <svg", ">more <svg"),
        ("https://physics.itmo.ru/ru/facilities", "https://physics.itmo.ru/en/facilities"),
        ("Производство микро- и наноструктур", "Fabrication of micro- and nanostructures"),
        ("Наночастицы:", "Nanoparticles:"),
        ('<span class="tag">золото</span><span class="tag">серебро</span><span class="tag">сульфида меди</span>',
         '<span class="tag">gold</span><span class="tag">silver</span><span class="tag">copper sulfide</span>'),
        ('<span class="tag">кремния</span><span class="tag">карбоната кальция</span><span class="tag">полимерные</span>',
         '<span class="tag">silicon</span><span class="tag">calcium carbonate</span><span class="tag">polymer</span>'),
        ("Квантовые точки сульфида серебра индия", "Silver indium sulfide quantum dots"),
        ("Металлорганические каркасы", "Metal–organic frameworks"),
        ('alt="Студентка настраивает оптическую схему в лаборатории"', 'alt="A student aligning an optical setup in the lab"'),
        ("Образовательный трек «Гибридные материалы»", "Educational track «Hybrid Materials»"),
        # на компьютере текст трека стоит без автопереноса, строки задают <br class="br-desk">.
        # Разбивка подобрана замером: английские строки той же ширины, что русские (822 px на 1920).
        # Название программы остается на двух языках, как в русской версии (решение владельца 24.09.2026)
        (re.compile(r'<p class="education__text">.*?</p>', re.S),
         '<p class="education__text"><b>Master’s program <span lang="ru">«Современные квантовые и нанофотонные <br class="br-desk">системы</span> / Advanced Quantum and Nanophotonic Systems».</b><br>\n'
         '          The track focuses on interdisciplinary research, so we welcome <br class="br-desk">'
         'students with different backgrounds (physicists, chemists, materials <br class="br-desk">'
         'scientists, biologists) who want to work at the intersection of sciences. <br class="br-desk">'
         'On this track you will learn the basics of numerical modeling, <br class="br-desk">'
         'materials science, experimental nanophotonics, as well as special <br class="br-desk">'
         'topics in organic chemistry and cell biology.</p>'),
        ('<span class="fact__full">код направления</span><span class="fact__short">направление</span>',
         '<span class="fact__full">program code</span><span class="fact__short">code</span>'),
        ('<p class="fact__note">Техническая физика</p>', '<p class="fact__note">Technical Physics</p>'),
        ('<span class="fact__full">язык обучения</span><span class="fact__short">язык</span>',
         '<span class="fact__full">language of study</span><span class="fact__short">language</span>'),
        ('<p class="fact__value">Английский</p>', '<p class="fact__value">English</p>'),
        ('<span class="fact__full">Форма · срок</span><span class="fact__short">форма</span>',
         '<span class="fact__full">Mode · duration</span><span class="fact__short">mode</span>'),
        ('<p class="fact__value">Очная</p><p class="fact__note">2 года</p>', '<p class="fact__value">Full-time</p><p class="fact__note">2 years</p>'),
        (">подробнее о треке<", ">more about the track<"),
        ('<h2 class="h2">Наука</h2>', '<h2 class="h2">Science</h2>'),
        ('<h2 class="h2">Индустрия</h2>', '<h2 class="h2">Industry</h2>'),
        ('<h2 class="h2">Образование</h2>', '<h2 class="h2">Education</h2>'),
        ('<h2 class="h2">Новости</h2>', '<h2 class="h2">News</h2>'),
        (">Все новости <svg", ">All news <svg"),
    ],
    "direction.html": [
        ("Научное направление Центра междисциплинарных технологий «Мост» Университета ИТМО: команда, исследования и публикации.",
         f"A research area of the {FULL}, ITMO University: team, research and publications."),
        ("Научное направление · ЦМТ «Мост»", f"Research area · {NAME}"),
        ('<h2 class="h2">О направлении</h2>', '<h2 class="h2">About</h2>'),
        ("Интересна совместная работа?", "Interested in working together?"),
        ("Расскажите о своей задаче или идее проекта, и мы обсудим, чем команда направления может помочь.",
         "Tell us about your task or project idea, and we will discuss how the team can help."),
        ('<h2 class="h2">Команда</h2>', '<h2 class="h2">Team</h2>'),
        ('aria-label="Предыдущие участники"', 'aria-label="Previous team members"'),
        ('aria-label="Следующие участники"', 'aria-label="Next team members"'),
        ('aria-label="Команда направления"', 'aria-label="Research area team"'),
        ('<h2 class="h2">Публикации</h2>', '<h2 class="h2">Publications</h2>'),
        (">все публикации <svg", ">all publications <svg"),
    ],
    "news.html": [
        ("Конференции, награды, достижения и новые проекты ЦМТ «Мост» Университета ИТМО.",
         f"Conferences, awards, achievements and new projects of {NAME}, ITMO University."),
        ("Новости · ЦМТ «Мост»", f"News · {NAME}"),
        ('alt="Команда ЦМТ «Мост» на причале у озера"', f'alt="The {NAME} team outdoors"'),
        ("<em>Новости</em><br>ЦМТ «Мост»", f"<em>News</em><br>{NAME}"),
        ("Конференции, награды, достижения <br>и новые проекты ЦМТ «Мост»", f"Conferences, awards, achievements <br>and new projects of {NAME}"),
        ('<h2 class="h2">Новость месяца</h2>', '<h2 class="h2">Story of the month</h2>'),
        ('<h2 class="h2">Все новости</h2>', '<h2 class="h2">All news</h2>'),
    ],
    "publications.html": [
        ("Статьи сотрудников ЦМТ «Мост» в рецензируемых журналах, труды конференций и патенты с 2015 года.",
         f"Papers by {NAME} researchers in peer-reviewed journals, conference proceedings and patents since 2015."),
        ("Статьи сотрудников ЦМТ «Мост» в рецензируемых журналах, труды конференций и патенты с 2015 года",
         f"Papers by {NAME} researchers in peer-reviewed journals, conference proceedings and patents since 2015"),
        ("Публикации · ЦМТ «Мост»", f"Publications · {NAME}"),
        ("<em>Публикации</em><br>ЦМТ «Мост»", f"<em>Publications</em><br>{NAME}"),
        ('aria-label="Фильтры публикаций"', 'aria-label="Publication filters"'),
        ('<span class="visually-hidden">Поиск</span>', '<span class="visually-hidden">Search</span>'),
        ('placeholder="Поиск по названию, автору или журналу"', 'placeholder="Search by title, author or journal"'),
        ('aria-label="Направление"><option value="">Все направления</option>', 'aria-label="Research area"><option value="">All research areas</option>'),
        ('aria-label="Год"><option value="">Все годы</option>', 'aria-label="Year"><option value="">All years</option>'),
        ('aria-label="Сортировка"', 'aria-label="Sort"'),
        ('<option value="new">Сначала новые</option>', '<option value="new">Newest first</option>'),
        ('<option value="old">Сначала старые</option>', '<option value="old">Oldest first</option>'),
        (">Сбросить<", ">Reset<"),
        ('<h2 class="h2">Все публикации</h2>', '<h2 class="h2">All publications</h2>'),
    ],
}


CYR = re.compile(r"[А-Яа-яЁё]")
HREFLANG = re.compile(r'\n  <link rel="alternate" hreflang="[^"]+" href="[^"]*">')


def page_url(site, name, lang):
    tail = "" if name == "index.html" else name
    return site + ("en/" if lang == "en" else "") + tail


def with_hreflang(text, site, name):
    """Ссылки на обе версии сразу после canonical"""
    text = HREFLANG.sub("", text)
    links = "".join(f'\n  <link rel="alternate" hreflang="{lang}" href="{page_url(site, name, code)}">'
                    for lang, code in [("ru", "ru"), ("en", "en"), ("x-default", "ru")])
    return re.sub(r'(<link rel="canonical" href="[^"]*">)', lambda m: m.group(1) + links, text, count=1)


def translate(text, pairs):
    """Сначала длинные фрагменты, потом короткие: иначе короткая пара съест кусок длинной"""
    unused = []
    plain = sorted([p for p in pairs if isinstance(p[0], str)], key=lambda p: -len(p[0]))
    regex = [p for p in pairs if not isinstance(p[0], str)]
    for pat, rep in regex:
        text, n = pat.subn(rep, text)
        if not n:
            unused.append(pat.pattern)
    for ru, en in plain:
        if ru in text:
            text = text.replace(ru, en)
        else:
            unused.append(ru)
    return text, unused


def english(ru, site, name):
    """Английская страница из русской. Отдает текст страницы, неиспользованные пары и строки с кириллицей."""
    text = re.sub(r"\s*<!--.*?-->", "", ru, flags=re.S)   # комментарии для разработчика, в них русский
    text, unused = translate(text, PAIRS[name] + COMMON)
    text = text.replace('<html lang="ru">', '<html lang="en">', 1)
    # адрес страницы: canonical, og:url и url организации ведут на английскую версию
    text = re.sub(r'(<link rel="canonical" href=")[^"]*(")', lambda m: m.group(1) + page_url(site, name, "en") + m.group(2), text)
    text = re.sub(r'(<meta property="og:url" content=")[^"]*(")', lambda m: m.group(1) + page_url(site, name, "en") + m.group(2), text)
    text = text.replace(f'"url": "{site}"', f'"url": "{site}en/"')
    text = re.sub(r'((?:href|src)=")assets/', r"\1../assets/", text)
    text = re.sub(r'(<script src="\.\./assets/js/data\.js" defer></script>)',
                  r'\1\n  <script src="../assets/js/en.js" defer></script>\n  <script src="../assets/js/en-content.js" defer></script>', text, count=1)
    text = text.replace("<!doctype html>", f"<!doctype html>\n<!-- Generated by tools/build.py from ../{name}. Do not edit by hand. -->", 1)
    # русский текст, оставленный намеренно, помечен <span lang="ru"> (название программы), его не считаем
    left = [f"{i}: {line.strip()[:120]}" for i, line in enumerate(text.splitlines(), 1)
            if CYR.search(re.sub(r'<span lang="ru">.*?</span>', "", line))]
    return text, unused, left


def build(dist, site):
    """Пишет dist/en/*.html и hreflang в русские страницы dist. Отдает список ошибок."""
    (dist / "en").mkdir(exist_ok=True)
    errors = []
    for name in PAGES:
        src = dist / name
        ru = with_hreflang(src.read_text(encoding="utf-8"), site, name)
        src.write_text(ru, encoding="utf-8", newline="\n")
        text, unused, left = english(ru, site, name)
        (dist / "en" / name).write_text(text, encoding="utf-8", newline="\n")
        for u in unused:
            # общие пары есть не на каждой странице, это нормально
            if not any(u == c[0] for c in COMMON):
                print(f"   ~ en/{name}: пара не нашлась в русской странице: {u[:90]}")
        errors += [f"en/{name}: осталась кириллица, допишите пары в tools/lib/english_pages.py: {line}" for line in left]
    return errors