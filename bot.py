import os
import logging
import gspread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from oauth2client.service_account import ServiceAccountCredentials

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Akses Sheet
sheet_odp = client.open("ID_SLOT_PORT").worksheet("TAGGING_ODP")
sheet_odc = client.open("ID_SLOT_PORT").worksheet("TAGGING_ODC")

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "📡 *Bot Tagging ODP & ODC*\n\n"
        "Gunakan perintah berikut untuk mencari tagging:\n\n"
        "🔹 /odptagging - Kirim daftar ODP untuk mencari koordinat TIKOR\n"
        "🔹 /odctagging - Kirim daftar ODC untuk mencari TAGGING ODC\n\n"
        "Contoh:\n"
        "/odptagging\nODP-XXX-01\nODP-YYY-02\n\n"
        "/odctagging\nODC-ABC-03\nODC-DEF-04"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# /odptagging
async def odptagging(update: Update, context: ContextTypes.DEFAULT_TYPE):
    input_text = update.message.text.replace("/odptagging", "").strip()
    input_list = [line.strip() for line in input_text.splitlines() if line.strip()]
    results = []
    data = sheet_odp.get_all_records()

    for odp_name in input_list:
        match = next((row for row in data if str(row.get("ODP_NAME", "")).strip() == odp_name), None)
        if match:
            tikor = match.get("TIKOR", "Tidak ditemukan")
            results.append(f"✅ *{odp_name}*: {tikor}")
        else:
            results.append(f"❌ *{odp_name}*: Tidak ditemukan.")
    await update.message.reply_text("\n".join(results), parse_mode="Markdown")

# /odctagging
async def odctagging(update: Update, context: ContextTypes.DEFAULT_TYPE):
    input_text = update.message.text.replace("/odctagging", "").strip()
    input_list = [line.strip() for line in input_text.splitlines() if line.strip()]
    results = []
    data = sheet_odc.get_all_records()

    for odc_name in input_list:
        match = next((row for row in data if str(row.get("ODC_NAME", "")).strip() == odc_name), None)
        if match:
            tagging = match.get("TAGGING", "Tidak ditemukan")
            results.append(f"✅ *{odc_name}*: {tagging}")
        else:
            results.append(f"❌ *{odc_name}*: Tidak ditemukan.")
    await update.message.reply_text("\n".join(results), parse_mode="Markdown")

# Main app
if __name__ == "__main__":
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("❌ BOT_TOKEN environment variable tidak ditemukan.")
        exit(1)

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("odptagging", odptagging))
    app.add_handler(CommandHandler("odctagging", odctagging))

    print("✅ Bot is running on Render...")
    app.run_polling()