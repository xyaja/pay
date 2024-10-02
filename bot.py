# bot.py

from pyrogram import Client, filters
import requests
from pymongo import MongoClient
from config import API_ID, API_HASH, BOT_TOKEN, TRIPAY_API_KEY, TRIPAY_API_URL, MONGODB_URI, DATABASE_NAME, LOG_CHANNEL_ID, GROUP_INVITE_LINK

import threading
import time

# Inisialisasi bot
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Koneksi MongoDB
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client[DATABASE_NAME]
payments_collection = db['payments']

@app.on_message(filters.command("start"))
def start(client, message):
    """Handle /start command."""
    message.reply("Selamat datang! Gunakan /pay untuk melakukan pembayaran.")

@app.on_message(filters.command("pay"))
def pay(client, message):
    """Handle /pay command to initiate payment."""
    user_id = message.from_user.id
    amount = 10000  # Misalnya 10.000 IDR
    payment_id = f"{user_id}_payment"  # Unique payment ID

    # Kirim permintaan ke Tripay
    headers = {
        'Authorization': f'Bearer {TRIPAY_API_KEY}'
    }
    payload = {
        "method": "qris",  # Menggunakan QRIS
        "amount": amount,
        "merchant_ref": payment_id,
        "customer_name": message.from_user.first_name,  # Hanya menggunakan nama depan pengguna
        "expired_time": "2023-12-31 23:59:59",  # Set waktu kedaluwarsa, contoh
        "note": "Pembayaran untuk akses grup selama 1 jam"  # Catatan pembayaran
    }

    # Melakukan permintaan pembayaran ke API Tripay
    response = requests.post(TRIPAY_API_URL, headers=headers, json=payload)
    data = response.json()

    if data.get('success'):
        # Kirim QRIS dan pesan
        qris_url = data['data']['checkout_url']
        message.reply(
            f"Silahkan melakukan pembayaran Rp.10.000 untuk join grup.\n"
            f"KODE PESANAN ANDA: {payment_id}\n"
            f"Link QRIS: {qris_url}"
        )
        
        # Simpan detail pembayaran ke MongoDB
        payment_data = {
            "user_id": user_id,
            "amount": amount,
            "status": "pending"  # Status awal pembayaran
        }
        payments_collection.insert_one(payment_data)

        # Kirim log pembayaran ke saluran
        log_payment(user_id, amount)

        # Kirim tautan grup
        message.reply(f"Terima kasih atas pembayaran Anda! Berikut adalah tautan untuk bergabung ke grup selama 1 jam: {GROUP_INVITE_LINK}")

        # Menghapus tautan grup setelah 1 jam
        threading.Thread(target=remove_invite_link, args=(user_id,)).start()
    else:
        message.reply("Terjadi kesalahan dalam pemrosesan pembayaran.")

def log_payment(user_id, amount):
    """Log payment to the designated channel."""
    message = f"Pembayaran diterima dari pengguna ID: {user_id}\nJumlah: {amount} IDR"
    app.send_message(LOG_CHANNEL_ID, message)

def remove_invite_link(user_id):
    """Menghapus akses grup setelah 1 jam."""
    time.sleep(3600)  # Tunggu selama 1 jam (3600 detik)
    
    # Logika untuk menghapus akses pengguna ke grup
    # Ini bisa dilakukan dengan menendang pengguna dari grup
    # Namun, Anda harus menjadi admin grup untuk melakukan ini
    # Contoh: app.kick_chat_member(chat_id=your_group_chat_id, user_id=user_id)

app.run()
