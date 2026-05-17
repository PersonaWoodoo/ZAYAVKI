import asyncio
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# ========== ТВОИ ПРЕМИУМ ЭМОДЗИ (ТОЛЬКО ДЛЯ ТЕКСТА) ==========
Q1 = '<tg-emoji emoji-id="5312436028991094686"></tg-emoji>'
Q2 = '<tg-emoji emoji-id="5312105174775380962"></tg-emoji>'
Q3 = '<tg-emoji emoji-id="5312494182848279871"></tg-emoji>'
Q4 = '<tg-emoji emoji-id="5309838054813352226"></tg-emoji>'
Q5 = '<tg-emoji emoji-id="5312511848048770881"></tg-emoji>'
Q6 = '<tg-emoji emoji-id="5312152011393742872"></tg-emoji>'
Q7 = '<tg-emoji emoji-id="5310076996728929446"></tg-emoji>'
Q8 = '<tg-emoji emoji-id="5310285032059845527"></tg-emoji>'
Q9 = '<tg-emoji emoji-id="5312478269994448954"></tg-emoji>'
Q10 = '<tg-emoji emoji-id="5312157624915999161"></tg-emoji>'
Q11 = '<tg-emoji emoji-id="5310206588777150960"></tg-emoji>'
Q12 = '<tg-emoji emoji-id="5312333740049972282"></tg-emoji>'
Q13 = '<tg-emoji emoji-id="5312093853241589837"></tg-emoji>'
Q14 = f"{Q1}{Q4}"

# Премиум для текста
EMOJI_SMILE = '<tg-emoji emoji-id="5409102114892842459"></tg-emoji>'
EMOJI_ROCKET = '<tg-emoji emoji-id="6003511896303474846"></tg-emoji>'
EMOJI_STAR = '<tg-emoji emoji-id="5848262654052800278"></tg-emoji>'
EMOJI_CHECK = '<tg-emoji emoji-id="5848241728972135129"></tg-emoji>'
EMOJI_CROSS = '<tg-emoji emoji-id="5859710176415716671"></tg-emoji>'
EMOJI_DOC = '<tg-emoji emoji-id="5444856076954520455"></tg-emoji>'
EMOJI_USER = '<tg-emoji emoji-id="6032994772321309200"></tg-emoji>'
EMOJI_CLOCK = '<tg-emoji emoji-id="5819011010484246753"></tg-emoji>'
EMOJI_FIRE = '<tg-emoji emoji-id="6010314222557206477"></tg-emoji>'
EMOJI_GEM = '<tg-emoji emoji-id="5848459028547507884"></tg-emoji>'
EMOJI_CROWN = '<tg-emoji emoji-id="5217822164362739968"></tg-emoji>'
EMOJI_POPPER = '<tg-emoji emoji-id="5215628200578655810"></tg-emoji>'
EMOJI_MAIL = '<tg-emoji emoji-id="5253742260054409879"></tg-emoji>'
EMOJI_WARNING = '<tg-emoji emoji-id="5447644880824181073"></tg-emoji>'
EMOJI_QUESTION = '<tg-emoji emoji-id="5314504236132747481"></tg-emoji>'

# ========== ОБЫЧНЫЕ ЭМОДЗИ ДЛЯ ИНЛАЙН-КНОПОК ==========
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

# ========== КНОПКИ (ТОЛЬКО ОБЫЧНЫЕ ЭМОДЗИ) ==========
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
                await message.answer(f"{EMOJI_CROSS} Тебе меньше {MIN_AGE} лет. Анкета отклонена.\n\nНажми /start чтобы начать заново.")
                await state.clear()
                return
            if age > 100:
                await message.answer(f"{EMOJI_CROSS} Укажи реальный возраст.")
                return
        except ValueError:
            await message.answer(f"{EMOJI_CROSS} Напиши возраст числом. Например: 16")
            return
    
    # Валидация хэштега
    if current == 14 and "#анкета" not in answer_text.lower():
        await message.answer(f"{EMOJI_CROSS} Не забудь добавить хэштег #анкета. Попробуй ещё раз.")
        return
    
    answers[current] = answer_text
    await state.update_data(answers=answers, current=current + 1)
    
    if current >= 14:
        # Показываем предпросмотр
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
        await message.answer(f"{EMOJI_CROSS} Напиши «да» для отправки или «нет» для отмены.")

# ========== КНОПКИ АДМИНА ==========
@dp.callback_query(F.data.startswith("accept_"))
async def accept_anketa(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer(f"{EMOJI_CROSS} Только для админа!", show_alert=True)
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
        await callback.answer(f"{EMOJI_CROSS} Только для админа!", show_alert=True)
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
        await message.answer(f"{EMOJI_CROSS} Отменено.")
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
        await message.answer(f"{BTN_CHECK} Отправлено @{username} с кнопкой правил")
    except Exception as e:
        await message.answer(f"{EMOJI_CROSS} Ошибка: {e}")
    
    await state.clear()

@dp.message(AdminStates.waiting_for_reject_message)
async def send_reject_message(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.answer(f"{EMOJI_CROSS} Отменено.")
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
        await message.answer(f"{BTN_CROSS} Отправлено @{username}")
    except Exception as e:
        await message.answer(f"{EMOJI_CROSS} Ошибка: {e}")
    
    await state.clear()

# ========== ЗАПУСК ==========
async def main():
    print("🤖 Бот для анкетирования UNIT CHAT запущен!")
    print(f"📨 Анкеты приходят админу: {ADMIN_ID}")
    print("✨ Премиум-эмодзи только в тексте, на кнопках обычные")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
