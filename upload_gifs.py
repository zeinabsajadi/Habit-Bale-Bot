# upload_gifs.py
import asyncio
from bale import Bot

TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"  # آیدی یه چت که ربات توش ادمینه

bot = Bot(token=TOKEN)

async def main():
    gifs = {
        "welcome": "gifs/welcome.gif",
        "success": "gifs/success.gif",
        "error":   "gifs/error.gif",
    }

    for name, path in gifs.items():
        with open(path, "rb") as f:
            msg = await bot.send_animation(chat_id=CHAT_ID, animation=f)
        print(f'"{name}": "{msg.animation.file_id}",')

asyncio.run(main())
