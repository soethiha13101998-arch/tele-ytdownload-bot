import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8878161711:AAF9hFhqclivp09aL-QqhpZfoY8S6tH7RKY"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('ဒေါင်းမဲ့ link ကိုပို့လိုက် ဝူးဝါး" အာလာမချောင်နဲ့ ပါးချခံရမယ်')

async def download_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if not (url.startswith("http://") or url.startswith("https://")):
        return

    msg = await update.message.reply_text(" ခဏစောင့်ပါ၊ သီချင်းဖိုင်ကို ထုတ်ယူနေပါပြီ...")

    try:
        # Cobalt API ကို အသုံးပြု၍ YouTube Link မှ MP3 တိုက်ရိုက်ရယူခြင်း
        response = requests.post("https://api.cobalt.tools/api/json", json={
            "url": url,
            "isAudioOnly": True,
            "filenamePattern": "classic"
        }, headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
        
        data = response.json()
        audio_url = None
        
        if data.get("status") in ["redirect", "stream"]:
            audio_url = data.get("url")
        elif data.get("status") == "picker":
            picker = data.get("picker")
            if picker and len(picker) > 0:
                audio_url = picker[0].get("url")
                
        if audio_url:
            await update.message.reply_audio(
                audio=audio_url,
                caption="ရော့....ရရင် ဒိုးတော့"
            )
            await msg.delete()
        else:
            await msg.edit_text(" ဖိုင်ထုတ်ယူ၍ မရပါ။ Link ကို ပြန်စစ်ပေးပါ။")

    except Exception as e:
        logging.error(f"Error: {e}")
        await msg.edit_text(" အမှားအယွင်း ဖြစ်သွားပါသည်။")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download_audio))
    
    print("Bot စတင်အလုပ်လုပ်နေပါပြီ...")
    app.run_polling()
