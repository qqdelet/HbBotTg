import telebot
import json
import time
import sqlite3
from datetime import datetime

# Загрузка конфигурации
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
token = config['token']
admin_id = config['dev_id']

with open('pre.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

bot = telebot.TeleBot(token)

# Инициализация базы данных SQLite
db_path = 'bot_database.sqlite3'
conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()

# Создание таблицы пользователей
cursor.execute("""
CREATE TABLE IF NOT EXISTS whitelist (
    user_id INTEGER PRIMARY KEY,
    username TEXT
)
""")
conn.commit()

# Проверка, находится ли пользователь в вайтлисте
def is_user_whitelisted(user_id):
    cursor.execute("SELECT user_id FROM whitelist WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None

# Добавление пользователя в вайтлист
def add_user_to_whitelist(user_id, username):
    cursor.execute("INSERT OR IGNORE INTO whitelist (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()

# Обработка команды /start
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.chat.id
    username = message.from_user.username or message.from_user.first_name
    
    
    if is_user_whitelisted(user_id):
        markup = start_menu_markup()
        bot.send_message(user_id, "Добро пожаловать обратно!", reply_markup=markup)
    else:
        bot.send_message(user_id, "Ваш запрос на доступ отправлен администратору.")
        bot.send_message(admin_id, f"Запрос на добавление в вайтлист от @{username} (ID: {user_id})\n"
                                    "Для подтверждения введите /approve {user_id} или /reject {user_id}")

# Команда для подтверждения пользователя
@bot.message_handler(commands=['approve'])
def approve_user(message):
    try:
        user_id = int(message.text.split()[1])
        cursor.execute("SELECT username FROM whitelist WHERE user_id = ?", (user_id,))
        username = cursor.fetchone()
        if username:
            bot.send_message(admin_id, "Этот пользователь уже добавлен.")
            return

        add_user_to_whitelist(user_id, "approved_user")
        bot.send_message(user_id, "Ваш доступ подтвержден! Приятного общения.")
        bot.send_message(admin_id, f"Пользователь с ID {user_id} добавлен в вайтлист.")
    except (IndexError, ValueError):
        bot.send_message(admin_id, "Ошибка: необходимо указать ID пользователя.")

@bot.message_handler(commands=['reject'])
def reject_user(message):
    try:
        user_id = int(message.text.split()[1])
        bot.send_message(user_id, "К сожалению, ваш запрос отклонен.")
        bot.send_message(admin_id, f"Пользователь с ID {user_id} отклонен.")
    except (IndexError, ValueError):
        bot.send_message(admin_id, "Ошибка: необходимо указать ID пользователя.")

# Обработка ответа админа пользователю
@bot.message_handler(commands=['reply'])
def reply_user(message):
    msg = bot.send_message(admin_id, "Введите ID пользователя, которому нужно ответить:")
    bot.register_next_step_handler(msg, process_user_id_reply)

def process_user_id_reply(message):
    try:
        user_id = int(message.text)
        msg = bot.send_message(admin_id, "Введите текст сообщения для отправки пользователю:")
        bot.register_next_step_handler(msg, process_reply_text, user_id)
    except ValueError:
        bot.send_message(admin_id, "Ошибка: необходимо указать корректный ID пользователя.")

def process_reply_text(message, user_id):
    reply_text = message.text
    bot.send_message(user_id, f"Сообщение от администратора: {reply_text}")
    bot.send_message(admin_id, f"Сообщение для {user_id} отправлено.")


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
