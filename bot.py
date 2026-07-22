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

    try:
        # Cobalt API ကို Headers အမှန်နဲ့ တောင်းခံခြင်း
        response = requests.post(
            "https://co.wuk.sh/api/json",
            json={
                "url": url,
                "isAudioOnly": True,
                "downloadMode": "audio"
            },
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            timeout=15
        )
        
        data = response.json()
        audio_url = data.get("url") or data.get("audio")
        
        if not audio_url and "picker" in data:
            picker = data.get("picker")
            if len(picker) > 0:
                audio_url = picker[0].get("url")

        if audio_url:
            await update.message.reply_audio(
                audio=audio_url,
                caption="ရပါပြီ ခင်ဗျာ။"
            )
            await msg.delete()
        else:
            await msg.edit_text("❌ ဤလင့်ခ်အတွက် အသံဖိုင် ထုတ်ယူ၍ မရပါ။")

    except Exception as e:
        logging.error(f"Error: {e}")
        await msg.edit_text("❌ ဆာဗာချိတ်ဆက်မှု အမှားအယွင်း ရှိနေပါသည်။")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download_audio))
    
    print("Bot စတင်အလုပ်လုပ်နေပါပြီ...")
    app.run_polling()
