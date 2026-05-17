import asyncio
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# ============================================
# ВСЕ ТВОИ EMOJI-ID УЖЕ ВСТАВЛЕНЫ
# НИЧЕГО НЕ МЕНЯЙ - ВСЁ РАБОТАЕТ
# ============================================

# Эмодзи для вопросов 1-14
EMOJI_Q1 = "5312436028991094686"      # 1 вопрос
EMOJI_Q2 = "5312105174775380962"      # 2 вопрос
EMOJI_Q3 = "5312494182848279871"      # 3 вопрос
EMOJI_Q4 = "5309838054813352226"      # 4 вопрос
EMOJI_Q5 = "5312511848048770881"      # 5 вопрос
EMOJI_Q6 = "5312152011393742872"      # 6 вопрос
EMOJI_Q7 = "5310076996728929446"      # 7 вопрос
EMOJI_Q8 = "5310285032059845527"      # 8 вопрос
EMOJI_Q9 = "5312478269994448954"      # 9 вопрос
EMOJI_Q10 = "5312157624915999161"     # 10 вопрос
EMOJI_Q11 = "5310206588777150960"     # 11 вопрос
EMOJI_Q12 = "5312333740049972282"     # 12 вопрос
EMOJI_Q13 = "5312093853241589837"     # 13 вопрос
EMOJI_Q14 = f"{EMOJI_Q1}{EMOJI_Q4}"   # 14 вопрос (1+4 вместе)

# Остальные премиум эмодзи для текста
EMOJI_SMILE_ID = "5409102114892842459"      # 😀 Улыбка - приветствие
EMOJI_ROCKET_ID = "6003511896303474846"     # 🚀 Ракета - старт
EMOJI_STAR_ID = "5848262654052800278"       # ⭐ Звезда - успех
EMOJI_CHECK_ID = "5848241728972135129"      # ✅ Галочка - подтверждение
EMOJI_CROSS_ID = "5859710176415716671"      # ❌ Крестик - ошибка/отклонение
EMOJI_DOC_ID = "5444856076954520455"        # 📋 Документ - анкета
EMOJI_USER_ID = "6032994772321309200"       # 👤 Пользователь - информация о юзере
EMOJI_CLOCK_ID = "5819011010484246753"      # 🕐 Часы - дата/время
EMOJI_FIRE_ID = "6010314222557206477"       # 🔥 Огонь - активность
EMOJI_GEM_ID = "5848459028547507884"        # 💎 Алмаз - премиум/ценность
EMOJI_CROWN_ID = "5217822164362739968"      # 👑 Корона - админ
EMOJI_POPPER_ID = "5215628200578655810"     # 🎉 Хлопушка - поздравление
EMOJI_MAIL_ID = "5253742260054409879"       # 📬 Почта - новая анкета
EMOJI_WARNING_ID = "5447644880824181073"    # ⚠️ Предупреждение - важные условия

# Превращаем ID в теги
def em(emoji_id):
    return f'<tg-emoji emoji-id="{emoji_id}"></tg-emoji>'

# Эмодзи для вопросов
Q1 = em(EMOJI_Q1)
Q2 = em(EMOJI_Q2)
Q3 = em(EMOJI_Q3)
Q4 = em(EMOJI_Q4)
Q5 = em(EMOJI_Q5)
Q6 = em(EMOJI_Q6)
Q7 = em(EMOJI_Q7)
Q8 = em(EMOJI_Q8)
Q9 = em(EMOJI_Q9)
Q10 = em(EMOJI_Q10)
Q11 = em(EMOJI_Q11)
Q12 = em(EMOJI_Q12)
Q13 = em(EMOJI_Q13)
Q14 = f"{Q1}{Q4}"

