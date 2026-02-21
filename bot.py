import asyncio
import sqlite3
import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo
from datetime import datetime

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
        bricks INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def sync_to_github():
    """Функция выгрузки списка игроков в JSON и пуш на GitHub"""
    try:
        conn = sqlite3.connect('economy_game.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username, bricks FROM users LIMIT 20")
        rows = cursor.fetchall()
        conn.close()

        players_data = [{"username": r[0], "bricks": r[1]} for r in rows]
        
        with open('players.json', 'w', encoding='utf-8') as f:
            json.dump(players_data, f, ensure_ascii=False, indent=4)
        
        # Команды для автоматического обновления GitHub
        os.system('git add players.json')
        os.system('git commit -m "Auto-update players list"')
        os.system('git push origin main')
        print("✅ Список игроков синхронизирован с GitHub")
    except Exception as e:
        print(f"❌ Ошибка синхронизации: {e}")

@dp.message(Command("start"))
async def start(message: types.Message):
    init_db()
    uid = message.from_user.id
    uname = message.from_user.first_name
    
    conn = sqlite3.connect('economy_game.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (uid, uname))
    cursor.execute("UPDATE users SET username = ? WHERE user_id = ?", (uname, uid))
    conn.commit()
    conn.close()
    
    print(f"\n🔔 Вход: {uname} (ID: {uid})")
    
    # Запускаем обновление сайта
    sync_to_github()
    
    markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="💎 Войти в игру", web_app=WebAppInfo(url=WEB_APP_URL))]
    ])
    await message.answer(f"Привет, {uname}!", reply_markup=markup)

async def main():
    init_db()
    print("🚀 Бот запущен. Жду игроков...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
