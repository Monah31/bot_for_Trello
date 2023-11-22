import datetime
import os

from aiogram import types, Dispatcher
from create_new_bot import dp
from database.sqlite_db import Database
from dotenv import load_dotenv, find_dotenv
from utils.kaiten import Kaiten

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv(find_dotenv())
admin_id = os.getenv('ADMIN_ID')

db = Database(db_name='data.db')
kaiten = Kaiten()
storage = {}



async def process_start_command(message: types.Message):
    desks = [desk[0] for desk in db.get_users_id(message.from_user.id)]

    if message.from_user.id in desks or message.from_user.id == int(admin_id):
        if not (db.check_user(message.from_user.id, 'users')):
            record = (message.from_user.id, 'token', 'token', 'active',
                    message.from_user.username)
            db.add_record('users', record)
            await message.reply(
                "Пользователь создан в базе. Теперь необходимо добавить domain и ключ вашего Kaiten. С помощью комманд /kaiten_api и /domain"
            )
        else:
            await message.reply(
                "Вы уже есть в базе. Можете воспользоваться командами - /menu")
    else:
        await message.reply(
                "У вас нет доступа к командам, обратитесь к админестратору бота")


async def get_api_key(message: types.Message):
    if (db.check_user(message.from_user.id, 'users')):
        await message.reply(
            "Введите ваш ключ Kaiten API. Если вы не знаете как получить ключ, зайдите в настройки профиля и в боковом меню найдите:\n'Ключ Доступа API'"
        )
        storage[message.from_user.id] = 'waiting_apikey'

    else:
        await message.reply("Выполните команду /start для добавления в базу")


async def get_domain(message: types.Message):
    if (db.check_user(message.from_user.id, 'users')):
        await message.reply("Введите ваш domain (Имя пользователя).")
        storage.update({message.from_user.id: 'waiting_token'})

    else:
        await message.reply("Выполните команду /start для добавления в базу")


async def menu_command(message: types.Message):

    if db.check_user(message.from_user.id, 'users'):
        if db.check_domain(message.from_user.id, 'users') and db.check_api(message.from_user.id, 'users'):

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
                "Выполни команду /kaiten_api и /domain, для добавления ключа и домена"
            )
    else:
        await message.reply("Выполни команду /start")

async def process_change_user_command(message: types.Message):  
    
    if message.from_user.id == int(admin_id):
        await message.reply(
            f'Введите ID пользователя которого хотите добавить\удалить\n'
        )
        storage[message.from_user.id] = 'waiting_user'
    else:
        await message.reply(
            f'Только админ может добавлять пользователей бота!\n'
        )


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

async def spaces_command(message: types.Message):
    desks = [desk[0] for desk in db.get_space_ids(message.from_user.id)]
    if desks:
        await message.reply(
            f'Ваши пространства: {desks}, что бы изменить отправте команду /change_spaces'
        )
    else:
        await message.reply(
            f'Вы не добавили ни одного пространства. Что бы добавить - отправьте команду /change_spaces'
        )


async def change_boards_command(message: types.Message):
    await message.reply(
        f'Введите ID доски которую хотите добавить\удалить\nЕсли вы не знаете ID интересующей вас доски воспользуйтесь командой /all_boards'
    )
    storage[message.from_user.id] = 'waiting_desk'

async def change_spaces_command(message: types.Message):
    await message.reply(
        f'Введите ID пространства которого хотите добавить\удалить\nЕсли вы не знаете ID интересующего вас пространства воспользуйтесь командой /all_spaces'
    )
    storage[message.from_user.id] = 'waiting_space'


