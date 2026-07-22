import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8878161711:AAF9hFhqclivp09aL-QqhpZfoY8S6tH7RKY"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('ဒေါင်းမဲ့ link ကိုပို့လိုက်ပါ အစ်ကိုရေ...')

async def download_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if not (url.startswith("http://") or url.startswith("https://")):
        return

    msg = await update.message.reply_text("⏳ ခဏစောင့်ပါ၊ သီချင်းဖိုင်ကို ထုတ်ယူနေပါပြီ...")

    audio_url = None

    # Method 1: Cobalt API သုံးရန်
    try:
        response = requests.post("https://api.cobalt.tools/api/json", json={
            "url": url,
            "isAudioOnly": True,
            "filenamePattern": "classic"
        }, headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        }, timeout=10)
        
        data = response.json()
        if data.get("status") in ["redirect", "stream"]:
            audio_url = data.get("url")
        elif data.get("status") == "picker":
            picker = data.get("picker")
            if picker and len(picker) > 0:
                audio_url = picker[0].get("url")
    except Exception as e:
        logging.error(f"Cobalt Error: {e}")

    # Method 2: Cobalt မရရင် DLTAPIs သို့မဟုတ် အခြားလင့်ခ်သို့ ပြောင်းရန်
    if not audio_url:
        try:
            alt_res = requests.get(f"https://delink.api.red-stone.workers.dev/?url={url}", timeout=10)
            alt_data = alt_res.json()
            if alt_data.get("success"):
                audio_url = alt_data.get("audio") or alt_data.get("url")
        except Exception as e:
            logging.error(f"Alt API Error: {e}")

    if audio_url:
        try:
            await update.message.reply_audio(
                audio=audio_url,
                caption="ရပါပြီ ခင်ဗျာ။"
            )
            await msg.delete()
            return
        except Exception as e:
            logging.error(f"Telegram Send Error: {e}")

    await msg.edit_text("❌ ဖိုင်ထုတ်ယူ၍ မရပါ။ YouTube ဘက်မှ လော့ခ်ချထားခြင်း သို့မဟုတ် API ချို့ယွင်းနေပါသည်။")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download_audio))
    
    print("Bot စတင်အလုပ်လုပ်နေပါပြီ...")
    app.run_polling()
