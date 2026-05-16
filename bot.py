import asyncio
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# ========== КОНФИГУРАЦИЯ ==========
BOT_TOKEN = "8966032196:AAHvnet7q7rqXPrznRwh0p9xRIM480CIImQ"  # СЮДА ТОКЕН БОТА ОТ @BotFather
ADMIN_ID = 8478884644  # ID админа, куда приходят анкеты
CHANNEL_LINK = "https://t.me/UNITcoin_chat"  # Ссылка на чат для подписки
CHANNEL_USERNAME = "@UNITcoin_chat"  # Юзернейм для проверки подписки
RULES_URL = "https://telegra.ph/PRAVILA-CHATA-05-14-80"  # Ссылка на правила
MIN_DAYS_IN_CHAT = 5  # Минимальное время в чате (дней)
MIN_AGE = 14  # Минимальный возраст

# ========== КНОПКИ ==========
def get_rules_button():
    """Кнопка для чтения правил"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📜 ПРОЧИТАТЬ ПРАВИЛА", url=RULES_URL)]
    ])

def get_main_menu():
    """Главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Заполнить анкету", callback_data="start_anketa")],
        [InlineKeyboardButton(text="❓ Проверить подписку", callback_data="check_subscribe")]
    ])

# ========== СОСТОЯНИЯ ДЛЯ АНКЕТЫ ==========
class AnketaStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_location = State()
    waiting_for_time = State()
    waiting_for_experience = State()
    waiting_for_chat_time = State()
    waiting_for_motivation = State()
    waiting_for_rules = State()
    waiting_for_rude_reaction = State()
    waiting_for_friend_violation = State()
    waiting_for_conflicts = State()
    waiting_for_varns = State()
    waiting_for_username = State()
    waiting_for_hash = State()
    waiting_for_confirm = State()

