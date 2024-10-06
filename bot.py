from pyrogram import Client, filters
import cv2
import os
from config import API_ID, API_HASH, BOT_TOKEN

# Ganti ini dengan informasi Anda

app = Client("video_thumbnail_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("img"))
def request_video(client, message):
    # Tandai pengguna sebagai menunggu video
    message.reply_text("Silakan kirimkan video yang ingin Anda ambil thumbnail-nya.")

@app.on_message(filters.video)
def handle_video(client, message):
    # Download the video
    video_path = message.download(file_name="temp_video.mp4")

    # Capture a frame from the video
    cap = cv2.VideoCapture(video_path)
    success, frame = cap.read()
    if success:
        # Resize the frame to create a thumbnail (optional)
        thumbnail_size = (320, 180)  # Ukuran thumbnail 16:9
        thumbnail = cv2.resize(frame, thumbnail_size)

        # Save the thumbnail as an image
        thumbnail_path = "thumbnail.jpg"
        cv2.imwrite(thumbnail_path, thumbnail)

        # Send the thumbnail back to the user
        client.send_photo(chat_id=message.chat.id, photo=thumbnail_path, caption="Berikut adalah thumbnail dari video Anda.")
    else:
        client.send_message(chat_id=message.chat.id, text="Gagal mengambil thumbnail dari video.")

    # Release the video capture and clean up
    cap.release()
    os.remove(video_path)
    if os.path.exists(thumbnail_path):
        os.remove(thumbnail_path)

app.run()
