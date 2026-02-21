import asyncio
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import WebAppInfo

TOKEN = "8409829464:AAH06p6GDkY6Pvj-Ou_RU3gMeVWyRnADpqE"
WEB_APP_URL = "https://kek918690-lab.github.io/my-bot-site/"

bot = Bot(token=TOKEN)
dp = Dispatcher()

def init_db():
    conn = sqlite3.connect('economy_game.db')
    cursor = conn.cursor()
    # Создаем таблицы
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, money INTEGER DEFAULT 100,
        wood INTEGER DEFAULT 0, food INTEGER DEFAULT 10, 
        hp INTEGER DEFAULT 100, business_type TEXT DEFAULT 'bricks')''')
    
    # Авто-исправление базы: добавляем колонку, если её нет
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN business_type TEXT DEFAULT 'bricks'")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

# Фоновая добыча раз в 2 минуты
async def resource_generator():
    while True:
        await asyncio.sleep(120)
        conn = sqlite3.connect('economy_game.db')
        cursor = conn.cursor()
        # Если есть еда — даем кирпичи (wood), забираем еду
        cursor.execute("UPDATE users SET wood = wood + 10, food = food - 1 WHERE food > 0 AND business_type = 'bricks'")
        # Ферма просто дает еду
        cursor.execute("UPDATE users SET food = food + 5 WHERE business_type = 'food'")
        conn.commit()
        conn.close()
        print(f"[{datetime.now().strftime('%H:%M')}] Ресурсы начислены.")

@dp.message(Command("start"))
async def start(message: types.Message):
    init_db()
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="💎 Войти в Империю", web_app=WebAppInfo(url=WEB_APP_URL)))
    await message.answer("🏗 Добро пожаловать! Управляй рабочими и ресурсами здесь:", reply_markup=builder.as_markup())

async def main():
    init_db()
    asyncio.create_task(resource_generator())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
