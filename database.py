import sqlite3 as sq
import cats
import calendar
import matplotlib.pyplot as plt
from datetime import datetime

def init_db():
    with open("commands.sql", "r") as script:
        sql = script.read()
    cursor.executescript(sql)
    connection.commit()
    print('init_db complete!')

def upload_data(table, row)->list:
    # выгрузка базы данных из таблиц
    cursor.execute(f'SELECT {row} FROM {table} LIMIT 1300')
    selection = cursor.fetchall()
    return [x[0] for x in selection]

def insert_data(note: list[cats.Note]):
    print('insert data: ', len(note))
    # запись распаршенного сообщения в базу main
    cursor.executemany('INSERT INTO main(name, sub_name, price, created, raw) VALUES(?,?,?,?,?)', note)
    connection.commit()
    print('ok')

def delete_note():
    # удаляет последнюю запись
    cursor.execute('DELETE FROM main WHERE id = (SELECT MAX(id) FROM main)')
    connection.commit()

def list_to_string(data:list)->str:
    # преобразует список кортежей значений категорий в обзац текста
    return ' '.join([x[0]+': ' + str(x[1]) + '\n' for x in data])

def diagram(labels, values):
    plt.pie(values[:-9], labels=labels[:-9], autopct='%1.1f%%')
    plt.axis('equal')
    plt.title('Month stats')
    plt.savefig('diagram.png')

def get_month(month:int)-> str:
    # Получение даты начала и конца месяца
    year = datetime.now().year # получаем текущий год
    _, last_day = calendar.monthrange(year, month)
    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month:02d}-{last_day}"
    for cat in cats.categori:
    # выборка значений трат в указанный месяц из таблицы main
        sql = f'''UPDATE month
                SET total_price = (SELECT ROUND(SUM(price),2)
                FROM main WHERE created BETWEEN '{start_date}' AND '{end_date}' and sub_name = '{cat}') 
                WHERE sub_name = '{cat}';'''
        cursor.execute(sql)
    cursor.execute(f'''UPDATE month SET total_price = (SELECT SUM(total_price) 
                        FROM month) WHERE sub_name = "Итого"''')
    # вставляем в значение Итого сумму все покупок за месяц
    cursor.execute(f'SELECT * FROM month')
    data = cursor.fetchall() #считываю все строчки из таблицы month
    data = list(filter(lambda x: None not in x, data)) # убираю пустые строчки
    labels, values = zip(*data) # формирую списки данных для диаграммы
    diagram(labels,values)
    connection.commit()
    return list_to_string(data)

def check_table(name):
    cursor.execute(f'SELECT sub_name FROM {name}')
    sub_cats = cursor.fetchall()
    if sub_cats:
        return True

def init_table(name):
    # в таблице day прописываем названия категорий
    if check_table(name):
        pass
    else:
        cursor.executemany(f'INSERT INTO {name} (sub_name) VALUES (?)', cats.categories )
    connection.commit()

def get_today()-> str:
    # Подытог трат за сегодня
    date = datetime.now().date()
    for cat in cats.categori:
    # выборка значений трат в текущий день
        sql = f'''UPDATE day
                SET total_price = (SELECT ROUND(SUM(price),2)
                FROM main WHERE created="{date}" and sub_name = '{cat}') 
                WHERE sub_name = '{cat}';'''
        cursor.execute(sql)
    cursor.execute(f'''UPDATE day SET total_price = (SELECT SUM(total_price) 
                        FROM day) WHERE sub_name = "Итого"''')
    cursor.execute(f'SELECT * FROM day')
    data = cursor.fetchall()
    filter_result = list(filter(lambda x: x[1] != None, data))
    print(filter_result)
    result = list_to_string(filter_result)
    connection.commit()
    return result

def make_packs(raw_messages: list):
    # формирует пакеты из архива телеграм-чата, дополняя датой и категорией траты
    pack = []
    date = '2022-02-23'
    for text in raw_messages:
        print(text)
        if cats.isdate(text):
            date = cats.format_date(text)
            continue
        else:
            x = cats.make_note(text, date) # формирую переменную NamedTuple c методом _make
            pack.append(x)  # добавляю переменную NamedTuple к пакету для отправки в БД
    insert_data(pack)

def message_handler(message, date):
    # формирует пакет типа NamedTuple с распаршиными записями и  вставляет в БД
    pack = []
    if '\n' in message:
        message = message.split('\n')
        for mes in message:
            pack.append(cats.make_note(mes, date))
    else:
        pack = [cats.make_note(message, date)] # формируем экземпляр Note
    insert_data(pack) # вставляем сформированное сообщение в БД

with sq.connect('newDB.db') as connection:
    cursor = connection.cursor()
    init_db()
    init_table('day')
    init_table('month')
    #source = [('messages','field1'),('messages2','field2')]
    source = [('archive', 'field1')]
    cursor.execute("SELECT ROUND(SUM(price),1) FROM main")
    check = cursor.fetchall()
    print(check)
    if check[0][0] == None:
        try:
            for s in source:
                raw_messages = upload_data(*s)
                make_packs(raw_messages)
        except:
            connection.rollback()





