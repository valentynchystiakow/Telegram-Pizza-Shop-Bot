# import DataBase Session
import logging
from middlewares.db import DataBaseSession
# import function that starts database
from database.engine import create_db
# import function that drops database
from database.engine import session_maker
# import routers
from handlers.admin_private import admin_router
from handlers.user_group import user_group_router
from handlers.user_private import user_private_router
# import libraries
import asyncio
import os
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher, types
# import bot commands list
# from common.bot_cmds_list import private
# load env file with bot configuration
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())
# import logging


# connecting to bot using token, parse_mode -let to format messages with HTML TAGS
bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
# list with bot's admins
bot.my_admins_list = []
# setting dispatcher
dp = Dispatcher()
# connecting routers to dispatcher
dp.include_router(user_private_router)
dp.include_router(user_group_router)
dp.include_router(admin_router)


# function that starts database
async def on_startup(bot):
    # await drop_db()
    await create_db()


# function that drops bot
async def on_shutdown(bot):
    print('Bot is not running')


# main function that's start bot
async def main():
    # starting database
    dp.startup.register(on_startup)
    # shutting down bot and database
    dp.shutdown.register(on_shutdown)
    # creating session for making requests to database
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await bot.delete_webhook(drop_pending_updates=True)
    # setting bot's commands
    # await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

# main function that runs bot
asyncio.run(main())
