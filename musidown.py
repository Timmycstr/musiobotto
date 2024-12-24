from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, FSInputFile
from pytube import YouTube
import asyncio
import os
import logging

logging.basicConfig(filename='bot.log', level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
BOT_TOKEN = '7817558551:AAGe1UthE8wwIBhOFC41SekSHutW4Cg1Zf8'

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
router = Router()
dp = Dispatcher()
dp.include_router(router)

# Папка для сохранения загруженных аудио
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@router.message(commands=['start', 'help'])
async def send_welcome(message: Message):
    await message.answer("Привет! Отправь мне ссылку на видео с YouTube, и я извлеку для тебя аудио.")

@router.message()
async def download_audio(message: Message):
    url = message.text
    if not url.startswith("http"):
        await message.answer("Пожалуйста, отправь корректную ссылку на видео с YouTube.")
        return

    try:
        await message.answer("Загружаю аудио, подожди немного...")
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        file_path = audio_stream.download(output_path=DOWNLOAD_FOLDER)

        # Отправляем файл пользователю
        audio_file = FSInputFile(file_path)
        await message.answer_audio(audio_file, caption=f"Вот твое аудио: {yt.title}")

        # Удаляем файл после отправки
        os.remove(file_path)
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")

async def main():
    dp.startup.register(on_startup)
    await dp.start_polling(bot)

async def on_startup():
    print("Бот запущен")

if __name__ == '__main__':
    asyncio.run(main())