async def kaiten_api_handler(message: types.Message):
    state = storage.get(message.from_user.id)
    if state == 'waiting_user':
        desks = [desk[0] for desk in db.get_users_id(message.from_user.id)]
        if message.text in desks:
            db.remove_users_id(message.from_user.id, message.text)
            await message.reply(f"Удалили пользователя: {message.text}")
        else:
            db.add_users_id(message.from_user.id, message.text)
            await message.reply(f"Добавили пользователя: {message.text}")
            storage[message.from_user.id] = 'finished'

    if state == 'waiting_desk':
        desks = [desk[0] for desk in db.get_table_ids(message.from_user.id)]
        if message.text in desks:
            db.remove_table(message.from_user.id, message.text)
            await message.reply(f"Удалили доску {message.text}")
        else:
            db.add_table(message.from_user.id, message.text)
            await message.reply(f"Добавили доску: {message.text}")
        storage[message.from_user.id] = 'finished'

    if state == 'waiting_space':
        desks = [desk[0] for desk in db.get_space_ids(message.from_user.id)]
        if message.text in desks:
            db.remove_space(message.from_user.id, message.text)
            await message.reply(f"Удалили пространство {message.text}")
        else:
            db.add_space(message.from_user.id, message.text)
            await message.reply(f"Добавили пространство: {message.text}")
        storage[message.from_user.id] = 'finished'

    if state == 'waiting_apikey':
        db.add_api_kaiten(message.text, message.from_user.id)
        await message.reply(
            f"Добавили ваш ключ в базу. {message.text[0:5]}XXXXXXXXXXXXXX")
        await message.delete()
        storage[message.from_user.id] = 'finished'
        
    if state == 'waiting_token':
        db.add_domain_kaiten(message.text, message.from_user.id)
        await message.reply(
            f"Добавили ваш домен в базу. {message.text[0:5]}XXXXX")
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
            domain = db.get_domain(callback.from_user.id)
            
            for desk in desks:

                try:
                    desks_names = await kaiten.get_board(api_key, domain, desk)   
        
                except Exception as e:
                    await message.edit_text(f"ошибка >> {e}")
                    break
             
               
                for name_desk in desks_names:

                    if int(desk) == int(name_desk.get('id')):
                        task_list += f"\nДоска: {name_desk.get('title')}\n"
                        dict_lable = {}
                        dict_lable['без направления'] = 0
                        for list_name in name_desk.get('columns'):
                            if list_name.get('title').lower() == 'in progress':
                                column_id = list_name.get('id')
                               
                        
                        for task in name_desk.get('cards'):
                            
                            if int(task.get('column_id')) == int(column_id):
                                due = task.get('due_date')
                                name = task.get('title')
                                text = f"{name}"

                                if due:
                                    due_date = datetime.datetime.strptime(due, '%Y-%m-%dT%H:%M:%S.%fZ') + datetime.timedelta(hours=3)
                                    now = datetime.datetime.now()
                                    time_left = due_date - now
                                    days = time_left.days
                                    hours = (time_left.seconds / 3600)
                                    minutes = ((time_left.seconds % 3600) // 60)
                                    time_left = f'Дедлайн: {days} дней, {round(hours, 0)} часов, {minutes} минут.'

                                    if days == 0 and (hours >= 0 or minutes >= 0):
                                        time_left = 'Просрочен'
                                        count_tasks += 1
                                        if not task.get('tags'): 
                                            label_name = 'без направления'
                                            dict_lable['без направления'] += 1                                           
                                            task_list += (f'\n{text}\nНаправление: {label_name}\n{time_left}\n')
                                        else:    
                                            text_label_name = ''                          
                                            for label in task.get('tags'):
                                                
                                                                                      
                                                label_name = label.get('name')   
                                                text_label_name += f'{label_name}; ' 

                                                if label_name in dict_lable:
                                                    dict_lable[label_name] += 1
                                                else:
                                                    dict_lable[label_name] = 1   
                                            task_list += (f'\n{text}\nНаправление: {text_label_name}\n{time_left}\n')                                     
                                        
                                else:
                                    time_left = 'Без дедлайна'


                count_lable = 'Количество задач в каждом направлении:\n'
                for i in dict_lable:
                    count_lable += f'{i}: {dict_lable[i]}\n'

                if count_tasks == 0:
                    task_list +='\nНет задач у которых скоро закончится дедлайн\n'
                else:
                    task_list += '\n' + count_lable

            await message.edit_text(task_list + '\n')

        else:
            await message.edit_text(f'Нет досок для отслеживания')

    elif callback.data == "tasks_2":

        desks = [desk[0] for desk in db.get_table_ids(callback.from_user.id)]
        task_list = "" 
        if desks:

            
            api_key = db.get_api_key(callback.from_user.id)
            domain = db.get_domain(callback.from_user.id)
            
            for desk in desks:

                try:
                    desks_names = await kaiten.get_board(api_key, domain, desk)   
        
                except Exception as e:
                    await message.edit_text(f"ошибка >> {e}")
                    break
             
               
                for name_desk in desks_names:

                    if int(desk) == int(name_desk.get('id')):
                        task_list += f"\nДоска: {name_desk.get('title')}\n"
                        dict_lable = {}
                        dict_lable['без направления'] = 0
                        count_tasks = 0
                        for list_name in name_desk.get('columns'):
                            if list_name.get('title').lower() == 'in progress':
                                column_id = list_name.get('id')
                            

                        
                        for task in name_desk.get('cards'):
                            
                            if int(task.get('column_id')) == int(column_id):
                                name = task.get('title')
                                due = task.get('due_date')
                                text = f"{name}"
                                if due:
                                    due_date = datetime.datetime.strptime(due, '%Y-%m-%dT%H:%M:%S.%fZ') + datetime.timedelta(hours=3)
                                    now = datetime.datetime.now()
                                    time_left = due_date - now
                                    days = time_left.days
                                    hours = (time_left.seconds / 3600)
                                    minutes = ((time_left.seconds % 3600) // 60)
                                    time_left = f'Дедлайн: {days} дней, {round(hours, 0)} часов, {minutes} минут.'
                                    
                                    if days < 0:
                                        time_left = 'Просрочен'
                                        count_tasks += 1
                                        if not task.get('tags'):                                     
                                            label_name = 'без направления'                                            
                                            dict_lable['без направления'] += 1                                    
                                            task_list += (f'\n{text}\nНаправление: {label_name}\n{time_left}\n')
                                        else:
                                            text_label_name = ''
                                            for label in task.get('tags'):    

                                                label_name = label.get('name')
                                                text_label_name += f'{label_name}; '
                                
                                            
                                                if label_name in dict_lable:
                                                    dict_lable[label_name] += 1
                                                else:
                                                    dict_lable[label_name] = 1                                            
                                                
                                            task_list += (f'\n{text}\nНаправление: {text_label_name}\n{time_left}\n')
                                
                                else:
                                    time_left = 'Без дедлайна'                           
                                            
                count_lable = 'Количество задач в каждом направлении:\n'
                for i in dict_lable:
                    count_lable += f'{i}: {dict_lable[i]}\n'

                if count_tasks == 0:
                    task_list +='\nНет просроченных задач\n\n'
                else:
                    task_list += '\n' + count_lable + "\n"

                    
            await message.edit_text(task_list + '\n')


        else:
            await message.edit_text(f'Нет досок для отслеживания')


    elif callback.data == "tasks_3":
        desks = [desk[0] for desk in db.get_table_ids(callback.from_user.id)]
        task_list = "" 
        if desks:
            
            api_key = db.get_api_key(callback.from_user.id)
            domain = db.get_domain(callback.from_user.id)
            
            for desk in desks:

                try:
                    desks_names = await kaiten.get_board(api_key, domain, desk)   
        
                except Exception as e:
                    await message.edit_text(f"ошибка >> {e}")
                    break
             
               
                for name_desk in desks_names:

                    if int(desk) == int(name_desk.get('id')):
                        task_list += f"\nДоска: {name_desk.get('title')}\n"
                        dict_lable = {}
                        dict_lable['без направленния'] = 0
                        count_tasks = 0
                        for list_name in name_desk.get('columns'):
                            if list_name.get('title').lower() == 'in progress':
                                column_id = list_name.get('id')
                                                       
                        for task in name_desk.get('cards'):
                            
                            if int(task.get('column_id')) == int(column_id):
                                name = task.get('title')  
                                due = task.get('due_date')   
                                text = f"{name}"
                                if not due:  
                                    count_tasks += 1                                                                        
                                    time_left = 'Без дедлайна'

                                    if not task.get('tags'): 
                                                                    
                                        label_name = 'без направленния'  

                                        dict_lable['без направленния'] += 1                                                 
                                        task_list += (f'\n{text}\nНаправление: {label_name}\n{time_left}\n')
                                            
                                    else:
                                        text_label_name = ''
                                        for label in task.get('tags'):                                                      
                                                                                                                        
                                            label_name = label.get('name')   
                                            text_label_name += f'{label_name}; '                               
                                            if label_name in dict_lable:
                                                dict_lable[label_name] += 1
                                            else:
                                                dict_lable[label_name] = 1           
                                        task_list += (f'\n{text}\nНаправление: {text_label_name}\n{time_left}\n')                              

                    count_lable = 'Количество задач в каждом направлении:\n'
                    for i in dict_lable:
                        count_lable += f'{i}: {dict_lable[i]}\n'

                    if count_tasks == 0:
                        task_list +='\nЗадач без дедлайна - нет!\n\n'
                    else:
                        task_list += '\n' + count_lable + '\n'
                    
            await message.edit_text(task_list + '\n')


        else:
            await message.edit_text(f'Нет досок для отслеживания')

    elif callback.data == "tasks_4":
        desks = [desk[0] for desk in db.get_table_ids(callback.from_user.id)]
        task_list = "" 
        if desks:

            count_tasks = 0
            api_key = db.get_api_key(callback.from_user.id)
            domain = db.get_domain(callback.from_user.id)
            
            for desk in desks:

                try:
                    desks_names = await kaiten.get_board(api_key, domain, desk)   

                except Exception as e:
                    await message.edit_text(f"ошибка >> {e}")
                    break
             
                
                for name_desk in desks_names:
                    if int(desk) == int(name_desk.get('id')):

                        task_list += f"\nДоска: {name_desk.get('title')}\n"
                        count_tasks = 0
                        dict_lable = {}
                        dict_lable['без направленния'] = 0

                        for list_name in name_desk.get('columns'):

                            if list_name.get('title').lower() == 'backlog':
                                column_id = list_name.get('id')

                        
                        for task in name_desk.get('cards'):

                            if int(task.get('column_id')) == int(column_id):
                                name = task.get('title') 
                                due = task.get('due_date')
                                count_tasks += 1 
                                text_label_name = ''
                                if not due:  

                                  
                                    if not task.get('tags'):
                                        label_name = 'без направленния' 
                                        
                                        dict_lable['без направленния'] += 1
                                        task_list += (f'\n{name}\nНаправление: {label_name}\n')

                                    else:
                                        
                                        for label in task.get('tags'):                                                                                
                                                                                
                                            label_name = label.get('name')
                                            text_label_name += f'{label_name}; '


                                            if label_name in dict_lable:
                                                dict_lable[label_name] += 1
                                            else:
                                                dict_lable[label_name] = 1           
                                        task_list += (f'\n{name}\nНаправление: {text_label_name}\n')   
                               
                count_lable = 'Количество задач в каждом направлении:\n'
                for i in dict_lable:
                    count_lable += f'{i}: {dict_lable[i]}\n'
                
                if count_tasks == 0:
                    task_list +='\nЗадач в backlog - нет.\n\n'
                else:
                    task_list += '\n' + count_lable + '\n'

            if len(task_list) > 4096:
                for x in range(0, len(task_list), 4096):
                    await message.answer(task_list[x:x+4096] + '\n')
                    
            else:
                await message.answer(task_list + '\n')


        else:
            await message.edit_text(f'Нет досок для отслеживания')

    elif callback.data == "tasks_5":
        desks = [desk[0] for desk in db.get_table_ids(callback.from_user.id)]
        task_list = "" 
        if desks:

            count_tasks = 0
            api_key = db.get_api_key(callback.from_user.id)
            domain = db.get_domain(callback.from_user.id)
            
            for desk in desks:

                try:
                    desks_names = await kaiten.get_board(api_key, domain, desk)   
        
                except Exception as e:
                    await message.edit_text(f"ошибка >> {e}")
                    break          
               
                for name_desk in desks_names:

                    if int(desk) == int(name_desk.get('id')):

                        task_list += f"\nДоска: {name_desk.get('title')}\n"
                        count_backlog_tasks = 0
                        dict_lable = {}
                        dict_lable['без направленния'] = 0
                        dict_tasks = {'Истекающие карточки': 0, 'Просроченные карточки': 0, 'Без дедлайна': 0}

                        for list_name in name_desk.get('columns'):

                            if list_name.get('title').lower() == 'in progress':
                                column_id = list_name.get('id')

                        
                        for task in name_desk.get('cards'):

                            if int(task.get('column_id')) == int(column_id):
                                name = task.get('title')
                                due = task.get('due_date')
                                text = f"{name}"
                                                                    
                                if due:
                                    due_date = datetime.datetime.strptime(due, '%Y-%m-%dT%H:%M:%S.%fZ') + datetime.timedelta(hours=3)
                                    now = datetime.datetime.now()
                                    time_left = due_date - now
                                    days = time_left.days
                                    hours = (time_left.seconds / 3600)
                                    minutes = ((time_left.seconds % 3600) // 60)
                                    time_left = f'Дедлайн: {days} дней, {round(hours, 0)} часов, {minutes} минут.'
                                    if days == 0 and (hours >= 0 or minutes >= 0):
                                        if not task.get('tags'):
                                            dict_lable['без направленния'] += 1   
                                        else:             
                                            for label in task.get('tags'):                                    
                                        
                                                label_name = label.get('name')
                                                if label_name in dict_lable:
                                                    dict_lable[label_name] += 1
                                                else:
                                                    dict_lable[label_name] = 1
                                        dict_tasks['Истекающие карточки'] += 1
                                        
                                    elif days < 0:
                                        if not task.get('tags'):
                                            dict_lable['без направленния'] += 1   
                                        else:             
                                            for label in task.get('tags'):                                    
                                        
                                                label_name = label.get('name')
                                                if label_name in dict_lable:
                                                    dict_lable[label_name] += 1
                                                else:
                                                    dict_lable[label_name] = 1
                                        dict_tasks['Просроченные карточки'] += 1

                                else:
                                    if not task.get('tags'):
                                        dict_lable['без направленния'] += 1   
                                    else:             
                                        for label in task.get('tags'):                                    
                                    
                                            label_name = label.get('name')
                                            if label_name in dict_lable:
                                                dict_lable[label_name] += 1
                                            else:
                                                dict_lable[label_name] = 1
                                            dict_tasks['Без дедлайна'] += 1


                        for list_name in name_desk.get('columns'):
                            if list_name.get('title').lower() == 'backlog':
                                column_id = list_name.get('id')
                                

                        
                        for task in name_desk.get('cards'):
                            if int(task.get('column_id')) == int(column_id):
                                count_backlog_tasks += 1
                                if not task.get('tags'):
                                    dict_lable['без направленния'] += 1   
                                else: 
                                    for label in task.get('tags'):
                                        label_name = label.get('name')
                                        if label_name in dict_lable:
                                            dict_lable[label_name] += 1
                                        else:
                                            dict_lable[label_name] = 1                                    
                                                

                count_lable = 'Количество задач в каждом направлении:\n'
                for i in dict_lable:
                    count_lable += f'{i}: {dict_lable[i]}\n'

                count_task = 'Количество задач:\n'
                for j in dict_tasks:
                    count_task += f'{j}: {dict_tasks[j]}\n'


                task_list += '\n' + count_task + f'\nКоличество задач в backlog: {count_backlog_tasks}\n\n' + count_lable + '\n'

                await message.edit_text(task_list + '\n')


        else:
            await message.edit_text(f'Нет досок для отслеживания')

    elif callback.data == "cancel":
        await message.edit_text(
            f'{callback.from_user.username}, жду команду из меню.')
        
def register_handler_start(dp: Dispatcher):
    dp.register_message_handler(process_start_command, commands=['start'])
    dp.register_message_handler(get_api_key, commands=['kaiten_api'])
    dp.register_message_handler(get_domain, commands=['domain'])
    dp.register_message_handler(menu_command, commands=['menu'])
    dp.register_message_handler(boards_command, commands=['active_boards'])
    dp.register_message_handler(spaces_command, commands=['active_spaces'])
    dp.register_message_handler(change_boards_command, commands=['change_boards'])
    dp.register_message_handler(change_spaces_command, commands=['change_spaces'])
    dp.register_message_handler(process_change_user_command, commands=["change_user"])
    dp.register_message_handler(kaiten_api_handler)
    dp.register_message_handler(button_click)
