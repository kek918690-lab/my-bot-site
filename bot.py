import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo

TOKEN = "8409829464:AAH06p6GDkY6Pvj-Ou_RU3gMeVWyRnADpqE"
WEB_APP_URL = "https://kek918690-lab.github.io/my-bot-site/"

bot = Bot(token=TOKEN)
dp = Dispatcher()

def init_db():
    conn = sqlite3.connect('economy_game.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, 
        username TEXT,
        money INTEGER DEFAULT 100,
        wood INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

@dp.message(Command("start"))
async def start(message: types.Message):
    init_db()
    uid = message.from_user.id
    uname = message.from_user.first_name
    
    conn = sqlite3.connect('economy_game.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (uid, uname))
    conn.commit()
    conn.close()
    
    markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="💎 Войти в Империю", web_app=WebAppInfo(url=WEB_APP_URL))]
    ])
    await message.answer(f"Привет, {uname}! Ты добавлен в список лидеров. Входи в игру:", reply_markup=markup)

async def main():
    init_db()
    print("Бот запущен и готов записывать игроков...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
