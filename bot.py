import asyncio
import sqlite3
import json
import os
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
    # Создаем таблицу со всеми нужными полями, включая инвентарь
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, 
        username TEXT,
        res INTEGER DEFAULT 0,
        money REAL DEFAULT 100,
        med INTEGER DEFAULT 0,
        arts INTEGER DEFAULT 0,
        hp REAL DEFAULT 100,
        shield_time INTEGER DEFAULT 0,
        inventory TEXT DEFAULT '[]')''')
    conn.commit()
    conn.close()

def sync_to_github():
    try:
        conn = sqlite3.connect('economy_game.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username, res, med FROM users ORDER BY res DESC LIMIT 10")
        rows = cursor.fetchall()
        conn.close()
        data = [{"username": r[0], "res": r[1], "med": r[2]} for r in rows]
        with open('players.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        # Авто-пуш на гитхаб
        os.system('git add players.json && git commit -m "leaderboard update" && git push origin main')
    except Exception as e:
        print(f"Ошибка синхронизации: {e}")

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
        [types.InlineKeyboardButton(text="🕹️ ВОЙТИ В ИГРУ", web_app=WebAppInfo(url=WEB_APP_URL))]
    ])
    await message.answer(f"Привет, {uname}! Твой завод готов к работе.", reply_markup=markup)

@dp.message(F.web_app_data)
async def handle_save(message: types.Message):
    # Принимаем JSON из игры
    try:
        d = json.loads(message.web_app_data.data)
        uid = message.from_user.id
        conn = sqlite3.connect('economy_game.db')
        cursor = conn.cursor()
        cursor.execute("""UPDATE users SET 
            res=?, money=?, med=?, arts=?, hp=?, shield_time=?, inventory=? 
            WHERE user_id=?""", 
            (d['res'], d['money'], d['med'], d['arts'], d['hp'], d['shield'], json.dumps(d.get('inv', [])), uid))
        conn.commit()
        conn.close()
        await message.answer("💾 Данные сохранены в облаке!")
        sync_to_github()
    except Exception as e:
        await message.answer("❌ Ошибка сохранения")
        print(e)

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