# ========== БАЗА ДАННЫХ ==========
def init_db():
    conn = sqlite3.connect("anketa_bot.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_answers (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            age TEXT,
            location TEXT,
            time_moderate TEXT,
            experience TEXT,
            chat_time TEXT,
            motivation TEXT,
            rules TEXT,
            rude_reaction TEXT,
            friend_violation TEXT,
            conflicts TEXT,
            varns TEXT,
            username TEXT,
            hash_tag TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_answers(user_id, data):
    conn = sqlite3.connect("anketa_bot.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO user_answers 
        (user_id, name, age, location, time_moderate, experience, chat_time, motivation, 
         rules, rude_reaction, friend_violation, conflicts, varns, username, hash_tag, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, 
          data.get('name'), data.get('age'), data.get('location'), data.get('time_moderate'),
          data.get('experience'), data.get('chat_time'), data.get('motivation'),
          data.get('rules'), data.get('rude_reaction'), data.get('friend_violation'),
          data.get('conflicts'), data.get('varns'), data.get('username'), data.get('hash_tag'),
          datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_answers(user_id):
    conn = sqlite3.connect("anketa_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_answers WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        columns = ['user_id', 'name', 'age', 'location', 'time_moderate', 'experience', 'chat_time', 
                   'motivation', 'rules', 'rude_reaction', 'friend_violation', 'conflicts', 
                   'varns', 'username', 'hash_tag', 'created_at']
        return dict(zip(columns, row))
    return None

# ========== ПРОВЕРКИ ==========
async def check_subscription(user_id: int, bot: Bot) -> bool:
    """Проверяет, подписан ли пользователь на канал"""
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

async def check_chat_time(user_id: int, bot: Bot) -> tuple:
    """Проверяет, сколько дней пользователь в чате"""
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.joined_date:
            days = (datetime.now() - member.joined_date).days
            return True, days
        return True, 999
    except Exception:
        return False, 0

# ========== ОТПРАВКА АДМИНУ ==========
async def send_anketa_to_admin(bot: Bot, user_id: int, user_data: dict, username: str):
    """Отправляет готовую анкету админу"""
    text = f"""
<b>📬 НОВАЯ АНКЕТА В АДМИНИСТРАЦИЮ UNIT CHAT</b>
━━━━━━━━━━━━━━━━━━━━━
👤 <b>От:</b> @{username} (ID: {user_id})
✅ <b>Подписка на чат:</b> подтверждена

<b>📋 Ответы на вопросы:</b>

1️⃣ <b>Имя/Ник:</b> {user_data.get('name', '—')}

2️⃣ <b>Возраст:</b> {user_data.get('age', '—')}

3️⃣ <b>Часовой пояс/Город:</b> {user_data.get('location', '—')}

4️⃣ <b>Время на модерацию:</b> {user_data.get('time_moderate', '—')}

5️⃣ <b>Опыт модерации:</b> {user_data.get('experience', '—')}

6️⃣ <b>Время в чате:</b> {user_data.get('chat_time', '—')}

7️⃣ <b>Мотивация:</b> {user_data.get('motivation', '—')}

8️⃣ <b>Ознакомлен с правилами:</b> {user_data.get('rules', '—')}

9️⃣ <b>Реакция на грубость:</b> {user_data.get('rude_reaction', '—')}

🔟 <b>Друг нарушил:</b> {user_data.get('friend_violation', '—')}

1️⃣1️⃣ <b>Конфликты:</b> {user_data.get('conflicts', '—')}

1️⃣2️⃣ <b>Нарушения и варны:</b> {user_data.get('varns', '—')}

1️⃣3️⃣ <b>Username/ID:</b> {user_data.get('username', '—')}

1️⃣4️⃣ <b>Хэштег:</b> {user_data.get('hash_tag', '—')}
━━━━━━━━━━━━━━━━━━━━━
🕐 <b>Дата заполнения:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}
"""
    await bot.send_message(ADMIN_ID, text, parse_mode="HTML")

# ========== ОБРАБОТЧИКИ ==========
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
init_db()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        f"🌟 <b>Добро пожаловать в бот анкетирования UNIT CHAT!</b> 🌟\n\n"
        f"📋 Здесь ты можешь заполнить анкету для вступления в администрацию чата.\n\n"
        f"⚠️ <b>Важные условия:</b>\n"
        f"• Минимальный возраст: {MIN_AGE}+ лет\n"
        f"• Время в чате: от {MIN_DAYS_IN_CHAT} дней\n"
        f"• Обязательная подписка на чат: {CHANNEL_LINK}\n\n"
        f"👇 <b>Нажми на кнопку ниже, чтобы начать</b>",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "start_anketa")
async def start_anketa(callback: CallbackQuery, state: FSMContext):
    """Начало заполнения анкеты"""
    user_id = callback.from_user.id
    
    if not await check_subscription(user_id, bot):
        await callback.message.edit_text(
            f"❌ <b>Ты не подписан на чат!</b>\n\n"
            f"Пожалуйста, подпишись: {CHANNEL_LINK}\n\n"
            f"После подписки нажми кнопку «Проверить подписку».",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    subscribed, days = await check_chat_time(user_id, bot)
    if days < MIN_DAYS_IN_CHAT:
        await callback.message.edit_text(
            f"❌ <b>Ты в чате меньше {MIN_DAYS_IN_CHAT} дней!</b>\n\n"
            f"Ты в чате: {days} дн.\n"
            f"Минимальный срок: {MIN_DAYS_IN_CHAT} дней.\n\n"
            f"Заполнить анкету можно будет позже.",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    await state.clear()
    await state.set_state(AnketaStates.waiting_for_name)
    await callback.message.edit_text(
        f"📝 <b>Анкета в администрацию UNIT CHAT</b>\n\n"
        f"Отвечай честно и по делу.\n\n"
        f"<b>Вопрос 1 из 14:</b>\n"
        f"Как тебя звать или как к тебе обращаться? (Имя/ник)",
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data == "check_subscribe")
async def check_sub(callback: CallbackQuery):
    """Проверка подписки по кнопке"""
    user_id = callback.from_user.id
    if await check_subscription(user_id, bot):
        await callback.message.edit_text(
            f"✅ <b>Подписка подтверждена!</b>\n\n"
            f"Теперь ты можешь заполнить анкету.",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            f"❌ <b>Ты всё ещё не подписан!</b>\n\n"
            f"Подпишись: {CHANNEL_LINK}\n\n"
            f"После подписки нажми кнопку снова.",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
    await callback.answer()

@dp.message(AnketaStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    if len(message.text.strip()) < 2:
        await message.answer("❌ Имя слишком короткое. Напиши хотя бы 2 символа.")
        return
    await state.update_data(name=message.text.strip())
    await state.set_state(AnketaStates.waiting_for_age)
    await message.answer(
        f"<b>Вопрос 2 из 14:</b>\n"
        f"Сколько тебе лет?\n"
        f"⚠️ От {MIN_AGE}+ лет. Укажи реальный возраст.",
        parse_mode="HTML"
    )

@dp.message(AnketaStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text.strip())
        if age < MIN_AGE:
            await message.answer(f"❌ Тебе меньше {MIN_AGE} лет. Анкета отклонена.\n\nНажми /start чтобы начать заново.")
            await state.clear()
            return
        if age > 100:
            await message.answer("❌ Укажи реальный возраст.")
            return
        await state.update_data(age=age)
        await state.set_state(AnketaStates.waiting_for_location)
        await message.answer(
            f"<b>Вопрос 3 из 14:</b>\n"
            f"Твой часовой пояс и город? (Для понимания времени активности)",
            parse_mode="HTML"
        )
    except ValueError:
        await message.answer("❌ Напиши возраст числом. Например: 16")

@dp.message(AnketaStates.waiting_for_location)
async def process_location(message: Message, state: FSMContext):
    if len(message.text.strip()) < 2:
        await message.answer("❌ Укажи хотя бы город или часовой пояс.")
        return
    await state.update_data(location=message.text.strip())
    await state.set_state(AnketaStates.waiting_for_time)
    await message.answer(
        f"<b>Вопрос 4 из 14:</b>\n"
        f"Сколько времени в день готов уделять модерации?\n"
        f"Например: 1-2 часа, 3-4 часа, больше. Будь честен.",
        parse_mode="HTML"
    )

@dp.message(AnketaStates.waiting_for_time)
async def process_time(message: Message, state: FSMContext):
    await state.update_data(time_moderate=message.text.strip())
    await state.set_state(AnketaStates.waiting_for_experience)
    await message.answer(
        f"<b>Вопрос 5 из 14:</b>\n"
        f"Есть ли опыт модерации/администрирования?\n"
        f"Если да — кратко где и что делал. Если нет — напиши «нет».",
        parse_mode="HTML"
    )

@dp.message(AnketaStates.waiting_for_experience)
async def process_experience(message: Message, state: FSMContext):
    await state.update_data(experience=message.text.strip())
    await state.set_state(AnketaStates.waiting_for_chat_time)
    await message.answer(
        f"<b>Вопрос 6 из 14:</b>\n"
        f"Сколько времени ты уже в чате UNIT CHAT? (Напиши примерно: дни/недели/месяцы)",
        parse_mode="HTML"
    )

@dp.message(AnketaStates.waiting_for_chat_time)
async def process_chat_time(message: Message, state: FSMContext):
    await state.update_data(chat_time=message.text.strip())
    await state.set_state(AnketaStates.waiting_for_motivation)
    await message.answer(
        f"<b>Вопрос 7 из 14:</b>\n"
        f"Почему хочешь стать админом?\n"
        f"Кратко: помочь, навести порядок, есть идеи?",
        parse_mode="HTML"
    )

@dp.message(AnketaStates.waiting_for_motivation)
async def process_motivation(message: Message, state: FSMContext):
    if len(message.text.strip()) < 5:
        await message.answer("❌ Ответ слишком короткий. Напиши чуть подробнее (минимум 5 символов).")
        return
    await state.update_data(motivation=message.text.strip())
    await state.set_state(AnketaStates.waiting_for_rules)
    await message.answer(
        f"<b>Вопрос 8 из 14:</b>\n"
        f"📜 Ознакомлен ли ты с правилами UNIT CHAT?\n\n"
        f"👇 <b>Нажми на кнопку, чтобы прочитать правила</b>\n"
        f"Затем напиши «да» или «нет».\n"
        f"Если «да» — добавь в этом же сообщении, какой пункт считаешь самым важным и почему.\n\n"
        f"📝 <b>Пример ответа:</b> «Да, пункт 2 про оскорбления — самое важное, чтобы в чате было уютно»",
        reply_markup=get_rules_button(),
        parse_mode="HTML"
    )

@dp.message(AnketaStates.waiting_for_rules)
async def process_rules(message: Message, state: FSMContext):
    answer = message.text.strip().lower()
    if answer not in ["да", "нет", "lf", "ytn"] and not answer.startswith("да") and not answer.startswith("нет"):
        await message.answer("❌ Пожалуйста, ответь «да» или «нет», а затем добавь пояснение.\n\nНажми на кнопку с правилами, если ещё не читал.")
        return
    await state.update_data(rules=message.text.strip())
    await state.set_state(AnketaStates.waiting_for_rude_reaction)
    await message.answer(
        f"<b>Вопрос 9 из 14:</b>\n"
        f"Представь: пользователь грубит, но правила не нарушает. Что сделаешь?\n"
        f"(вмешаешься / предупредишь / проигнорируешь / другое)",
        parse_mode="HTML"
    )

@dp.message(AnketaStates.waiting_for_rude_reaction)
async def process_rude(message: Message, state: FSMContext):
    await state.update_data(rude_reaction=message.text.strip())
    await state.set_state(AnketaStates.waiting_for_friend_violation)
    await message.answer(
        f"<b>Вопрос 10 из 14:</b>\n"
        f"Что ты сделаешь, если твой друг нарушил правило?\n"
        f"(Проверка на объективность)",
        parse_mode="HTML"
    )

@dp.message(AnketaStates.waiting_for_friend_violation)
async def process_friend(message: Message, state: FSMContext):
    await state.update_data(friend_violation=message.text.strip())
    await state.set_state(AnketaStates.waiting_for_conflicts)
    await message.answer(
        f"<b>Вопрос 11 из 14:</b>\n"
        f"Были ли у тебя конфликты с участниками или админами этого чата?\n"
        f"Если да — кратко с кем и за что. Если нет — напиши «нет».\n\n"
        f"⚠️ Мы не осуждаем, просто должны знать.",
        parse_mode="HTML"
    )

@dp.message(AnketaStates.waiting_for_conflicts)
async def process_conflicts(message: Message, state: FSMContext):
    await state.update_data(conflicts=message.text.strip())
    await state.set_state(AnketaStates.waiting_for_varns)
    await message.answer(
        f"<b>Вопрос 12 из 14:</b>\n"
        f"Были ли у тебя нарушения и варны в чате UNIT CHAT?\n"
        f"Если да — напиши за что. Если нет — напиши «нет».\n\n"
        f"⚠️ Это не отказ, но важно знать.",
        parse_mode="HTML"
    )

@dp.message(AnketaStates.waiting_for_varns)
async def process_varns(message: Message, state: FSMContext):
    await state.update_data(varns=message.text.strip())
    await state.set_state(AnketaStates.waiting_for_username)
    await message.answer(
        f"<b>Вопрос 13 из 14:</b>\n"
        f"Укажи свой @username (или ID, если нет юзернейма)",
        parse_mode="HTML"
    )

@dp.message(AnketaStates.waiting_for_username)
async def process_username(message: Message, state: FSMContext):
    username = message.text.strip()
    if not username.startswith("@") and not username.isdigit():
        username = "@" + username
    await state.update_data(username=username)
    await state.set_state(AnketaStates.waiting_for_hash)
    await message.answer(
        f"<b>Вопрос 14 из 14:</b>\n"
        f"Добавь хэштег #анкета\n\n"
        f"Пример: #анкета",
        parse_mode="HTML"
    )

@dp.message(AnketaStates.waiting_for_hash)
async def process_hash(message: Message, state: FSMContext):
    hash_tag = message.text.strip()
    if "#анкета" not in hash_tag.lower():
        await message.answer("❌ Не забудь добавить хэштег #анкета. Попробуй ещё раз.")
        return
    await state.update_data(hash_tag=hash_tag)
    
    data = await state.get_data()
    user_id = message.from_user.id
    username = message.from_user.username or str(user_id)
    
    preview = f"""
<b>📋 ПРЕДПРОСМОТР АНКЕТЫ</b>
━━━━━━━━━━━━━━━━━━━━━

1️⃣ <b>Имя/Ник:</b> {data.get('name')}
2️⃣ <b>Возраст:</b> {data.get('age')}
3️⃣ <b>Часовой пояс/Город:</b> {data.get('location')}
4️⃣ <b>Время на модерацию:</b> {data.get('time_moderate')}
5️⃣ <b>Опыт модерации:</b> {data.get('experience')}
6️⃣ <b>Время в чате:</b> {data.get('chat_time')}
7️⃣ <b>Мотивация:</b> {data.get('motivation')}
8️⃣ <b>Ознакомлен с правилами:</b> {data.get('rules')}
9️⃣ <b>Реакция на грубость:</b> {data.get('rude_reaction')}
🔟 <b>Друг нарушил:</b> {data.get('friend_violation')}
1️⃣1️⃣ <b>Конфликты:</b> {data.get('conflicts')}
1️⃣2️⃣ <b>Нарушения и варны:</b> {data.get('varns')}
1️⃣3️⃣ <b>Username/ID:</b> {data.get('username')}
1️⃣4️⃣ <b>Хэштег:</b> {data.get('hash_tag')}

━━━━━━━━━━━━━━━━━━━━━
✅ <b>Всё верно?</b>
Напиши <b>«да»</b> для отправки анкеты
Напиши <b>«нет»</b> чтобы отменить и начать заново
"""
    await message.answer(preview, parse_mode="HTML")
    await state.set_state(AnketaStates.waiting_for_confirm)

@dp.message(AnketaStates.waiting_for_confirm)
async def process_confirm(message: Message, state: FSMContext):
    answer = message.text.strip().lower()
    
    if answer in ["да", "lf", "yes", "давай", "отправить"]:
        data = await state.get_data()
        user_id = message.from_user.id
        username = message.from_user.username or str(user_id)
        
        save_answers(user_id, data)
        await send_anketa_to_admin(bot, user_id, data, username)
        
        await message.answer(
            f"✅ <b>Анкета отправлена админу!</b>\n\n"
            f"Администрация рассмотрит твою заявку в ближайшее время.\n"
            f"Ответ придёт в личные сообщения.\n\n"
            f"Спасибо за честность! 🙏",
            parse_mode="HTML"
        )
        await state.clear()
        
    elif answer in ["нет", "ytn", "no", "не"]:
        await message.answer(
            f"❌ <b>Анкета отменена.</b>\n\n"
            f"Можешь начать заново с помощью /start",
            parse_mode="HTML"
        )
        await state.clear()
    else:
        await message.answer("❌ Напиши «да» для отправки или «нет» для отмены.")

# ========== ЗАПУСК ==========
async def main():
    print("🤖 Бот для анкетирования UNIT CHAT запущен!")
    print(f"📨 Анкеты будут приходить админу: {ADMIN_ID}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
