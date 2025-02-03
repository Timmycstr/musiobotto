import telebot
import yt_dlp
import os
import re
import sys

# Замените на ваш токен от BotFather
BOT_TOKEN = '--------------------------'
bot = telebot.TeleBot(BOT_TOKEN)

YOUTUBE_URL_REGEX = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"

def download_audio(url, message):
    ydl_opts = {
        'format': 'bestaudio[ext=mp3]/bestaudio',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': []
    }
    
    status_msg = bot.reply_to(message, "Загружаю аудио...")
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            audio_file = ydl.prepare_filename(info)
            
            # Проверяем, если файл не имеет расширение .mp3, переименовываем
            if not audio_file.endswith('.mp3'):
                base, ext = os.path.splitext(audio_file)
                new_file = base + '.mp3'
                
                # Проверяем, существует ли уже файл с таким именем
                if not os.path.exists(new_file):
                    os.rename(audio_file, new_file)
                audio_file = new_file
            
            return audio_file, status_msg
    except Exception as e:
        bot.edit_message_text("Ошибка загрузки аудио", message.chat.id, status_msg.message_id)
        raise RuntimeError(f"Ошибка загрузки аудио: {e}")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне ссылку на видео с YouTube, и я скачаю аудио дорожку!")

@bot.message_handler(commands=['reb'])
def restart_bot(message):
    bot.reply_to(message, "Перезапускаю бота...")
    os.execv(sys.executable, ['python'] + sys.argv)

@bot.message_handler(func=lambda message: re.match(YOUTUBE_URL_REGEX, message.text))
def handle_message(message):
    url = message.text
    try:
        audio_file, status_msg = download_audio(url, message)

        if os.path.getsize(audio_file) > 50 * 1024 * 1024:
            bot.delete_message(message.chat.id, status_msg.message_id)
            bot.reply_to(message, "Файл слишком большой для отправки через Telegram.")
            os.remove(audio_file)
            return

        sending_msg = bot.reply_to(message, "Отправляю аудио...")
        
        with open(audio_file, 'rb') as audio:
            bot.send_audio(message.chat.id, audio, caption="")

        bot.delete_message(message.chat.id, status_msg.message_id)
        bot.delete_message(message.chat.id, sending_msg.message_id)
        os.remove(audio_file)
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")

@bot.message_handler(func=lambda message: True)
def handle_invalid_message(message):
    bot.reply_to(message, "Пожалуйста, отправьте действительную ссылку на видео YouTube.")

if __name__ == '__main__':
    os.makedirs('downloads', exist_ok=True)
    print("Бот запущен и готов к работе.")
    bot.infinity_polling()

