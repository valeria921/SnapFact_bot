import telebot
from telebot import types
import requests
import time
from dotenv import load_dotenv
import os


load_dotenv()

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

user_last_start = {}


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    now = time.time()

    # Prevent repeated /start within 2 seconds
    if user_id in user_last_start and now - user_last_start[user_id] < 10:
        return

    user_last_start[user_id] = now

    bot.send_message(
        user_id,
        f"Hey {message.from_user.first_name}! 🤓\n\n"
        "You weren’t planning to learn something totally random today, but... here you are. "
        "Get ready for a fact so weird it’ll stick in your brain forever!"
    )
    send_category_menu(user_id)


def send_category_menu(chat_id):
    response = requests.get('https://idonotlikedocker.com/api/categories')
    data = response.json()

    markup = types.InlineKeyboardMarkup()
    for item in data:
        button = types.InlineKeyboardButton(
            text=item['category_title'],
            callback_data=f"category_{item['id']}"
        )
        markup.add(button)

    bot.send_message(chat_id, '👇 Choose a category to get a fact:', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data.startswith("category_"):
        # User chose a category
        category_id = call.data.split("_")[1]
        send_random_fact(call.message.chat.id, category_id)

    elif call.data.startswith("next_"):
        # User clicked "next fact"
        category_id = call.data.split("_")[1]
        send_random_fact(call.message.chat.id, category_id)

    elif call.data == "change":
        send_category_menu(call.message.chat.id)


def send_random_fact(chat_id, category_id):
    response = requests.get(f"https://idonotlikedocker.com/api/categories/{category_id}/random_fact/")
    data = response.json()

    title = data.get('fact_title', 'No title')
    text = data.get('fact_text', 'No text found')

    message = f"🧠 *{title}*\n\n{text}"  # Bold title, normal text

    # Create buttons: Next Fact and Change Category
    markup = types.InlineKeyboardMarkup()
    next_button = types.InlineKeyboardButton("🔁 Next Fact", callback_data=f"next_{category_id}")
    change_button = types.InlineKeyboardButton("🔄 Change Category", callback_data="change")
    markup.add(next_button, change_button)

    bot.send_message(chat_id, message, parse_mode='Markdown', reply_markup=markup)


@bot.message_handler(commands=['website'])
def site(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text="🌐 Visit Website", url="https://idonotlikedocker.com")
    markup.add(btn)
    bot.send_message(message.chat.id, "Check out our website:", reply_markup=markup)


bot.polling(none_stop=True, allowed_updates=["message", "callback_query"])
