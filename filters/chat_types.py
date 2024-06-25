# function with routers filters
# import libraries
from aiogram import types, Bot
from aiogram.filters import Filter


# creating filter that filters Chats
class ChatTypeFilter(Filter):
    # initializating Filter Class atrributes
    def __init__(self, chat_types: list[str]) -> None:
        # setting chats where this router will work
        self.chat_types = chat_types

    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in self.chat_types


# creating filter that filters Admins messages(commands)
class IsAdmin(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        return message.from_user.id in bot.my_admins_list
