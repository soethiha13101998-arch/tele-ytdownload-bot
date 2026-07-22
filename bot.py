import os
import logging
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8878161711:AAF9hFhqclivp09aL-QqhpZfoY8S6tH7RKY"
WORLD_TIDES_API_KEY = "b41048e0-35f9-4ff4-8591-fd5ff25a3309"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('⚓ မင်္ဂလာပါ အစ်ကိုရေ! ဆိပ်ကမ်းနာမည် (ဥပမာ - Lagos, Durban, Cape Town) ကို ပို့ပေးပါ၊ ရာသီဥတုနှင့် 00:00 မှ 24:00 ထိ တစ်ရက်စာ နာရီအလိုက် ဒီရေဇယားကို ရှာဖွေပေးပါမယ်။')

async def get_port_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    port_name = update.message.text.strip()
    msg = await update.message.reply_text(f"🔍 {port_name} ဆိပ်ကမ်း၏ ရာသီဥတုနှင့် ဒီရေအချက်အလက်များကို ဆွဲထုတ်နေပါပြီ...")

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

        # 3. WorldTides API (00:00 ကနေစပြီး တနာရီခြားစီ 24 နာရီစာ ယူရန်)
        tide_url = f"https://www.worldtides.info/api/v3?heights&step=3600&days=1&lat={lat}&lon={lon}&key={WORLD_TIDES_API_KEY}"
        tide_res = requests.get(tide_url, timeout=10).json()
        
        # ယနေ့ရက်စွဲကို ပထမဆုံးရရှိသော ဒေတာမှ (သို့မဟုတ် လက်ရှိအချိန်မှ) ထုတ်ယူရန်
        target_date = datetime.now().strftime("%Y-%m-%d")
        heights_data = tide_res.get("heights", [])
        
        if heights_data and "date" in heights_data[0]:
            target_date = heights_data[0]["date"].split("T")[0]

        tide_text = f"\n🌊 **Tide Table ({target_date}):**\n```text\n"
        
        if heights_data:
            added_hours = set()
            for item in heights_data:
                full_date = item["date"]
                if "T" in full_date:
                    date_part, time_part_full = full_date.split("T")
                    # တောင်းဆိုထားသော ရက်စွဲနှင့် ကိုက်ညီမှသာ ထည့်မည်
                    if date_part == target_date:
                        time_hm = time_part_full[:5] # HH:MM
                        # တနာရီခြားစီ (ဥပမာ - 00:00, 01:00 ... 24:00) မိနစ် 00 ဖြစ်မှယူမည်
                        if time_hm.endswith(":00") and time_hm not in added_hours:
                            height = float(item["height"])
                            h_str = f"+{height:.2f} m" if height >= 0 else f"{height:.2f} m"
                            tide_text += f"{time_hm} ➔ {h_str}\n"
                            added_hours.add(time_hm)
            
            # အကယ်၍ 24:00 (သို့မဟုတ် 00:00 နောက်တစ်ရက်) စာရင်းပါလာလျှင် 24:00 အဖြစ်ပြရန်
            for item in heights_data:
                full_date = item["date"]
                if "T" in full_date:
                    date_part, time_part_full = full_date.split("T")
                    time_hm = time_part_full[:5]
                    if time_hm == "00:00" and date_part != target_date and "24:00" not in added_hours:
                        height = float(item["height"])
                        h_str = f"+{height:.2f} m" if height >= 0 else f"{height:.2f} m"
                        tide_text += f"24:00 ➔ {h_str}\n"
                        added_hours.add("24:00")

            tide_text += "```"
        else:
            tide_text = f"\n🌊 **Tide Table ({target_date}):** ဤဆိပ်ကမ်းအတွက် ဒေတာ မရှိသေးပါ။"

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
