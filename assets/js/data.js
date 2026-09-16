/* Контент сайта. Тексты взяты из макета Figma.
   Чтобы добавить публикацию, новость или направление, достаточно дописать объект сюда. */

window.SITE = {
  email: "bridge@metalab.ifmo.ru",
  phone: "+7 911 771 8421",
  links: {
    physics: "https://physics.itmo.ru/",
    itmo: "https://itmo.ru/",
    track: "https://abit.itmo.ru/",
  },
};

/* Научные направления. Карточки на главной и страницы direction.html?id=... */
window.DIRECTIONS = [
  { id: "eco-nano", title: "Экологически чистая нано- и микротехнология", team: 12, pubs: 7, image: "sci-1.webp", imagePos: "center bottom" },
  {
    id: "puf",
    title: "Неклонируемые защитные метки",
    heroTitle: "<em>Неклонируемые</em> защитные метки",
    subtitle: "Уникальные физические защитные метки, которые невозможно воспроизвести или скопировать",
    team: 5, pubs: 12, awards: "10+", conferences: "10+",
    image: "sci-2.webp", imagePos: "40% 45%",
    about: [
      "Команда данного направления исследует и создает физически неклонируемые метки для защиты товаров и документов от подделки. Уникальность меток возникает из случайностей при лазерной обработке материала, поэтому повторить метку не может даже ее изготовитель.",
      "Мы реализуем всю цепочку, от физики наноструктур и лазерной печати до алгоритмов распознавания и идентификации смартфоном. В качестве юнитов для меток используются резонансные кремниевые наночастицы, гибридные золото-кремниевые структуры, кремний-эрбиевые пленки и медные микроструктуры на гибкой подложке.",
    ],
    tags: ["PUF метки", "антиконтрафакт", "наноструктуры", "лазерная печать", "фотолюминесценция", "Компьютерное зрение", "гибкие подложки", "кремний", "золото", "эрбий"],
    people: [
      { name: "Дмитрий Зуев", role: "кандидат физико-математических наук, ведущий научный сотрудник", photo: "person-1.webp", pos: "45% center" },
      { name: "Павел Кустов", role: "кандидат физико-математических наук, научный сотрудник", photo: "person-2.webp", pos: "47% center" },
      { name: "Елена Петрова", role: "аспирант 3-го года, младший научный сотрудник", photo: "person-3.webp" },
      { name: "Мартин Сандомирский", role: "магистр 2-го года, инженер", photo: "person-4.webp" },
      { name: "Мария Федорова", role: "бакалавр 3-го года, лаборант", photo: "person-5.webp" },
    ],
  },
  { id: "hybrid-nanophotonics", title: "Гибридная металло-диэлектрическая нанофотоника", team: 18, pubs: 10, image: "sci-3.webp", imagePos: "center 30%" },
  { id: "ai-nanophotonics", title: "ИИ в нанофотонике", team: 18, pubs: 10, image: "sci-4.webp", imagePos: "center 40%" },
  { id: "integrated-nanophotonics", title: "Интегральная нанофотоника", team: 18, pubs: 10, image: "sci-5.webp", imagePos: "center 40%" },
  { id: "photothermal", title: "Фототермическая и регенеративная терапия", team: 18, pubs: 10, image: "sci-6.webp", imagePos: "center 55%" },
  { id: "drug-delivery", title: "Системы доставки лекарств и биоактивных веществ", team: 18, pubs: 10, image: "sci-7.webp", imagePos: "center 45%" },
  { id: "biosensing", title: "Биосенсорика", team: 18, pubs: 10, image: "sci-8.webp", imagePos: "center 50%" },
  { id: "microfluidics", title: "Микрофлюидные технологии", team: 18, pubs: 10, image: "sci-9.webp", imagePos: "center 40%" },
  { id: "bio-thermometry", title: "Измерение температуры в биологических объектах", team: 18, pubs: 10, image: "sci-10.webp", imagePos: "center 45%" },
];

