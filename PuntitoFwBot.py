from dotenv import load_dotenv
load_dotenv()
import os
TOKEN = os.getenv("TOKEN")
import telebot
bot = telebot.TeleBot(TOKEN)

canal_id="-1001285680844"

@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(message, "Hola! soy PuntitoForWardBot, simplemente utiliza /forward respondiendo a un mensaje para reenviarlo uwu")

@bot.message_handler(commands=["forward"])
def forwardeo(message):
    if "group" in message.chat.type:
        if message.reply_to_message is not None and not message.reply_to_message.from_user.is_bot:
            bot.forward_message(message.chat.id, message.chat.id, message.reply_to_message.message_id)
            bot.forward_message(canal_id, message.chat.id, message.reply_to_message.message_id)
        else:
            bot.reply_to(message, "El comando se usa citando un mensaje de otro usuario po, owo")
    else:
        bot.reply_to(message, "Disculpa, solo funciono en grupos uwu")

@bot.message_handler(commands=["canal"])
def send_canal(message):
    bot.reply_to(message, "https://t.me/PuntitoForwarded")

bot.polling(none_stop=True)

