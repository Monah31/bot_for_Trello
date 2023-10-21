from aiogram import types, Dispatcher
from utils.kaiten import Kaiten
from database.sqlite_db import Database

db = Database(db_name="data.db")
kaiten = Kaiten()
users_list = []


async def process_my_spaces_command(message: types.Message):
    if db.check_user(message.from_user.id, "users"):
        if db.check_domain(message.from_user.id, "users") and db.check_api(
                message.from_user.id, "users"):

            api_key = db.get_api_key(message.from_user.id)
            domain = db.get_domain(message.from_user.id)

            if api_key and domain:

                try:
                    response_text = await kaiten.get_all_spaces(
                        api_key, domain)
                except Exception as e:
                    await message.edit_text(f"ошибка >>> {e}")

                text = ''
                for desks in response_text:
                    for desk in desks:
                        id_desk = desk.get("id")
                        name = desk.get("title")
                        url = f'https://{domain[0]}.kaiten.ru/space/{id_desk}'
                        text += f"\n[{name}]({url}): {id_desk}\n"

                await message.reply(f"ID моих пространств:\n{text}", parse_mode="Markdown")
            else:
                await message.reply(
                    f"Выполни команду /kaiten_api и /domain, для добавления ключа и домена"
                )

async def process_my_boards_command(message: types.Message):
    if db.check_user(message.from_user.id, "users"):
        if db.check_domain(message.from_user.id, "users") and db.check_api(
                message.from_user.id, "users"):

            api_key = db.get_api_key(message.from_user.id)
            domain = db.get_domain(message.from_user.id)
            spaces_id = [desk[0] for desk in db.get_space_ids(message.from_user.id)]

            for space_id in spaces_id:
         
                if api_key and domain:

                    try:
                        response_text = await kaiten.get_all_boards(
                            api_key, domain, space_id)
                    except Exception as e:
                        await message.edit_text(f"ошибка >>> {e}")

                    text = ''
                    for desks in response_text:
                        for desk in desks:
                            id_desk = desk.get("id")
                            name = desk.get("title")
                            url = f'https://{domain[0]}.kaiten.ru/space/{space_id}'
                            text += f"\n[{name}]({url}): {id_desk}\n"

                    await message.reply(f"ID моих моих досок в пространстве {space_id}:\n{text}", parse_mode="Markdown")
                else:
                    await message.reply(
                        f"Выполни команду /kaiten_api и /domain, для добавления ключа и домена"
                    )

#Отправляем обратное сообщение с ответом на запрос

async def help_command(message: types.Message):
    """
    Инструкция: 
    1. /start - Запустить бота
    2. После запуска бота и добавления Вас в базу, добавте ключ c помощью команды /kaiten_api (https://'Ваш домен'.kaiten.ru/profile/api-key), и домен с помощью комнады /domain 
    3. Добавте ID пространства с помощью команды /change_spaces.
    4. Добавте ID доски с помощью команды /change_boards.
    5. Что бы узнать ID пространства которое вас интересует воспользуйтесь командой - /all_spaces
    6. Что бы узнать ID доски которая вас интересует воспользуйтесь командой - /all_boards
    7. /active_spaces - Проверить какие ID пространств вы уже добавили в базу данных
    8. /active_boards - Проверить какие ID досок вы уже добавили в базу данных
    9. /menu - выберете нужный отчет который вам нужен.
    """
    await message.answer(help_command.__doc__)


async def process_change_user_command(message: types.Message):  
    if message.from_user.username == 'viktormonah':
        await message.reply(
            f'Введите ID пользователя которого хотите добавить\удалить\nЕсли вы не знаете ID интересующей вас доски воспользуйтесь командой /all_boards'
        )
        

def register_handler_descs(dp: Dispatcher):
    dp.register_message_handler(process_my_spaces_command, commands=["all_spaces"])
    dp.register_message_handler(process_my_boards_command, commands=["all_boards"])
    dp.register_message_handler(help_command, commands=["help"])
    dp.register_message_handler(process_change_user_command, commands=["change_user"])
    
