from aiogram import Router, types, F
from aiogram import html
# from aiogram import exceptions
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import db
import bot


rt = Router()
# rt.message.filter((F.text == "/start") | (F.text == "/help") | (F.text == "В главное меню"))
# rt.callback_query.filter(F.data == "main_menu")


user_cache = {}
conn = db.DBConnection()
conn.executeonce("SELECT user_id, user_name, with_adminkey, isadmin, buro.name FROM \
    public.users JOIN public.buro ON buro.id = buro_id ORDER BY buro.id")
users = {i[0]:{'user_name':i[1], 'with_adminkey':i[2], 'isadmin':i[3], 'buro':i[4]} for i in conn.fetchall()}


conn.executeonce("SELECT user_id FROM banned_users")
banned_users = [i[0] for i in conn.fetchall()]

conn.executeonce("SELECT name FROM buro")
buros = [i[0] for i in conn.fetchall()]

#-------
async def clear_db():
    conn.executeonce("DELETE FROM history * WHERE id not in (SELECT id FROM history ORDER BY time DESC LIMIT 10);")

async def notification():
    if get_alarm_status():
        conn.executeonce("SELECT public.users.user_id FROM public.history, public.users \
                WHERE public.history.user_id = public.users.id ORDER BY time DESC LIMIT 1;")
        await bot.send_message_to_user(conn.fetchall()[0][0], "Не забудь поставить на охрану!")

#-------
def get_key_status():   # True = ключ снят
    conn.executeonce("SELECT event_id FROM public.history WHERE (event_id >= 10 AND event_id < 20) OR event_id = 21 ORDER BY time DESC LIMIT 1;")
    res = conn.fetchall()
    if len(res) != 0 and res[0][0]%10 == 0:
        return True
    else:
        return False

def get_alarm_status():
    conn.executeonce("SELECT event_id FROM public.history WHERE event_id >= 20 OR event_id = 10 ORDER BY time DESC LIMIT 1;")
    res = conn.fetchall()
    if len(res) != 0 and res[0][0]%10 == 0:
        return True
    else:
        return False


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)

def get_main_admin_menu_keyboard(_userid):
    return get_main_menu_keyboard(_userid)

def get_main_menu_keyboard(_userid):
    kstatus = get_key_status()
    alstatus = get_alarm_status()
    
    conn.executeonce("SELECT public.users.user_id, public.history.event_id FROM public.users, public.history WHERE public.users.id = public.history.user_id ORDER BY time DESC LIMIT 1")
    res = conn.fetchall()
    
    if len(res) > 0 and res[0][0] != _userid and res[0][1]%10 != 1 and res[0][1] < 20:
        buttons = [
            [types.InlineKeyboardButton(text="А кто у нас есть?", callback_data="view_users")],
            [types.InlineKeyboardButton(text="У кого ключ?", callback_data="view_key_status")],
        ]
    
    else:
        if users[_userid]['with_adminkey'] == False:
            buttons = [
                [types.InlineKeyboardButton(text="Взял ключ" if not kstatus else "Вернул ключ", 
                                            callback_data="get_key" if not kstatus else "return_key"),
                types.InlineKeyboardButton(text="Снял с охраны" if not alstatus else "Поставил на охрану", 
                                            callback_data="remove_alarm" if not alstatus else "add_alarm")],
                
                [types.InlineKeyboardButton(text="Отдал ключ", callback_data="give_key")] if len(res) > 0 and res[0][1]%10 == 0 and res[0][1] < 20 and res[0][0] == _userid else [],
                [types.InlineKeyboardButton(text="А кто у нас есть?", callback_data="view_users")]
            ]
        else:
            buttons = [
                [types.InlineKeyboardButton(text="Снял с охраны" if not alstatus else "Поставил на охрану", 
                                            callback_data="remove_alarm" if not alstatus else "add_alarm")],
                [types.InlineKeyboardButton(text="А кто у нас есть?", callback_data="view_users")]
            ]        
        
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    
    return keyboard

# @rt.message(lambda x: Command("start", "help") or F.text == "В главное меню" or F.data == "main_menu")
@rt.message(F.text == "/start")
async def cmd_start(message: types.Message, state: FSMContext):
    custom_text=""
    if state != None:
        await state.clear()
    if message.chat.id in banned_users:
        # await message.answer("Ты забанен!")
        await message.answer_audio(caption="Ты забанен!", audio='CQACAgIAAxkBAAMHZaxedhhSVhd2YZVaqE446cyQWoQAAlEXAAKrJDlIsN2Kmr1ziAI0BA')
        return
    
    user_cache[message.chat.id] = {}
    # print(message.chat.id)

        
    if message.chat.id not in users.keys():
        await message.answer("Ти хто? Зарегайся:", reply_markup=types.ReplyKeyboardRemove())
        await message.answer("Введи свои фамилию и имя (Иванов Иван):")
        await state.set_state(UserRegister.input_name)
        return
        # conn.executeonce("INSERT INTO users (user_id) VALUES (%s)", [message.chat.id])
        # users[message.chat.id] = {}
        # users[message.chat.id]['isadmin'] = False
    
    tmsg = await message.answer("Удаляю лишнее...", reply_markup=types.ReplyKeyboardRemove())
    await tmsg.delete()
    
    # print(f"!!!!\n\n{users}\n{message.chat.id}\n\n{message.chat.id}\n\n")
    
    if custom_text != "":
        if users[message.chat.id]['isadmin']:
            await message.answer(custom_text, reply_markup=get_main_menu_keyboard(message.chat.id))
        else:
            await message.answer(custom_text, reply_markup=get_main_menu_keyboard(message.chat.id))
    else:
        if users[message.chat.id]['isadmin']:
            await message.answer(f"Я готов выполнить что угодно, вот список услуг:", reply_markup=get_main_menu_keyboard(message.chat.id))
        else:
            await message.answer(f"Я готов выполнить что угодно, вот список услуг:", reply_markup=get_main_menu_keyboard(message.chat.id))

