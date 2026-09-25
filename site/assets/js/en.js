/* Английская версия: словарь интерфейса и переводы данных.
   Грузится только на страницах en/ (их собирает tools/build.py), после data.js.
   ui: строка интерфейса по-русски → по-английски, ее спрашивает t() из layout.js.
   directions, news, people: переводы полей по id направления, id новости и имени человека,
   их подставляет tr() поверх русских данных. Чего нет в переводе, остается по-русски.
   Полное название центра взято с английского логотипа: Interdisciplinary Technologies Center «Bridge»,
   краткое по образцу «ЦМТ «Мост»»: ITC «Bridge». */
window.EN = {
  ui: {
    // шапка и подвал
    "ЦМТ «Мост», на главную": "ITC «Bridge», home page",
    "Меню": "Menu",
    "Основное меню": "Main menu",
    "Главная": "Home",
    "наука": "science",
    "индустрия": "industry",
    "образование": "education",
    "Новости": "News",
    "Научные <br>направления": "Research <br>areas",
    "Публикации": "Publications",
    "Наверх": "Back to top",
    "О нас": "About us",
    "Наука": "Science",
    "Индустрия": "Industry",
    "Образование": "Education",
    "Документы": "Documents",
    "Политика по обработке<br>персональных данных": "Personal data<br>processing policy",
    "Информация об организации": "About the organization",
    "Сайт нового физтеха": "Faculty of Physics website",
    "Сайт ИТМО": "ITMO website",
    "Контакты": "Contacts",
    "© Все права защищены": "© All rights reserved",
    "ЦМТ «Мост» · Университет ИТМО": "ITC «Bridge» · ITMO University",
    "ЦМТ «Мост»": "ITC «Bridge»",

    // окна
    "написать": "contact us",
    "Написать нам": "Contact us",
    "Мы открыты к сотрудничеству и рады любым вопросам. Расскажите о своей задаче или идее, и мы подскажем, чем можем помочь.":
      "We are open to collaboration and happy to answer any questions. Tell us about your task or idea, and we will see how we can help.",
    "открыть почту": "open email",
    "скопировать адрес": "copy address",
    "Закрыть": "Close",
    "Скопируйте вручную": "Copy manually",
    "Скопировано": "Copied",

    // публикации
    "Цитировать": "Cite",
    "Скопировать": "Copy",
    "копировать": "copy",
    "ГОСТ": "GOST",
    "Показать абстракт целиком": "Show full abstract",
    "Свернуть абстракт": "Collapse abstract",
    "весь абстракт": "full abstract",
    "свернуть": "collapse",
    "Ключевые теги": "Keywords",
    "подробнее": "more",
    "Ничего не найдено. Попробуйте изменить фильтры.": "Nothing found. Try changing the filters.",
    "Вид списка": "List view",
    "Карточки": "Cards",
    "Список": "List",
    "Найдено": "Found",

    // направления
    "человек в команде": "people on the team",
    "публикаций": "publications",
    "цитирований": "citations",
    "индекс Хирша": "h-index",
    "статей в Q1 и Q2": "papers in Q1 and Q2",
    "читать полностью": "read more",
    "Научное направление ЦМТ «Мост»": "Research area of ITC «Bridge»",
    "Описание направления готовится. Пока можно написать нам, и мы расскажем о проектах команды.":
      "The description of this research area is on its way. Meanwhile, write to us and we will tell you about the team’s projects.",
    "Совместная работа": "Collaboration",

    // новости
    "Читать": "Read",
    "Конференция": "Conference",
    "Достижение": "Achievement",
    "Публикация": "Publication",
    "Событие": "Event",
    "Интервью": "Interview",
    "Статья": "Article",
  },

  // переводы данных появятся на следующих этапах: направления и люди, затем новости
  directions: {},
  people: {},
  news: {},
};

// у сайтов ИТМО и физфака есть английские версии
Object.assign(SITE.links, { itmoEn: "https://en.itmo.ru/", physicsEn: "https://physics.itmo.ru/en" });
