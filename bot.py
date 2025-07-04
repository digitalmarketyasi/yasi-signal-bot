from db import init_db
init_db()
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from db import (
    init_db, add_user, get_user, update_subscription,
    get_subscription_info, check_tx_hash, save_tx_hash,
    add_lottery_chance, get_user_chances, generate_ref_link,
    add_referral, get_user_ref_chances, get_total_ref_count
)
from datetime import datetime, timedelta

TOKEN = 'توکن_تو_اینجا'

bot = telebot.TeleBot(TOKEN)
init_db()

MAIN_MENU = [
    '🎯 دریافت سیگنال روزانه',
    '🛒 خرید اشتراک',
    '💼 وضعیت اشتراک من',
    '🎁 شرکت در قرعه کشی',
    '📘 راهنمای شرکت در قرعه کشی',
    '🎫 تعداد شانس‌های من'
]

# ---------- START ----------
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    ref_code = message.text.split(' ')[1] if len(message.text.split()) > 1 else None
    add_user(user_id, ref_code)
    send_main_menu(message.chat.id, "سلام به ربات خوش آمدید 👋")

# ---------- MAIN MENU ----------
def send_main_menu(chat_id, text="منوی اصلی"):
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [InlineKeyboardButton(text=opt, callback_data=opt) for opt in MAIN_MENU]
    markup.add(*buttons)
    bot.send_message(chat_id, text, reply_markup=markup)

# ---------- CALLBACKS ----------
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id

    if call.data == '🎯 دریافت سیگنال روزانه':
        if get_subscription_info(user_id)['active']:
            bot.answer_callback_query(call.id, "✅ شما اشتراک فعال دارید. سیگنال‌ها ارسال خواهند شد.")
        else:
            bot.answer_callback_query(call.id, "❌ شما در حال حاضر اشتراکی ندارید.")
            bot.send_message(call.message.chat.id, "🔒 لطفاً برای دریافت روزانه سیگنال‌ها اشتراک تهیه کنید.")

    elif call.data == '🛒 خرید اشتراک':
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("📅 اشتراک ماهانه - ۱۵ تتر", callback_data='sub_month'),
            InlineKeyboardButton("📅 اشتراک ۳ ماهه - ۴۰ تتر", callback_data='sub_3month'),
            InlineKeyboardButton("📅 اشتراک ۶ ماهه - ۷۵ تتر", callback_data='sub_6month'),
            InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data='back_main')
        )
        bot.edit_message_text("🛒 یکی از پلن‌های زیر را انتخاب کنید:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith('sub_'):
        duration = {'sub_month': 30, 'sub_3month': 90, 'sub_6month': 180}[call.data]
        bot.send_message(call.message.chat.id, f"""💸 لطفاً مبلغ اشتراک را به یکی از آدرس‌های زیر واریز کنید و هش تراکنش را ارسال نمایید:

💠 BSC: `0x526f90D8C0085d1Ad3b2ef99EA2c35c2BA896089`
💠 TRON: `TF8sWHTVH6SoXTkkyuGZYkCkr5H68Q16n8`

مدت اشتراک: {duration} روز
""", parse_mode='Markdown')
        update_subscription(user_id, duration)

    elif call.data == '💼 وضعیت اشتراک من':
        sub = get_subscription_info(user_id)
        if sub['active']:
            bot.send_message(call.message.chat.id, f"""✅ اشتراک فعال دارید:

📅 تاریخ فعال‌سازی: {sub['start']}
📅 تاریخ انقضا: {sub['end']}""")
        else:
            bot.send_message(call.message.chat.id, "❌ اشتراک فعالی ندارید.")

    elif call.data == '🎁 شرکت در قرعه کشی':
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("💰 خرید شانس", callback_data='buy_chance'),
            InlineKeyboardButton("👥 دعوت کاربر جدید", callback_data='invite_user'),
            InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data='back_main')
        )
        bot.edit_message_text("🎁 شرکت در قرعه‌کشی:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == 'buy_chance':
        bot.send_message(call.message.chat.id, """💸 لطفاً مبلغ هر شانس (۱ تتر) را به یکی از آدرس‌های زیر واریز کنید و هش تراکنش را ارسال نمایید:

🔹 BSC: `0x33e5Eb673df62Dcf4c18810da9a6b9cD4D8114D8`
🔹 TRON: `TPwLFsinNaA1C1i3Meq46TsC6vNFmPaY1Z`

سپس هش تراکنش را همینجا ارسال کنید. پس از تأیید، کد شانس برای شما صادر می‌شود.""", parse_mode='Markdown')

    elif call.data == 'invite_user':
        link = generate_ref_link(user_id)
        bot.send_message(call.message.chat.id, f"""🔗 لینک دعوت اختصاصی شما:

https://t.me/YourBotUsername?start={link}

هر ۳ دعوت = ۱ شانس در قرعه‌کشی""")

    elif call.data == '🎫 تعداد شانس‌های من':
        bought = get_user_chances(user_id)
        refs = get_user_ref_chances(user_id)
        total_refs = get_total_ref_count(user_id)
        bot.send_message(call.message.chat.id, f"""🎫 شانس‌های شما:

✅ شانس‌های خریداری‌شده: {len(bought)}
کدها: {' - '.join(bought) if bought else 'ندارید'}

✅ شانس‌های دعوت: {len(refs)} (از {total_refs} دعوت)
کدها: {' - '.join(refs) if refs else 'ندارید'}""")

    elif call.data == '📘 راهنمای شرکت در قرعه کشی':
        bot.send_message(call.message.chat.id, """📘 راهنمای شرکت در قرعه‌کشی:

۱. با پرداخت ۱ تتر می‌توانید یک شانس خریداری کنید.
۲. با دعوت ۳ نفر به ربات، یک شانس رایگان دریافت می‌کنید.
۳. به محض رسیدن تعداد شرکت‌کنندگان به حد نصاب، قرعه‌کشی انجام خواهد شد.
۴. کدهای شانس شما را می‌توانید از گزینه "🎫 تعداد شانس‌های من" مشاهده کنید.""")

    elif call.data == '🔙 بازگشت به منوی اصلی' or call.data == 'back_main':
        send_main_menu(call.message.chat.id)

# ---------- HASH MESSAGE ----------
@bot.message_handler(func=lambda m: True)
def handle_messages(message):
    user_id = message.from_user.id
    if len(message.text) == 64 and message.text.isalnum():
        tx = message.text
        if check_tx_hash(tx):
            bot.reply_to(message, "❌ این هش قبلاً استفاده شده.")
        else:
            code = add_lottery_chance(user_id, tx)
            save_tx_hash(tx)
            bot.reply_to(message, f"✅ هش تأیید شد.\nکد شانس شما: {code}")
    else:
        bot.send_message(message.chat.id, "❌ پیام نامعتبر. لطفاً فقط هش یا گزینه‌ای از منو را انتخاب کنید.")

# ---------- POLLING ----------
bot.infinity_polling()
