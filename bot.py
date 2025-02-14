from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import datetime
from persiantools.jdatetime import JalaliDate
import pytz

TOKEN = "7772533851:AAFBokdPxskFT8kEPB55pl9cP8XXZMDdTAA"

# دکمه‌های کیبورد
back_button = KeyboardButton("🔙 برگشت به منوی اصلی")

main_keyboard = ReplyKeyboardMarkup(
    [[KeyboardButton("📅 نمایش تاریخ امروز")],
     [KeyboardButton("🔄 تبدیل میلادی به شمسی"), KeyboardButton("🔄 تبدیل شمسی به میلادی")],
     [KeyboardButton("⏰ اختلاف ساعت بین پایتخت‌ها")]],
    resize_keyboard=True
)

capital_timezones = {
    "Tehran": "Asia/Tehran", "Washington": "America/New_York", "London": "Europe/London",
    "Berlin": "Europe/Berlin", "Beijing": "Asia/Shanghai", "Tokyo": "Asia/Tokyo",
    "Moscow": "Europe/Moscow", "Paris": "Europe/Paris", "Rome": "Europe/Rome",
    "Ottawa": "America/Toronto", "Canberra": "Australia/Sydney", "Brasília": "America/Sao_Paulo",
    "New Delhi": "Asia/Kolkata", "Ankara": "Europe/Istanbul", "Cairo": "Africa/Cairo",
    "Madrid": "Europe/Madrid", "Athens": "Europe/Athens", "Oslo": "Europe/Oslo",
    "Stockholm": "Europe/Stockholm", "Helsinki": "Europe/Helsinki", "Bangkok": "Asia/Bangkok",
    "Jakarta": "Asia/Jakarta", "Seoul": "Asia/Seoul", "Buenos Aires": "America/Argentina/Buenos_Aires",
    "Mexico City": "America/Mexico_City", "Riyadh": "Asia/Riyadh", "Baghdad": "Asia/Baghdad",
    "Kuwait City": "Asia/Kuwait", "Abu Dhabi": "Asia/Dubai", "Doha": "Asia/Qatar",
    "Kuala Lumpur": "Asia/Kuala_Lumpur", "Hanoi": "Asia/Ho_Chi_Minh", "Manila": "Asia/Manila",
    "Pretoria": "Africa/Johannesburg", "Nairobi": "Africa/Nairobi", "Addis Ababa": "Africa/Addis_Ababa",
    "Amsterdam": "Europe/Amsterdam"
}

async def start(update: Update, context: CallbackContext):
    # زمانی که دکمه برگشت فشرده می‌شود یا دستور start ارسال می‌شود، منوی اصلی را نشان می‌دهیم
    await update.message.reply_text(
        "سلام! از دکمه‌های زیر استفاده کن:",
        reply_markup=main_keyboard
    )

