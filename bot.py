import asyncio
import logging
import os
import random
import string
import sys
from dotenv import load_dotenv

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

settings_module = None
for item in os.listdir(BASE_DIR):
    item_path = os.path.join(BASE_DIR, item)
    if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "settings.py")):
        settings_module = f"{item}.settings"
        break

if settings_module:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
    try:
        import django
        django.setup()
        from django.contrib.auth.models import User
        HAS_DJANGO = True
    except Exception as e:
        HAS_DJANGO = False

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
SITE_LOGIN_URL = os.getenv("SITE_LOGIN_URL", "http://127.0.0.1:8000/login/")
TEAM_INVITE_CODE = os.getenv("TEAM_INVITE_CODE", "nekto2026")
PROXY_URL = os.getenv("TELEGRAM_PROXY", None)

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    CallbackQuery
)

if PROXY_URL:
    session = AiohttpSession(proxy=PROXY_URL, timeout=30.0)
else:
    session = AiohttpSession(timeout=30.0)

bot = Bot(token=BOT_TOKEN, session=session)
dp = Dispatcher(storage=MemoryStorage())

class ApplicationForm(StatesGroup):
    role = State()
    experience = State()
    portfolio = State()

def generate_credentials(username_base):
    clean_name = "".join(c for c in username_base if c.isalnum()).lower()
    if not clean_name:
        clean_name = "user"
    random_num = random.randint(1000, 9999)
    username = f"{clean_name}_{random_num}"
    
    chars = string.ascii_letters + string.digits + "!@#$"
    password = "".join(random.choice(chars) for _ in range(10))
    return username, password

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Ознакомиться с требованиями")],
            [KeyboardButton(text="🎯 Подать заявку в NEKTO Voice")],
        ],
        resize_keyboard=True
    )

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привет! Это официальный бот команды NEKTO Voice 🎙️\n\n"
        "Мы ищем опытных специалистов в наш коллектив. Выбери действие ниже:",
        reply_markup=get_main_keyboard()
    )

@dp.message(Command("team"))
@dp.message(Command("access"))
async def cmd_team_access(message: Message):
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.answer(
            "🔑 <b>Быстрый доступ для действующей команды NEKTO Voice</b>\n\n"
            "Если ты уже состоишь в нашем коллективе, введи команду вместе с секретным ключом:\n"
            "<code>/team ваш_секретный_ключ</code>",
            parse_mode="HTML"
        )
        return

    provided_code = args[1].strip()

    if provided_code != TEAM_INVITE_CODE:
        await message.answer("❌ Неверный секретный ключ доступа!")
        return

    user = message.from_user
    username_base = user.username or f"team_{user.id}"
    username, password = generate_credentials(username_base)

    db_status = "Пропущено"
    if HAS_DJANGO:
        try:
            user_obj, created = User.objects.get_or_create(username=username)
            user_obj.set_password(password)
            user_obj.is_staff = True
            user_obj.save()
            db_status = "Успешно зарегистрирован в БД"
        except Exception as e:
            db_status = f"Ошибка БД: {e}"

    response_text = (
        f"🎉 <b>Добро пожаловать на портал NEKTO Voice!</b>\n\n"
        f"Твой аккаунт сотрудника успешно создан:\n"
        f"🌐 <b>Ссылка для входа:</b> {SITE_LOGIN_URL}\n"
        f"👤 <b>Логин:</b> <code>{username}</code>\n"
        f"🔑 <b>Пароль:</b> <code>{password}</code>\n\n"
        f"<i>Сохрани эти данные для входа в рабочую панель.</i>"
    )
    
    await message.answer(response_text, parse_mode="HTML")

    if ADMIN_CHAT_ID:
        try:
            admin_msg = (
                f"ℹ️ <b>Действующий сотрудник получил доступ:</b>\n"
                f"<b>Пользователь:</b> @{user.username if user.username else 'без юзернейма'} ({user.full_name})\n"
                f"<b>Создан логин:</b> <code>{username}</code>"
            )
            await bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_msg, parse_mode="HTML")
        except Exception:
            pass

@dp.message(F.text == "📋 Ознакомиться с требованиями")
async def show_requirements(message: Message):
    req_text = (
        "<b>📋 ТРЕБОВАНИЯ К КАНДИДАТАМ NEKTO VOICE:</b>\n\n"
        "<b>🎙️ Дабберы (Парни / Девушки):</b>\n"
        "• Опыт от 1–2 лет в озвучке.\n"
        "• Качественный микрофон + звуковая карта.\n"
        "• Подготовленное помещение без эха.\n"
        "• Высокая актерская подача и липсинк.\n\n"
        "<b>🎛️ Звукорежиссеры / Таймеры:</b>\n"
        "• Опыт от 1–2 лет, софт — REAPER.\n"
        "• Умение делать полный дубляж и рекасты.\n\n"
        "<b>📝 Переводчики / Липсеры:</b>\n"
        "• Знание английского B2/C1.\n"
        "• Умение адаптировать текст под дубляж.\n\n"
        "<b>💬 Сабберы:</b>\n"
        "• Отличное владение Aegisub.\n\n"
        "⚠️ <i>Заявки без демо-записей и портфолио отклоняются!</i>"
    )
    await message.answer(req_text, parse_mode="HTML")

