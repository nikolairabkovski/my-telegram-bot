import os
import random
import telebot
from telebot import types
import sqlite3
from datetime import datetime

# Токен из переменной окружения (для Render)
TOKEN = os.getenv("8216947861:AAHvMJz0ZwkEP4ovH5OX9tXepuhyHvPkrpo")  # если не задана, используем "0" (но лучше всегда задавать)
bot = telebot.TeleBot(TOKEN)

# -------- База данных (SQLite) --------
def init_db():
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

init_db()  # при старте создаём таблицу

# -------- Обработчики --------

# Приветствие
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

# Меню
@bot.message_handler(func=lambda message: message.text == "Открыть меню 📜")
def show_menu(message):
    bot.send_message(
        message.chat.id,
        "Главное меню:\n"
        "• Напиши «я красивый» – узнай свой рейтинг красоты 😉\n"
        "• В группе спроси «кто крутой?» – я выберу случайного счастливчика!"
    )

# -------- Новая функциональность --------

# 1. "я красивый" – процент красоты
@bot.message_handler(func=lambda message: message.text.lower() == 'я красивый')
def beauty_rating(message):
    user = message.from_user
    # случайное число от 0 до 100
    rating = random.randint(0, 100)
    # упоминаем пользователя (по имени или юзернейму)
    mention = f"[{user.first_name}](tg://user?id={user.id})"
    response = f"{mention}, вы красивы на {rating}%! 🌟"
    # сохраняем статистику
    update_stats(user.id, user.first_name, 'beauty')
    bot.reply_to(message, response, parse_mode='Markdown')

# 2. "кто крутой" – случайный участник чата (только для групп/супергрупп)
@bot.message_handler(func=lambda message: message.text.lower() == 'кто крутой')
def who_is_cool(message):
    chat = message.chat
    # Проверяем, что это группа или супергруппа
    if chat.type not in ['group', 'supergroup']:
        bot.reply_to(message, "Эта команда работает только в групповых чатах!")
        return

    # Получаем список участников (максимум 200, но для демонстрации хватит)
    # Если бот не администратор, может не получить полный список, но попробуем
    try:
        members = bot.get_chat_members(chat.id)
        # Исключаем ботов и самого бота (опционально)
        users = [m.user for m in members if not m.user.is_bot]
        if not users:
            bot.reply_to(message, "В чате нет обычных пользователей 😅")
            return
        chosen = random.choice(users)
        mention = f"[{chosen.first_name}](tg://user?id={chosen.id})"
        response = f"🏆 Самый крутой сегодня – {mention}! 🎉"
        # сохраняем статистику для выбранного пользователя
        update_stats(chosen.id, chosen.first_name, 'cool')
        bot.reply_to(message, response, parse_mode='Markdown')
    except Exception as e:
        # Если не удалось получить список (например, бот не администратор), предложим альтернативу
        bot.reply_to(message, "Не удалось получить список участников. Убедитесь, что я администратор в этом чате, или попробуйте позже.")

# Можно добавить обработчик на "я крутой" – тогда ответит тому, кто спросил
@bot.message_handler(func=lambda message: message.text.lower() == 'я крутой')
def i_am_cool(message):
    user = message.from_user
    rating = random.randint(0, 100)
    mention = f"[{user.first_name}](tg://user?id={user.id})"
    response = f"{mention}, вы крутой на {rating}%! 🔥"
    update_stats(user.id, user.first_name, 'cool')
    bot.reply_to(message, response, parse_mode='Markdown')

# -------- Запуск --------
if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()