import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from json import load
import logging
import logging.handlers
from datetime import date, datetime
import main_menu
import key
from apscheduler.schedulers.asyncio import AsyncIOScheduler

bot = Bot(token=open('bot_token', 'r').readline())
scheduler = AsyncIOScheduler(timezone='Europe/Moscow')

async def send_message_to_user(user_id, message, kb = None, pm = None):
    await bot.send_message(chat_id=user_id, text=message, reply_markup=kb, parse_mode=pm)



async def main():
    cmd_logger = logging.getLogger()
    cmd_logger.setLevel(logging.INFO)
    cmd_logger_handler = logging.StreamHandler()
    cmd_logger_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    cmd_logger.addHandler(cmd_logger_handler)
    
    # logging.basicConfig(level=logging.INFO)
    
    file_logger = logging.getLogger()
    file_logger.setLevel(logging.INFO)
    # fl_handler = logging.FileHandler(f"{__name__}.log", mode='w')
    fl_handler = logging.handlers.RotatingFileHandler(filename=f"logs/{date.today().strftime('%d-%m-%Y')}.log",
                                                      maxBytes=50000, backupCount=24, mode='a', encoding='utf-8')
    fl_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    file_logger.addHandler(fl_handler)
    
    scheduler.add_job(main_menu.clear_db, 'cron', day='1', hour='6', id="clean_db_shedule")
    scheduler.add_job(main_menu.notification, 'cron', hour=20, minute=30, id="notif_shedule_1", name="notif_1")
    scheduler.add_job(main_menu.notification, 'cron', hour=22, minute=30, id="notif_shedule_2", name="notif_2")
    scheduler.start()
    print(scheduler.get_jobs())
    
    dp = Dispatcher()

    commands = {}
    try:
        f = open('commands.json', encoding='UTF-8')
        commands = load(f)
    except Exception as exc:
        print(exc)
    finally:
        f.close()     
    
        
    await bot.set_my_commands([BotCommand(command=comm, description=desc) for comm, desc in commands.items()])
    
    dp.include_routers(key.rt, main_menu.rt)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())