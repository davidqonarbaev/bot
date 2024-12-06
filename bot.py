from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
from datetime import datetime, timedelta
import threading
import schedule


# Sana nomlarini qo'lda o'rnatish
oylik_nomlar = {
    "01": "январь", "02": "февраль", "03": "март", "04": "апрель",
    "05": "май", "06": "июнь", "07": "июль", "08": "август",
    "09": "сентябрь", "10": "октябрь", "11": "ноябрь", "12": "декабрь"
}

# Bot tokeningizni o'rnating
BOT_TOKEN = "7906134403:AAHOXU5h3Hy2bHikbUijlhnP5UZP8L1uito"


# Matnni bo‘laklarga bo‘luvchi funksiya
def split_message(text, max_length=4096):
    """Matnni maksimal uzunlikka qarab bo‘laklarga bo‘ladimi."""
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]


# Inline tugmalar yaratish
def create_inline_buttons():
    keyboard = [
        [
            InlineKeyboardButton("START", callback_data="start"),
            InlineKeyboardButton("TODAY", callback_data="today"),
            InlineKeyboardButton("NEXT DAY", callback_data="next_day")
        ],
        [
            InlineKeyboardButton("AVTO ON", callback_data="auto_on"),
            InlineKeyboardButton("AVTO OFF", callback_data="auto_off")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# Global variable to track auto mode status
auto_mode = False


# Auto mode functionality to fetch next day's lot numbers
def auto_check():
    """Check the next day's lots every morning."""
    while True:
        if auto_mode:
            next_day = datetime.now() + timedelta(days=1)
            kiritilgan_sana = next_day.strftime("%d%m%Y")
            # Call check function to get data
            # (Make sure you pass correct parameters to fetch the data)
            print(f"Auto checking for date: {kiritilgan_sana}")
            # You could also use the check function for fetching data here
        time.sleep(86400)  # Sleep for 1 day


# Botning start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.callback_query:
        # Inline tugmalarni yuborish
        await update.callback_query.message.reply_text(
            "Ассалаўма алейкум! Автономерлар бойынша маглыумат алиу ушын томендеги кнопкаларды басын:",
            reply_markup=create_inline_buttons()
        )
    else:
        # Agar update.callback_query bo'lmasa, boshqa xabarni yuborish
        await update.message.reply_text(
            "Ассалаўма алейкум! Автономерлар бойынша маглыумат алиу ушын томендеги кнопкаларды басын:",
            reply_markup=create_inline_buttons()
        )


# Bugungi kun uchun sana olish
async def today(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    current_date = datetime.now()
    kiritilgan_sana = current_date.strftime("%d%m%Y")
    await check(update, context, kiritilgan_sana)


# Keyingi kun uchun sana olish
async def next_day(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    next_day = datetime.now() + timedelta(days=1)
    kiritilgan_sana = next_day.strftime("%d%m%Y")
    await check(update, context, kiritilgan_sana)


# Sana kiritish
async def enter_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.message.reply_text(
        "Iltimos, sana kiriting (DDMMYYYY formatida):"
    )


# Auto mode ON
async def auto_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global auto_mode
    auto_mode = True
    await update.callback_query.message.reply_text("✅ Автомат тексериу режими косылды!")


# Auto mode OFF
async def auto_off(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global auto_mode
    auto_mode = False
    await update.callback_query.message.reply_text("❌ Автомат тексериу режими оширилди!")


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE, kiritilgan_sana: str) -> None:
    try:
        # Sana formatini tekshirish va formatlash
        sana_obj = datetime.strptime(kiritilgan_sana, "%d%m%Y")
        kun = sana_obj.strftime("%d")
        oy = sana_obj.strftime("%m")
        yil = sana_obj.strftime("%Y")
        inson_formatdagi_sana = f"{kun}-{oylik_nomlar[oy]} {yil}г"
    except ValueError:
        await update.callback_query.message.reply_text("⚠️ Сане кате кириритилген 'ДДММГГГГ'.")
        return

    await update.callback_query.message.reply_text("🔄 Маглыуматлар жукленбекте, кутип турын...")

    # Selenium orqali ma'lumotlarni olish
    driver = webdriver.Chrome()
    lot_data = []
    try:
        driver.get("https://avtoraqam.uzex.uz")
        time.sleep(2)

        # Sahifani kichraytirish
        driver.execute_script("document.body.style.zoom='40%'")
        time.sleep(2)

        # Pop-up oyna mavjudligini tekshirib, uni yopish
        try:
            pop_up_close_button = driver.find_element(By.XPATH, "//button[contains(@class, 'swal2-confirm')]")
            pop_up_close_button.click()  # Pop-up oynasini yopish
            time.sleep(1)
        except:
            print("Pop-up айнасы тауылмады.")

        # Region bo'limiga 95 kiritish
        input_box = driver.find_element(By.NAME, "SearchNum")
        input_box.clear()
        input_box.send_keys("95")
        time.sleep(1)

        # Qidiruv tugmasini bosish
        search_button = driver.find_element(By.CLASS_NAME, "scrollBlock")
        search_button.click()
        time.sleep(1)

        # Sana kiritish
        input_box = driver.find_element(By.ID, "EndDate")
        input_box.clear()
        input_box.send_keys(kiritilgan_sana)
        time.sleep(1)



        # Qidiruv tugmasini bosish
        search_button = driver.find_element(By.CLASS_NAME, "goSearch")
        search_button.click()
        time.sleep(2)

        # Ma'lumotlarni yuklash
        while True:
            try:
                load_more_button = driver.find_element(By.CLASS_NAME, "jscroll-next")
                ActionChains(driver).move_to_element(load_more_button).click().perform()
                time.sleep(2)
            except:
                break

        # Aktiv lotlarni olish
        lots_container = driver.find_element(By.ID, "activeLotsContainer")
        lots = lots_container.find_elements(By.CLASS_NAME, "numberBlockInner")

        for lot in lots:
            try:
                number = lot.find_element(By.CLASS_NAME, "numberImg").text
                start_price = lot.find_element(By.XPATH,
                                               ".//span[contains(text(), 'Старт.цена')]/following-sibling::span").text
                start_price = start_price.replace(' ', '').replace(',', '.')
                start_price = float(start_price)
                lot_data.append((number, start_price))
            except Exception:
                continue

        # Raqamlarni va narxlarni tartiblash
        lot_data.sort(key=lambda x: (x[0].lower(), x[1]))

        # Ma'lumotlarni yuborish
        if not lot_data:
            await update.callback_query.message.reply_text("⚠️ Усы сане ушын маглыумат тауылмады.")
        else:
            reply_text = (
                f"📣 Ассалаўма алейкум @nukus_broker канал агзалары! \n\n📅 Сауда болатын кун: {inson_formatdagi_sana}\n"
                f"📋 Саудага қойылган автономерлер саны: {len(lot_data)}\n ℹ️ | Аукционнанда автономерге Заказ бермекши болсаниз томендеги номерге телеграм аркалы байланысын!\n☎️ | +998999560950 -BROKER\n❇️ | @DOMINANT_admin -BROKER\n\n"
                "✅[Автономерлар дизими] 💰[Стартовая цена]\n"
            )
            for number, price in lot_data:
                formatted_price = f"{int(price):,}".replace(",", " ")
                reply_text += f"✅[{number}]     💰{formatted_price} сум\n"

            reply_text += f"\n📅 Сауда болатын кун: {inson_formatdagi_sana}\n \n ℹ️ | Аукционнанда автономерге Заказ бермекши болсаниз томендеги номерге телеграм аркалы байланысын!\n☎️ | +998999560950 -BROKER \n❇️ | @DOMINANT_admin -BROKER\n📲 | Каналда кунде таза партия койылады. Сол ушын агза болын! @nukusbroker"  # @nukus_broker qo'shish


            # Xabarni bo‘laklarga bo‘lib yuborish
            for part in split_message(reply_text):
                await update.callback_query.message.reply_text(part)
    finally:
        driver.quit()


# Botni ishga tushirish
def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(today, pattern="today"))
    application.add_handler(CallbackQueryHandler(next_day, pattern="next_day"))
    application.add_handler(CallbackQueryHandler(enter_date, pattern="enter_date"))
    application.add_handler(CallbackQueryHandler(auto_on, pattern="auto_on"))
    application.add_handler(CallbackQueryHandler(auto_off, pattern="auto_off"))
    application.add_handler(CallbackQueryHandler(start, pattern="start"))

    print("🤖 Bot иследи ✅")

    # Start auto checking in a separate thread
    threading.Thread(target=auto_check, daemon=True).start()

    application.run_polling()


if __name__ == "__main__":
    main()
