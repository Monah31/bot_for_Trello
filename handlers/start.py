import datetime
from aiogram import types, Dispatcher
from create_new_bot import dp
from database.sqlite_db import Database
from utils.trello import Trello

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

db = Database(db_name='data.db')
trello = Trello()
storage = {}


async def process_start_command(message: types.Message):
    if not (db.check_user(message.from_user.id, 'users')):
        record = (message.from_user.id, 'token', 'token', 'active',
                  message.from_user.username)
        db.add_record('users', record)
        await message.reply(
            "Пользователь создан в базе. Теперь необходимо добавить ключ и токен вашего Trello. С помощью комманд /trello_api и /trello_token"
        )
    else:
        await message.reply(
            "Вы уже есть в базе. Можете воспользоваться командами - /menu")


async def get_api_key(message: types.Message):
    if (db.check_user(message.from_user.id, 'users')):
        await message.reply(
            "Введите ваш ключ Trello API. Если вы не знаете как получить ключ, перейдите по ссылке:\nhttps://trello.com/power-ups/admin"
        )
        storage[message.from_user.id] = 'waiting_apikey'

    else:
        await message.reply("Выполните команду /start для добавления в базу")


async def get_token(message: types.Message):
    if (db.check_user(message.from_user.id, 'users')):
        await message.reply("Введите ваш токен Trello API.")
        storage.update({message.from_user.id: 'waiting_token'})

    else:
        await message.reply("Выполните команду /start для добавления в базу")


async def menu_command(message: types.Message):

    if db.check_user(message.from_user.id, 'users'):
        if db.check_token(message.from_user.id, 'users') and db.check_api(message.from_user.id, 'users'):

            button_1 = InlineKeyboardButton("Задачи с истекающим сроком!", callback_data="tasks_1")
            button_2 = InlineKeyboardButton("Просроченные задачи!", callback_data="tasks_2")
            button_3 = InlineKeyboardButton("Отчет по задачам без дедлайна", callback_data="tasks_3")
            button_4 = InlineKeyboardButton("Задачи в backlog", callback_data="tasks_4")
            button_5 = InlineKeyboardButton("Отчет всех задач по проекту", callback_data="tasks_5")
            button_6 = InlineKeyboardButton("Отмена.", callback_data="cancel")
            

            keyboard = InlineKeyboardMarkup(row_width=1)
            keyboard.add(button_1).add(button_2).add(button_3).add(button_4).add(button_5).add(button_6)

            await message.reply("Что вы хотите посмотреть?", reply_markup=keyboard)
        else:
            await message.reply(
                "Выполни команду /trello_api и /trello_token, для добавления ключа и токена"
            )
    else:
        await message.reply("Выполни команду /start")


async def boards_command(message: types.Message):
    desks = [desk[0] for desk in db.get_table_ids(message.from_user.id)]
    if desks:
        await message.reply(
            f'Ваши доски: {desks}, что бы изменить отправте команду /change_boards'
        )
    else:
        await message.reply(
            f'Вы не добавили ни одной доски. Что бы добавить - отправьте команду /change_boards'
        )


async def change_boards_command(message: types.Message):
    await message.reply(
        f'Введите ID доски которую хотите добавить\удалить\nЕсли вы не знаете ID интересующей вас доски воспользуйтесь командой /all_boards'
    )
    storage[message.from_user.id] = 'waiting_desk'


async def trello_api_handler(message: types.Message):
    state = storage.get(message.from_user.id)
    if state == 'waiting_desk':
        desks = [desk[0] for desk in db.get_table_ids(message.from_user.id)]
        if message.text in desks:
            db.remove_table(message.from_user.id, message.text)
            await message.reply(f"Удалили доску {message.text}")
        else:
            db.add_table(message.from_user.id, message.text)
            await message.reply(f"Добавили доску: {message.text}")
        storage[message.from_user.id] = 'finished'
    if state == 'waiting_apikey':
        db.add_api_trello(message.text, message.from_user.id)
        await message.reply(
            f"Добавили ваш ключ в базу. {message.text[0:5]}XXXXXXXXXXXXXX")
        await message.delete()
        storage[message.from_user.id] = 'finished'
    if state == 'waiting_token':
        db.add_token_trello(message.text, message.from_user.id)
        await message.reply(
            f"Добавили ваш токен в базу. {message.text[0:5]}XXXXXXXXXXXXXX")
        await message.delete()
        storage[message.from_user.id] = 'finished'

