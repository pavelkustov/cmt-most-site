# Работы с неполной датой

У этих работ в дате нет дня, а иногда и месяца: так их отдают OpenAlex и Crossref.
Полная дата обычно стоит на странице статьи у издателя, например «15 December 2026».
Откройте ссылку и впишите дату под заголовком «Дата», вместо строки-подсказки.
Понимаются три формата: 15.12.2026, 2026-12-15 и 15 December 2026.

Потом: `python tools/fix_dates.py --import-md` перенесет даты
в `docs/dates_manual.json` и проставит их в `data.js`.

Всего работ: 1

## Topological States of Interacting Photon Pairs Emulated in a Topolectrical Circuit

<!-- doi: title:topologicalstatesofinteractingphotonpairsemulatedinatopolect -->

2019 Photonics   Electromagnetics Research Symposium - Fall (PIERS - Fall). Сейчас на сайте: 2019

DOI у работы нет, искать по названию в поиске издателя или в eLibrary

### Дата

_впишите сюда_
