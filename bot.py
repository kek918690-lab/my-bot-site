import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import WebAppInfo

TOKEN = "8409829464:AAH06p6GDkY6Pvj-Ou_RU3gMeVWyRnADpqE"
WEB_APP_URL = "https://kek918690-lab.github.io/my-bot-site/"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    # Убираем всё лишнее, оставляем только WebApp
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="💎 Войти в Империю", 
        web_app=WebAppInfo(url=WEB_APP_URL))
    )
    await message.answer("Добро пожаловать! Всё управление ресурсами, рабочими и настройками теперь внутри:", 
                         reply_markup=builder.as_markup())

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