@dp.callback_query_handler()
async def button_click(callback: types.CallbackQuery):
    message = callback.message

    if callback.data == "tasks_1":
        
        desks = [desk[0] for desk in db.get_table_ids(callback.from_user.id)]
        task_list = "" 

        if desks:
            count_tasks = 0

            api_key = db.get_api_key(callback.from_user.id)
            api_token = db.get_api_token(callback.from_user.id)

            for desk in desks:
                try:
                    desks_names = await trello.get_all_boards(api_key, api_token)
                except Exception as e:
                    await message.edit_text(f"ошибка >> {e}")
                    break

                try:
                    lists = await trello.get_all_lists(api_key, api_token, desk)
                except Exception as e:
                    await message.edit_text(f"ошибка >>> {e}")

                for name_desk in desks_names:
                    if desk == name_desk.get('id'):
                        task_list += f"\nДоска: {name_desk.get('name')}\n"
                        dict_lable = {}
                        for list_name in lists:
                            if list_name.get('name').lower() == 'in progress':
                                try:
                                    tasks = await trello.get_board_tasks(api_key, api_token, list_name.get('id'))
                                except Exception as e:
                                    await message.edit_text(f"ошибка > {e}")
                                
                                for task in tasks:
                                    try:
                                        labels = await trello.get_labels(api_key, api_token, task.get('id'))
                                    except Exception as e:
                                        await message.edit_text(f"ошибка >>> {e}")

                                    
                                    for label in labels:
                                        list_name_for_card = list_name.get('name')
                                        name = task.get('name')
                                        url = task.get('url')
                                        label_name = label.get('name')
                                        due = task.get('due')
                                        text = f"[{name}]({url})"
                                        if due:
                                            due_date = datetime.datetime.strptime(due, '%Y-%m-%dT%H:%M:%S.%fZ') + datetime.timedelta(hours=3)

                                            now = datetime.datetime.now()
                                            time_left = due_date - now
                                            days = time_left.days
                                            hours = (time_left.seconds / 3600)
                                            minutes = ((time_left.seconds % 3600) // 60)
                                            time_left = f'Дедлайн: {days} дней, {round(hours, 0)} часов, {minutes} минут.'
                                            if days == 0 and (hours >= 0 or minutes >= 0):
                                                label_name = label.get('name')
                                                if label_name in dict_lable:
                                                    dict_lable[label_name] += 1
                                                else:
                                                    dict_lable[label_name] = 1                                            
                                                task_list += (f'\n{list_name_for_card}\n{text}\nНаправление: {label_name}\n{time_left}\n')
                                                count_tasks += 1
                                                time_left = 'Просрочен'
                                        else:
                                            time_left = 'Без дедлайна'

                count_lable = 'Количество задач в каждом направлении:\n'
                for i in dict_lable:
                    count_lable += f'{i}: {dict_lable[i]}\n'

                if count_tasks == 0:
                    task_list +='\nНет задач у которых скоро закончится дедлайн\n'
                else:
                    task_list += '\n' + count_lable

            await message.edit_text(task_list + '\n', parse_mode="Markdown")

    elif callback.data == "tasks_2":
        desks = [desk[0] for desk in db.get_table_ids(callback.from_user.id)]
        task_list = ""    
        count_tasks = 0
        
        if desks:
            api_key = db.get_api_key(callback.from_user.id)
            api_token = db.get_api_token(callback.from_user.id)

            for desk in desks:
                try:
                    desks_names = await trello.get_all_boards(api_key, api_token)
                except Exception as e:
                    await message.edit_text(f"ошибка >> {e}")
                    break

                try:
                    lists = await trello.get_all_lists(api_key, api_token, desk)
                except Exception as e:
                    await message.edit_text(f"ошибка >>> {e}")

                for name_desk in desks_names:
                    if desk == name_desk.get('id'):
                        task_list += f"\nДоска: {name_desk.get('name')}\n"
                        dict_lable = {}
                        for list_name in lists:
                            if list_name.get('name').lower() == 'in progress':
                                try:
                                    tasks = await trello.get_board_tasks(api_key, api_token, list_name.get('id'))
                                except Exception as e:
                                    await message.edit_text(f"ошибка > {e}")
                                
                                for task in tasks:
                                    try:
                                        labels = await trello.get_labels(api_key, api_token, task.get('id'))
                                    except Exception as e:
                                        await message.edit_text(f"ошибка >>> {e}")

                                    for label in labels:
                                        list_name_for_card = list_name.get('name')
                                        name = task.get('name')
                                        url = task.get('url')
                                        label_name = label.get('name')
                                        due = task.get('due')
                                        text = f"[{name}]({url})"
                                        if due:
                                            due_date = datetime.datetime.strptime(due, '%Y-%m-%dT%H:%M:%S.%fZ') + datetime.timedelta(hours=3)
                                            now = datetime.datetime.now()
                                            time_left = due_date - now
                                            days = time_left.days
                                            hours = (time_left.seconds / 3600)
                                            minutes = ((time_left.seconds % 3600) // 60)
                                            time_left = f'Дедлайн: {days} дней, {round(hours, 0)} часов, {minutes} минут.'

                                            if days < 0:
                                                label_name = label.get('name')
                                                if label_name in dict_lable:
                                                    dict_lable[label_name] += 1
                                                else:
                                                    dict_lable[label_name] = 1                                            
                                                time_left = 'Просрочен'
                                                task_list += (f'\n{list_name_for_card}\n{text}\nНаправление: {label_name}\n{time_left}\n')
                                                count_tasks += 1
                                        else:
                                            time_left = 'Без дедлайна'

                count_lable = 'Количество задач в каждом направлении:\n'
                for i in dict_lable:
                    count_lable += f'{i}: {dict_lable[i]}\n'

                if count_tasks == 0:
                    task_list +='\nНет просроченных задач\n\n'
                else:
                    task_list += '\n' + count_lable + "\n"

            await message.edit_text(task_list + '\n', parse_mode="Markdown")


        else:
            await message.edit_text(f'Нет досок для отслеживания')


    elif callback.data == "tasks_3":
        desks = [desk[0] for desk in db.get_table_ids(callback.from_user.id)]
        task_list = ""    
        count_tasks = 0
        if desks:
            api_key = db.get_api_key(callback.from_user.id)
            api_token = db.get_api_token(callback.from_user.id)

            for desk in desks:
                try:
                    desks_names = await trello.get_all_boards(api_key, api_token)
                except Exception as e:
                    await message.edit_text(f"ошибка >> {e}")
                    break

                try:
                    lists = await trello.get_all_lists(api_key, api_token, desk)
                except Exception as e:
                    await message.edit_text(f"ошибка >>> {e}")

                for name_desk in desks_names:
                    if desk == name_desk.get('id'):
                        task_list += f"\nДоска: {name_desk.get('name')}\n"
                        dict_lable = {}
                        for list_name in lists:
                            if list_name.get('name').lower() == 'in progress':
                                try:
                                    tasks = await trello.get_board_tasks(api_key, api_token, list_name.get('id'))
                                except Exception as e:
                                    await message.edit_text(f"ошибка > {e}")
                                
                                for task in tasks:
                                    try:
                                        labels = await trello.get_labels(api_key, api_token, task.get('id'))
                                    except Exception as e:
                                        await message.edit_text(f"ошибка >>> {e}")

                                    for label in labels:
                                        list_name_for_card = list_name.get('name')
                                        name = task.get('name')
                                        url = task.get('url')
                                        label_name = label.get('name')
                                        due = task.get('due')
                                        text = f"[{name}]({url})"
                                        if not due:  
                                            count_tasks += 1                                                                        
                                            time_left = 'Без дедлайна'

                                            if label_name in dict_lable:
                                                dict_lable[label_name] += 1
                                            else:
                                                dict_lable[label_name] = 1           
                                            task_list += (f'\n{list_name_for_card}\n{text}\nНаправление: {label_name}\n{time_left}\n')                              

                count_lable = 'Количество задач в каждом направлении:\n'
                for i in dict_lable:
                    count_lable += f'{i}: {dict_lable[i]}\n'

                if count_tasks == 0:
                    task_list +='\nЗадач без дедлайна - нет!\n\n'
                else:
                    task_list += '\n' + count_lable + '\n'

            await message.edit_text(task_list + '\n', parse_mode="Markdown")


        else:
            await message.edit_text(f'Нет досок для отслеживания')

    elif callback.data == "tasks_4":
        desks = [desk[0] for desk in db.get_table_ids(callback.from_user.id)]
        task_list = ""    
        
        if desks:
            api_key = db.get_api_key(callback.from_user.id)
            api_token = db.get_api_token(callback.from_user.id)

            for desk in desks:
                try:
                    desks_names = await trello.get_all_boards(api_key, api_token)
                except Exception as e:
                    await message.edit_text(f"ошибка >> {e}")
                    break

                try:
                    lists = await trello.get_all_lists(api_key, api_token, desk)
                except Exception as e:
                    await message.edit_text(f"ошибка >>> {e}")

                for name_desk in desks_names:
                    if desk == name_desk.get('id'):
                        task_list += f"\nДоска: {name_desk.get('name')}\n"
                        count_tasks = 0
                        dict_lable = {}
                        for list_name in lists:
                            if list_name.get('name').lower() == 'backlog':

                                try:
                                    tasks = await trello.get_board_tasks(api_key, api_token, list_name.get('id'))
                                except Exception as e:
                                    await message.edit_text(f"ошибка > {e}")
                                
                                for task in tasks:
                                    try:
                                        labels = await trello.get_labels(api_key, api_token, task.get('id'))
                                    except Exception as e:
                                        await message.edit_text(f"ошибка >>> {e}")

                                    for label in labels:
                                        list_name_for_card = list_name.get('name')
                                        name = task.get('name')
                                        url = task.get('url')
                                        label_name = label.get('name')
                                        due = task.get('due')
                                        text = f"[{name}]({url})"
                                        count_tasks += 1 
                                        if not due:  
                                                                                                                   
                                            time_left = 'Без дедлайна'

                                            if label_name in dict_lable:
                                                dict_lable[label_name] += 1
                                            else:
                                                dict_lable[label_name] = 1           
                                            task_list += (f'\n{list_name_for_card}\n{text}\nНаправление: {label_name}\n')                              

                count_lable = 'Количество задач в каждом направлении:\n'
                for i in dict_lable:
                    count_lable += f'{i}: {dict_lable[i]}\n'
                
                if count_tasks == 0:
                    task_list +='\nЗадач в backlog - нет.\n\n'
                else:
                    task_list += '\n' + count_lable + '\n'

            await message.edit_text(task_list + '\n', parse_mode="Markdown")


        else:
            await message.edit_text(f'Нет досок для отслеживания')

    elif callback.data == "tasks_5":
        desks = [desk[0] for desk in db.get_table_ids(callback.from_user.id)]
        task_list = ""
        
        if desks:
            
            api_key = db.get_api_key(callback.from_user.id)
            api_token = db.get_api_token(callback.from_user.id)

            for desk in desks:
                try:
                    desks_names = await trello.get_all_boards(api_key, api_token)
                except Exception as e:
                    await message.edit_text(f"ошибка >> {e}")
                    break

                try:
                    lists = await trello.get_all_lists(api_key, api_token, desk)
                except Exception as e:
                    await message.edit_text(f"ошибка >>> {e}")
                
                for name_desk in desks_names:
                    if desk == name_desk.get('id'):
                        task_list += f"Доска: [{name_desk.get('name')}]({name_desk.get('url')})\n"
                        count_backlog_tasks = 0
                        dict_lable = {}
                        dict_tasks = {'Истекающие карточки': 0, 'Просроченные карточки': 0, 'Без дедлайна': 0}
                        for list_name in lists:
                            if list_name.get('name').lower() == 'in progress':
                                try:
                                    tasks = await trello.get_board_tasks(api_key, api_token, list_name.get('id'))
                                except Exception as e:
                                    await message.edit_text(f"ошибка > {e}")
                                
                                for task in tasks:
                                    try:
                                        labels = await trello.get_labels(api_key, api_token, task.get('id'))
                                    except Exception as e:
                                        await message.edit_text(f"ошибка >>> {e}")
                                
                                    for label in labels:
                                        label_name = label.get('name')
                                        list_name_for_card = list_name.get('name')
                                        name = task.get('name')
                                        url = task.get('url')
                                        due = task.get('due')
                                        text = f"[{name}]({url})"
                                        if due:
                                            due_date = datetime.datetime.strptime(due, '%Y-%m-%dT%H:%M:%S.%fZ') + datetime.timedelta(hours=3)
                                            now = datetime.datetime.now()
                                            time_left = due_date - now
                                            days = time_left.days
                                            hours = (time_left.seconds / 3600)
                                            minutes = ((time_left.seconds % 3600) // 60)
                                            time_left = f'Дедлайн: {days} дней, {round(hours, 0)} часов, {minutes} минут.'
                                            if days == 0 and (hours >= 0 or minutes >= 0):
                                                if label_name in dict_lable:
                                                    dict_lable[label_name] += 1
                                                else:
                                                    dict_lable[label_name] = 1
                                                dict_tasks['Истекающие карточки'] += 1
                                                
                                            elif days < 0:
                                                if label_name in dict_lable:
                                                    dict_lable[label_name] += 1
                                                else:
                                                    dict_lable[label_name] = 1
                                                dict_tasks['Просроченные карточки'] += 1

                                        else:
                                            if label_name in dict_lable:
                                                dict_lable[label_name] += 1
                                            else:
                                                dict_lable[label_name] = 1
                                            dict_tasks['Без дедлайна'] += 1

                            elif list_name.get('name').lower() == 'backlog':
                                try:
                                    tasks = await trello.get_board_tasks(api_key, api_token, list_name.get('id'))
                                except Exception as e:
                                    await message.edit_text(f"ошибка > {e}")
                                
                                for task in tasks:
                                    try:
                                        labels = await trello.get_labels(api_key, api_token, task.get('id'))
                                    except Exception as e:
                                        await message.edit_text(f"ошибка >>> {e}")
                                
                                    for label in labels:
                                        label_name = label.get('name')
                                        if label_name in dict_lable:
                                            dict_lable[label_name] += 1
                                        else:
                                            dict_lable[label_name] = 1                                    
                                    count_backlog_tasks +=1

                count_lable = 'Количество задач в каждом направлении:\n'
                for i in dict_lable:
                    count_lable += f'{i}: {dict_lable[i]}\n'

                count_task = 'Количество задач:\n'
                for j in dict_tasks:
                    count_task += f'{j}: {dict_tasks[j]}\n'


                task_list += '\n' + count_task + f'\nКоличество задач в backlog: {count_backlog_tasks}\n\n' + count_lable + '\n'

                await message.edit_text(task_list + '\n', parse_mode="Markdown")


        else:
            await message.edit_text(f'Нет досок для отслеживания')

    elif callback.data == "cancel":
        await message.edit_text(
            f'{callback.from_user.username}, жду команду из меню.')
        
def register_handler_start(dp: Dispatcher):
    dp.register_message_handler(process_start_command, commands=['start'])
    dp.register_message_handler(get_api_key, commands=['trello_api'])
    dp.register_message_handler(get_token, commands=['trello_token'])
    dp.register_message_handler(menu_command, commands=['menu'])
    dp.register_message_handler(boards_command, commands=['active_boards'])
    dp.register_message_handler(change_boards_command, commands=['change_boards'])
    dp.register_message_handler(trello_api_handler)
    dp.register_message_handler(button_click)
