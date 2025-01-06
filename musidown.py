import telebot
import yt_dlp
import os
import re

# Замените на ваш токен от BotFather
BOT_TOKEN = '-----------'
bot = telebot.TeleBot(BOT_TOKEN)

YOUTUBE_URL_REGEX = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"

def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio[ext=mp3]/bestaudio',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': []
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            audio_file = ydl.prepare_filename(info)

            # Проверяем, если файл не имеет расширение mp3, переименовываем
            if not audio_file.endswith('.mp3'):
                base, ext = os.path.splitext(audio_file)
                new_file = base + '.mp3'
                os.rename(audio_file, new_file)
                return new_file

            return audio_file
    except Exception as e:
        raise RuntimeError(f"Ошибка загрузки аудио: {e}")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне ссылку на видео с YouTube, и я скачаю аудио дорожку!")

@bot.message_handler(commands=['d'])
def activate_group_mode(message):
    bot.reply_to(message, "Групповой режим активирован! Отправьте ссылку на YouTube для скачивания аудио.")

@bot.message_handler(func=lambda message: re.match(YOUTUBE_URL_REGEX, message.text))
def handle_message(message):
    url = message.text
    bot.reply_to(message, "Скачиваю аудио, подождите...")
    try:
        audio_file = download_audio(url)

        # Проверяем размер файла
        if os.path.getsize(audio_file) > 50 * 1024 * 1024:  # Ограничение Telegram
            bot.reply_to(message, "Файл слишком большой для отправки через Telegram.")
            os.remove(audio_file)
            return

        with open(audio_file, 'rb') as audio:
            bot.send_audio(
                message.chat.id,
                audio,
                caption="Ваше аудио готово!"
            )

        # Удаляем временный файл
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
