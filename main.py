import telebot
import json
import time
from datetime import datetime

# Загрузка конфигурации
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
token = config['token']
dev_id = config['dev_id']

bot = telebot.TeleBot(token)

# Загрузка данных из JSON
with open('pre.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

@bot.message_handler(commands=['start'])
def start_command(message):

    if message.chat.id == 653303971:
        bot.send_message(message.chat.id, "куку, Миша я знаю твою тестерскую натуру, так что сильно не душни, ахаххаха, кста это сообщение заготовленно только для тебя по твоему телеграм ID ")  # Отправляем сообщение тестеру

    markup = start_menu_markup()
    bot.send_message(
        message.chat.id,
        f"Привет {message.from_user.first_name}... \nя рад что ты всё же решила взглянуть...",
        reply_markup=markup
    )
    bot.send_message(chat_id=7924880320, text=f"Пользователь @{message.from_user.username or message.from_user.first_name} использовал /start")
    print("ID пользователя, отправившего сообщение:", message.chat.id)

def start_menu_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("полная версия", "только поздравление")
    return markup

@bot.message_handler(func=lambda msg: msg.text == "полная версия")
def full_version_handler(message):
    chat_id = message.chat.id
    
    # Начинаем с последовательного редактирования сообщений из "мысли"
    msg = bot.send_message(chat_id, "ㅤ")  # Отправляем пустое сообщение для начала
    for thought in data["мысли"]:
        bot.send_chat_action(chat_id, "typing")  # Показываем статус "Bot is typing..."
        time.sleep(2.3)  # Задержка между изменениями (в секундах)
        bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=thought)
    
    time.sleep(2.3)  # Задержка между изменениями (в секундах)
    # После завершения "мысли" начинаем дополнять итоговое сообщение
    final_message = "Привет Лиз..."
    msg = bot.send_message(chat_id, final_message)  # Отправляем первое пустое сообщение
    for line in data["итог"]:
        bot.send_chat_action(chat_id, "typing")  # Показываем статус "Bot is typing..."
        time.sleep(3)  # Задержка перед добавлением строки
        final_message += line + "\n"  # Добавляем строку с переводом строки
        bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=final_message)

@bot.message_handler(func=lambda msg: msg.text == "только поздравление")
def just_congratulation_handler(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "\n".join(data["итог"]))  # Отправляем поздравление сразу без анимаций

@bot.message_handler(func=lambda m: True)
def log_message(message):
    chat_name = message.chat.title if message.chat.type != "private" else "Личные сообщения"
    print(f"[{chat_name}] {message.from_user.first_name}: {message.text}")

# Запуск бота
if __name__ == "__main__":
    start_time = datetime.now()
    print(f"Бот запущен в {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    bot.infinity_polling()