/* Публикации. image можно не указывать, тогда будет зеленая заглушка. */
window.PUBLICATIONS = [
  {
    date: "2026-07-08", journal: "Langmuir", quartile: "Q1", direction: "puf",
    title: "Laser-Induced Stochastic Copper Microstructures for Flexible Physically Unclonable Labels",
    authors: "Elena Petrova, Viktoria Orekhova, Maria Fedorova, Martin Sandomirskii, Pavel Kustov, Kirill Bogdanov, Lev Logunov, Dmitry Zuev",
    desc: "Физически неклонируемые метки (PUF) защищают товар от подделки, но массовому выпуску мешают дорогая технология и особые материалы. В данной работе неклонируемую метку создают лазером прямо на гибком полиимиде, восстанавливая медь из эвтектического раствора.",
    tags: ["Медь", "лазеры", "производство", "растворители", "осаждение"],
    doi: "https://doi.org/10.1021/acs.langmuir.6c02138", image: "pub-1.webp",
  },
  {
    date: "2025-06-02", journal: "Nature Communications", quartile: "Q1", direction: "puf",
    title: "Spectral physical unclonable functions: downscaling randomness with multi-resonant hybrid particles",
    authors: "Martin Sandomirskii, Elena Petrova, Pavel Kustov, Lev Chizhov, Artem Larin, Stéphanie Bruyère, Vitaly Yaroshenko, Eduard Ageev, Pavel Belov, Dmitry Zuev",
    desc: "В данной работе случайность, которой характеризуется PUF метки, перенесена с микроуровня на наноуровень. Гибридные золото-кремниевые частицы обладают несколькими резонансами и неизбежно отличаются разбросом наноразмеров.",
    tags: ["Хранение информации", "Кремний-золото", "Фотолюминесценция", "криптография"],
    doi: "https://doi.org/10.1038/s41467-025-60121-9",
  },
  {
    date: "2025-06-12", journal: "ACS Applied Optical Materials", quartile: "Q2", direction: "puf",
    title: "Polarization-Sensitive Scattering from Tunable Hybrid Au–Si Nanoantennas for Anticounterfeiting Applications",
    authors: "Kustov P., Yaroshenko V., Sandomirskii M., Petrova E., Fedorova M., Ageev E., Mukhin I., Zuev D.A.",
    desc: "Поляризация света дает дополнительную степень свободы при считывании метки. Несимметричные гибридные золото-кремниевые наноантенны перестраивают фемтосекундным лазером, после чего их рассеяние по-разному меняется для разных поляризаций.",
    tags: ["Наноантенны", "Кремний-золото", "Рассеяние", "Поляризационно-зависимое"],
    doi: "https://doi.org/10.1021/acsaom.5c00156",
  },
  {
    date: "2024-09-16", journal: "The Journal of Physical Chemistry Letters", quartile: "Q1", direction: "puf",
    title: "IR Hidden Patterns for Security Labels",
    authors: "Vitaly Yaroshenko, Artem Larin, Sergey Syubaev, Ivan Vazhenin, Pavel Kustov, Dmitry Dolgintsev, Eduard Ageev, Stanislav Gurbatov, Alina Maksimova, Kristina Novikova, Sergey Babin, Aleksey Kozlov, Alexandr Dostovalov, Aleksandr Kuchmizhak, Dmitry Zuev",
    desc: "Скрытая метка, которую видно только в инфракрасном свете. Тонкую пленку кремний-эрбий-кремний обрабатывают фемтосекундным лазером, получая случайные или квазирегулярные нанотекстуры. Попутное окисление меняет оптику.",
    tags: ["эрбий", "Тонкие пленки", "Фемтосекундный лазер", "ИК-люминесценция"],
    doi: "https://doi.org/10.1021/acs.jpclett.4c02051",
  },
  {
    date: "2023-07-02", journal: "IEEE NANO 2023", direction: "puf",
    title: "Femtosecond Direct Laser Writing on Bi-Layer Gold-Silicon Films for Hidden Data Storage and Random Key Generation",
    authors: "Martin Sandomirskii, Ekaterina Ponkratova, Elena Petrova, Pavel Kustov, Artem Larin, Eduard Ageev, Dmitry Zuev",
    desc: "Данные пишут фемтосекундным лазером по двухслойной пленке золото-кремний при малой плотности энергии. В оптическом микроскопе запись не видна совсем, а считывается она по карте фотолюминесценции. Метод простой и стабильный, усложнять технику записи не требуется.",
    tags: ["Лазерная запись", "Кремний-золото", "Фотолюминесценция", "Случайные ключи"],
    doi: "https://doi.org/10.1109/NANO58406.2023.10231269",
  },
  {
    date: "2023-07-02", journal: "IEEE NANO 2023", direction: "puf",
    title: "Multiphoton Luminescence in Resonant Silicon Nanoparticles for Physically Unclonable Anticounterfeiting Labels",
    authors: "Elena Petrova, Pavel Kustov, Martin Sandomirskii, Yali Sun, Dmitry Zuev",
    desc: "Метка из резонансных кремниевых наночастиц, напечатанных лазерным переносом, уже дает несколько уровней защиты, это координаты частиц, их цвет и разброс радиусов. Здесь добавлен еще один уровень, многофотонная фотолюминесценция кремния. Она зависит от индивидуальных свойств каждой частицы, поэтому усложняет копирование метки и повышает емкость кодирования.",
    tags: ["Резонансы Ми", "Кремний", "наночастицы", "Многофотонная люминесценция"],
    doi: "https://doi.org/10.1109/NANO58406.2023.10231179",
  },
  {
    date: "2022-08-04", journal: "Advanced Functional Materials", quartile: "Q1", direction: "puf",
    title: "Coding of Non-Linear White-Light Luminescence from Gold-Silicon Structures for Physically Unclonable Security Labels",
    authors: "Ekaterina Ponkratova, Eduard Ageev, Peter Trifonov, Pavel Kustov, Martin Sandomirskii, Mikhail Zhukov, Artem Larin, Ivan Mukhin, Thierry Belmonte, Alexandre Nomine, Stéphanie Bruyère, Dmitry Zuev",
    desc: "Гибридные металл-полупроводниковые структуры пишут фемтосекундным лазером, они дают нелинейное белое свечение. Спектр свечения связан с внутренним составом структуры, поэтому спектры соседних элементов отличаются.",
    tags: ["Нелинейная люминесценция", "Кремний-золото", "Полярные коды", "Кодирование"],
    doi: "https://doi.org/10.1002/adfm.202205859",
  },
  {
    date: "2022-08-02", journal: "ACS Applied Nano Materials", quartile: "Q1", direction: "puf",
    title: "Mie-Resonant Silicon Nanoparticles for Physically Unclonable Anti-Counterfeiting Labels",
    authors: "Pavel Kustov, Elena Petrova, Mikhail Nazarov, Almaz Gilmullin, Martin Sandomirskii, Ekaterina Ponkratova, Vitaly Yaroshenko, Eduard Ageev, Dmitry Zuev",
    desc: "Метка собрана из кластеров кремниевых наночастиц с резонансами Ми, напечатанных лазерным переносом. Первый уровень защиты дают число кластеров и их взаимное расположение, это видно в обычной оптике.",
    tags: ["Резонансы Ми", "Кремний", "наночастицы", "Лазерный перенос", "Кластеризация"],
    doi: "https://doi.org/10.1021/acsanm.2c01878",
  },
  {
    date: "2022-09-12", journal: "Metamaterials 2022", direction: "puf",
    title: "All-dielectric silicon nanoparticles on flexible substrate for anticounterfeiting labels",
    authors: "Pavel Kustov, Elena Petrova, Martin Sandomirskii, Dmitry Zuev",
    desc: "Кремниевые наночастицы печатают фемтосекундным лазером прямо на полипропиленовую пленку, то есть на гибкую и дешевую подложку. Частицы резонансные, их оптический отклик вместе со случайным расположением по площади годится как криминалистический уровень защиты.",
    tags: ["Гибкая подложка", "Кремний", "Рассеяние", "наночастицы", "полипропилен"],
    doi: "https://doi.org/10.1109/Metamaterials54993.2022.9920716",
  },
  {
    date: "2022-02-01", journal: "JETP Letters", quartile: "Q2", direction: "puf",
    title: "Resonant Hybrid Metal-Dielectric Nanostructures for Local Color Generation",
    authors: "E. I. Ageev, V. A. Iudin, Y. Sun, E. A. Petrova, P. N. Kustov, V. V. Yaroshenko, J. V. Mikhailova, A. S. Gudovskikh, I. S. Mukhin, D. A. Zuev",
    desc: "Локальный цвет наноструктуры меняют лазером. Несимметричные золото-кремниевые наноструктуры переплавляют фемтосекундным импульсом, резонанс сдвигается в диапазоне от 500 до 800 нанометров.",
    tags: ["Генерация цвета", "Кремний-золото", "деветтинг", "Рассеяние"],
    doi: "https://doi.org/10.1134/S0021364022040014",
  },
  {
    date: "2021-03-11", journal: "Advanced Materials", quartile: "Q2", direction: "puf",
    title: "Luminescent Erbium-Doped Silicon Thin Films for Advanced Anti-Counterfeit Labels",
    authors: "Artem Larin, Liliia N. Dvoretckaia, Alexey Mozharov, Ivan Mukhin, Artem Cherepakhin, Ivan Shishkin, Eduard Ageev, Dmitry Zuev",
    desc: "Метка светится в инфракрасном на длине волны 1530 нанометров. Двухслойную пленку эрбий на кремнии облучают фемтосекундным лазером, эрбий входит в кремниевую матрицу, кремний кристаллизуется, и возникают оптически активные центры.",
    tags: ["Эрбий", "Кремниевые пленки", "Фотолюминесценция", "Прямая лазерная запись"],
    doi: "https://doi.org/10.1002/adma.202005886",
  },
  {
    date: "2016-01-06", journal: "Advanced Materials", quartile: "Q1", direction: "puf",
    title: "Fabrication of Hybrid Nanostructures via Nanoscale Laser-Induced Reshaping for Advanced Light Manipulation",
    authors: "Dmitry Zuev, Sergey Makarov, Valentin Milichko, S. V. Starikov, Ivan Mukhin, I. A. Morozov, Ivan Shishkin, Alexander Krasnok, Pavel Belov",
    desc: "Базовая работа группы по лазерной переплавке. Асимметричные металл-диэлектрические наночастицы золото-кремний делают литографией, а затем плавят фемтосекундным лазером. Плавится только металлическая часть, кремниевая остается целой.",
    tags: ["Хранение информации", "Кремний-золото", "Управление светом", "деветтинг"],
    doi: "https://doi.org/10.1002/adma.201505346",
  },
];

