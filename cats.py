import re
from datetime import datetime
from typing import NamedTuple
# import pandas as pd
import exceptions
import database

class Note(NamedTuple):
    #Структура сообщения
    name: str
    sub_name: str
    price: float
    data: str
    raw: str

Category = {
    "зефир": ("сахарная пудра", "агар", "сахар", "коробки", "черная смородина", "фисташка", "миндаль", "грецкий орех",
                  "глюкозный сироп", "зефир", "твороженный сыр","сливки", "калибо", "пектин", "пакет", "малина",
              "сублимирован", "бумага для выпечки", "желатин", "фундук", "клубника", "упаковка", "кондитер", "шоколад", "темный",
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
    'транспорт':('проезд','такси', "автобус"),
    'другое': (None,),
    'крупные покупки': (None,)}

categori = list(map(lambda x: x, Category.keys()))
categories = [[x] for x in categori[:-2]]
# df = pd.DataFrame(list(Category.items()), columns=['Category', 'Products'])

def dots(x):
    # замена <,> на <.> в сообщениях
    return x.replace(',', '.')
def isdate(text:str):
    # шаблон для поиска даты в строках
    pattern = r"(\d+)\s+(\w+)\s+(\d+)"
    return re.fullmatch(pattern, text)

def format_date(text:str) -> str:
    # переводим дату в строку
    day = datetime.strptime(text, '%d %B %Y')
    return str(day.date())

def pars_message(message: str) -> list:
    # парсит сообщение из входящей строчки, возвращает список продукт, цена
    pattern_1 = r"([\w+'& \-,.(/)]+) ((?<=\s)\d{0,3}[\.|,]?\d{1,2})"
    pattern_2 = r"(\d{0,3}[\.|,]?\d{1,2}) ((?<=\s)[\w+ ,.\-(/)]+)"
    x1 = re.match(pattern_1, message)
    x2 = re.match(pattern_2, message)
    if isinstance(x1, re.Match):
        return [x1[1], dots(x1[2])]
    elif isinstance(x2, re.Match):
        return [x2[2], dots(x2[1])]
    else:
        raise exceptions.MessageError ('не парсится')
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


def category_finder(product):
    product = part_request(product)
    database.cursor.execute(f'SELECT category_id FROM products WHERE name LIKE "{product}%"')
    categori_id = database.cursor.fetchall()
    categori_id = int(categori_id[0][0])
    try:
        for key, val in category_ids.items():
            if val == categori_id:
                return key
    except: ValueError("товар не известен")

# def category_finder (raw_message: str) -> str:
#     # поиск и присвоение категории трате
#     sub_name = 'другое'
#     for key, value in Category.items():
#         if raw_message.lower() in value:
#             sub_name = key
#             break
#         else:
#             continue
#     return sub_name

# def category_finder(product: str) -> str:
#     df['MatchScore'] = df['Products'].apply(lambda x: fuzz.partial_ratio(product.lower(), x))
#     max_score = df['MatchScore'].max()
#     category = df.loc[df['MatchScore'] == max_score, 'Category'].values[0]
#     return category

def make_note(row_message:str, date:str) -> Note:
    # формируем сообщение в формате Note
    message = pars_message(row_message)
    sub_name =  category_finder(message[0])
    if category_finder(message[0])=='другое' and float(message[1]) > 100:
       sub_name = 'крупные покупки'
    message.extend([sub_name, date, row_message])
    message[1], message[2], message[3] = message[2], message[1], message[3]
    return Note._make(message)
