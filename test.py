import sqlite3 as sq
def part_request(word):
    match len(word):
        case 3:
            return word
        case 4:
            return word[:-1]
        case 5:
            return word[:-1]
        case 6:
            return word[:-2]
        case _:
            return word[:-3]

with sq.connect('newDB.db') as conn:
    cursor = conn.cursor()

    # Пример исходного словаря с категориями и продуктами
    dictionary = {
        "зефир": ("сахарная пудра", "агар", "сахар", "коробки", "черная смородина", "фисташка", "миндаль", "грецкий орех",
                  "глюкозный сироп", "зефир", "твороженный сыр","сливки", "калибо", "пектин", "пакет", "малина",
                  "сублимирован",
                  "бумага для выпечки", "желатин", "фундук", "клубника", "упаковка", "кондитер", "шоколад", "темный",
                  "белый"),
        'овощи': ('морковь','тыква','картофель', 'свекла', 'капуста', 'лук', 'чеснок', 'огурец', ' помидор',
                  'зелень', 'овощи','черри', "томат"),
        'фрукты': ('яблоки', 'груша', 'апельсин','персик', 'банан', 'персик', 'абрикос', 'чернослив', 'арбуз', 'слива',
                   'дыня', 'вишня', 'киви',"клубника", "черника", "лимон"),
        'молочка': ('молоко', 'кефир', 'творог', 'сметана', 'сыр', 'сливки', 'айран', 'йогурт', "масло",
                    "моцарелла"),
        'мясо': ('колбаса', 'курица', 'шея', 'фарш', 'говядина', 'сосики', 'мясо',"грудка"),
        'хлеб': ('шоти', 'хлеб','лаваш'),
        "яйца": ("яйца",),
        'п/фабрикаты': ('пельмени', 'хинкали', 'курица-гриль', "блинчики"),
        'крупы': ('макароны','спагетти' ,'булгур','мука','рис'),
        "др. продукты": ("продукты Carrefour","продукты Низилбе", "подсолнечное масло", "соус", "майонез", "сода",
                            "соль", "уксус", "оливки", "томатная паста","специи", "продукты", "аджика"),
        'вкусняшки': ('печенье', 'Барни', 'шоколадка', 'сникерс', 'сушки', 'пироженка', 'булочка', 'гамбургер',
                      'пирожок', 'хачапури', "пирожок", "мороженое", "жвачка", "чипсы"),
        'напитки': ('сок', 'газировка', 'кола', 'компот', 'минералка','чай','кофе', "растворимый"),
        "животные": ("корм", "котята", "таблетки глистогон", "смесь", "паштет", "собак", "несквик"),
        'алкоголь': ('пиво', 'шампанское', 'вино', 'чача', 'коньяк', 'целикаури', 'саперави', 'игристое вино'),
        "бытовая химия":("зубная паста","порошок", "стиральный порошок", "мыло", "хозяйствен", "шампунь", "жидкость для стирки",
        "бумага туалет"),
        'Уля':('театральная студия','театр','подготовка к школе','гимнастика', "канцелярия", "картон", "цветная",
               "альбом", "листы", "носки", "маркеры"),
        'связь': ('телефон', 'интернет', 'минуты', 'magti', 'silknet', "magti", "сотовый"),
        'комуналка': ('газ', 'электричество', 'вода','коммуналка', "ситиком"),
        "ремонт": ("гидроизоляция", "краска"),
        'кафе': ('кафе', 'Dona'),
        'транспорт':('проезд','такси', "автобус")
    }
    # Создаем таблицу категорий
    cursor.executescript('''DROP TABLE IF EXISTS categories;
                   CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY, name TEXT)''')
    # Создаем таблицу товаров с внешним ключом, связывающим товары с категориями
    cursor.executescript('''DROP TABLE IF EXISTS products;
                CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, 
                name TEXT, 
                category_id INTEGER, 
                FOREIGN KEY(category_id) REFERENCES categories(id))''')

    for category in dictionary.keys():
        cursor.execute('INSERT INTO categories (name) VALUES (?)', (category,))

    # Получаем id вставленных категорий
    cursor.execute('SELECT id, name FROM categories')
    categories = cursor.fetchall()
    # создаем словарь категория - ID
    category_ids = {name: category_id for category_id, name in categories}

    # Вставляем товары в таблицу products, связывая их с соответствующими категориями
    for category, products in dictionary.items():
        category_id = category_ids[category]
        for product in products:
            cursor.execute('INSERT INTO products (name, category_id) VALUES (?, ?)', (product, category_id))
    conn.commit()

    def find_category(product):
        product = part_request(product)
        cursor.execute(f'SELECT category_id FROM products WHERE name LIKE "{product}%"')
        categori_id = cursor.fetchall()
        if len(categori_id) == 0:
            raise ("товар не известен")
        categori_id = int(categori_id[0][0])
        try:
            for key, val in category_ids.items():
                if val == categori_id:
                    return key
        except: ValueError("товар не известен")

    while True:
        x = input("введите товар: ")
        print(find_category(x))

