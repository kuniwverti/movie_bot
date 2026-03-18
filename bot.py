import asyncio
from aiogram import Bot, Dispatcher 
from config import TOKEN
from handlers.start import router 

async def main(): 
    print("Start...")
    bot = Bot(token=TOKEN)
    me = await bot.get_me()
    print(f"Бот: @{me.username}")
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot, polling_timeout=10)

if __name__ == "__main__":
        asyncio.run(main())


