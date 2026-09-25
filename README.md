# Сайт ЦМТ «Мост»

Сайт Центра междисциплинарных технологий «Мост» физического факультета Университета ИТМО.
Сверстан по макету в Figma. Статический сайт на HTML, CSS и JS без фреймворков, данные в JSON,
сборка на чистом Python. Публикуется на GitHub Pages через GitHub Actions, готов к переезду
на свой сервер (`deploy/README.md`).

## Структура

```
site/                исходники сайта: страницы, стили, скрипты, картинки, шрифты
  index.html         главная: о центре, наука, индустрия, образование, новости
  direction.html     страница научного направления (direction.html?id=puf)
  publications.html  все публикации с поиском, фильтрами и видом «карточки / список»
  news.html          новости, новость месяца и окно новости (news.html?open=<id>)
  404.html           «не найдено», одна на обе версии, ее тег base вписывает сборка
  assets/css         style.css (1rem = 10px на ширине 1920, дальше масштабируется), fonts.css
  assets/js          layout.js (шапка, подвал, типографика, язык), main.js (логика страниц),
                     en.js (словарь интерфейса английской версии)
content/             данные сайта, из них сборка пишет assets/js/data.js и другие файлы данных
  *.json             site, people, directions, publications, news, abstracts, citations, english
  manual/            ручные правки владельца: абстракты, даты, теги, ссылки, заголовки новостей
  collected/         собранное из внешних сервисов: база статей, карта квартилей журналов
  edit/              рабочие листы в markdown: владелец правит, скрипт забирает правки
tools/               сборка, проверка и скрипты для контента (у каждого описание в начале файла)
deploy/              конфигурация nginx и инструкция для переезда на свой сервер
docs/                план работ, бэклог, отчеты
data/                исходники владельца, только на его машине: книга, анкета, фото, SJR, Figma
dist/                собранный сайт (появляется после сборки, в git не уходит)
```

Подробнее про данные: `content/README.md`.

## Посмотреть локально

```powershell
python tools/serve.py
```

Сайт соберется и откроется на http://127.0.0.1:8000/cmt-most-site/, по тому же пути, что
и в интернете. После правки исходников сервер надо перезапустить: он собирает сайт при старте.

## Сборка и проверка

```powershell
python tools/build.py     # собрать dist/: данные, английские страницы, sitemap, метки версий
python tools/smoke.py     # собрать и проверить: ошибки JS, битые картинки, горизонтальный
                          # скролл, нарушения CSP, 404, сценарии на 4 ширинах и в окнах разной высоты
python tools/smoke.py --shots                                            # плюс скриншоты в tools/shots/
python tools/smoke.py --base https://pavelkustov.github.io/cmt-most-site/  # проверить живой сайт
```

Сборке нужен только Python. Скриптам для контента и смоуку нужны пакеты:

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
```

Проверка кода скриптов: `python -m pyflakes tools`.

## Публикация

Пуш в `main` запускает GitHub Actions (`.github/workflows/deploy.yml`): сборка, смоук, проверка
кода и выкладка `dist/` на GitHub Pages. Если смоук упал, сайт не обновляется. Наружу уходит
только собранный сайт: исходники, скрипты, документы и база статей по адресу сайта не открываются.

В настройках репозитория источник Pages: Settings → Pages → Source: **GitHub Actions**.

Адрес сайта задан в одном месте, `content/site.json` (поле `url`). Переезд на другой домен
описан в `deploy/README.md`.

## Как менять контент

| Что | Где правится | Чем переносится на сайт |
|---|---|---|
| Новости | анкета `data/news/011_Новости.docx` | `python tools/news/form.py` |
| Фото новостей | `data/photos/<номер новости>.jpg` | `python tools/news/photos.py` |
| Заголовки новостей | `content/edit/NEWS_TITLES_LINES.md` | `python tools/news/titles.py --import` |
| Сотрудники | книга `data/book/ЦМТ Мост.xlsx` | `python tools/people/book.py` |
| Тексты направлений | `content/edit/DIRECTIONS_TEXT.md` | `python tools/texts/directions.py --import` |
| Английские тексты | `content/edit/EN_*.md` | `python tools/texts/english.py --import` |
| Новые публикации | OpenAlex, ORCID, Crossref | `python tools/publications/collect.py`, затем `to_site.py` |
| Абстракты, даты, теги | `content/edit/*_MISSING.md` | `abstracts.py`, `dates.py`, `tags.py` с ключом `--import-md` |
| Квартили журналов | выгрузки SJR в `data/sjr` | `python tools/publications/enrich.py` |

После добавления публикаций: `tools/publications/citations.py` (данные для окна «Цитировать»),
`enrich.py` (квартиль и цитирования), `abstracts.py`, `titles.py`, `tags.py`, `authors.py`, `dates.py`.

Руками в JSON правится только то, чего нет в анкетах и книге: `heroTitle` и картинки направлений,
размеры команды для направлений без списка людей, словари `MANUAL` в скриптах. Цифры центра
на главной и метрики направлений считаются в `main.js` по данным, руками не задаются.

Картинки кладутся в `site/assets/img/` (лучше WebP до 300 КБ), в данных указывается имя файла.
Шрифты Inter и Roboto лежат в `site/assets/fonts` (из России так быстрее и нет зависимости
от Google Fonts), обновляет их `python tools/assets/fonts.py`. Картинки превью для соцсетей
и PNG-иконки рисует `python tools/assets/share_images.py`.

## Безопасность

- Политика CSP в `<meta>` каждой страницы: скрипты, стили, шрифты и картинки только с самого
  сайта, встроенных скриптов и атрибутов `style` нет. Смоук ловит любое нарушение политики.
- Внешних скриптов и счетчиков нет, данные из адреса (`?id=`, `?open=`) используются только
  как ключ поиска, текст экранируется при выводе.
- Персональные данные из книги сотрудников (почты, телефоны, даты рождения, идентификаторы)
  в репозиторий не переносятся, исходники владельца закрыты правилами `.gitignore`.
- Заголовки сервера (HSTS, запрет встраивания, nosniff) задаются на своем сервере,
  готовая конфигурация в `deploy/`.
