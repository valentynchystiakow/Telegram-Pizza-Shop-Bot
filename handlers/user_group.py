# import libraries
from string import punctuation

from aiogram import F, Bot, types, Router
# import filters
from aiogram.filters import Command

from filters.chat_types import ChatTypeFilter
# import restricted words file
from common.restricted_words import restricted_words

# setting router
user_group_router = Router()
# router filter that filters group messages
user_group_router.message.filter(ChatTypeFilter(["group", "supergroup"]))
# router filter that filters group edited messages
user_group_router.edited_message.filter(
    ChatTypeFilter(["group", "supergroup"]))


# function that processes admin command and checks if user is un admins list
@user_group_router.message(Command("admin"))
async def get_admins(message: types.Message, bot: Bot):
    chat_id = message.chat.id
    admins_list = await bot.get_chat_administrators(chat_id)
    admins_list = [
        member.user.id
        for member in admins_list
        if member.status == "creator" or member.status == "administrator"
    ]
    bot.my_admins_list = admins_list
    if message.from_user.id in admins_list:
        await message.delete()


def clean_text(text: str):
    return text.translate(str.maketrans("", "", punctuation))


# function that processes edited messages
@user_group_router.edited_message()
@user_group_router.message()
async def cleaner(message: types.Message):
    if restricted_words.intersection(clean_text(message.text.lower()).split()):
        await message.answer(
            f"{message.from_user.first_name}, Keep order in chat!"
        )
        await message.delete()
