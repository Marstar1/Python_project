from aiogram import Router, types, F
from aiogram import html
# from aiogram import exceptions
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
# from bot import bot.send_message_to_user
# from bot import cmd_mess_edit, cmd_start
import bot
import main_menu as mm
import db

rt = Router()
rt.callback_query.filter((F.data == "get_key") | (F.data == "return_key") | (F.data == "remove_alarm")
                         | (F.data == "add_alarm") | (F.data == "give_key") | (F.data == "view_key_status"))

conn = db.DBConnection()
user_cache = {}


def check_security(_userid):
    conn.executeonce("SELECT public.users.user_id, public.history.event_id FROM public.users, public.history WHERE public.users.id = public.history.user_id ORDER BY time DESC LIMIT 1")
    res = conn.fetchall()
    
    if len(res) > 0 and res[0][0] != _userid and res[0][1]%10 != 1 and res[0][1] < 20:
        return False
    return True


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for item in items:
         builder.add(types.KeyboardButton(text=item))
    # row = [KeyboardButton(text=item) for item in items]
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def get_to_main_menu_kb():
    return types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="В главное меню", callback_data="to_main_menu")]])


@rt.callback_query(F.data == "get_key")
async def get_key(callback: types.CallbackQuery):
    if not check_security(callback.message.chat.id):
        await callback.message.answer("Не балуйся! Иди лучше в главное меню:", reply_markup=get_to_main_menu_kb())
        return
    
    conn.executeonce("SELECT user_id FROM users")
    users = [i[0] for i in conn.fetchall()]
    
    if callback.message.chat.id not in user_cache.keys():
        conn.executeonce("SELECT id, user_name FROM users WHERE user_id = %s", [callback.message.chat.id])
        res = conn.fetchall()
        user_cache[callback.message.chat.id] = {}
        user_cache[callback.message.chat.id]['id'] = res[0][0]
        user_cache[callback.message.chat.id]['name'] = res[0][1]

    conn.executeonce("INSERT INTO public.history(event_id, user_id) VALUES (10, %s);", [user_cache[callback.message.chat.id]['id']])
    
    for i in users:
        if i != callback.message.chat.id:
            await bot.send_message_to_user(i, f"Ключ взят \([{user_cache[callback.message.chat.id]['name']}](tg://user?id={callback.message.chat.id})\)", 
                                           kb=get_to_main_menu_kb(), pm="MarkdownV2")
    
    await mm.cmd_mess_edit(callback.message, "Я готов выполнить что угодно, вот список услуг:")



@rt.callback_query(F.data == "return_key")
async def return_key(callback: types.CallbackQuery):
    if not check_security(callback.message.chat.id):
        await callback.message.answer("Не балуйся! Иди лучше в главное меню:", reply_markup=get_to_main_menu_kb())
        return
    
    conn.executeonce("SELECT user_id FROM users")
    users = [i[0] for i in conn.fetchall()]
    
    if callback.message.chat.id not in user_cache.keys():
        conn.executeonce("SELECT id, user_name FROM users WHERE user_id = %s", [callback.message.chat.id])
        res = conn.fetchall()
        user_cache[callback.message.chat.id] = {}
        user_cache[callback.message.chat.id]['id'] = res[0][0]
        user_cache[callback.message.chat.id]['name'] = res[0][1]

    conn.executeonce("INSERT INTO public.history(event_id, user_id) VALUES (11, %s);", [user_cache[callback.message.chat.id]['id']])
    
    for i in users:
        if i != callback.message.chat.id:
            await bot.send_message_to_user(i, f"Ключ на охране \([{user_cache[callback.message.chat.id]['name']}](tg://user?id={callback.message.chat.id})\)", 
                                           kb=get_to_main_menu_kb(), pm="MarkdownV2")

    await mm.cmd_mess_edit(callback.message, "Я готов выполнить что угодно, вот список услуг:")



@rt.callback_query(F.data == "remove_alarm")
async def remove_alarm(callback: types.CallbackQuery):
    if not check_security(callback.message.chat.id):
        await callback.message.answer("Не балуйся! Иди лучше в главное меню:", reply_markup=get_to_main_menu_kb())
        return

    
    conn.executeonce("SELECT user_id FROM users")
    users = [i[0] for i in conn.fetchall()]
    
    if callback.message.chat.id not in user_cache.keys():
        conn.executeonce("SELECT id, user_name FROM users WHERE user_id = %s", [callback.message.chat.id])
        res = conn.fetchall()
        user_cache[callback.message.chat.id] = {}
        user_cache[callback.message.chat.id]['id'] = res[0][0]
        user_cache[callback.message.chat.id]['name'] = res[0][1]

    conn.executeonce("INSERT INTO public.history(event_id, user_id) VALUES (20, %s);", [user_cache[callback.message.chat.id]['id']])
    
    for i in users:
        if i != callback.message.chat.id:
            await bot.send_message_to_user(i, f"Сигнализация ВЫКЛ \([{user_cache[callback.message.chat.id]['name']}](tg://user?id={callback.message.chat.id})\)", 
                                           kb=get_to_main_menu_kb(), pm="MarkdownV2")
    
    await mm.cmd_mess_edit(callback.message, "Я готов выполнить что угодно, вот список услуг:")


