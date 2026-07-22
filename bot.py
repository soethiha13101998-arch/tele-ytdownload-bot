import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import yt_dlp

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8878161711:AAF9hFhqclivp09aL-QqhpZfoY8S6tH7RKY"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('ဒေါင်းမဲ့ link ကိုပို့လိုက် ဝူးဝါး" အာလာမချောင်နဲ့ ပါးချခံရမယ်')

async def download_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if not (url.startswith("http://") or url.startswith("https://")):
        return

    msg = await update.message.reply_text("⏳ ခဏစောင့်ပါ၊ သီချင်းဖိုင်ကို ထုတ်ယူနေပါပြီ...")

    output_file = "song.mp3"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        # MP3 ဖိုင်အဖြစ် ပြောင်းသွားမည့် နာမည်
        if os.path.exists("song.mp3"):
            audio_path = "song.mp3"
        elif os.path.exists("song.m4a"):
            audio_path = "song.m4a"
        else:
            audio_path = "song"

        await update.message.reply_audio(
            audio=open(audio_path, 'rb'),
            caption="ရော့....ရရင် ဒိုးတော့"
        )
        
        # ပို့ပြီးပါက Server ထဲမှ ဖိုင်ကို ရှင်းလင်းရန်
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
        await msg.delete()

    except Exception as e:
        logging.error(f"Error: {e}")
        await msg.edit_text("❌ ဖိုင်ထုတ်ယူ၍ မရပါ။ Link ကို ပြန်စစ်ပေးပါ။")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download_audio))
    
    print("Bot စတင်အလုပ်လုပ်နေပါပြီ...")
    app.run_polling()