async def get_date(update: Update, context: CallbackContext):
    today_gregorian = datetime.datetime.now().strftime("%Y-%m-%d")
    today_jalali = JalaliDate.today().strftime("%Y-%m-%d")
    keyboard = [[back_button]]  # اضافه کردن دکمه برگشت به منو اصلی
    await update.message.reply_text(
        f"📆 تاریخ امروز:\nمیلادی: {today_gregorian}\nشمسی: {today_jalali}",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def gregorian_to_jalali(update: Update, context: CallbackContext):
    await update.message.reply_text("یک تاریخ میلادی به فرم YYYY-MM-DD ارسال کنید:")
    context.user_data['convert'] = 'gregorian_to_jalali'
    keyboard = [[back_button]]  # اضافه کردن دکمه برگشت به منو اصلی
    await update.message.reply_text(reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def jalali_to_gregorian(update: Update, context: CallbackContext):
    await update.message.reply_text("یک تاریخ شمسی به فرم YYYY-MM-DD ارسال کنید:")
    context.user_data['convert'] = 'jalali_to_gregorian'
    keyboard = [[back_button]]  # اضافه کردن دکمه برگشت به منو اصلی
    await update.message.reply_text(reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def convert_date(update: Update, context: CallbackContext):
    text = update.message.text
    conversion_type = context.user_data.get('convert')
    
    try:
        if conversion_type == 'gregorian_to_jalali':
            year, month, day = map(int, text.split('-'))
            jalali_date = JalaliDate(datetime.date(year, month, day)).strftime("%Y-%m-%d")
            await update.message.reply_text(f"📆 تاریخ شمسی: {jalali_date}")
        elif conversion_type == 'jalali_to_gregorian':
            year, month, day = map(int, text.split('-'))
            gregorian_date = JalaliDate(year, month, day).to_gregorian().strftime("%Y-%m-%d")
            await update.message.reply_text(f"📆 تاریخ میلادی: {gregorian_date}")
        else:
            await update.message.reply_text("❌ لطفاً یک گزینه معتبر را انتخاب کنید.")
    except Exception:
        await update.message.reply_text("❌ فرمت تاریخ نادرست است! لطفاً مجدداً ارسال کنید.")
    
    context.user_data.pop('convert', None)

async def select_countries(update: Update, context: CallbackContext):
    keyboard = [[KeyboardButton(capital)] for capital in capital_timezones.keys()] + [[back_button]]  # اضافه کردن دکمه برگشت به منو اصلی
    await update.message.reply_text("لطفاً شهر پایتخت مبدا را انتخاب کنید:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    context.user_data['time_difference_step'] = 'origin'

async def handle_country_selection(update: Update, context: CallbackContext):
    capital = update.message.text
    step = context.user_data.get('time_difference_step')
    
    if capital == "🔙 برگشت به منوی اصلی":
        # اگر دکمه برگشت فشار داده شد، منوی اصلی را نمایش می‌دهیم
        await start(update, context)
        return
    
    if step == 'origin':
        context.user_data['origin'] = capital
        keyboard = [[KeyboardButton(capital)] for capital in capital_timezones.keys() if capital != context.user_data['origin']] + [[back_button]]  # اضافه کردن دکمه برگشت
        await update.message.reply_text("لطفاً شهر پایتخت مقصد را انتخاب کنید:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        context.user_data['time_difference_step'] = 'destination'
    elif step == 'destination':
        context.user_data['destination'] = capital
        origin_tz = pytz.timezone(capital_timezones[context.user_data['origin']])
        destination_tz = pytz.timezone(capital_timezones[capital])
        now = datetime.datetime.utcnow()
        origin_offset = origin_tz.utcoffset(now).total_seconds() / 3600
        destination_offset = destination_tz.utcoffset(now).total_seconds() / 3600
        time_difference = destination_offset - origin_offset
        
        # نمایش ساعت دقیق مبدأ و مقصد
        origin_time = datetime.datetime.now(origin_tz).strftime("%H:%M")
        destination_time = datetime.datetime.now(destination_tz).strftime("%H:%M")
        
        keyboard = [[back_button]]  # اضافه کردن دکمه برگشت به منو اصلی
        await update.message.reply_text(f"⏰ اختلاف ساعت بین {context.user_data['origin']} و {context.user_data['destination']} برابر با {time_difference} ساعت است.\n"
                                       f"⏰ ساعت فعلی در {context.user_data['origin']}: {origin_time}\n"
                                       f"⏰ ساعت فعلی در {context.user_data['destination']}: {destination_time}",
                                       reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        context.user_data.pop('time_difference_step', None)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Text("📅 نمایش تاریخ امروز"), get_date))
    app.add_handler(MessageHandler(filters.Text("🔄 تبدیل میلادی به شمسی"), gregorian_to_jalali))
    app.add_handler(MessageHandler(filters.Text("🔄 تبدیل شمسی به میلادی"), jalali_to_gregorian))
    app.add_handler(MessageHandler(filters.Text("⏰ اختلاف ساعت بین پایتخت‌ها"), select_countries))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_country_selection))
    
    print("✅ ربات در حال اجراست...")
    app.run_polling()

if __name__ == "__main__":
    main()
