import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8878161711:AAF9hFhqclivp09aL-QqhpZfoY8S6tH7RKY"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('⚓ မင်္ဂလာပါ အစ်ကိုရေ! ဆိပ်ကမ်းနာမည် (ဥပမာ - Walvis Bay သို့မဟုတ် Singapore) ကို ပို့ပေးပါ၊ ရာသီဥတုနဲ့ ဒီရေအချက်အလက်များကို ရှာဖွေပေးပါမယ်။')

async def get_port_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    port_name = update.message.text.strip()
    msg = await update.message.reply_text(f"🔍 {port_name} ဆိပ်ကမ်း၏ ရာသီဥတုအချက်အလက်များကို ရှာဖွေနေပါပြီ...")

    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={port_name}&count=1&language=en&format=json"
    try:
        geo_res = requests.get(geo_url, timeout=10).json()
        if not geo_res.get("results"):
            await msg.edit_text("❌ ထိုဆိပ်ကမ်းအမည်ကို ရှာမတွေ့ပါ။ စာလုံးပေါင်း ပြန်စစ်ပြီး ရိုက်ထည့်ပေးပါ။")
            return
        
        location = geo_res["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        country = location.get("country", "")
        city = location.get("name", port_name)

        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m,wind_direction_10m"
        weather_res = requests.get(weather_url, timeout=10).json()
        
        current = weather_res.get("current", {})
        temp = current.get("temperature_2m", "N/A")
        wind_speed = current.get("wind_speed_10m", "N/A")
        wind_dir = current.get("wind_direction_10m", "N/A")

        response_text = (
            f"📍 **Port:** {city} ({country})\n"
            f"🌍 **Coordinates:** Lat {lat}, Lon {lon}\n\n"
            f"🌡 **Temperature:** {temp}°C\n"
            f"💨 **Wind Speed:** {wind_speed} km/h (Dir: {wind_dir}°)\n\n"
            f"💡 *မှတ်ချက်:* ဆိပ်ကမ်းဒီရေ (Tide) အချက်အလက်များပါ ထပ်မံထည့်သွင်းပေးပါမည်။"
        )

        await msg.edit_text(response_text, parse_mode="Markdown")

    except Exception as e:
        logging.error(f"Error: {e}")
        await msg.edit_text("❌ အချက်အလက်ရယူရာတွင် ဆာဗာချိတ်ဆက်မှု အမှားအယွင်း ရှိသွားပါသည်။")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), get_port_info))
    
    print("Port Weather Bot စတင်အလုပ်လုပ်နေပါပြီ...")
    app.run_polling()
