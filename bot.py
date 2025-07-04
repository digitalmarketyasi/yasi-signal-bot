
import telebot

BOT_TOKEN = "5225970776:AAGgVaLPicOps-in5IS7XamfPXp4oOufUEk"

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "سلام! به ربات خوش آمدید. 🎉")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "دستور شما: " + message.text)

bot.polling()