@dp.message(F.text == "🎯 Подать заявку в NEKTO Voice")
async def start_application(message: Message, state: FSMContext):
    await state.set_state(ApplicationForm.role)
    await message.answer("Выбери роль или напиши свою (Даббер, Звукорежиссер, Переводчик, Саббер):")

@dp.message(ApplicationForm.role)
async def process_role(message: Message, state: FSMContext):
    await state.update_data(role=message.text)
    await state.set_state(ApplicationForm.experience)
    await message.answer("Укажи твой опыт работы (например: 2 года, участвовал в релизах...):")

@dp.message(ApplicationForm.experience)
async def process_experience(message: Message, state: FSMContext):
    await state.update_data(experience=message.text)
    await state.set_state(ApplicationForm.portfolio)
    await message.answer("Отправь ссылку на портфолио, примеры работ или демо-запись голоса:")

@dp.message(ApplicationForm.portfolio)
async def process_portfolio(message: Message, state: FSMContext):
    await state.update_data(portfolio=message.text)
    data = await state.get_data()
    user = message.from_user

    admin_markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🟢 Принять", callback_data=f"accept:{user.id}"),
            InlineKeyboardButton(text="🔴 Отклонить", callback_data=f"reject:{user.id}")
        ]
    ])

    admin_text = (
        f"<b>📥 НОВАЯ ЗАЯВКА В КОМАНДУ!</b>\n\n"
        f"<b>Кандидат:</b> @{user.username if user.username else 'без юзернейма'} (ID: {user.id})\n"
        f"<b>Имя:</b> {user.full_name}\n"
        f"<b>Роль:</b> {data['role']}\n"
        f"<b>Опыт:</b> {data['experience']}\n"
        f"<b>Портфолио/Демо:</b> {data['portfolio']}"
    )

    if ADMIN_CHAT_ID:
        try:
            await bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_text, parse_mode="HTML", reply_markup=admin_markup)
        except Exception as e:
            logging.error(f"Ошибка отправки админу: {e}")

    await message.answer("✅ Твоя заявка успешно отправлена кураторам! Мы свяжемся с тобой после проверки.", reply_markup=get_main_keyboard())
    await state.clear()

@dp.callback_query(F.data.startswith("accept:"))
async def accept_user(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])
    username_base = callback.from_user.username or f"user_{user_id}"
    
    username, password = generate_credentials(username_base)

    db_status = "Пропущено"
    if HAS_DJANGO:
        try:
            user, created = User.objects.get_or_create(username=username)
            user.set_password(password)
            user.is_staff = True
            user.save()
            db_status = "Пользователь создан в БД"
        except Exception as e:
            db_status = f"Ошибка БД: {e}"

    updated_card = (
        f"{callback.message.text}\n\n"
        f"<b>STATUS: 🟢 ПРИНЯТ</b>\n"
        f"<b>Логин:</b> <code>{username}</code>\n"
        f"<b>Пароль:</b> <code>{password}</code>\n"
        f"<b>Инфо БД:</b> {db_status}"
    )
    await callback.message.edit_text(updated_card, parse_mode="HTML")
    await callback.answer("Заявка одобрена, доступы сгенерированы!")

    candidate_text = (
        f"🎉 <b>Поздравляем! Твоя заявка в команду NEKTO Voice принята!</b>\n\n"
        f"Для тебя создана учетная запись на нашем портале:\n"
        f"🌐 <b>Ссылка для входа:</b> {SITE_LOGIN_URL}\n"
        f"👤 <b>Логин:</b> <code>{username}</code>\n"
        f"🔑 <b>Пароль:</b> <code>{password}</code>\n\n"
        f"<i>Пожалуйста, сохрани эти данные. После входа ты получишь доступ к рабочим материалам и тайтлам.</i>"
    )

    try:
        await bot.send_message(chat_id=user_id, text=candidate_text, parse_mode="HTML")
    except Exception as e:
        await callback.message.answer(f"Не удалось отправить доступы кандидату: {e}")

@dp.callback_query(F.data.startswith("reject:"))
async def reject_user(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])
    
    await callback.message.edit_text(callback.message.text + "\n\n<b>STATUS: 🔴 ОТКЛОНЕН</b>", parse_mode="HTML")
    await callback.answer("Заявка отклонена.")
    
    try:
        await bot.send_message(
            chat_id=user_id,
            text="К сожалению, твоя заявка в NEKTO Voice отклонена. Благодарим за интерес к нашей команде и желаем успехов!",
            parse_mode="HTML"
        )
    except Exception as e:
        await callback.message.answer(f"Не удалось отправить сообщение кандидату: {e}")

async def main():
    while True:
        try:
            print("🤖 Бот запущен и ожидает сообщений...")
            await dp.start_polling(bot)
        except Exception as e:
            print(f"⚠️ Сетевая ошибка: {e}. Переподключение через 3 секунды...")
            await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())