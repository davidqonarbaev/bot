from selenium import webdriver
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
import time
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# ChromeDriver avtomatik yuklash va sozlash
chromedriver_autoinstaller.install()

# Brauzerni ochish
driver = webdriver.Chrome()

def search_numbers(numbers, price):
    """
    Ushbu funksiya raqamlarni qidiradi va natijalarni chiqaradi.
    :param numbers: Tanlangan raqamlar ro'yxati
    :param price: Boshlang'ich narx
    """
    results = [f"Старт.цена {price:,} сум\n"]
    for num in numbers:
        # Raqamni formatlash
        lot_number = f"95A{str(num).zfill(3)}SA"

        # Qidiruv inputlarini topish va to'ldirish
        input_box = driver.find_element(By.NAME, "SearchNum")
        input_box.clear()
        input_box.send_keys("95")

        input_box_region = driver.find_element(By.NAME, "SearchRegion")
        input_box_region.clear()
        input_box_region.send_keys(lot_number)

        # Qidiruv tugmasini bosish
        search_button = driver.find_element(By.CLASS_NAME, "goSearch")
        search_button.click()

        # Natijani kutish
        time.sleep(1)

        # Natijalarni olish
        try:
            result = driver.find_element(By.CLASS_NAME, "numberImg")
            results.append(f"{result.text}")
        except:
            continue

    results.append(
        "Joqarıdaǵı avtonomerler alıw kerek bolsa +99899 956 0950 @dominant_admin xabarlasıń! @nukus_broker \n"
    )
    return "\n".join(results)

# Telegram bot uchun /search komandasini yaratish
def search_command(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    context.bot.send_message(chat_id=update.effective_chat.id, text="Qidiruvni boshlayapman...")

    try:
        # Saytga kirish
        driver.get("https://avtoraqam.uzex.uz")

        # Raqamlar to'plami va ularning narxlari
        data = [
            ([1, 7, 100, 111, 222, 555, 700, 777, 888], 9375000),
            ([2, 5, 10, 20, 50, 70, 77, 80, 101, 200, 202, 300, 333, 444, 500, 505, 707, 800, 808, 999], 3750000),
            # Boshqa raqamlar va narxlar qo'shish mumkin
        ]

        # Har bir raqam to'plamini qidirish va natijalarni yuborish
        for numbers, price in data:
            result_text = search_numbers(numbers, price)
            context.bot.send_message(chat_id=update.effective_chat.id, text=result_text)

    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Xatolik yuz berdi: {e}")

    finally:
        driver.quit()

# Botni ishga tushirish
def main():
    updater = Updater("7906134403:AAHOXU5h3Hy2bHikbUijlhnP5UZP8L1uito")  # O'zingizning bot tokeningizni yozing
    dispatcher = updater.dispatcher

    # /search komandasini botga ulash
    dispatcher.add_handler(CommandHandler("search", search_command))

    # Botni ishga tushirish
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
