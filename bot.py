import os
import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Logging konfigurasi
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Token bot dari environment variable
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN tidak ditemukan di environment variable.")

# Koneksi ke Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

sheet = client.open("ID_SLOT_PORT").worksheet("ACTIVE_DEVICE_INFO_JATIMSEL_TIM")

# Fungsi bantu
def log_search(query_type, query_value):
    with open("log.csv", "a") as f:
        f.write(f"{query_type},{query_value}\n")

# Command /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = (
        "<b>Selamat datang di Bot Helpdesk!</b>\n\n"
        "Berikut adalah daftar perintah yang tersedia:\n\n"
        "<b>/start</b> - Menampilkan pesan ini\n"
        "<b>/help</b> - Menampilkan bantuan umum\n"
        "<b>/log</b> - Menampilkan log pencarian data\n\n"
        "<b>🔍 Fitur Pencarian:</b>\n"
        "Kirim <code>/port ipnodeframe/slot/port</code> untuk mencari:\n"
        "• PORT_ID dan TARGET_ID\n"
        "Command :\n"
        "/port 172.55.xx.xxx0/x/x => HWI\n"
        "/port 172.55.xx.xxx1-1-x-x => ZTE\n\n"
        "Standarisasi pencarian Port GPON :\n"
        "1-1-X-X = ZTE|ALU|FIBERHOME\n"
        "0/X/X = HWI\n\n"
        "Lakukan pencarian /ipbb terlebih dahulu agar bisa menentukan Merk OLT tersebut\n\n"
        "Kirim <code>/portid idgpon</code> untuk mencari:\n"
        "• PORT_NUMBER dan NAME_NE\n"
        "Command : /portid 1234xxx-1234xxx\n\n"
        "Kirim <code>/ipbb ipolt</code> untuk mencari:\n"
        "• MERK, VLAN_BROADBAND dan VLAN_VOICE\n"
        "Command : /ipbb 172.55.xx.xxx\n\n"
        "Kirim <code>/sto sto</code> untuk mencari:\n"
        "• Daftar unik NAME_NE dan VENDOR berdasarkan STO\n"
        "Command : /sto sto\n\n"
        "<i>Pastikan data dikirim dalam format yang sesuai.</i>"
    )
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.HTML)

# /help command
async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "<b>Panduan Bot Helpdesk!</b>\n\n"
        "<b>🔍 Fitur Pencarian:</b>\n"
        "Kirim <code>/port ipnodeframe/slot/port</code> untuk mencari:\n"
        "• PORT_ID dan TARGET_ID\n"
        "Command :\n"
        "/port 172.55.xx.xxx0/x/x => HWI\n"
        "/port 172.55.xx.xxx1-1-x-x => ZTE\n\n"
        "Standarisasi pencarian Port GPON :\n"
        "1-1-X-X = ZTE|ALU|FIBERHOME\n"
        "0/X/X = HWI\n\n"
        "Lakukan pencarian /ipbb terlebih dahulu agar bisa menentukan Merk OLT tersebut\n\n"
        "Kirim <code>/portid idgpon</code> untuk mencari:\n"
        "• PORT_NUMBER dan NAME_NE\n"
        "Command : /portid 1234xxx-1234xxx\n\n"
        "Kirim <code>/ipbb ipolt</code> untuk mencari:\n"
        "• MERK, VLAN_BROADBAND dan VLAN_VOICE\n"
        "Command : /ipbb 172.55.xx.xxx\n\n"
        "Kirim <code>/sto sto</code> untuk mencari:\n"
        "• Daftar unik NAME_NE dan VENDOR berdasarkan STO\n"
        "Command : /sto sto\n\n"
        "<i>Pastikan data dikirim dalam format yang sesuai.</i>"
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)

# /port command
async def port(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("❗ Gunakan format: /port <CODE>")
        return
    code = context.args[0].strip()
    data = sheet.get_all_records()
    result = next((row for row in data if str(row.get("CODE", "")).strip() == code), None)
    if result:
        text = f"🔍 *CODE*: `{code}`\n*PORT_ID*: `{result['PORT_ID']}`\n*TARGET_ID*: `{result['TARGET_ID']}`"
        log_search("PORT", code)
    else:
        text = f"❌ Data tidak ditemukan untuk CODE `{code}`"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# /portid command
async def portid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("❗ Gunakan format: /portid <PORT_ID>")
        return
    port_id = context.args[0].strip()
    data = sheet.get_all_records()
    result = next((row for row in data if str(row.get("PORT_ID", "")).strip() == port_id), None)
    if result:
        text = f"🔌 *PORT_ID*: `{port_id}`\n*PORT_NUMBER*: `{result['PORT_NUMBER']}`\n*NAME_NE*: `{result['NAME_NE']}`\n*VLAN_BROADBAND*: `{result['VLAN_BROADBAND']}`\n*VLAN_VOICE*: `{result['VLAN_VOICE']}`"
        log_search("PORTID", port_id)
    else:
        text = f"❌ Data tidak ditemukan untuk PORT_ID `{port_id}`"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# /ipbb command
async def ipbb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("❗ Gunakan format: /ipbb <IP_BB>")
        return
    code = context.args[0].strip()
    data = sheet.get_all_records()
    result = next((row for row in data if str(row.get("IP_BB", "")).strip() == code), None)
    if result:
        text = f"🌐 *IP_BB*: `{code}`\n*MERK*: `{result['MERK']}`\n*NAME_NE*: `{result['NAME_NE']}`\n*STO*: `{result['STO']}`\n*VLAN_BROADBAND*: `{result['VLAN_BROADBAND']}`\n*VLAN_VOICE*: `{result['VLAN_VOICE']}`"
        log_search("IP_BB", code)
    else:
        text = f"❌ Data tidak ditemukan untuk CODE `{code}`"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# /sto command
async def sto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("❗ Gunakan format: /sto <STO>")
        return
    sto = context.args[0].strip().upper()
    data = sheet.get_all_records()
    matches = [row for row in data if str(row.get("STO", "")).strip().upper() == sto]
    if matches:
        text = f"📍 Perangkat untuk STO `{sto}`:"
        for row in matches[:10]:  # Batasi agar tidak terlalu panjang
            text += f"- `{row['NAME_NE']}` ({row['IP OLT']})"
        log_search("STO", sto)
    else:
        text = f"❌ Tidak ada perangkat ditemukan untuk STO `{sto}`"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# /log command
async def show_log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open("log.csv", "r") as f:
            lines = f.readlines()[-10:]
        log_text = "📋 *Log Pencarian Terakhir:*\\n" + "".join([f"- {line}" for line in lines])
    except FileNotFoundError:
        log_text = "📭 Belum ada log pencarian."
    await update.message.reply_text(log_text, parse_mode=ParseMode.MARKDOWN)

# Main
if __name__ == '__main__':
    print("✅ idslotport_bot is running on Render...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("port", port))
    app.add_handler(CommandHandler("portid", portid))
    app.add_handler(CommandHandler("ipbb", ipbb))
    app.add_handler(CommandHandler("sto", sto))
    app.add_handler(CommandHandler("log", show_log))
    app.run_polling()