/* Новости. В макете карточки-заглушки одинаковые, заменить на реальные. */
const PLACEHOLDER_NEWS = {
  tag: "Грант", date: "2026-05-14", image: "news-1.webp",
  title: "Сотрудники центра выступили на ICLO-2026",
  text: "Финансирование направлено на новое оборудование для синтеза квантовых точек и масштабирование прикладных R&D-проектов с индустриальными партнерами",
};

window.NEWS = [
  {
    id: "kustov-phd", featured: true, tag: "Достижение", date: "2026-05-14", image: null,
    title: "Новоиспеченный кандидат физико-математических наук Павел Кустов",
    text: "Его исследования посвящены разработке и изучению оптических свойств кремниевых микро- и наносистем, которые могут стать основой для передовых масштабируемых нанофотонных защитных меток.",
    body: {
      lead: "Его исследования посвящены разработке и изучению оптических свойств кремниевых микро- и наносистем, которые могут стать основой для передовых масштабируемых нанофотонных защитных меток.",
      quote: [
        "Спрос на надежные технологии защиты от подделок стремительно растет. Существующие решения, представленные на рынке, уже не обеспечивают достаточного уровня безопасности, поэтому все большее развитие получает направление физически неклонируемых меток.",
        "Такие метки невозможно воспроизвести или скопировать даже производителю. Нанофотонные структуры на основе кремния открывают путь к созданию подобных технологий благодаря своей универсальности и оптической стабильности.",
      ],
      note: "В своей работе Павел показывает, как управление оптическими свойствами четырех различных типов нанофотонных структур позволяет создавать скрытые физически неклонируемые защитные метки.",
    },
  },
  ...Array.from({ length: 8 }, (_, i) => ({ id: `news-${i + 1}`, ...PLACEHOLDER_NEWS })),
];
