import json
import telebot
import openai

# 🔹 Telegram және OpenAI API кілттеріңді енгіз
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

# 🔹 Сөйлесу тарихын сақтау (есте сақтау үшін)
conversation_memory = {}

def generate_ai_response(user_id, user_message):
    """OpenAI Chat Model арқылы жауап генерациялау"""
    history = conversation_memory.get(user_id, [])

    # Соңғы 5 хабарламаны сақтау
    messages = [{"role": "system", "content": "You are a helpful flower shop assistant."}]
    for msg in history[-5:]:
        messages.append({"role": "user", "content": msg})

    messages.append({"role": "user", "content": user_message})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7
    )

    reply = response.choices[0].message.content.strip()

    # Жаңа хабарламаны жадыға сақтау
    conversation_memory.setdefault(user_id, []).append(user_message)
    conversation_memory[user_id].append(reply)

    return reply


def save_order_to_file(order_data):
    """Google Sheets орнына тапсырысты JSON файлға сақтау"""
    try:
        with open("orders.json", "r", encoding="utf-8") as f:
            orders = json.load(f)
    except FileNotFoundError:
        orders = []

    orders.append(order_data)

    with open("orders.json", "w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=4)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    text = message.text.strip()

    # Егер тапсырыс берілсе, файлға жазамыз
    if "гүл" in text.lower() or "rose" in text.lower() or "order" in text.lower():
        order_data = {
            "user": message.from_user.username or message.from_user.first_name,
            "message": text
        }
        save_order_to_file(order_data)
        bot.send_message(user_id, "🌸 Тапсырысыңыз қабылданды! Рақмет!")
    else:
        reply = generate_ai_response(user_id, text)
        bot.send_message(user_id, reply)


print("🤖 Flower Shop Bot жұмыс істеп тұр...")
bot.polling(non_stop=True)