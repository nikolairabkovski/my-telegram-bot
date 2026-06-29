import os
import telebot
from telebot import types

# Хостинг сам передаст токен из настроек в эту переменную
BOT_TOKEN = os.environ.get('7759838197:AAF2MXrM4gqbjQh47_HrBpJPIdZn3jST6Cw')
bot = telebot.TeleBot(BOT_TOKEN)

# Реагируем на текст "привет", "Привет" или команду /start
@bot.message_handler(func=lambda message: message.text.lower() == 'привет' or message.text == '/start')
def welcome(message):
    # Создаем клавиатуру с кнопкой
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu_button = types.KeyboardButton("Открыть меню 📜")
    markup.add(menu_button)
    
    # Отправляем приветствие
    bot.send_message(
        message.chat.id, 
        f"Привет, {message.from_user.first_name}! Рад тебя видеть. Нажми на кнопку ниже, чтобы перейти в меню.", 
        reply_markup=markup
    )

# Реагируем на нажатие кнопки меню
@bot.message_handler(func=lambda message: message.text == "Открыть меню 📜")
def show_menu(message):
    bot.send_message(
        message.chat.id, 
        "Вы перешли в главное меню! Здесь пока пусто, но скоро появятся новые функции. 😉"
    )

# Запуск бота в режиме постоянного опроса
if __name__ == '__main__':
    print("Бот успешно запущен и слушает сервер...")
    bot.infinity_polling()
