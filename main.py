from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import database
import re
import calendar
import exceptions
from os import getenv

TOKEN_API = os.getenv('BOT_TOKEN')
bot = Bot(TOKEN_API)
dp = Dispatcher(bot)
id = '541172529'

HELP_COMMAND = '''
/today - статистика за день
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
    try:
        result = database.get_today()
        await message.answer(result)
    except:
        text = "сегодня трат не было!"
        await message.answer(text)
        raise exceptions.MessageError(text)
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
        x = database.message_handler(txt, date_str)
        await message.answer(f"Принято! Добавлено в категории : {x}")
    except:
        text = "!трата должна быть в формате <трата> <цена>!"
        await message.answer(text)
        raise exceptions.MessageError ('сообщение не вставилось в базу')

if __name__ == '__main__':
    executor.start_polling(dp)


