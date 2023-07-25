from aiogram import types, Dispatcher
from utils.trello import Trello
from database.sqlite_db import Database

db = Database(db_name="data.db")
trello = Trello()



async def process_my_desks_command(message: types.Message):
    if db.check_user(message.from_user.id, "users"):
        if db.check_token(message.from_user.id, "users") and db.check_api(
                message.from_user.id, "users"):

            api_key = db.get_api_key(message.from_user.id)
            api_token = db.get_api_token(message.from_user.id)

            if api_key and api_token:

                try:
                    response_text = await trello.get_all_boards(
                        api_key, api_token)
                except Exception as e:
                    await message.edit_text(f"ошибка >>> {e}")

                text = ''
                for desk in response_text:
                    id_desk = desk.get("id")
                    name = desk.get("name")
                    url = desk.get("url")
                    text += f"\n[{name}]({url}): {id_desk}\n"

                await message.reply(f"ID моих досок:\n{text}", parse_mode="Markdown")
            else:
                await message.reply(
                    f"Выполни команду /trello_api и /trello_token, для добавления ключа и токена"
                )

#Отправляем обратное сообщение с ответом на запрос

async def help_command(message: types.Message):
    """
    Инструкция: 
    1. /start - Запустить бота
    2. После запуска бота и добавления Вас в базу, добавте ключ c помощью команды /trello_api, (https://trello.com/power-ups/admin) и токен Trello с помощью комнады /trello_token 
    3. Добавте ID доски с помощью команды /change_boards.
    4. Что бы узнать ID доски которая вас интересует воспользуйтесь командой - /active_boards
    5. /all_boards - Проверить какие ID досок вы уже добавили в базу данных
    6. /menu - выберете нужный отчет.
    """
    await message.answer(help_command.__doc__)

def register_handler_descs(dp: Dispatcher):
    dp.register_message_handler(process_my_desks_command, commands=["all_boards"])
    dp.register_message_handler(help_command, commands=["help"])
    
