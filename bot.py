import asyncio
import os
import re
import logging
import sys
import subprocess

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.token import TokenValidationError
from dotenv import load_dotenv

load_dotenv()

api_token = os.environ['TOKEN']
bot_username = '@'
channel_username = "@zimmermans_channel"
channel_link = f"https://t.me/{channel_username.lstrip('@')}"

user_downloading = {}  # Для отслеживания скачиваний пользователями

dp = Dispatcher()

async def is_valid_url(url: str) -> bool:
    youtube_regex = r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\&v=)?([^&=%\?]{11})"
    return re.match(youtube_regex, url) is not None

async def is_subscribed(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=channel_username, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Ошибка проверки подписки: {e}")
        return False

async def download_and_send_video(url: str, chat_id: int, user_id: int, bot: Bot):
    try:
        filename = f"{user_id}.mp4"
        process = await asyncio.create_subprocess_exec(
            "./yt-dlp",
            "-f", "bv*[vcodec^=avc1]+ba[acodec^=mp4a]/best[ext=mp4]/best",
            "--merge-output-format", "mp4",
            "-o", filename,
            url,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise Exception(stderr.decode())

        try:
            video = FSInputFile(filename)
            await bot.send_video(
                chat_id,
                video,
                caption=f"Загружено через {bot_username}"
            )
        except Exception as e:
            await bot.send_message(
                chat_id,
                "Не удалось скачать видео ИЛИ его размер превышает 50МБ."
            )
        finally:
            if os.path.exists(filename):
                os.remove(filename)
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await bot.send_message(
            chat_id,
            "Произошла ошибка при скачивании. Попробуйте позже или отправьте другое видео."
        )

@dp.message(CommandStart())
async def cmd_start(message: Message, bot: Bot) -> None:
    await message.answer("Отправьте ссылку на видео YouTube (Shorts).")

@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "Этот бот предназначен для скачивания коротких видео из YouTube (Shorts).\n\n"
        "⚠️ Бот может скачать видео <b>размером до 50МБ</b> (такое ограничение установлено в API Telegram).\n\n"
        "📌 Если вам нужно скачать короткий кусок большого видео из YouTube — используйте функцию \"Создать клип\" "
        "на YouTube, затем отправьте ссылку на клип боту.\n\n"
        "🔒 Часть Reels видео могут не скачиваться из-за настроек приватности у владельца видео.\n\n"
        "👤 Создатель бота: @lokinehn"
    )
    await message.answer(help_text)

@dp.message(F.text)
async def process_url(message: Message, bot: Bot):
    user_id = message.from_user.id
    url = message.text
    chat_id = message.chat.id

    if await is_subscribed(bot, user_id):
        if not await is_valid_url(url):
            await message.answer("Некорректная ссылка.")
            return

        if chat_id in user_downloading:
            await message.answer("Пожалуйста, дождитесь завершения предыдущего скачивания.")
            return

        user_downloading[chat_id] = True
        await message.answer("Скачивание началось...")

        await download_and_send_video(url, chat_id, user_id, bot)

        del user_downloading[chat_id]
    else:
        await message.answer(f"Чтобы пользоваться ботом, подпишись на канал: {channel_link}")

async def main() -> None:
    bot = Bot(token=api_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except TokenValidationError:
        print("Неверный токен бота.")
