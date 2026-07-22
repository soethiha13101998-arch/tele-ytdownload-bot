import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8878161711:AAF9hFhqclivp09aL-QqhpZfoY8S6tH7RKY"
WORLD_TIDES_API_KEY = "YOUR_WORLD_TIDES_API_KEY_HERE" # ကိုယ့်ရဲ့ API Key ထည့်ရန်

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('⚓ မင်္ဂလာပါ အစ်ကိုရေ! ဆိပ်ကမ်းနာမည် (ဥပမာ - Lome, Walvis Bay) ကို ပို့ပေးပါ၊ ရာသီဥတုနှင့် တစ်ရက်စာ နာရီအလိုက် ဒီရေဇယားကို ရှာဖွေပေးပါမယ်။')

async def get_port_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    port_name = update.message.text.strip()
    msg = await update.message.reply_text(f"🔍 {port_name} ဆိပ်ကမ်း၏ ရာသီဥတုနှင့် တစ်ရက်စာ ဒီရေဇယားကို ဆွဲထုတ်နေပါပြီ...")

    # 1. Geocoding
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

        # 2. Weather API
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m,wind_direction_10m"
        weather_res = requests.get(weather_url, timeout=10).json()
        current = weather_res.get("current", {})
        temp = current.get("temperature_2m", "N/A")
        wind_speed = current.get("wind_speed_10m", "N/A")
        wind_dir = current.get("wind_direction_10m", "N/A")

        # 3. WorldTides API (တနာရီခြားစီဖြင့် တစ်ရက်စာ ယူရန် step=3600 လိုအပ်သည်)
        tide_url = f"https://www.worldtides.info/api/v3?heights&step=3600&days=1&lat={lat}&lon={lon}&key={WORLD_TIDES_API_KEY}"
        tide_res = requests.get(tide_url, timeout=10).json()
        
        tide_text = "\n🌊 **တရက်စာ နာရီအလိုက် ဒီရေဇယား (Tide Table):**\n```text\n"
        if "heights" in tide_res and tide_res["heights"]:
            for item in tide_res["heights"]:
                # အချိန်ကို 24 နာရီစနစ် (HH:MM) ဖြင့်ထုတ်ရန်
                dt = item["date"].split("T")[1][:5]
                height = float(item["height"])
                # မီတာ တန်ဖိုးကို + သို့မဟုတ် - လက္ခဏာနှင့်အတူ အသေသပ်ဆုံးပြရန်
                h_str = f"+{height:.2f} m" if height >= 0 else f"{height:.2f} m"
                tide_text += f"{dt} ➔ {h_str}\n"
            tide_text += "```"
        else:
            tide_text = "\n🌊 **တရက်စာ ဒီရေဇယား:** အချက်အလက် ရယူ၍ မရပါ။"

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