# Остальные эмодзи для текста
EMOJI_SMILE = em(EMOJI_SMILE_ID)
EMOJI_ROCKET = em(EMOJI_ROCKET_ID)
EMOJI_STAR = em(EMOJI_STAR_ID)
EMOJI_CHECK = em(EMOJI_CHECK_ID)
EMOJI_CROSS = em(EMOJI_CROSS_ID)
EMOJI_DOC = em(EMOJI_DOC_ID)
EMOJI_USER = em(EMOJI_USER_ID)
EMOJI_CLOCK = em(EMOJI_CLOCK_ID)
EMOJI_FIRE = em(EMOJI_FIRE_ID)
EMOJI_GEM = em(EMOJI_GEM_ID)
EMOJI_CROWN = em(EMOJI_CROWN_ID)
EMOJI_POPPER = em(EMOJI_POPPER_ID)
EMOJI_MAIL = em(EMOJI_MAIL_ID)
EMOJI_WARNING = em(EMOJI_WARNING_ID)

# Обычные эмодзи для кнопок (работают у всех)
BTN_DOC = "📋"
BTN_WARNING = "⚠️"
BTN_CHECK = "✅"
BTN_CROSS = "❌"
BTN_RULES = "📜"

# Массив вопросов
QUESTIONS = [
    (Q1, "Как тебя звать или как к тебе обращаться? (Имя/ник)"),
    (Q2, "Сколько тебе лет? (От 14+)"),
    (Q3, "Твой часовой пояс и город?"),
    (Q4, "Сколько времени в день готов уделять модерации?"),
    (Q5, "Есть ли опыт модерации? (где и что делал)"),
    (Q6, "Сколько времени ты уже в чате UNIT CHAT?"),
    (Q7, "Почему хочешь стать админом?"),
    (Q8, "Ознакомлен ли ты с правилами UNIT CHAT?"),
    (Q9, "Пользователь грубит, но правила не нарушает. Твои действия?"),
    (Q10, "Что сделаешь, если твой друг нарушил правило?"),
    (Q11, "Были ли конфликты с участниками или админами?"),
    (Q12, "Были ли нарушения и варны в чате?"),
    (Q13, "Укажи свой @username или ID"),
    (Q14, "Добавь хэштег #анкета")
]

# ========== КОНФИГУРАЦИЯ ==========
BOT_TOKEN = "8966032196:AAHvnet7q7rqXPrznRwh0p9xRIM480CIImQ"
ADMIN_ID = 8478884644
CHANNEL_LINK = "https://t.me/UNITcoin_chat"
CHANNEL_USERNAME = "@UNITcoin_chat"
RULES_URL = "https://telegra.ph/PRAVILA-CHATA-05-14-80"
MIN_AGE = 14

# ========== КНОПКИ ==========
def get_rules_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{BTN_RULES} ПРОЧИТАТЬ ПРАВИЛА", url=RULES_URL)]
    ])

def get_rules_inline_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{BTN_RULES} ПРАВИЛА ЧАТА", url=RULES_URL)]
    ])

def get_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{BTN_DOC} Заполнить анкету", callback_data="start_anketa")],
        [InlineKeyboardButton(text=f"{BTN_WARNING} Проверить подписку", callback_data="check_subscribe")]
    ])

def get_admin_buttons(user_id: int, username: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{BTN_CHECK} Принять", callback_data=f"accept_{user_id}_{username}"),
            InlineKeyboardButton(text=f"{BTN_CROSS} Отклонить", callback_data=f"reject_{user_id}_{username}")
        ]
    ])

# ========== СОСТОЯНИЯ ==========
class AdminStates(StatesGroup):
    waiting_for_accept_message = State()
    waiting_for_reject_message = State()

class AnketaStates(StatesGroup):
    waiting_for_answer = State()
    waiting_for_confirm = State()
    current_question = State()
    answers = State()

