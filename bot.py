import telebot
from telebot import types
import os

# دریافت توکن از متغیر محیطی
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# حذف وب‌هوک قبلی اگر وجود داشته باشه
bot.remove_webhook()

# هندلر برای دستور /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("🎁 شرکت در قرعه‌کشی")
    item2 = types.KeyboardButton("📜 قوانین")
    item3 = types.KeyboardButton("💰 موجودی من")
    item4 = types.KeyboardButton("ℹ️ درباره ما")

    markup.add(item1)
    markup.add(item2, item3)
    markup.add(item4)

    bot.send_message(message.chat.id, "سلام! به ربات خوش آمدید 🎉", reply_markup=markup)

# اجرای ربات
print("ربات در حال اجراست...")
bot.infinity_polling()
