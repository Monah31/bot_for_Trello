from aiogram.utils import executor

from create_new_bot import dp
from handlers import start, my_desks



async def on_startup(dp):
    print("Start bot")

my_desks.register_handler_descs(dp)
start.register_handler_start(dp)





# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)