@rt.callback_query(F.data == "add_alarm")
async def add_alarm(callback: types.CallbackQuery):
    if not check_security(callback.message.chat.id):
        await callback.message.answer("Не балуйся! Иди лучше в главное меню:", reply_markup=get_to_main_menu_kb())
        return

    
    conn.executeonce("SELECT user_id FROM users")
    users = [i[0] for i in conn.fetchall()]
    
    if callback.message.chat.id not in user_cache.keys():
        conn.executeonce("SELECT id, user_name FROM users WHERE user_id = %s", [callback.message.chat.id])
        res = conn.fetchall()
        user_cache[callback.message.chat.id] = {}
        user_cache[callback.message.chat.id]['id'] = res[0][0]
        user_cache[callback.message.chat.id]['name'] = res[0][1]

    conn.executeonce("INSERT INTO public.history(event_id, user_id) VALUES (21, %s);", [user_cache[callback.message.chat.id]['id']])
    
    for i in users:
        if i != callback.message.chat.id:
            await bot.send_message_to_user(i, f"Сигнализация ВКЛ \([{user_cache[callback.message.chat.id]['name']}](tg://user?id={callback.message.chat.id})\)", 
                                           kb=get_to_main_menu_kb(), pm="MarkdownV2")

    await mm.cmd_mess_edit(callback.message, "Я готов выполнить что угодно, вот список услуг:")
    
    
@rt.callback_query(F.data == "give_key")
async def give_key(callback: types.CallbackQuery):
    if not check_security(callback.message.chat.id):
        await callback.message.answer("Не балуйся! Иди лучше в главное меню:", reply_markup=get_to_main_menu_kb())
        return

    
    conn.executeonce("SELECT user_id, user_name FROM users")
    users = {i[0] : i[1] for i in conn.fetchall()}
    users.pop(callback.message.chat.id)
    print(users.values())
    
    await bot.send_message_to_user(callback.message.chat.id, "Кому отдаешь ключ?", kb=make_row_keyboard(users.values()))
    
    @rt.message(F.text.in_(users.values()))
    async def get_name(message: types.Message):
        userid = list(users)[list(users.values()).index(message.text)]
        
        conn.executeonce("SELECT id FROM users WHERE user_id = %s", [callback.message.chat.id])
        conn.executeonce("INSERT INTO public.history(event_id, user_id) VALUES (1, %s);", [conn.fetchall()[0][0]])
        
        conn.executeonce("SELECT id FROM users WHERE user_id = %s", [userid])
        conn.executeonce("INSERT INTO public.history(event_id, user_id) VALUES (0, %s);", [conn.fetchall()[0][0]])
        
        try:
            await callback.answer()
        except:
            pass
        
        await mm.cmd_start(message, None)
        for i in users:
            if i == userid:
                await bot.send_message_to_user(i, f"Забирайте ключ, господин:", 
                                           kb=get_to_main_menu_kb(), pm="MarkdownV2")
            else:
                await bot.send_message_to_user(i, f"Ключ передан \([{message.text}](tg://user?id={userid})\)", 
                                           kb=get_to_main_menu_kb(), pm="MarkdownV2")
        
        
@rt.callback_query(F.data == "view_key_status")
async def view_key_status(callback: types.CallbackQuery):
    conn.executeonce("SELECT public.history.event_id, public.users.user_name, public.users.user_id FROM public.history, public.users \
		WHERE public.history.user_id = public.users.id ORDER BY time DESC LIMIT 1;")
    res = conn.fetchall()[0]
    event_id, user_name, userid = res[0], res[1], res[2]
    
    if event_id%10 == 0:
        await callback.message.answer(f"Ключ у пользователя \"[{user_name}](tg://user?id={userid})\"", 
                    reply_markup=get_to_main_menu_kb(), parse_mode="MarkdownV2")
    else:
        await callback.message.answer(f"Ключ на охране")
    
    await callback.answer()
            