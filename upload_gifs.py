# upload_gifs.py
import asyncio
from bale import Bot, InputFile

TOKEN = "636408536:4T6tFFifbOGZ7Y_J6BZEyBg4-I2t6ie8sYw"
CHAT_ID = 479945362

async def main():
    gifs = {
        "Amirjalali": "gifs/Amirjalali.gif",
    }
    async with Bot(token=TOKEN) as bot:
        for name, path in gifs.items():
            with open(path, "rb") as f:
                file_bytes = f.read()
            
            msg = await bot.send_animation(
                chat_id=CHAT_ID,
                animation=InputFile(file_bytes, file_name=f"{name}.gif")
            )
            print(f'"{name}": "{msg.animation.file_id}",')

asyncio.run(main())