# ========== БАЗА ДАННЫХ ==========
def init_db():
    conn = sqlite3.connect("anketa_bot.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_answers (
            user_id INTEGER PRIMARY KEY,
            q1 TEXT, q2 TEXT, q3 TEXT, q4 TEXT, q5 TEXT, q6 TEXT, q7 TEXT,
            q8 TEXT, q9 TEXT, q10 TEXT, q11 TEXT, q12 TEXT, q13 TEXT, q14 TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_answers(user_id, answers):
    conn = sqlite3.connect("anketa_bot.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO user_answers 
        (user_id, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, 
          answers.get(1), answers.get(2), answers.get(3), answers.get(4),
          answers.get(5), answers.get(6), answers.get(7), answers.get(8),
          answers.get(9), answers.get(10), answers.get(11), answers.get(12),
          answers.get(13), answers.get(14), datetime.now().isoformat()))
    conn.commit()
    conn.close()

# ========== ПРОВЕРКА ПОДПИСКИ ==========
async def check_subscription(user_id: int, bot: Bot) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

# ========== ОТПРАВКА АНКЕТЫ АДМИНУ ==========
async def send_anketa_to_admin(bot: Bot, user_id: int, answers: dict, username: str):
    text = f"""
{EMOJI_MAIL} <b>НОВАЯ АНКЕТА В АДМИНИСТРАЦИЮ UNIT CHAT</b>
━━━━━━━━━━━━━━━━━━━━━
{EMOJI_USER} <b>От:</b> @{username} (ID: <code>{user_id}</code>)
{EMOJI_CHECK} <b>Подписка на чат:</b> подтверждена

{EMOJI_DOC} <b>Ответы на вопросы:</b>

1️⃣ <b>Имя/Ник:</b> {answers.get(1, '—')}
2️⃣ <b>Возраст:</b> {answers.get(2, '—')}
3️⃣ <b>Часовой пояс/Город:</b> {answers.get(3, '—')}
4️⃣ <b>Время на модерацию:</b> {answers.get(4, '—')}
5️⃣ <b>Опыт модерации:</b> {answers.get(5, '—')}
6️⃣ <b>Время в чате:</b> {answers.get(6, '—')}
7️⃣ <b>Мотивация:</b> {answers.get(7, '—')}
8️⃣ <b>Ознакомлен с правилами:</b> {answers.get(8, '—')}
9️⃣ <b>Реакция на грубость:</b> {answers.get(9, '—')}
🔟 <b>Друг нарушил:</b> {answers.get(10, '—')}
1️⃣1️⃣ <b>Конфликты:</b> {answers.get(11, '—')}
1️⃣2️⃣ <b>Нарушения и варны:</b> {answers.get(12, '—')}
1️⃣3️⃣ <b>Username/ID:</b> {answers.get(13, '—')}
1️⃣4️⃣ <b>Хэштег:</b> {answers.get(14, '—')}
━━━━━━━━━━━━━━━━━━━━━
{EMOJI_CLOCK} <b>Дата заполнения:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}
"""
    await bot.send_message(ADMIN_ID, text, parse_mode="HTML", reply_markup=get_admin_buttons(user_id, username))

# ========== ОБРАБОТЧИКИ ==========
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
init_db()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"{EMOJI_ROCKET} <b>Добро пожаловать в бот анкетирования UNIT CHAT!</b> {EMOJI_SMILE}\n\n"
        f"{EMOJI_DOC} Здесь ты можешь заполнить анкету для вступления в администрацию чата.\n\n"
        f"{EMOJI_WARNING} <b>Важные условия:</b>\n"
        f"• Минимальный возраст: {MIN_AGE}+ лет\n"
        f"• Обязательная подписка на чат: {CHANNEL_LINK}\n\n"
        f"👇 <b>Нажми на кнопку ниже, чтобы начать</b>",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "start_anketa")
