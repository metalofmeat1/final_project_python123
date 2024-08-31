import os
import json
import asyncio
import sqlite3
import logging
from aiogram import types, Router, Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from dotenv import load_dotenv, find_dotenv

# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('bot.log'),
                              logging.StreamHandler()])

load_dotenv(find_dotenv())
bot = Bot(token=os.getenv('TOKEN'))

dp = Dispatcher()
user_private_router = Router()
dp.include_router(user_private_router)

db_path = os.path.join(os.path.dirname(__file__), 'bot_data.db')
admins_file = os.path.join(os.path.dirname(__file__), 'admins.json')


def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS user_requests (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        message TEXT NOT NULL,
                        answered_by INTEGER,
                        status TEXT NOT NULL DEFAULT 'pending'
                      )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS feedback_ratings (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            rating INTEGER CHECK(rating BETWEEN 1 AND 5),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                          )''')

    conn.commit()
    conn.close()
    logging.info("Database initialized.")


def get_all_requests():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT id, user_id, message, answered_by, status FROM user_requests')
    result = cursor.fetchall()

    conn.close()
    logging.info(f"Retrieved all requests: {result}")
    return result


def add_feedback_rating(user_id, rating):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('INSERT INTO feedback_ratings (user_id, rating) VALUES (?, ?)', (user_id, rating))
        conn.commit()
        conn.close()
        logging.info(f"Feedback rating added successfully: user_id={user_id}, rating={rating}")
    except sqlite3.Error as e:
        logging.error(f"SQLite error occurred while adding feedback rating: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while adding feedback rating: {e}")


def get_average_rating():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT AVG(rating) FROM feedback_ratings')
        result = cursor.fetchone()[0]
        conn.close()

        if result is not None:
            average_rating = round(result, 2)
            logging.info(f"Retrieved average rating: {average_rating}")
        else:
            average_rating = None
            logging.info("No ratings found for average calculation.")

        return average_rating
    except sqlite3.Error as e:
        logging.error(f"SQLite error occurred while retrieving average rating: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while retrieving average rating: {e}")
        return None


async def send_feedback_request(user_id):
    try:
        await bot.send_message(user_id,
                               "🌟 Оцініть, будь ласка, якість нашої зворотного зв'язку (від 1 до 5). Напишіть /feedback (ваша оцінка).")
    except Exception as e:
        logging.error(f"Error sending feedback request to user_id={user_id}: {e}")


def get_user_requests(user_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT id, message, answered_by, status FROM user_requests WHERE user_id = ?', (user_id,))
    result = cursor.fetchall()

    conn.close()
    logging.info(f"Retrieved all requests for user_id={user_id}: {result}")
    return result


def add_user_request(user_id, message):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('INSERT INTO user_requests (user_id, message) VALUES (?, ?)', (user_id, message))
    request_id = cursor.lastrowid

    conn.commit()
    conn.close()
    logging.info(f"User request added: id={request_id}, user_id={user_id}, message='{message}'")
    return request_id


def check_request_status(user_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT id, status FROM user_requests WHERE user_id = ? AND status = "pending"', (user_id,))
    result = cursor.fetchall()

    conn.close()
    logging.info(f"Checked request status for user_id={user_id}: {result}")
    return result


def add_admin(user_id):
    admins = read_json(admins_file)
    if user_id not in admins:
        admins.append(user_id)
        with open(admins_file, 'w') as f:
            json.dump(admins, f, indent=4)
        logging.info(f"Admin ID {user_id} added.")
        return True
    return False


async def update_request_status(request_id, admin_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('UPDATE user_requests SET answered_by = ?, status = "answered" WHERE id = ?', (admin_id, request_id))

    # Получаем user_id, чтобы отправить запрос на обратную связь
    cursor.execute('SELECT user_id FROM user_requests WHERE id = ?', (request_id,))
    user_id = cursor.fetchone()[0]

    conn.commit()
    conn.close()
    logging.info(f"Updated request status: request_id={request_id}, answered_by={admin_id}")

    # Отправляем запрос на обратную связь
    asyncio.create_task(send_feedback_request(user_id))


def get_request_details(request_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT user_id, message, answered_by, status FROM user_requests WHERE id = ?', (request_id,))
    result = cursor.fetchone()

    conn.close()
    logging.info(f"Retrieved request details for request_id={request_id}: {result}")
    return result


def read_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
                return data
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON from {file_path}: {e}")
                return []
    else:
        return []


def parse_command_args(command_text):
    parts = command_text.split(maxsplit=2)
    if len(parts) < 2:
        return None, None
    user_id = parts[1]
    if not user_id.isdigit():
        return None, None
    message = parts[2] if len(parts) > 2 else ''
    return int(user_id), message


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("Привіт, це бот для підтримки користувачів, тут ти зможеш зв'язатись з адміністратором")
    logging.info(f"Start command received from user_id={message.from_user.id}")


@user_private_router.message(Command('msg'))
async def handle_msg_command(message: types.Message):
    admin_ids = read_json(admins_file)

    # Разделяем команду на части
    command_parts = message.text.split(maxsplit=2)

    # Проверка для админа: он должен ввести 3 части (id, сообщение)
    if str(message.from_user.id) in admin_ids:
        if len(command_parts) != 3:
            await message.answer("⚙️ Неправильний формат команди. Використовуйте /msg [id] [повідомлення].")
            logging.warning(f"Invalid command format from admin user_id={message.from_user.id}")
            return
        user_id = command_parts[1]
        user_message = command_parts[2]
    else:
        # Проверка для обычного пользователя: он должен ввести 2 части (сообщение)
        if len(command_parts) != 2:
            await message.answer("⚙️ Неправильний формат команди. Використовуйте /msg [повідомлення].")
            logging.warning(f"Invalid command format from user_id={message.from_user.id}")
            return
        user_id = None  # Адресат будет выбран автоматически
        user_message = command_parts[1]

    if str(message.from_user.id) not in admin_ids:
        # Логика для обычного пользователя
        request_id = add_user_request(message.from_user.id, user_message)

        for admin_id in admin_ids:
            try:
                await bot.send_message(admin_id,
                                       f"Сообщение от пользователя {message.from_user.full_name} (ID: {message.from_user.id}): '{user_message}'")
            except Exception as e:
                logging.error(f"Error sending message to admin_id={admin_id}: {e}")
        await message.answer("Ваше повідомлення було відправлено адміністраторам.")
        await send_feedback_request(message.from_user.id)
    else:
        # Логика для админа
        request_list = check_request_status(user_id)
        if request_list:
            request_id, status = request_list[0]
            try:
                await bot.send_message(user_id, f"️Сообщение от админа: '{user_message}'")
                await update_request_status(request_id, message.from_user.id)
                await message.answer(f"Повідомлення відправлено користувачу {user_id}.")
            except Exception as e:
                await message.answer(f"Ошибка при отправке сообщения пользователю {user_id}.")
                logging.error(f"Error sending admin message to user_id={user_id}: {e}")
        else:
            await message.answer(f"Запитів від користувача {user_id} немає, або вони були оброблені адмінами.")


@user_private_router.message(Command('requests'))
async def handle_all_requests_command(message: types.Message):
    admin_ids = read_json(admins_file)

    if str(message.from_user.id) not in admin_ids:
        await message.answer("⚙️ Тільки адміністратори можуть використовувати цю команду.")
        logging.warning(f"Unauthorized requests command attempt by user_id={message.from_user.id}")
        return

    command_args = message.text.split(maxsplit=1)
    if len(command_args) < 2:
        await message.answer("⚙️ Неправильний формат команди. Використовуйте /requests [id].")
        logging.warning(f"Invalid requests command format from user_id={message.from_user.id}")
        return

    user_id = command_args[1]
    if not user_id.isdigit():
        await message.answer("⚙️ Неправильний формат ID. Введіть числовий ID.")
        logging.warning(f"Invalid user ID format: {user_id}")
        return

    user_id = int(user_id)
    logging.info(f"Processing requests command for user_id={user_id}")

    all_requests = get_user_requests(user_id)
    if all_requests:
        response_message = f"🔍 Запити для користувача ID: {user_id}\n\n"
        response_message += f"{'ID':<5} {'Повідомлення':<30} {'Відповів':<10} {'Статус':<10}\n"
        response_message += "─" * 36 + "\n"

        for request in all_requests:
            request_id, user_message, answered_by, status = request
            answered_by_name = "Ніхто" if answered_by is None else f"ID {answered_by}"
            status_emoji = "✅" if status == "answered" else "⏳" if status == "pending" else ""
            response_message += (
                f"{request_id:<5} {user_message:<30} {answered_by_name:<10} {status_emoji} {status:<10}\n")

        await message.answer(response_message)
        logging.info(f"Requests details for user_id={user_id} sent to admin user_id={message.from_user.id}")
    else:
        await message.answer(f"Немає запитів для користувача ID: {user_id}.")
        logging.info(f"No requests found for user_id={user_id}.")


@user_private_router.message(Command('addadmin'))
async def handle_add_admin_command(message: types.Message):
    admin_ids = read_json(admins_file)

    if str(message.from_user.id) not in admin_ids:
        await message.answer("⚙️ Тільки адміністратори можуть використовувати цю команду.")
        logging.warning(f"Unauthorized addadmin command attempt by user_id={message.from_user.id}")
        return

    command_args = message.text.split(maxsplit=1)
    if len(command_args) < 2:
        await message.answer("⚙️ Неправильний формат команди. Використовуйте /addadmin [id].")
        logging.warning(f"Invalid addadmin command format from user_id={message.from_user.id}")
        return

    new_admin_id = command_args[1]
    if not new_admin_id.isdigit():
        await message.answer("⚙️ Неправильний формат ID. Введіть числовий ID.")
        logging.warning(f"Invalid admin ID format: {new_admin_id}")
        return

    new_admin_id = int(new_admin_id)
    if add_admin(new_admin_id):
        await message.answer(f"Адміністратор з ID {new_admin_id} був доданий.")
        logging.info(f"Admin ID {new_admin_id} added by user_id={message.from_user.id}")
    else:
        await message.answer(f"Адміністратор з ID {new_admin_id} вже є в списку.")
        logging.info(f"Admin ID {new_admin_id} already exists in the list.")


@user_private_router.message(Command('feedback'))
async def handle_feedback_command(message: types.Message):
    user_id = message.from_user.id
    command_parts = message.text.split(maxsplit=1)

    if len(command_parts) < 2:
        await message.answer("⚙️ Неправильний формат команди. Використовуйте /feedback [рейтинг].")
        logging.warning(f"Feedback command format error from user_id={user_id}.")
        return

    rating = command_parts[1]

    if not rating.isdigit() or not (1 <= int(rating) <= 5):
        await message.answer("⚙️ Неправильний формат рейтингу. Введіть число від 1 до 5.")
        logging.warning(f"Invalid feedback rating from user_id={user_id}: {rating}")
        return

    try:
        add_feedback_rating(user_id, int(rating))
        await message.answer("Дякуємо за ваш відгук!")
        logging.info(f"Feedback rating added from user_id={user_id}: {rating}")
    except Exception as e:
        await message.answer("⚙️ Сталася помилка при збереженні вашого рейтингу.")
        logging.error(f"Error adding feedback rating from user_id={user_id}: {e}")


@user_private_router.message(Command('average_rating'))
async def handle_average_rating_command(message: types.Message):
    logging.info(f"Received /average_rating command from user_id={message.from_user.id}")

    average_rating = get_average_rating()
    if average_rating is not None:
        await message.answer(f"🔍 Середній рейтинг зворотного зв'язку: {average_rating}")
        logging.info(f"Average rating sent to user_id={message.from_user.id}")
    else:
        await message.answer("⚙️ Немає даних для обчислення середнього рейтингу.")
        logging.info(f"No average rating data available for user_id={message.from_user.id}")


async def on_shutdown():
    logging.info('Bot is shutting down')


async def main():
    init_db()

    dp.shutdown.register(on_shutdown)
    await bot.delete_webhook(drop_pending_updates=True)

    update_types = dp.resolve_used_update_types()
    logging.info(f"Allowed update types: {update_types}")

    await dp.start_polling(bot, allowed_updates=update_types)

if __name__ == "__main__":
    asyncio.run(main())
