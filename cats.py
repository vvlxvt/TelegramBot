import re
from datetime import datetime
from typing import NamedTuple
import pandas as pd
from fuzzywuzzy import fuzz
import exceptions


class Note(NamedTuple):
    #Структура сообщения
    name: str
    sub_name: str
    price: float
    data: str
    raw: str

Category = {
    'овощи': ('морковь','тыква','картофель', 'свекла', 'капуста', 'лук', 'чеснок', 'огурец', ' помидор',
              'зелень', 'овощи','черри', "томат"),
    'фрукты': ('яблоки', 'груша', 'апельсин','персик', 'банан', 'персик', 'абрикос', 'чернослив', 'арбуз', 'слива',
               'дыня', 'вишня', 'киви',"клубника", "черника","мандарин"),
    "яйца": ("яйца"),
    'молочка': ('молоко', 'кефир', 'творог', 'сметана', 'сыр', 'сливки', 'айран', 'йогурт', "сыр", "масло"),
    'мясо': ('колбаса', 'курица', 'шея', 'фарш', 'говядина', 'сосики', 'мясо',"грудка"),
    'хлеб': ('шоти', 'хлеб','лаваш'),
    "яйца": ("яйца"),
    'полуфабрикаты': ('пельмени', 'хинкали', 'курица-гриль', "блинчики"),
    'крупы': ('макароны','спагетти' ,'булгур','мука','рис'),
    "другие продукты": ("продукты Carrefour","продукты Низилбе", "подсолнечное масло", "соус", "майонез", "сода",
                        "соль", "уксус", "оливки", "томатная паста","специи"),
    'вкусняшки': ('печенье', 'Барни', 'шоколад', 'сникерс', 'сушки', 'пироженка', 'булочка', 'гамбургер', 'пирожок', 'хачапури',
    "мороженое"),
    'напитки': ('сок', 'газировка', 'кола', 'компот', 'минералка','чай','кофе'),
    "животные": ("корм Несквику", "корм котятам"),
    'алкоголь': ('пиво', 'шампанское', 'вино', 'чача', 'коньяк', 'целикаури', 'саперави', 'игристое вино'),
    "бытовая химия":("зубная паста","порошок", "стиральный порошок", "мыло","шампунь", "жидкость для стирки"),
    'Уля':('театральная студия','театр','подготовка к школе','гимнастика', "канцелярия"),
    'связь': ('телефон', 'интернет', 'минуты', 'magti', 'silknet', "magti", "сотовый"),
    'комуналка': ('газ', 'электричество', 'вода','коммуналка'),
    'кафе': ('кафе', 'Dona'),
    'транспорт':('проезд','такси', "автобус"),
    'другое': (None,),
    'крупные покупки': (None,),
    'Итого': (None,)
}

categori = list(map(lambda x: x, Category.keys()))
categories = [[x] for x in categori]
df = pd.DataFrame(list(Category.items()), columns=['Category', 'Products'])

def dots(x):
    # замена <,> на <.>
    return x.replace(',', '.')
def isdate(text:str)-> bool:
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

def category_finder(product: str) -> str:
    df['MatchScore'] = df['Products'].apply(lambda x: fuzz.partial_ratio(product, x))
    max_score = df['MatchScore'].max()
    category = df.loc[df['MatchScore'] == max_score, 'Category'].values[0]
    return category

def make_note(row_message:str, date:str) -> Note:
    # формируем сообщение в формате Note
    message = pars_message(row_message)
    sub_name = category_finder(message[0])
    if category_finder(message[0])=='другое' and float(message[1]) > 100:
       sub_name = 'крупные покупки'
    message.extend([sub_name, date, row_message])
    message[1], message[2], message[3] = message[2], message[1], message[3]
    return Note._make(message)
