from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import database
import re
import calendar
import exceptions

TOKEN_API = '6006947703:AAFiIBqbYWhmZUl6l1crqb3ZbQI4CpiXkoU'
bot = Bot(TOKEN_API)
dp = Dispatcher(bot)

HELP_COMMAND = '''
/day - статистика за день
/month 1-12 статистика за месяц
/del - удалить последнюю запись 
'''

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.answer(text=HELP_COMMAND)
    await message.delete()

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer('Wellcome!\n text /help - список команд ')
    await message.delete()

@dp.message_handler(commands=['today'])
async def start_command(message: types.Message):
    result = database.get_today()
    await message.answer(result)
    await message.delete()

@dp.message_handler(commands=['del'])
async def delete_message(message: types.Message):
    database.delete_note()
    await message.answer('удалено последнее сообщение!')
    await message.delete()

@dp.message_handler(lambda message: message.text.startswith('/month '))
async def month(message: types.Message):
    command_text = message.text
    pattern = r'/month (\d+)'  # Регулярное выражение для получения параметра
    match = re.match(pattern, command_text)  # Ищем соответствие в тексте команды
    try:
        month = match.group(1)  # Получаем месяц
        result = database.get_month(int(month))
        await message.answer(f'общие затраты за : {calendar.month_name[int(month)]}\n {result}')
        with open('diagram.png', 'rb') as photo:
            await bot.send_photo(chat_id=message.chat.id, photo=photo)

    except:
        text = "Неверный формат команды /month. Используйте /month <число>."
        await message.answer(text)
        raise exceptions.MessageError

@dp.message_handler()
async def add_expense(message: types.Message):
    try:
        txt, date = message.text, message.date # берем текст и дату из сообщения
        date_str = date.strftime("%Y-%m-%d") # переводим дату в формат SQL
        database.message_handler(txt, date_str)
        await message.answer("принято!")
    except:
        text = "трата должна быть в формате <Трата> <цена>"
        await message.answer(text)
        raise exceptions.MessageError ('сообщение не вставилось в базу')

if __name__ == '__main__':
    executor.start_polling(dp)

