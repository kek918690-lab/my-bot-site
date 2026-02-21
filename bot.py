import asyncio
import sqlite3
import json
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo
from datetime import datetime

# Твои данные
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
        bricks INTEGER DEFAULT 0,
        money INTEGER DEFAULT 100)''')
    conn.commit()
    conn.close()

def sync_to_github():
    """Выгрузка топ-игроков на GitHub"""
    try:
        conn = sqlite3.connect('economy_game.db')
        cursor = conn.cursor()
        # Сортируем по количеству кирпичей (Топ игроков)
        cursor.execute("SELECT username, bricks FROM users ORDER BY bricks DESC LIMIT 20")
        rows = cursor.fetchall()
        conn.close()

        players_data = [{"username": r[0], "bricks": r[1]} for r in rows]
        
        with open('players.json', 'w', encoding='utf-8') as f:
            json.dump(players_data, f, ensure_ascii=False, indent=4)
        
        os.system('git add players.json')
        os.system('git commit -m "Update leaderboard"')
        os.system('git push origin main')
        print("✅ Рейтинг обновлен на GitHub")
    except Exception as e:
        print(f"❌ Ошибка Гита: {e}")

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
    
    print(f"🔔 Зашел: {uname}")
    sync_to_github()
    
    markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="💎 Войти в Империю", web_app=WebAppInfo(url=WEB_APP_URL))]
    ])
    await message.answer(f"Привет, {uname}! Твои кирпичи сохраняются в общем рейтинге.", reply_markup=markup)

# ОБРАБОТЧИК СОХРАНЕНИЯ ИЗ ИГРЫ
@dp.message(F.web_app_data)
async def handle_save(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        bricks = data.get("bricks", 0)
        uid = message.from_user.id
        
        conn = sqlite3.connect('economy_game.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET bricks = ? WHERE user_id = ?", (bricks, uid))
        conn.commit()
        conn.close()
        
        print(f"💾 Игрок {message.from_user.first_name} сохранил {bricks} кирпичей")
        await message.answer(f"✅ Прогресс сохранен! У тебя {bricks}🧱 в рейтинге.")
        sync_to_github() # Сразу пушим новый топ на сайт
    except Exception as e:
        print(f"Ошибка сохранения: {e}")

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
