import asyncio, logging
from contextlib import asynccontextmanager, suppress

from aiogram import Router, Bot, Dispatcher
from aiogram.types import Message, Update
from aiogram.filters import CommandStart
from aiogram.utils.markdown import hlink

from middlewares.throttling import ThrottlingMiddleware
from handlers import user_group_commands

from config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH
from fastapi import FastAPI, Request # pip install fastapi[all]
# from app import keep_alive

@asynccontextmanager
async def on_startup(app: FastAPI) -> None:
    await bot.delete_webhook(True)
    await bot.set_webhook(WEBHOOK_URL) # Устанавливаем URL для наших вебхуков
    yield


bot = Bot(BOT_TOKEN, parse_mode='HTML')
dp = Dispatcher()
app = FastAPI(lifespan=on_startup) # lifespan, как on_startup

logging.basicConfig(level=logging.INFO)

router = Router()


@router.message(CommandStart())
async def start_cmd(message: Message) -> None:
  await message.answer(
      f'Привет, {hlink(message.from_user.first_name, f"tg://user?id={message.from_user.id}")}\n\nДобавь меня в группу, чтобы начать работу!'
  )


@app.post(WEBHOOK_PATH)
async def bot_webhook_updates(request: Request) -> None:
    # Осуществляем валидацию входящего обновления и получаем ответ

    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)


async def main() -> None:
  dp.message.middleware(ThrottlingMiddleware())

  dp.include_routers(router, user_group_commands.router)

  await bot.delete_webhook(False)
  await dp.start_polling(bot)


# keep_alive()

if __name__ == "__main__":
  asyncio.run(main())
