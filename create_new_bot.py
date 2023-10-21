from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv, find_dotenv

import logging
import os

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()

load_dotenv(find_dotenv())
bot = Bot(os.getenv('BOT_TOKEN'))
dp = Dispatcher(bot, storage=storage)