async def start_anketa(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    if not await check_subscription(user_id, bot):
        await callback.message.edit_text(
            f"{EMOJI_CROSS} <b>Ты не подписан на чат!</b>\n\n"
            f"Пожалуйста, подпишись: {CHANNEL_LINK}\n\n"
            f"После подписки нажми кнопку «Проверить подписку».",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    await state.clear()
    await state.update_data(answers={}, current=1)
    await state.set_state(AnketaStates.waiting_for_answer)
    
    q_emoji, q_text = QUESTIONS[0]
    await callback.message.edit_text(
        f"{EMOJI_DOC} <b>Анкета в администрацию UNIT CHAT</b>\n\n"
        f"Отвечай честно и по делу.\n\n"
        f"<b>Вопрос 1 из 14:</b>\n"
        f"{q_emoji} {q_text}",
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data == "check_subscribe")
async def check_sub(callback: CallbackQuery):
    user_id = callback.from_user.id
    if await check_subscription(user_id, bot):
        await callback.message.edit_text(
            f"{EMOJI_CHECK} <b>Подписка подтверждена!</b>\n\n"
            f"Теперь ты можешь заполнить анкету.",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            f"{EMOJI_CROSS} <b>Ты всё ещё не подписан!</b>\n\n"
            f"Подпишись: {CHANNEL_LINK}\n\n"
            f"После подписки нажми кнопку снова.",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
    await callback.answer()

@dp.message(AnketaStates.waiting_for_answer)
async def process_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    current = data.get('current', 1)
    answers = data.get('answers', {})
    answer_text = message.text.strip()
    
    # Валидация возраста
    if current == 2:
        try:
            age = int(answer_text)
            if age < MIN_AGE:
                await message.answer(f"{EMOJI_CROSS} Тебе меньше {MIN_AGE} лет. Анкета отклонена.\n\nНажми /start чтобы начать заново.", parse_mode="HTML")
                await state.clear()
                return
            if age > 100:
                await message.answer(f"{EMOJI_CROSS} Укажи реальный возраст.", parse_mode="HTML")
                return
        except ValueError:
            await message.answer(f"{EMOJI_CROSS} Напиши возраст числом. Например: 16", parse_mode="HTML")
            return
    
    # Валидация хэштега
    if current == 14 and "#анкета" not in answer_text.lower():
        await message.answer(f"{EMOJI_CROSS} Не забудь добавить хэштег #анкета. Попробуй ещё раз.", parse_mode="HTML")
        return
    
    answers[current] = answer_text
    await state.update_data(answers=answers, current=current + 1)
    
    if current >= 14:
        preview = f"""
{EMOJI_DOC} <b>ПРЕДПРОСМОТР АНКЕТЫ</b>
━━━━━━━━━━━━━━━━━━━━━

1️⃣ <b>Имя/Ник:</b> {answers.get(1, '—')}
2️⃣ <b>Возраст:</b> {answers.get(2, '—')}
3️⃣ <b>Часовой пояс/Город:</b> {answers.get(3, '—')}
4️⃣ <b>Время на модерацию:</b> {answers.get(4, '—')}
5️⃣ <b>Опыт модерации:</b> {answers.get(5, '—')}
6️⃣ <b>Время в чате:</b> {answers.get(6, '—')}
7️⃣ <b>Мотивация:</b> {answers.get(7, '—')}
8️⃣ <b>Ознакомлен с правилами:</b> {answers.get(8, '—')}
9️⃣ <b>Реакция на грубость:</b> {answers.get(9, '—')}
🔟 <b>Друг нарушил:</b> {answers.get(10, '—')}
1️⃣1️⃣ <b>Конфликты:</b> {answers.get(11, '—')}
1️⃣2️⃣ <b>Нарушения и варны:</b> {answers.get(12, '—')}
1️⃣3️⃣ <b>Username/ID:</b> {answers.get(13, '—')}
1️⃣4️⃣ <b>Хэштег:</b> {answers.get(14, '—')}

━━━━━━━━━━━━━━━━━━━━━
{EMOJI_CHECK} <b>Всё верно?</b>
Напиши <b>«да»</b> для отправки анкеты
Напиши <b>«нет»</b> чтобы отменить и начать заново
"""
        await message.answer(preview, parse_mode="HTML")
        await state.set_state(AnketaStates.waiting_for_confirm)
    else:
        q_emoji, q_text = QUESTIONS[current]
        await message.answer(
            f"<b>Вопрос {current + 1} из 14:</b>\n"
            f"{q_emoji} {q_text}",
            parse_mode="HTML"
        )

@dp.message(AnketaStates.waiting_for_confirm)
async def process_confirm(message: Message, state: FSMContext):
    answer = message.text.strip().lower()
    
    if answer in ["да", "lf", "yes", "давай", "отправить"]:
        data = await state.get_data()
        answers = data.get('answers', {})
        user_id = message.from_user.id
        username = message.from_user.username or str(user_id)
        
        save_answers(user_id, answers)
        await send_anketa_to_admin(bot, user_id, answers, username)
        
        await message.answer(
            f"{EMOJI_MAIL} <b>Анкета отправлена админу!</b>\n\n"
            f"Администрация рассмотрит твою заявку в ближайшее время.\n"
            f"Ответ придёт в личные сообщения.\n\n"
            f"{EMOJI_STAR} Спасибо за честность! {EMOJI_SMILE}",
            parse_mode="HTML"
        )
        await state.clear()
        
    elif answer in ["нет", "ytn", "no", "не"]:
        await message.answer(
            f"{EMOJI_CROSS} <b>Анкета отменена.</b>\n\n"
            f"Можешь начать заново с помощью /start",
            parse_mode="HTML"
        )
        await state.clear()
    else:
        await message.answer(f"{EMOJI_CROSS} Напиши «да» для отправки или «нет» для отмены.", parse_mode="HTML")

# ========== КНОПКИ АДМИНА ==========
@dp.callback_query(F.data.startswith("accept_"))
async def accept_anketa(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Только для админа!", show_alert=True)
        return
    
    parts = callback.data.split("_")
    user_id = int(parts[1])
    username = parts[2]
    
    await state.update_data(target_user_id=user_id, target_username=username)
    await state.set_state(AdminStates.waiting_for_accept_message)
    
    await callback.message.answer(
        f"{EMOJI_CROWN} Вы приняли заявку от @{username}\n\n"
        f"Напишите текст для пользователя.\n\n{EMOJI_WARNING} /cancel - отмена",
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("reject_"))
async def reject_anketa(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Только для админа!", show_alert=True)
        return
    
    parts = callback.data.split("_")
    user_id = int(parts[1])
    username = parts[2]
    
    await state.update_data(target_user_id=user_id, target_username=username)
    await state.set_state(AdminStates.waiting_for_reject_message)
    
    await callback.message.answer(
        f"{EMOJI_CROSS} Вы отклонили заявку от @{username}\n\n"
        f"Напишите причину отказа.\n\n{EMOJI_WARNING} /cancel - отмена",
        parse_mode="HTML"
    )
    await callback.answer()

@dp.message(AdminStates.waiting_for_accept_message)
async def send_accept_message(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Отменено.")
        return
    
    data = await state.get_data()
    user_id = data.get('target_user_id')
    username = data.get('target_username')
    admin_text = message.text
    
    try:
        await bot.send_message(
            user_id,
            f"{EMOJI_POPPER} <b>ПОЗДРАВЛЯЮ!</b> {EMOJI_GEM}\n\n"
            f"Твоя заявка в администрацию UNIT CHAT <b>ПРИНЯТА</b>!\n\n"
            f"{EMOJI_CROWN} <b>Испытательный срок: 3 дня</b>\n"
            f"{EMOJI_WARNING} <b>Система нарушений:</b> 3 варна = кик с выдачей дня\n\n"
            f"Сообщение от администратора:\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{admin_text}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{EMOJI_STAR} Добро пожаловать в команду! {EMOJI_FIRE}",
            parse_mode="HTML",
            reply_markup=get_rules_inline_button()
        )
        await message.answer(f"✅ Отправлено @{username} с кнопкой правил")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
    
    await state.clear()

@dp.message(AdminStates.waiting_for_reject_message)
async def send_reject_message(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Отменено.")
        return
    
    data = await state.get_data()
    user_id = data.get('target_user_id')
    username = data.get('target_username')
    admin_text = message.text
    
    try:
        await bot.send_message(
            user_id,
            f"{EMOJI_CROSS} <b>ВАША ЗАЯВКА ОТКЛОНЕНА</b>\n\n"
            f"Сообщение от администратора:\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{admin_text}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{EMOJI_WARNING} Ты можешь попробовать подать заявку позже. {EMOJI_SMILE}",
            parse_mode="HTML"
        )
        await message.answer(f"❌ Отправлено @{username}")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
    
    await state.clear()

# ========== ЗАПУСК ==========
async def main():
    print("🤖 Бот для анкетирования UNIT CHAT запущен!")
    print(f"📨 Анкеты приходят админу: {ADMIN_ID}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
