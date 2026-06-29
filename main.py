import os
import random
import telebot
from telebot import types
import sqlite3

# -------- Получение токена --------
# Токен должен быть задан в переменной окружения BOT_TOKEN (на Render)
TOKEN = os.getenv("8216947861:AAHvMJz0ZwkEP4ovH5OX9tXepuhyHvPkrpo")
if not TOKEN:
    print("❌ Ошибка: переменная окружения BOT_TOKEN не задана!")
    print("Пожалуйста, добавьте её в настройках Render (Environment Variables).")
    exit(1)  # остановка, если токена нет

bot = telebot.TeleBot(TOKEN)

# -------- База данных (SQLite) --------
def init_db():
    # Если используете Persistent Disk на Render, измените путь, например: '/data/bot_stats.db'
    conn = sqlite3.connect('bot_stats.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stats (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            beauty_requests INTEGER DEFAULT 0,
            cool_mentions INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def update_stats(user_id, name, field):
    conn = sqlite3.connect('bot_stats.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO stats (user_id, name, beauty_requests, cool_mentions)
        VALUES (?, ?, 0, 0)
        ON CONFLICT(user_id) DO UPDATE SET name = excluded.name
    ''', (user_id, name))
    if field == 'beauty':
        cursor.execute('UPDATE stats SET beauty_requests = beauty_requests + 1 WHERE user_id = ?', (user_id,))
    elif field == 'cool':
        cursor.execute('UPDATE stats SET cool_mentions = cool_mentions + 1 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

init_db()  # создаём таблицу при старте

# -------- Обработчики команд --------

@bot.message_handler(func=lambda message: message.text.lower() == 'привет' or message.text == '/start')
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu_button = types.KeyboardButton("Открыть меню 📜")
    markup.add(menu_button)
    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! Рад тебя видеть. Нажми на кнопку ниже, чтобы перейти в меню.",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "Открыть меню 📜")
def show_menu(message):
    bot.send_message(
        message.chat.id,
        "Главное меню:\n"
        "• Напиши «я красивый» – узнай свой рейтинг красоты 😉\n"
        "• В группе спроси «кто крутой?» – я выберу случайного счастливчика!"
    )

@bot.message_handler(func=lambda message: message.text.lower() == 'я красивый')
def beauty_rating(message):
    user = message.from_user
    rating = random.randint(0, 100)
    mention = f"[{user.first_name}](tg://user?id={user.id})"
    response = f"{mention}, вы красивы на {rating}%! 🌟"
    update_stats(user.id, user.first_name, 'beauty')
    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text.lower() == 'кто крутой')
def who_is_cool(message):
    chat = message.chat
    if chat.type not in ['group', 'supergroup']:
        bot.reply_to(message, "Эта команда работает только в групповых чатах!")
        return
    try:
        members = bot.get_chat_members(chat.id)
        users = [m.user for m in members if not m.user.is_bot]
        if not users:
            bot.reply_to(message, "В чате нет обычных пользователей 😅")
            return
        chosen = random.choice(users)
        mention = f"[{chosen.first_name}](tg://user?id={chosen.id})"
        response = f"🏆 Самый крутой сегодня – {mention}! 🎉"
        update_stats(chosen.id, chosen.first_name, 'cool')
        bot.reply_to(message, response, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, "Не удалось получить список участников. Убедитесь, что я администратор в этом чате, или попробуйте позже.")

@bot.message_handler(func=lambda message: message.text.lower() == 'я крутой')
def i_am_cool(message):
    user = message.from_user
    rating = random.randint(0, 100)
    mention = f"[{user.first_name}](tg://user?id={user.id})"
    response = f"{mention}, вы крутой на {rating}%! 🔥"
    update_stats(user.id, user.first_name, 'cool')
    bot.reply_to(message, response, parse_mode='Markdown')

if __name__ == '__main__':
    print("✅ Бот успешно запущен и слушает сервер...")
    bot.infinity_polling()