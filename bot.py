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

    # API 1: Cobalt
    try:
        res = requests.post("https://api.cobalt.tools/api/json", json={
            "url": url,
            "isAudioOnly": True,
            "filenamePattern": "classic"
        }, headers={"Accept": "application/json", "Content-Type": "application/json"}, timeout=8)
        data = res.json()
        if data.get("status") in ["redirect", "stream"]:
            audio_url = data.get("url")
        elif data.get("status") == "picker":
            picker = data.get("picker")
            if picker and len(picker) > 0:
                audio_url = picker[0].get("url")
    except Exception:
        pass

    # API 2: SaveFrom / Alternative public endpoint
    if not audio_url:
        try:
            res = requests.get(f"https://delink.api.red-stone.workers.dev/?url={url}", timeout=8)
            data = res.json()
            if data.get("success"):
                audio_url = data.get("audio") or data.get("url")
        except Exception:
            pass

    if audio_url:
        try:
            await update.message.reply_audio(audio=audio_url, caption="ရပါပြီ ခင်ဗျာ။")
            await msg.delete()
            return
        except Exception:
            pass

    await msg.edit_text("❌ YouTube ဘက်မှ လော့ခ်ချထားသဖြင့် ဤလင့်ခ်ကို ထုတ်ယူ၍ မရပါ။")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download_audio))
    app.run_polling()