async def cmd_mess_edit(message: types.Message, custom_text, kb = None, parse_mode = "MarkdownV2"):
    if kb == None:
        if users[message.chat.id]['isadmin']:
            await message.edit_text(custom_text, parse_mode=parse_mode, reply_markup=get_main_menu_keyboard(message.chat.id))
        else:
            await message.edit_text(custom_text, parse_mode=parse_mode, reply_markup=get_main_menu_keyboard(message.chat.id))
    
    else:
        await message.edit_text(custom_text, parse_mode=parse_mode, reply_markup=kb)

    
@rt.callback_query(F.data == "to_main_menu")
async def to_cmd_start(callback: types.CallbackQuery):
    await callback.answer()
    await cmd_start(callback.message, None)

@rt.message(Command(commands=["cancel"]))
async def cmd_cancel(message: types.Message, state: FSMContext):
    await cmd_start(message, state)

@rt.callback_query(F.data == "view_users")
async def to_cmd_start(callback: types.CallbackQuery):
    global users
    conn.executeonce("SELECT user_id, user_name, with_adminkey, isadmin, buro.name FROM \
        public.users JOIN public.buro ON buro.id = buro_id ORDER BY buro.id")
    users = {i[0]:{'user_name':i[1], 'with_adminkey':i[2], 'isadmin':i[3], 'buro':i[4]} for i in conn.fetchall()}
    
    await callback.message.answer(''.join([f"• *[{users[i]['user_name']}](tg://user?id={i})* _{users[i]['buro']}_ \n" for i in users.keys()]),
                                  parse_mode="MarkdownV2", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="В главное меню", callback_data="to_main_menu")]]))    
    
    await callback.answer()


#### Регистрация
class UserRegister(StatesGroup):
    input_name = State()
    input_buro = State()

@rt.message(UserRegister.input_name)
async def inputing_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Выбери свое бюро:", reply_markup=make_row_keyboard(buros))
    await state.set_state(UserRegister.input_buro)

@rt.message(UserRegister.input_buro)
async def inputing_buro(message: types.Message, state: FSMContext):
    global user_cache
    await state.update_data(buro=message.text)
    
    user_cache[message.chat.id] = await state.get_data()

    if str(user_cache[message.chat.id]['name']).lower().replace(' ', '') in [str(users[i]['user_name']).lower().replace(' ', '') for i in users.keys()]:
        banned_users.append(message.chat.id)
        conn.executeonce("INSERT INTO public.banned_users(user_id) VALUES (%s);", [message.chat.id])
        await message.answer(f"Такой человек уже существует! Можешь больше не приходить!", reply_markup=types.ReplyKeyboardRemove())

        try:
            conn.executeonce("SELECT user_id FROM public.users WHERE isadmin = true")
            admins = conn.fetchall()
            if len(admins) > 0:
                for i in admins:
                    await bot.send_message_to_user(i[0], f"*Забанен* пользователь\! \([{message.chat.id} {user_cache[message.chat.id]['name']}](tg://user?id={message.chat.id})\)",
                                        pm="MarkdownV2")
        
        except Exception as exc:
            bot.logging.error("Send notification error!", exc_info=True)
        
    else:
        conn.executeonce("SELECT id FROM buro WHERE name=%s", [user_cache[message.chat.id]['buro']])
        user_cache[message.chat.id]['buro_id'] = conn.fetchall()[0][0]
        
        conn.executeonce("INSERT INTO public.users(user_id, user_name, buro_id) \
	                        VALUES (%s, %s, %s);", 
                        [message.chat.id, user_cache[message.chat.id]['name'], user_cache[message.chat.id]['buro_id']])

        users[message.chat.id] = {'user_name':user_cache[message.chat.id]['name'], 
                                  'with_adminkey': False, 'isadmin':False, 'buro':user_cache[message.chat.id]['buro']}
        
    
    
        try:
            conn.executeonce("SELECT user_id FROM public.users WHERE isadmin = true")
            admins = conn.fetchall()
            if len(admins) > 0:
                for i in admins:
                    await bot.send_message_to_user(i[0], f"Зарегистрирован новый пользователь\! \([{message.chat.id} {user_cache[message.chat.id]['name']}](tg://user?id={message.chat.id})\)",
                                        pm="MarkdownV2")
        
        except Exception as exc:
            bot.logging.error("Send notification error!", exc_info=True)
        
    
    await cmd_start(message, state)
    await state.clear()