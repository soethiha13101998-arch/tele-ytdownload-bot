import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import yt_dlp

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8878161711:AAF9hFhqclivp09aL-QqhpZfoY8S6tH7RKY"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('ဒေါင်းမဲ့ link ကိုပို့လိုက်ပါ အစ်ကိုရေ...')

async def download_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if not (url.startswith("http://") or url.startswith("https://")):
        return

    msg = await update.message.reply_text("⏳ ခဏစောင့်ပါ၊ သီချင်းဖိုင်ကို ဒေါင်းလုဒ်လုပ်နေပါပြီ...")

    output_file = "song.mp3"
    
    # ဖိုင်ဟောင်းရှိနေရင် ဖျက်ရန်
    if os.path.exists(output_file):
        os.remove(output_file)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'song',
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        if os.path.exists(output_file):
            with open(output_file, 'rb') as audio:
                await update.message.reply_audio(
                    audio=audio,
                    caption="ရပါပြီ ခင်ဗျာ။"
                )
            await msg.delete()
        else:
            await msg.edit_text("❌ ဖိုင်ထုတ်ယူ၍ မရပါ။")
            
    except Exception as e:
        logging.error(f"Error: {e}")
        await msg.edit_text("❌ Error ဖြစ်သွားပါသည်။ Link ကို စစ်ဆေးပေးပါ။")
        
    finally:
        if os.path.exists(output_file):
            os.remove(output_file)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download_audio))
    
    print("Bot စတင်အလုပ်လုပ်နေပါပြီ...")
    app.run_polling()
