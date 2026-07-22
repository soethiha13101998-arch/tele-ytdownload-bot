import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8878161711:AAF9hFhqclivp09aL-QqhpZfoY8S6tH7RKY"
WORLD_TIDES_API_KEY = "b41048e0-35f9-4ff4-8591-fd5ff25a3309" # ကိုယ့်ရဲ့ WorldTides API Key ထည့်ရန်

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('⚓ မင်္ဂလာပါ အစ်ကိုရေ! ဆိပ်ကမ်းနာမည် (ဥပမာ - Walvis Bay, Lagos Bar, Abidjan) ကို ပို့ပေးပါ၊ ရာသီဥတုနှင့် နာရီအလိုက် ဒီရေအတတ်အကျများကို ရှာဖွေပေးပါမယ်။')

async def get_port_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    port_name = update.message.text.strip()
    msg = await update.message.reply_text(f"🔍 {port_name} ဆိပ်ကမ်း၏ ရာသီဥတုနှင့် ဒီရေအချက်အလက်များကို ဆွဲထုတ်နေပါပြီ...")

    # 1. Geocoding: ဆိပ်ကမ်းနာမည်မှ Latitude / Longitude ရယူရန်
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

        # 2. Weather API: အပူချိန်နှင့် လေတိုက်နှုန်း
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m,wind_direction_10m"
        weather_res = requests.get(weather_url, timeout=10).json()
        current = weather_res.get("current", {})
        temp = current.get("temperature_2m", "N/A")
        wind_speed = current.get("wind_speed_10m", "N/A")
        wind_dir = current.get("wind_direction_10m", "N/A")

        # 3. WorldTides API: နာရီအလိုက် ရေအတတ်အကျ အချိန်နှင့် အမြင့်
        tide_url = f"https://www.worldtides.info/api/v3?heights&extremes&lat={lat}&lon={lon}&key={WORLD_TIDES_API_KEY}"
        tide_res = requests.get(tide_url, timeout=10).json()
        
        tide_text = "\n🌊 **Hourly Tide Table (နာရီအလိုက် ရေအတတ်အကျ):**\n"
        if "heights" in tide_res and tide_res["heights"]:
            for item in tide_res["heights"][:6]: # ပထမဆုံး ၆ ခု (နာရီအလိုက်)
                # အချိန်ကို Formatted လုပ်ရန် (ISO format မှ HH:MM သို့)
                dt = item["date"].split("T")[1][:5]
                height = item["height"]
                tide_text += f"• {dt} - {height} m\n"
        else:
            tide_text += "• ဒီရေအချက်အလက် ရယူ၍ မရပါ။\n"

        # ဆိပ်ကမ်းအခြေအနေ အပြည့်အစုံ တည်ဆောက်ခြင်း
        response_text = (
            f"📍 **Port:** {city} ({country})\n"
            f"🌍 **Coordinates:** Lat {lat}, Lon {lon}\n\n"
            f"🌡 **Temperature:** {temp}°C\n"
            f"💨 **Wind Speed:** {wind_speed} km/h (Dir: {wind_dir}°)\n"
            f"{tide_text}"
        )

        await msg.edit_text(response_text, parse_mode="Markdown")

    except Exception as e:
        logging.error(f"Error: {e}")
        await msg.edit_text("❌ အချက်အလက်ရယူရာတွင် ဆာဗာချိတ်ဆက်မှု အမှားအယွင်း ရှိသွားပါသည်။")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), get_port_info))
    
    print("Port Weather & Tide Bot စတင်အလုပ်လုပ်နေပါပြီ...")
    app.run_polling()
