import asyncio
import logging
import json
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, WebAppInfo, MenuButtonDefault
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from config import BOT_TOKEN, ADMINS, ADMIN_PASSWORD, WEBAPP_URL
from database import Database

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
db = Database()

LANGS = {
    "uz": {
        "start": "Assalomu alaykum", "menu": "🍔 Menyu", "back": "🔙 Asosiy menyu",
        "kafe": "🏢 Kafe + Bino", "masofaviy": "🛵 Masofaviy", "kuryer": "📦 Kuryer bo'lish",
        "kabinet": "👤 Kabinetim", "aloqa": "☎️ Admin bilan aloqa", "xona": "🚪 Xona",
        "stollar": "🍽 Kafe", "cancel": "❌ Bekor qilish", "send_loc": "📍 Lokatsiyani yuborish",
        "skip": "⏩ O'tkazib yuborish", "send_phone": "📱 Raqamni yuborish",
        "main_menu": "Bosh menyuga qaytdingiz.", "choose_loc": "Joylashuvni tanlang:",
        "room_num": "Xona raqamini kiriting:", "table_num": "Stol raqamini kiriting:",
        "remote_order": "Masofaviy buyurtma!\nPastdagi <b>🍔 Menyu</b> tugmasini bosib mahsulot tanlang:",
        "my_orders": "📦 Buyurtmalarim",
        "start_msg": "🔥 <b>Food Markaziga xush kelibsiz!</b>\n\n📖 <b>Qisqacha qo'llanma:</b>\n1️⃣ Avval o'zingiz xohlagan kafeni tanlang\n2️⃣ So'ngra yetkazib berish turini tanlang\n3️⃣ <b>🍔 Menyu</b> tugmasi orqali buyurtma bering\n\n👇 Iltimos, o'zingizga kerakli bo'limni tanlang:",
        "comment_prompt": "Qo'shimcha izoh qoldiring (Yoki 'Yo'q' deb yozing):", "no": "Yo'q",
        "address_prompt": "Yetkazib berish uchun manzilingizni yozing (yoki lokatsiya yuboring):",
        "comment_prompt_short": "Qo'shimcha izoh qoldiring (Yoki 'Yo'q' deb yozing):",
        "cabinet_title": "👤 <b>Foydalanuvchi kabineti</b>", "name": "Ism",
        "total_orders": "Jami xaridlar soni", "total_spent": "Sarflangan summa",
        "no_orders": "Sizda hali buyurtmalar yo'q.", "last_orders": "📦 <b>Sizning oxirgi 5 ta buyurtmangiz:</b>",
        "order_num": "Buyurtma", "date": "Sana", "products": "Mahsulotlar", "total": "Jami",
        "status": "Holati", "order_accepted": "Buyurtmangiz yuborildi!", "your_purchase": "Xaridingiz",
        "admin_wait": "Adminlar tez orada ko'rib chiqishadi.", "change_lang": "⚙️ Tilni o'zgartirish",
        "delivery_type_remote": "🛍 <b>Yetkazib berish turi: Masofaviy</b>",
        "you_selected": "Siz quyidagi mahsulotlarni tanladingiz:", "order_preparing": "qabul qilindi, tayyorlanmoqda tez orada tayyor bo'ladi.",
        "cart_accepted": "🛍 <b>Savat qabul qilindi!</b>\n\nIltimos, buyurtmani rasmiylashtirish uchun yetkazib berish turini tanlang:",
        "cart_empty": "Savat bo'sh.", "checkout_error": "Buyurtmani qayta ishlashda xatolik yuz berdi.",
        "phone_prompt": "Iltimos, tasdiqlash uchun <b>📱 Raqamni yuborish</b> tugmasi orqali telefoningizni yuboring:",
        "confirmed": "Tasdiqlandi",
        "courier_pw_prompt": "Kuryer bo'lish uchun kompaniya tanlang va parolni kiriting:",
        "courier_pw_correct": "✅ Parol to'g'ri!\n\nIltimos, ism va familiyangizni kiriting:",
        "courier_pw_wrong": "❌ Noto'g'ri parol!", "courier_phone_prompt": "Telefon raqamingizni yuboring:",
        "courier_success": "✅ Siz kuryer sifatida ro'yxatdan o'tdingiz!\nSizning ID raqamingiz: <b>{id}</b>\nBuyurtmalar tushishini kuting.",
        "contact_admin_title": "📞 <b>Admin bilan bog'lanish:</b>\n\n",
        "contact_name": "👨‍💼 Ism:", "contact_phone": "📱 Telefon:", "contact_tg": "💬 Telegram:",
        "order_rejected": "❌ Uzr, sizning #{id} buyurtmangiz bekor qilindi.",
        "courier_assigned": "Sizning kuryeringiz", "arriving_soon": "Tez orada yetib boradi!",
        "choose_company": "🏪 O'zingiz xohlagan kafeni tanlang:"
    },
    "ru": {
        "start": "Здравствуйте", "menu": "🍔 Меню", "back": "🔙 Главное меню",
        "kafe": "🏢 Кафе + Здание", "masofaviy": "🛵 Удаленно", "kuryer": "📦 Стать курьером",
        "kabinet": "👤 Мой кабинет", "aloqa": "☎️ Связь с админом", "xona": "🚪 Комната",
        "stollar": "🍽 Кафе", "cancel": "❌ Отмена", "send_loc": "📍 Отправить локацию",
        "skip": "⏩ Пропустить", "send_phone": "📱 Отправить номер",
        "main_menu": "Вы вернулись в главное меню.", "choose_loc": "Выберите место:",
        "room_num": "Введите номер комнаты:", "table_num": "Введите номер стола:",
        "remote_order": "Удаленный заказ!\nВыберите продукты через кнопку <b>🍔 Меню</b>:",
        "my_orders": "📦 Мои заказы",
        "start_msg": "🔥 <b>Добро пожаловать в Food Центр!</b>\n\n👇 Выберите нужный раздел:",
        "comment_prompt": "Оставьте комментарий (Или напишите 'Нет'):", "no": "Нет",
        "address_prompt": "Напишите адрес доставки (или отправьте локацию):",
        "comment_prompt_short": "Оставьте комментарий (Или напишите 'Нет'):",
        "cabinet_title": "👤 <b>Личный кабинет</b>", "name": "Имя",
        "total_orders": "Общее количество покупок", "total_spent": "Потраченная сумма",
        "no_orders": "У вас пока нет заказов.", "last_orders": "📦 <b>Ваши последние 5 заказов:</b>",
        "order_num": "Заказ", "date": "Дата", "products": "Продукты", "total": "Итого",
        "status": "Статус", "order_accepted": "Ваш заказ принят!", "your_purchase": "Ваша покупка",
        "admin_wait": "Админы скоро рассмотрят.", "change_lang": "⚙️ Изменить язык",
        "delivery_type_remote": "🛍 <b>Тип доставки: Удаленно</b>",
        "you_selected": "Вы выбрали следующие продукты:", "order_preparing": "принят и готовится!",
        "cart_accepted": "🛍 <b>Корзина принята!</b>\n\nВыберите тип доставки:",
        "cart_empty": "Корзина пуста.", "checkout_error": "Произошла ошибка при обработке заказа.",
        "phone_prompt": "Отправьте ваш телефон для подтверждения заказа:",
        "confirmed": "Подтверждено", "courier_pw_prompt": "Выберите компанию и введите пароль курьера:",
        "courier_pw_correct": "✅ Правильный пароль!\n\nВведите ваше имя:", "courier_pw_wrong": "❌ Неверный пароль!",
        "courier_phone_prompt": "Отправьте номер телефона:",
        "courier_success": "✅ Вы зарегистрированы как курьер!\nВаш ID: <b>{id}</b>\nОжидайте заказов.",
        "contact_admin_title": "📞 <b>Связь с админом:</b>\n\n",
        "contact_name": "👨‍💼 Имя:", "contact_phone": "📱 Телефон:", "contact_tg": "💬 Телеграм:",
        "order_rejected": "❌ Ваш заказ #{id} отменен.",
        "courier_assigned": "Ваш курьер", "arriving_soon": "Скоро прибудет!",
        "choose_company": "🏪 Выберите желаемое кафе:"
    },
    "en": {
        "start": "Hello", "menu": "🍔 Menu", "back": "🔙 Main menu",
        "kafe": "🏢 Cafe + Building", "masofaviy": "🛵 Delivery", "kuryer": "📦 Become courier",
        "kabinet": "👤 My Profile", "aloqa": "☎️ Contact Admin", "xona": "🚪 Room",
        "stollar": "🍽 Cafe", "cancel": "❌ Cancel", "send_loc": "📍 Send Location",
        "skip": "⏩ Skip", "send_phone": "📱 Send Number",
        "main_menu": "Returned to main menu.", "choose_loc": "Choose location:",
        "room_num": "Enter room number:", "table_num": "Enter table number:",
        "remote_order": "Remote delivery!\nChoose items via the <b>🍔 Menu</b> button:",
        "my_orders": "📦 My Orders",
        "start_msg": "🔥 <b>Welcome to Food Center!</b>\n\n👇 Please select a section:",
        "comment_prompt": "Leave a comment (Or write 'No'):", "no": "No",
        "address_prompt": "Write your delivery address (or send location):",
        "comment_prompt_short": "Leave a comment (Or write 'No'):",
        "cabinet_title": "👤 <b>User Profile</b>", "name": "Name",
        "total_orders": "Total orders", "total_spent": "Total spent",
        "no_orders": "You have no orders yet.", "last_orders": "📦 <b>Your last 5 orders:</b>",
        "order_num": "Order", "date": "Date", "products": "Products", "total": "Total",
        "status": "Status", "order_accepted": "Your order is accepted!", "your_purchase": "Your purchase",
        "admin_wait": "Admins will review shortly.", "change_lang": "⚙️ Change language",
        "delivery_type_remote": "🛍 <b>Delivery type: Remote</b>",
        "you_selected": "You selected the following items:", "order_preparing": "is accepted and being prepared!",
        "cart_accepted": "🛍 <b>Cart accepted!</b>\n\nPlease select the delivery type:",
        "cart_empty": "Cart is empty.", "checkout_error": "An error occurred while processing the order.",
        "phone_prompt": "Please send your phone number to confirm:",
        "confirmed": "Confirmed", "courier_pw_prompt": "Select company and enter courier password:",
        "courier_pw_correct": "✅ Password correct!\n\nPlease enter your name:", "courier_pw_wrong": "❌ Wrong password!",
        "courier_phone_prompt": "Send your phone number:",
        "courier_success": "✅ You are registered as a courier!\nYour ID: <b>{id}</b>\nWait for new orders.",
        "contact_admin_title": "📞 <b>Contact Admin:</b>\n\n",
        "contact_name": "👨‍💼 Name:", "contact_phone": "📱 Phone:", "contact_tg": "💬 Telegram:",
        "order_rejected": "❌ Your order #{id} has been canceled.",
        "courier_assigned": "Your courier", "arriving_soon": "Arriving soon!",
        "choose_company": "🏪 Choose your desired cafe:"
    }
}

def get_text(lang, key):
    return LANGS.get(lang, LANGS["uz"]).get(key, LANGS["uz"].get(key, ""))

async def is_admin(user_id):
    db_admins = await db.get_admins()
    return user_id in ADMINS or user_id in db_admins

# --- FSM States ---
class AdminLogin(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()

class AdminContact(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_username = State()

class AdminManage(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()
    waiting_for_name = State()

class CompanyManage(StatesGroup):
    waiting_for_name = State()
    waiting_for_login = State()
    waiting_for_password = State()

class CategoryManage(StatesGroup):
    waiting_for_new_category = State()

class AddProduct(StatesGroup):
    waiting_for_name = State()
    waiting_for_category = State()
    waiting_for_desc = State()
    waiting_for_price = State()
    waiting_for_image = State()

class EditProduct(StatesGroup):
    waiting_for_desc = State()
    waiting_for_price = State()
    waiting_for_image = State()

class Broadcast(StatesGroup):
    waiting_for_message = State()

class OrderFlow(StatesGroup):
    waiting_for_company = State()
    waiting_for_room = State()
    waiting_for_table = State()
    waiting_for_phone = State()
    waiting_for_address = State()
    waiting_for_comment = State()
    waiting_for_type_after_checkout = State()
    waiting_for_room_after_checkout = State()
    waiting_for_table_after_checkout = State()

class CourierReg(StatesGroup):
    waiting_for_company = State()
    waiting_for_password = State()
    waiting_for_name = State()
    waiting_for_phone = State()

class AssignCourier(StatesGroup):
    waiting_for_courier_id = State()

# --- Keyboards ---
def get_start_keyboard(lang='uz'):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, "masofaviy"))],
            [KeyboardButton(text=get_text(lang, "kuryer")), KeyboardButton(text=get_text(lang, "kabinet"))],
            [KeyboardButton(text=get_text(lang, "aloqa")), KeyboardButton(text=get_text(lang, "change_lang"))]
        ],
        resize_keyboard=True
    )

def get_kafe_bino_keyboard(lang='uz'):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, "xona")), KeyboardButton(text=get_text(lang, "stollar"))],
            [KeyboardButton(text=get_text(lang, "back"))]
        ], resize_keyboard=True
    )

def get_webapp_keyboard(lang='uz', user_id=0, company_id=None):
    url = f"{WEBAPP_URL}?lang={lang}&user_id={user_id}"
    if company_id:
        url += f"&company_id={company_id}"
    if url.startswith("http://"):
        url = url.replace("http://", "https://")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🍔 " + get_text(lang, "menu"), web_app=WebAppInfo(url=url))]
        ]
    )

def get_admin_keyboard(is_superadmin=False):
    base = [
        [KeyboardButton(text="➕ MENU qo'shish"), KeyboardButton(text="📝 O'chirish / Tahrirlash")],
        [KeyboardButton(text="📢 Reklama tarqatish"), KeyboardButton(text="👥 Foydalanuvchilar")],
        [KeyboardButton(text="🚚 Kuryerlar ma'lumotlari"), KeyboardButton(text="⚙️ Aloqa sozlamalari")],
        [KeyboardButton(text="👨‍💻 Adminlar"), KeyboardButton(text="🏷 Kategoriyalar")],
        [KeyboardButton(text="📊 Analiz"), KeyboardButton(text="🔄 Balansni nolga tushirish")],
        [KeyboardButton(text="🔄 Saytni yangilash"), KeyboardButton(text="🔙 Asosiy menyu")]
    ]
    if is_superadmin:
        base.insert(0, [KeyboardButton(text="🏢 Kompaniyalar"), KeyboardButton(text="➕ Kompaniya qo'shish")])
    return ReplyKeyboardMarkup(keyboard=base, resize_keyboard=True)

def get_contact_keyboard(lang='uz'):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=get_text(lang, "send_phone"), request_contact=True)],
                  [KeyboardButton(text=get_text(lang, "cancel"))]],
        resize_keyboard=True
    )

def get_location_keyboard(lang='uz'):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, "send_loc"), request_location=True)],
            [KeyboardButton(text=get_text(lang, "skip"))],
            [KeyboardButton(text=get_text(lang, "cancel"))]
        ],
        resize_keyboard=True
    )

# =================== USER HANDLERS ===================
@dp.message(F.text.in_([LANGS["uz"]["change_lang"], LANGS["ru"]["change_lang"], LANGS["en"]["change_lang"]]))
async def cmd_change_lang(message: Message, state: FSMContext):
    await cmd_start(message, state)

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await db.add_user(message.from_user.id, message.from_user.full_name, username=message.from_user.username)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇺🇿 O'zbek")],
            [KeyboardButton(text="🇷🇺 Русский")],
            [KeyboardButton(text="🇬🇧 English")]
        ], resize_keyboard=True
    )
    await message.answer("Tilni tanlang / Выберите язык / Choose language:", reply_markup=keyboard)

@dp.message(F.text.in_(["🇺🇿 O'zbek", "🇷🇺 Русский", "🇬🇧 English"]))
async def lang_selected(message: Message, state: FSMContext):
    lang_map = {"🇺🇿 O'zbek": "uz", "🇷🇺 Русский": "ru", "🇬🇧 English": "en"}
    lang = lang_map[message.text]
    await db.set_user_lang(message.from_user.id, lang)
    try:
        await bot.set_chat_menu_button(chat_id=message.chat.id, menu_button=MenuButtonDefault())
    except Exception as e:
        print(f"Menu button set error: {e}")
    await message.answer(get_text(lang, "start") + f", <b>{message.from_user.full_name}</b>!\n\n" + get_text(lang, "start_msg"), reply_markup=get_start_keyboard(lang))

@dp.message(F.text.in_([LANGS["uz"]["back"], LANGS["ru"]["back"], LANGS["en"]["back"]]))
@dp.message(F.text.in_([LANGS["uz"]["cancel"], LANGS["ru"]["cancel"], LANGS["en"]["cancel"]]))
async def back_to_main(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    lang = user.get("lang", "uz") if user else "uz"
    await state.clear()
    await message.answer(get_text(lang, "main_menu"), reply_markup=get_start_keyboard(lang))

# --- COMPANY SELECTION for user (inline) ---
async def show_companies_keyboard(message: Message, lang: str):
    companies = await db.get_companies()
    active_companies = [c for c in companies if not c.get('is_frozen')]
    if not active_companies:
        await message.answer("Hozircha kompaniyalar yo'q.")
        return False
    keyboard = []
    for c in active_companies:
        keyboard.append([InlineKeyboardButton(text=f"🏪 {c['name']}", callback_data=f"selcomp_{c['id']}")])
    await message.answer(get_text(lang, "choose_company"), reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    return True

# --- ORDER FLOW: user selects Kafe/Bino ---
@dp.message(StateFilter(None), F.text.in_([LANGS["uz"]["kafe"], LANGS["ru"]["kafe"], LANGS["en"]["kafe"]]))
async def kafe_bino(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    lang = user.get("lang", "uz") if user else "uz"
    await state.update_data(order_type="Kafe_Xona", lang=lang)
    await state.set_state(OrderFlow.waiting_for_company)
    await show_companies_keyboard(message, lang)

@dp.message(StateFilter(None), F.text.in_([LANGS["uz"]["masofaviy"], LANGS["ru"]["masofaviy"], LANGS["en"]["masofaviy"]]))
async def choose_masofaviy(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    lang = user.get("lang", "uz") if user else "uz"
    await state.update_data(order_type="Masofaviy", room_table="Yo'q", lang=lang)
    await state.set_state(OrderFlow.waiting_for_company)
    await show_companies_keyboard(message, lang)

@dp.callback_query(OrderFlow.waiting_for_company, F.data.startswith("selcomp_"))
async def user_company_selected(call: CallbackQuery, state: FSMContext):
    company_id = int(call.data.split("_")[1])
    company = await db.get_company(company_id)
    if not company:
        await call.answer("Kompaniya topilmadi!", show_alert=True)
        return
    await state.update_data(company_id=company_id, company_name=company["name"])
    data = await state.get_data()
    lang = data.get("lang", "uz")
    order_type = data.get("order_type", "Masofaviy")
    try:
        await call.message.delete()
    except Exception:
        pass

    if order_type == "Kafe_Xona":
        await call.message.answer(get_text(lang, "choose_loc"), reply_markup=get_kafe_bino_keyboard(lang))
        await state.set_state(None)
    else:
        await call.message.answer(
            f"🏪 <b>{company['name']}</b> tanlandi!\n\nBuyurtma berish uchun pastdagi tugmani bosing:",
            reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=get_text(lang, "back"))]], resize_keyboard=True)
        )
        await call.message.answer("👇", reply_markup=get_webapp_keyboard(lang, call.from_user.id, company_id))
        await state.set_state(None)
    await call.answer()

@dp.message(StateFilter(None), F.text.in_([LANGS["uz"]["xona"], LANGS["ru"]["xona"], LANGS["en"]["xona"]]))
async def choose_xona(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    lang = user.get("lang", "uz") if user else "uz"
    await state.update_data(order_type="Xona")
    await message.answer(get_text(lang, "room_num"), reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=get_text(lang, "back"))]], resize_keyboard=True))
    await state.set_state(OrderFlow.waiting_for_room)

@dp.message(OrderFlow.waiting_for_room, F.text)
async def process_room(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    lang = user.get("lang", "uz") if user else "uz"
    if message.text in [LANGS["uz"]["back"], LANGS["ru"]["back"], LANGS["en"]["back"]]:
        return await back_to_main(message, state)
    await state.update_data(room_table=message.text)
    data = await state.get_data()
    company_id = data.get("company_id")
    await message.answer(f"{get_text(lang, 'xona')}: {message.text}.\n\nBuyurtma uchun quyidagi tugmani bosing!", reply_markup=get_webapp_keyboard(lang, message.from_user.id, company_id))

@dp.message(StateFilter(None), F.text.in_([LANGS["uz"]["stollar"], LANGS["ru"]["stollar"], LANGS["en"]["stollar"]]))
async def choose_kafe(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    lang = user.get("lang", "uz") if user else "uz"
    await state.update_data(order_type="Kafe")
    await message.answer(get_text(lang, "table_num"), reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=get_text(lang, "back"))]], resize_keyboard=True))
    await state.set_state(OrderFlow.waiting_for_table)

@dp.message(OrderFlow.waiting_for_table, F.text)
async def process_table(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    lang = user.get("lang", "uz") if user else "uz"
    if message.text in [LANGS["uz"]["back"], LANGS["ru"]["back"], LANGS["en"]["back"]]:
        return await back_to_main(message, state)
    await state.update_data(room_table=message.text)
    data = await state.get_data()
    company_id = data.get("company_id")
    await message.answer(f"{get_text(lang, 'stollar')}: {message.text}.\n\nBuyurtma uchun quyidagi tugmani bosing!", reply_markup=get_webapp_keyboard(lang, message.from_user.id, company_id))

# --- COURIER REGISTRATION ---
@dp.message(F.text.in_([LANGS["uz"]["kuryer"], LANGS["ru"]["kuryer"], LANGS["en"]["kuryer"]]))
async def kuryer_reg_start(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    lang = user.get("lang", "uz") if user else "uz"
    companies = await db.get_companies()
    active_companies = [c for c in companies if not c.get('is_frozen')]
    if not active_companies:
        await message.answer("Hozircha kompaniyalar yo'q.")
        return
    keyboard = []
    for c in active_companies:
        keyboard.append([InlineKeyboardButton(text=f"🏪 {c['name']}", callback_data=f"coucomp_{c['id']}")])
    await message.answer("Qaysi kompaniyaga kuryer bo'lmoqchisiz?", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await state.set_state(CourierReg.waiting_for_company)

@dp.callback_query(CourierReg.waiting_for_company, F.data.startswith("coucomp_"))
async def kuryer_company_selected(call: CallbackQuery, state: FSMContext):
    company_id = int(call.data.split("_")[1])
    company = await db.get_company(company_id)
    if not company:
        await call.answer("Kompaniya topilmadi!", show_alert=True)
        return
    await state.update_data(courier_company_id=company_id)
    user = await db.get_user(call.from_user.id)
    lang = user.get("lang", "uz") if user else "uz"
    try:
        await call.message.delete()
    except Exception:
        pass
    await call.message.answer(
        f"🏪 <b>{company['name']}</b> uchun kuryer.\n\nKuryer parolini kiriting:",
        reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=get_text(lang, "back"))]], resize_keyboard=True)
    )
    await state.set_state(CourierReg.waiting_for_password)
    await call.answer()

@dp.message(CourierReg.waiting_for_password)
async def kuryer_reg_password(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    lang = user.get("lang", "uz") if user else "uz"
    if message.text in [LANGS["uz"]["back"], LANGS["ru"]["back"], LANGS["en"]["back"]]:
        return await back_to_main(message, state)
    if message.text == "1155":
        await message.answer(get_text(lang, "courier_pw_correct"))
        await state.set_state(CourierReg.waiting_for_name)
    else:
        await message.answer(get_text(lang, "courier_pw_wrong"))

@dp.message(CourierReg.waiting_for_name)
async def kuryer_reg_name(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    lang = user.get("lang", "uz") if user else "uz"
    if message.text in [LANGS["uz"]["back"], LANGS["ru"]["back"], LANGS["en"]["back"]]:
        return await back_to_main(message, state)
    await state.update_data(name=message.text)
    await message.answer(get_text(lang, "courier_phone_prompt"), reply_markup=get_contact_keyboard(lang))
    await state.set_state(CourierReg.waiting_for_phone)

@dp.message(CourierReg.waiting_for_phone, F.contact | F.text)
async def kuryer_reg_phone(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    lang = user.get("lang", "uz") if user else "uz"
    if message.text and message.text in [LANGS["uz"]["cancel"], LANGS["ru"]["cancel"], LANGS["en"]["cancel"]]:
        return await back_to_main(message, state)
    phone = message.contact.phone_number if message.contact else message.text
    data = await state.get_data()
    name = data["name"]
    company_id = data.get("courier_company_id")
    courier = await db.add_courier(message.from_user.id, name, phone, company_id=company_id)
    await state.clear()
    await message.answer(get_text(lang, "courier_success").format(id=courier["id"]), reply_markup=get_start_keyboard(lang))
    
    # Adminga xabar
    company = await db.get_company(company_id) if company_id else None
    comp_name = company["name"] if company else "Umumiy"
    
    all_admins = set(ADMINS + await db.get_admins())
    for a_id in all_admins:
        try:
            await bot.send_message(a_id, f"🆕 <b>YANGI KURYER</b>\n🏪 Kompaniya: {comp_name}\nID: {courier['id']}\nIsm: {name}\nTel: {phone}")
        except Exception:
            pass

# --- CABINET & ORDERS ---
@dp.message(F.text.in_([LANGS["uz"]["kabinet"], LANGS["ru"]["kabinet"], LANGS["en"]["kabinet"]]))
async def cmd_cabinet(message: Message):
    user = await db.get_user(message.from_user.id)
    lang = user.get("lang", "uz") if user else "uz"
    stats = await db.get_user_stats(message.from_user.id)
    text = (
        f"{get_text(lang, 'cabinet_title')}\n\n"
        f"👤 <b>{get_text(lang, 'name')}:</b> {message.from_user.full_name}\n"
        f"🆔 <b>ID:</b> {message.from_user.id}\n\n"
        f"📦 <b>{get_text(lang, 'total_orders')}:</b> {stats['order_count']}\n"
        f"💸 <b>{get_text(lang, 'total_spent')}:</b> {stats['total_spent']:,}".replace(",", " ")
    )
    await message.answer(text)

@dp.message(F.text.in_([LANGS["uz"]["my_orders"], LANGS["ru"]["my_orders"], LANGS["en"]["my_orders"]]))
async def cmd_my_orders(message: Message):
    user = await db.get_user(message.from_user.id)
    lang = user.get("lang", "uz") if user else "uz"
    orders = await db.get_user_orders(message.from_user.id, limit=5)
    if not orders:
        return await message.answer(get_text(lang, "no_orders"))
    text = f"{get_text(lang, 'last_orders')}\n\n"
    for o in orders:
        text += f"🔖 <b>{get_text(lang, 'order_num')} #{o['id']}</b> ({o.get('order_type', 'Oddiy')})\n"
        text += f"📅 {get_text(lang, 'date')}: {o['created_at']}\n"
        text += f"🛍 <b>{get_text(lang, 'products')}:</b>\n"
        for item in o.get("items", []):
            text += f"  ▪️ {item['name']} x {item['quantity']}\n"
        text += f"💰 {get_text(lang, 'total')}: {o['total_price']:,}".replace(",", " ") + "\n"
        text += f"📊 {get_text(lang, 'status')}: <b>{o['status']}</b>\n\n"
    await message.answer(text)

@dp.message(F.text.in_([LANGS["uz"]["aloqa"], LANGS["ru"]["aloqa"], LANGS["en"]["aloqa"]]))
async def cmd_contact_admin(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    lang = user.get("lang", "uz") if user else "uz"
    companies = await db.get_companies()
    active_companies = [c for c in companies if not c.get('is_frozen')]
    
    if not active_companies:
        contact = await db.get_admin_contact()
        await message.answer(
            get_text(lang, "contact_admin_title") +
            f"{get_text(lang, 'contact_name')} {contact.get('name', 'Admin')}\n"
            f"{get_text(lang, 'contact_phone')} {contact.get('phone', '')}\n"
            f"{get_text(lang, 'contact_tg')} {contact.get('username', '')}\n\n"
        )
        return
        
    if len(active_companies) == 1:
        c = active_companies[0]
        contact = await db.get_admin_contact(company_id=c['id'])
        if not contact:
            contact = {"name": "Admin", "phone": "Kiritilmagan", "username": ""}
        await message.answer(
            get_text(lang, "contact_admin_title") +
            f"{get_text(lang, 'contact_name')} {contact.get('name', 'Admin')}\n"
            f"{get_text(lang, 'contact_phone')} {contact.get('phone', 'Kiritilmagan')}\n"
            f"{get_text(lang, 'contact_tg')} {contact.get('username', '')}\n\n"
        )
        return

    keyboard = []
    for c in active_companies:
        keyboard.append([InlineKeyboardButton(text=f"🏪 {c['name']}", callback_data=f"contactcomp_{c['id']}")])
    text = "Qaysi kafening admini bilan bog'lanmoqchisiz?" if lang=="uz" else ("Выберите кафе для связи с админом:" if lang=="ru" else "Choose a cafe to contact admin:")
    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

@dp.callback_query(F.data.startswith("contactcomp_"))
async def contactcomp_callback(call: CallbackQuery):
    company_id = int(call.data.split("_")[1])
    user = await db.get_user(call.from_user.id)
    lang = user.get("lang", "uz") if user else "uz"
    contact = await db.get_admin_contact(company_id=company_id)
    if not contact:
        contact = {"name": "Admin", "phone": "Kiritilmagan", "username": ""}
    await call.message.edit_text(
        get_text(lang, "contact_admin_title") +
        f"{get_text(lang, 'contact_name')} {contact.get('name', 'Admin')}\n"
        f"{get_text(lang, 'contact_phone')} {contact.get('phone', 'Kiritilmagan')}\n"
        f"{get_text(lang, 'contact_tg')} {contact.get('username', '')}\n\n"
    )
    await call.answer()

# =================== CHECKOUT FLOW ===================
def format_location(loc):
    if loc != "Yo'q" and loc != "Kiritilmagan" and "," in loc and not any(c.isalpha() for c in loc):
        return f"https://maps.google.com/?q={loc}"
    return loc

@dp.message(F.web_app_data)
async def web_app_data_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    order_type = data.get("order_type")
    company_id = data.get("company_id")
    user = await db.get_user(message.from_user.id)
    lang = user.get("lang", "uz") if user else "uz"

    if message.web_app_data.data:
        try:
            web_data = json.loads(message.web_app_data.data)
            if web_data.get("action") == "checkout":
                items = web_data.get("items", [])
                if not items:
                    return await message.answer(get_text(lang, "cart_empty"))
                
                if not company_id:
                    company_id = web_data.get("company_id")
                    if company_id:
                        company_id = int(company_id)
                        
                db_products = await db.get_products(company_id=company_id)
                product_dict = {p["id"]: p["price"] for p in db_products}
                total = 0
                for item in items:
                    real_price = product_dict.get(int(item["id"]), item.get("price", 0))
                    if real_price is None:
                        real_price = 0
                    item["price"] = real_price
                    total += real_price * int(item["quantity"])
                    
                await state.update_data(items=items, total=total, company_id=company_id)
                if not order_type:
                    await message.answer(get_text(lang, "cart_accepted"), reply_markup=ReplyKeyboardMarkup(
                        keyboard=[[KeyboardButton(text=get_text(lang, "masofaviy"))]],
                        resize_keyboard=True
                    ))
                    await state.set_state(OrderFlow.waiting_for_type_after_checkout)
                else:
                    text = f"🛍 <b>{get_text(lang, 'you_selected')}</b>\n\n"
                    for item in items:
                        text += f"▪️ {item['name']} x {item['quantity']} = {item['price'] * item['quantity']:,} so'm\n".replace(",", " ")
                    text += f"\n💰 <b>{get_text(lang, 'total')}:</b> {total:,} so'm\n\n".replace(",", " ")
                    text += get_text(lang, "phone_prompt")
                    await message.answer(text, reply_markup=get_contact_keyboard(lang))
                    await state.set_state(OrderFlow.waiting_for_phone)
        except Exception as e:
            logging.error(f"WebApp Data Error: {e}")
            await message.answer(get_text(lang, "checkout_error"))

@dp.message(OrderFlow.waiting_for_type_after_checkout, F.text)
async def process_type_after_checkout(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    lang = user.get("lang", "uz") if user else "uz"
    data = await state.get_data()
    items = data.get("items", [])
    total = data.get("total", 0)
    if message.text in [LANGS["uz"]["kafe"], LANGS["ru"]["kafe"], LANGS["en"]["kafe"]]:
        await message.answer(get_text(lang, "choose_loc"), reply_markup=get_kafe_bino_keyboard(lang))
    elif message.text in [LANGS["uz"]["xona"], LANGS["ru"]["xona"], LANGS["en"]["xona"]]:
        await state.update_data(order_type="Xona")
        await message.answer(get_text(lang, "room_num"), reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=get_text(lang, "back"))]], resize_keyboard=True))
        await state.set_state(OrderFlow.waiting_for_room_after_checkout)
    elif message.text in [LANGS["uz"]["stollar"], LANGS["ru"]["stollar"], LANGS["en"]["stollar"]]:
        await state.update_data(order_type="Kafe")
        await message.answer(get_text(lang, "table_num"), reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=get_text(lang, "back"))]], resize_keyboard=True))
        await state.set_state(OrderFlow.waiting_for_table_after_checkout)
    elif message.text in [LANGS["uz"]["masofaviy"], LANGS["ru"]["masofaviy"], LANGS["en"]["masofaviy"]]:
        await state.update_data(order_type="Masofaviy", room_table="Yo'q")
        text = f"{get_text(lang, 'delivery_type_remote')}\n{get_text(lang, 'you_selected')}\n\n"
        for item in items:
            text += f"▪️ {item['name']} x {item['quantity']} = {item['price'] * item['quantity']:,} so'm\n".replace(",", " ")
        text += f"\n💰 <b>{get_text(lang, 'total')}:</b> {total:,} so'm\n\n".replace(",", " ")
        text += get_text(lang, "phone_prompt")
        await message.answer(text, reply_markup=get_contact_keyboard(lang))
        await state.set_state(OrderFlow.waiting_for_phone)

@dp.message(OrderFlow.waiting_for_room_after_checkout, F.text)
async def process_room_after_checkout(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    lang = user.get("lang", "uz") if user else "uz"
    if message.text in [LANGS["uz"]["back"], LANGS["ru"]["back"], LANGS["en"]["back"]]:
        return await back_to_main(message, state)
    await state.update_data(room_table=message.text)
    data = await state.get_data()
    items = data["items"]
    total = data["total"]
    text = f"🏢 <b>{get_text(lang, 'xona')}: {message.text}</b> {get_text(lang, 'confirmed')}!\n\n"
    for item in items:
        text += f"▪️ {item['name']} x {item['quantity']} = {item['price'] * item['quantity']:,} so'm\n".replace(",", " ")
    text += f"\n💰 <b>{get_text(lang, 'total')}:</b> {total:,} so'm\n\n".replace(",", " ")
    text += get_text(lang, "phone_prompt")
    await message.answer(text, reply_markup=get_contact_keyboard(lang))
    await state.set_state(OrderFlow.waiting_for_phone)

@dp.message(OrderFlow.waiting_for_table_after_checkout, F.text)
async def process_table_after_checkout(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    lang = user.get("lang", "uz") if user else "uz"
    if message.text in [LANGS["uz"]["back"], LANGS["ru"]["back"], LANGS["en"]["back"]]:
        return await back_to_main(message, state)
    await state.update_data(room_table=message.text)
    data = await state.get_data()
    items = data["items"]
    total = data["total"]
    text = f"🍽 <b>{get_text(lang, 'stollar')}: {message.text}</b> {get_text(lang, 'confirmed')}!\n\n"
    for item in items:
        text += f"▪️ {item['name']} x {item['quantity']} = {item['price'] * item['quantity']:,} so'm\n".replace(",", " ")
    text += f"\n💰 <b>{get_text(lang, 'total')}:</b> {total:,} so'm\n\n".replace(",", " ")
    text += get_text(lang, "phone_prompt")
    await message.answer(text, reply_markup=get_contact_keyboard(lang))
    await state.set_state(OrderFlow.waiting_for_phone)

@dp.message(OrderFlow.waiting_for_phone, F.contact | F.text)
async def process_phone(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    lang = user.get("lang", "uz") if user else "uz"
    if message.text and message.text in [LANGS["uz"]["cancel"], LANGS["ru"]["cancel"], LANGS["en"]["cancel"]]:
        return await back_to_main(message, state)
    phone = message.contact.phone_number if message.contact else message.text
    await state.update_data(phone=phone)
    data = await state.get_data()
    if data.get("order_type") == "Masofaviy":
        await message.answer(get_text(lang, "address_prompt"), reply_markup=get_location_keyboard(lang))
        await state.set_state(OrderFlow.waiting_for_address)
    else:
        await message.answer(get_text(lang, "comment_prompt"), reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=get_text(lang, "no"))]], resize_keyboard=True))
        await state.set_state(OrderFlow.waiting_for_comment)

@dp.message(OrderFlow.waiting_for_address, F.location | F.text)
async def process_address(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    lang = user.get("lang", "uz") if user else "uz"
    if message.text and message.text in [LANGS["uz"]["cancel"], LANGS["ru"]["cancel"], LANGS["en"]["cancel"]]:
        return await back_to_main(message, state)
    location = "Kiritilmagan"
    if message.location:
        location = f"{message.location.latitude},{message.location.longitude}"
    elif message.text and message.text not in [LANGS["uz"]["skip"], LANGS["ru"]["skip"], LANGS["en"]["skip"]]:
        location = message.text
    await state.update_data(location=location)
    await message.answer(get_text(lang, "comment_prompt_short"), reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=get_text(lang, "no"))]], resize_keyboard=True))
    await state.set_state(OrderFlow.waiting_for_comment)

@dp.message(OrderFlow.waiting_for_comment)
async def process_comment(message: Message, state: FSMContext):
    comment = message.text
    data = await state.get_data()
    order_type = data.get("order_type", "Oddiy")
    room_table = data.get("room_table", "Yo'q")
    phone = data.get("phone")
    location = data.get("location", "Yo'q")
    items = data["items"]
    total = data["total"]
    company_id = data.get("company_id")
    order_id = await db.create_order(message.from_user.id, total, location, phone, items, order_type, room_table, comment, company_id=company_id)

    company = await db.get_company(company_id) if company_id else None
    comp_name = company["name"] if company else "Umumiy"

    admin_text = f"🆕 <b>YANGI BUYURTMA #{order_id}</b>\n"
    if company:
        admin_text += f"🏪 <b>Kompaniya:</b> {comp_name}\n"
    admin_text += f"\n📊 <b>Turi:</b> {order_type}\n"
    if order_type == "Xona":
        admin_text += f"🚪 <b>Xona:</b> {room_table}\n"
    elif order_type == "Kafe":
        admin_text += f"🍽 <b>Stol:</b> {room_table}\n"
    elif order_type == "Masofaviy":
        admin_text += f"📍 <b>Manzil:</b> {format_location(location)}\n"
    admin_text += f"👤 Ism: {message.from_user.full_name}\n"
    admin_text += f"📱 Tel: {phone}\n"
    admin_text += f"💬 Izoh: {comment}\n\n"
    admin_text += "🛍 <b>Mahsulotlar:</b>\n"
    for item in items:
        admin_text += f"▪️ {item['name']} x {item['quantity']} = {item['price'] * item['quantity']} so'm\n"
    admin_text += f"\n💰 <b>Jami: {total:,} so'm</b>".replace(",", " ")

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"acc_{order_id}_{company_id or 0}"),
         InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"rej_{order_id}_{company_id or 0}")]
    ])

    sent_ids = set()
    if company_id:
        for acc in db.admin_accounts:
            if acc.get("company_id") == company_id:
                for uid, login in db.admin_sessions.items():
                    if login == acc.get("login"):
                        try:
                            await bot.send_message(chat_id=int(uid), text=admin_text, reply_markup=markup)
                            sent_ids.add(int(uid))
                        except Exception:
                            pass
    else:                        
        all_admins = set(ADMINS + await db.get_admins())
        for admin_id in all_admins:
            if admin_id not in sent_ids:
                try:
                    await bot.send_message(chat_id=admin_id, text=admin_text, reply_markup=markup)
                except Exception:
                    pass

    user = await db.get_user(message.from_user.id)
    lang = user.get("lang", "uz") if user else "uz"
    await state.clear()
    
    success_text = f"✅ <b>{get_text(lang, 'order_accepted')}</b>\n\n"
    success_text += f"🔖 <b>{get_text(lang, 'order_num')}:</b> #{order_id}\n"
    if company:
        success_text += f"🏪 <b>Kompaniya:</b> {comp_name}\n"
    success_text += f"🛍 <b>{get_text(lang, 'your_purchase')}:</b>\n"
    for item in items:
        success_text += f"▪️ {item['name']} x {item['quantity']} = {item['price'] * item['quantity']:,} so'm\n".replace(",", " ")
    success_text += f"\n💰 <b>{get_text(lang, 'total')}:</b> {total:,} so'm\n\n".replace(",", " ")
    success_text += get_text(lang, "admin_wait")
    
    await message.answer(success_text, reply_markup=get_start_keyboard(lang))

# =================== ADMIN PANEL ===================
@dp.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if await is_admin(message.from_user.id):
        is_super = await db.is_superadmin_session(message.from_user.id)
        await message.answer("Admin paneliga xush kelibsiz!", reply_markup=get_admin_keyboard(is_superadmin=is_super))
    else:
        await message.answer("Siz admin emassiz.\n\nLoginni kiriting:", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Asosiy menyu")]], resize_keyboard=True))
        await state.set_state(AdminLogin.waiting_for_login)

@dp.message(AdminLogin.waiting_for_login)
async def admin_login_step(message: Message, state: FSMContext):
    if message.text == "🔙 Asosiy menyu":
        return await back_to_main(message, state)
    await state.update_data(admin_login=message.text)
    await message.answer("Parolni kiriting:", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Asosiy menyu")]], resize_keyboard=True))
    await state.set_state(AdminLogin.waiting_for_password)

@dp.message(AdminLogin.waiting_for_password)
async def admin_password_step(message: Message, state: FSMContext):
    if message.text == "🔙 Asosiy menyu":
        return await back_to_main(message, state)
    login = (await state.get_data()).get("admin_login")
    password = message.text
    accounts = await db.get_admin_accounts()
    valid = False
    name = ""
    is_super = False
    for acc in accounts:
        if acc["login"] == login and acc["password"] == password:
            valid = True
            name = acc["name"]
            is_super = acc.get("is_superadmin", False)
            break
    if valid or (login == "superadmin" and password == ADMIN_PASSWORD):
        session_name = name if valid else "Asosiy Admin"
        if not valid:
            is_super = True
        await db.set_admin_session(message.from_user.id, login if valid else "superadmin")
        await message.answer(f"✅ Muvaffaqiyatli kirdingiz, {session_name}!", reply_markup=get_admin_keyboard(is_superadmin=is_super))
        await state.clear()
    else:
        await message.answer("❌ Noto'g'ri login yoki parol.")
        await state.clear()

# --- COMPANY MANAGEMENT (superadmin only) ---
@dp.message(F.text == "🏢 Kompaniyalar")
async def admin_companies_list(message: Message):
    if not await is_admin(message.from_user.id):
        return
    is_super = await db.is_superadmin_session(message.from_user.id)
    if not is_super:
        await message.answer("Bu funksiya faqat superadmin uchun.")
        return
    companies = await db.get_companies()
    if not companies:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="➕ Kompaniya qo'shish", callback_data="add_company_start")]])
        await message.answer("Hozircha kompaniyalar yo'q.", reply_markup=keyboard)
        return
    text = "🏢 <b>Kompaniyalar ro'yxati:</b>\n\n"
    keyboard = []
    for c in companies:
        prod_count = len(c.get("products", []))
        cour_count = len(c.get("couriers", []))
        ord_count = len(c.get("orders", []))
        status = "❄️ Muzlatilgan" if c.get("is_frozen") else "✅ Faol"
        text += f"🏪 <b>{c['name']}</b> (ID: {c['id']}) - {status}\n"
        text += f"   Mahsulotlar: {prod_count} | Kuryerlar: {cour_count} | Zakazlar: {ord_count}\n\n"
        btn_frz = InlineKeyboardButton(text="♻️ Faollashtirish" if c.get("is_frozen") else "❄️ Muzlatish", callback_data=f"frzcomp_{c['id']}")
        btn_del = InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"delcomp_{c['id']}")
        keyboard.append([btn_frz, btn_del])
    keyboard.insert(0, [InlineKeyboardButton(text="➕ Yangi kompaniya qo'shish", callback_data="add_company_start")])
    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

@dp.message(F.text == "➕ Kompaniya qo'shish")
async def add_company_btn(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    is_super = await db.is_superadmin_session(message.from_user.id)
    if not is_super:
        await message.answer("Bu funksiya faqat superadmin uchun.")
        return
    await message.answer("Yangi kompaniya nomini kiriting:", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Asosiy menyu")]], resize_keyboard=True))
    await state.set_state(CompanyManage.waiting_for_name)

@dp.callback_query(F.data == "add_company_start")
async def add_company_start(call: CallbackQuery, state: FSMContext):
    if not await is_admin(call.from_user.id):
        return
    await call.message.answer("Yangi kompaniya nomini kiriting:", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Asosiy menyu")]], resize_keyboard=True))
    await state.set_state(CompanyManage.waiting_for_name)
    await call.answer()

@dp.message(CompanyManage.waiting_for_name)
async def company_add_name(message: Message, state: FSMContext):
    if message.text == "🔙 Asosiy menyu":
        return await back_to_main(message, state)
    await state.update_data(company_name=message.text)
    await message.answer("Bu kompaniya admini uchun LOGIN kiriting:")
    await state.set_state(CompanyManage.waiting_for_login)

@dp.message(CompanyManage.waiting_for_login)
async def company_add_login(message: Message, state: FSMContext):
    if message.text == "🔙 Asosiy menyu":
        return await back_to_main(message, state)
    accounts = await db.get_admin_accounts()
    if any(a["login"] == message.text for a in accounts):
        await message.answer("❌ Bu login allaqachon mavjud! Boshqa login kiriting:")
        return
    await state.update_data(company_login=message.text)
    await message.answer("Bu kompaniya admini uchun PAROL kiriting:")
    await state.set_state(CompanyManage.waiting_for_password)

@dp.message(CompanyManage.waiting_for_password)
async def company_add_password(message: Message, state: FSMContext):
    if message.text == "🔙 Asosiy menyu":
        return await back_to_main(message, state)
    data = await state.get_data()
    company = await db.add_company(data["company_name"], data["company_login"], message.text)
    await state.clear()
    is_super = await db.is_superadmin_session(message.from_user.id)
    await message.answer(
        f"✅ Kompaniya qo'shildi!\n\n"
        f"🏪 Nom: <b>{company['name']}</b>\n"
        f"🔑 Login: <b>{data['company_login']}</b>\n"
        f"🔒 Parol: <b>{message.text}</b>\n\n"
        f"Bu login/parol bilan kompaniya panelga kirish mumkin.",
        reply_markup=get_admin_keyboard(is_superadmin=is_super)
    )

@dp.callback_query(F.data.startswith("delcomp_"))
async def delete_company(call: CallbackQuery):
    if not await is_admin(call.from_user.id):
        return
    is_super = await db.is_superadmin_session(call.from_user.id)
    if not is_super:
        await call.answer("Ruxsat yo'q!", show_alert=True)
        return
    company_id = int(call.data.split("_")[1])
    company = await db.get_company(company_id)
    name = company["name"] if company else "?"
    await db.delete_company(company_id)
    await call.answer(f"{name} o'chirildi!")
    try: await call.message.delete()
    except: pass
    await admin_companies_list(call.message)

@dp.callback_query(F.data.startswith("frzcomp_"))
async def freeze_company(call: CallbackQuery):
    if not await is_admin(call.from_user.id):
        return
    is_super = await db.is_superadmin_session(call.from_user.id)
    if not is_super:
        await call.answer("Ruxsat yo'q!", show_alert=True)
        return
    company_id = int(call.data.split("_")[1])
    await db.toggle_company_freeze(company_id)
    await call.answer("Holat o'zgartirildi!")
    try: await call.message.delete()
    except: pass
    await admin_companies_list(call.message)

# --- ORDER CALLBACKS ---
@dp.callback_query(F.data.startswith("acc_"))
async def accept_order(call: CallbackQuery):
    if not await is_admin(call.from_user.id):
        return
    parts = call.data.split("_")
    order_id = int(parts[1])
    company_id = int(parts[2]) if len(parts) > 2 and parts[2] != "0" else None
    await db.update_order_status(order_id, "Qabul qilindi va tayyorlanmoqda", company_id=company_id)
    order = db.find_order(order_id, company_id)
    inline_keyboard = []
    if order and order.get("order_type") == "Masofaviy":
        inline_keyboard.append([InlineKeyboardButton(text="🚚 Kuryerga berish", callback_data=f"sendcour_{order_id}_{company_id or 0}")])
    admin_name = await db.get_admin_session(call.from_user.id)
    await call.message.edit_text(call.message.text + f"\n\n✅ Qabul qildi: <b>{admin_name}</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard) if inline_keyboard else None)
    await call.answer("Buyurtma qabul qilindi.")
    if order:
        try:
            order_user = await db.get_user(order["user_id"])
            lang = order_user.get("lang", "uz") if order_user else "uz"
            await bot.send_message(chat_id=order["user_id"], text=f"🎉 <b>{get_text(lang, 'order_num')} #{order_id}</b> {get_text(lang, 'order_preparing')}")
        except Exception:
            pass

@dp.callback_query(F.data.startswith("rej_"))
async def reject_order(call: CallbackQuery):
    if not await is_admin(call.from_user.id):
        return
    parts = call.data.split("_")
    order_id = int(parts[1])
    company_id = int(parts[2]) if len(parts) > 2 and parts[2] != "0" else None
    admin_name = await db.get_admin_session(call.from_user.id)
    await db.update_order_status(order_id, "Bekor qilingan", company_id=company_id)
    await call.answer("Buyurtma bekor qilindi.")
    await call.message.edit_text(call.message.text + f"\n\n❌ Bekor qildi: <b>{admin_name}</b>")
    order = db.find_order(order_id, company_id)
    if order:
        try:
            order_user = await db.get_user(order["user_id"])
            lang = order_user.get("lang", "uz") if order_user else "uz"
            await bot.send_message(chat_id=order["user_id"], text=get_text(lang, "order_rejected").format(id=order_id))
        except Exception:
            pass

@dp.callback_query(F.data.startswith("sendcour_"))
async def prompt_courier_id(call: CallbackQuery, state: FSMContext):
    parts = call.data.split("_")
    order_id = int(parts[1])
    company_id = int(parts[2]) if len(parts) > 2 and parts[2] != "0" else None
    await state.update_data(assign_order_id=order_id, assign_company_id=company_id)
    await state.set_state(AssignCourier.waiting_for_courier_id)
    await call.message.answer(f"Buyurtma #{order_id} qaysi kuryerga biriktiriladi?\nKuryer ID raqamini yozing:")
    await call.answer()

@dp.message(AssignCourier.waiting_for_courier_id)
async def assign_courier(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Faqat raqam kiriting!")
    courier_id = int(message.text)
    data = await state.get_data()
    order_id = data["assign_order_id"]
    company_id = data.get("assign_company_id")
    couriers = await db.get_couriers(company_id=company_id)
    courier = next((c for c in couriers if c["id"] == courier_id), None)
    if not courier:
        return await message.answer("Bunday ID li kuryer topilmadi!")
    order = db.find_order(order_id, company_id)
    if order:
        c_text = f"📦 <b>YANGI MASOFAVIY BUYURTMA</b>\n\n"
        c_text += f"📍 Manzil: {format_location(order['location'])}\n"
        c_text += f"📱 Mijoz tel: {order['phone']}\n"
        c_text += f"💬 Izoh: {order['comment']}\n\n"
        c_text += "🛍 <b>Mahsulotlar:</b>\n"
        for item in order["items"]:
            c_text += f"▪️ {item['name']} x {item['quantity']}\n"
        c_text += f"\n💰 Olinadigan summa: {order['total_price']:,} so'm".replace(",", " ")
        try:
            await bot.send_message(courier["telegram_id"], c_text)
            await message.answer(f"✅ Buyurtma tayyor bo'ldi va kuryer #{courier_id} ({courier['fullname']}) ga topshirildi!")
            order_user = await db.get_user(order["user_id"])
            lang = order_user.get("lang", "uz") if order_user else "uz"
            cust_text = f"✅ <b>Buyurtmangiz tayyor bo'ldi va kuryerga topshirildi!</b>\n\n"
            cust_text += f"🛵 <b>{get_text(lang, 'courier_assigned')}:</b>\n"
            cust_text += f"👤 {get_text(lang, 'name')}: {courier['fullname']}\n"
            cust_text += f"📱 {get_text(lang, 'contact_phone')} {courier['phone']}\n\n{get_text(lang, 'arriving_soon')}"
            await bot.send_message(order["user_id"], cust_text)
        except Exception as e:
            await message.answer(f"Xabar yuborishda xatolik: {e}")
    await state.clear()

# =================== COURIERS ===================
@dp.message(F.text == "🚚 Kuryerlar ma'lumotlari")
async def admin_couriers(message: Message):
    if not await is_admin(message.from_user.id): return
    company_id = await db.get_company_id_for_admin(message.from_user.id)
    is_super = await db.is_superadmin_session(message.from_user.id)
    if is_super:
        companies = await db.get_companies()
        text = "🚚 <b>Barcha kuryerlar:</b>\n\n"
        keyboard = []
        for c in companies:
            couriers = c.get("couriers", [])
            if couriers:
                text += f"🏪 <b>{c['name']}</b>:\n"
                for cur in couriers:
                    text += f"  🆔 {cur['id']} | {cur['fullname']} | {cur['phone']}\n"
                    keyboard.append([InlineKeyboardButton(text=f"❌ {cur['fullname']} ({c['name']})", callback_data=f"delcour_{cur['id']}_{c['id']}")])
                text += "\n"
        if not any(c.get("couriers") for c in companies):
            text = "Hozircha kuryerlar yo'q."
        await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard) if keyboard else None)
    else:
        couriers = await db.get_couriers(company_id=company_id)
        if not couriers:
            return await message.answer("Hozircha kuryerlar yo'q.")
        keyboard = []
        text = f"🚚 <b>Kuryerlar ({len(couriers)} ta):</b>\n\n"
        for c in couriers:
            text += f"🆔 <b>{c['id']}</b> | {c['fullname']} | {c['phone']}\n"
            keyboard.append([InlineKeyboardButton(text=f"❌ {c['fullname']} ({c['id']}) ni o'chirish", callback_data=f"delcour_{c['id']}_{company_id or 0}")])
        await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

@dp.callback_query(F.data.startswith("delcour_"))
async def admin_delete_courier(call: CallbackQuery):
    if not await is_admin(call.from_user.id): return
    parts = call.data.split("_")
    courier_id = int(parts[1])
    company_id = int(parts[2]) if len(parts) > 2 and parts[2] != "0" else None
    await db.delete_courier(courier_id, company_id=company_id)
    await call.answer("Kuryer o'chirildi!")
    await admin_couriers(call.message)

# =================== USERS ===================
@dp.message(F.text == "👥 Foydalanuvchilar")
async def admin_users(message: Message):
    if not await is_admin(message.from_user.id): return
    users = await db.get_all_users()
    text = f"👥 <b>Barcha foydalanuvchilar ({len(users)} ta):</b>\n\n"
    for u in users[:40]:
        username = f"| @{u.get('username')} " if u.get('username') else ""
        text += f"ID: {u.get('telegram_id')} | Ism: {u.get('fullname')} {username}\n"
    await message.answer(text)

# =================== BALANCE RESET ===================
@dp.message(F.text == "🔄 Balansni nolga tushirish")
async def admin_reset_revenue(message: Message):
    if not await is_admin(message.from_user.id): return
    company_id = await db.get_company_id_for_admin(message.from_user.id)
    await db.reset_revenue(company_id=company_id)
    is_super = await db.is_superadmin_session(message.from_user.id)
    await message.answer("✅ Barcha daromadlar nolga tushirildi (Archivlandi).", reply_markup=get_admin_keyboard(is_superadmin=is_super))

# =================== CONTACT SETTINGS ===================
@dp.message(F.text == "⚙️ Aloqa sozlamalari")
async def admin_update_contact_start(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    company_id = await db.get_company_id_for_admin(message.from_user.id)
    contact = await db.get_admin_contact(company_id=company_id)
    await message.answer(f"Hozirgi ism: {contact.get('name','')}\n\nYangi ismni kiriting:", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Asosiy menyu")]], resize_keyboard=True))
    await state.set_state(AdminContact.waiting_for_name)

@dp.message(AdminContact.waiting_for_name)
async def admin_update_contact_name(message: Message, state: FSMContext):
    if message.text == "🔙 Asosiy menyu": return await back_to_main(message, state)
    await state.update_data(contact_name=message.text)
    await message.answer("Yangi telefon raqamni kiriting:")
    await state.set_state(AdminContact.waiting_for_phone)

@dp.message(AdminContact.waiting_for_phone)
async def admin_update_contact_phone(message: Message, state: FSMContext):
    if message.text == "🔙 Asosiy menyu": return await back_to_main(message, state)
    await state.update_data(contact_phone=message.text)
    await message.answer("Yangi Telegram usernameni kiriting (masalan: @admin):")
    await state.set_state(AdminContact.waiting_for_username)

@dp.message(AdminContact.waiting_for_username)
async def admin_update_contact_username(message: Message, state: FSMContext):
    if message.text == "🔙 Asosiy menyu": return await back_to_main(message, state)
    data = await state.get_data()
    company_id = await db.get_company_id_for_admin(message.from_user.id)
    await db.update_admin_contact(data["contact_name"], data["contact_phone"], message.text, company_id=company_id)
    await state.clear()
    is_super = await db.is_superadmin_session(message.from_user.id)
    await message.answer("✅ Aloqa ma'lumotlari yangilandi!", reply_markup=get_admin_keyboard(is_superadmin=is_super))

# =================== ADMIN ACCOUNTS ===================
@dp.message(F.text == "👨‍💻 Adminlar")
async def admin_manage_accounts(message: Message):
    if not await is_admin(message.from_user.id): return
    is_super = await db.is_superadmin_session(message.from_user.id)
    company_id = await db.get_company_id_for_admin(message.from_user.id)
    accounts = await db.get_admin_accounts()
    text = "👨‍💻 <b>Adminlar ro'yxati:</b>\n\n"
    keyboard = []
    for acc in accounts:
        if not is_super and acc.get("company_id") != company_id:
            continue
        comp_info = ""
        if acc.get("company_id"):
            comp = await db.get_company(acc["company_id"])
            comp_info = f" [{comp['name'] if comp else '?'}]"
        role = "👑 Superadmin" if acc.get("is_superadmin") else "🏪 Kompaniya admin"
        text += f"{role}{comp_info}\n👤 {acc['name']} (Login: {acc['login']})\n\n"
        if not acc.get("is_superadmin") and is_super:
            keyboard.append([InlineKeyboardButton(text=f"❌ {acc['name']} ni o'chirish", callback_data=f"deladmin_{acc['login']}")])
    if is_super:
        keyboard.insert(0, [InlineKeyboardButton(text="➕ Yangi Admin qo'shish", callback_data="add_admin_acc")])
    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard) if keyboard else None)

@dp.callback_query(F.data == "add_admin_acc")
async def add_admin_acc_start(call: CallbackQuery, state: FSMContext):
    if not await is_admin(call.from_user.id): return
    is_super = await db.is_superadmin_session(call.from_user.id)
    if not is_super:
        await call.answer("Ruxsat yo'q!", show_alert=True)
        return
    await call.message.answer("Yangi admin uchun LOGIN kiriting:", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Asosiy menyu")]], resize_keyboard=True))
    await state.set_state(AdminManage.waiting_for_login)
    await call.answer()

@dp.message(AdminManage.waiting_for_login)
async def add_admin_login(message: Message, state: FSMContext):
    if message.text == "🔙 Asosiy menyu": return await back_to_main(message, state)
    await state.update_data(new_login=message.text)
    await message.answer("Yangi admin uchun PAROL kiriting:")
    await state.set_state(AdminManage.waiting_for_password)

@dp.message(AdminManage.waiting_for_password)
async def add_admin_password(message: Message, state: FSMContext):
    if message.text == "🔙 Asosiy menyu": return await back_to_main(message, state)
    await state.update_data(new_pass=message.text)
    await message.answer("Adminning ismini kiriting:")
    await state.set_state(AdminManage.waiting_for_name)

@dp.message(AdminManage.waiting_for_name)
async def add_admin_name(message: Message, state: FSMContext):
    if message.text == "🔙 Asosiy menyu": return await back_to_main(message, state)
    data = await state.get_data()
    await db.add_admin_account(data["new_login"], data["new_pass"], message.text, is_superadmin=False)
    await state.clear()
    is_super = await db.is_superadmin_session(message.from_user.id)
    await message.answer(f"✅ Yangi admin qo'shildi!\nLogin: {data['new_login']}\nParol: {data['new_pass']}", reply_markup=get_admin_keyboard(is_superadmin=is_super))

@dp.callback_query(F.data.startswith("deladmin_"))
async def delete_admin_acc(call: CallbackQuery):
    if not await is_admin(call.from_user.id): return
    login = call.data.split("_", 1)[1]
    await db.remove_admin_account(login)
    await call.answer("Admin o'chirildi.")
    await admin_manage_accounts(call.message)

# =================== CATEGORIES ===================
@dp.message(F.text == "🏷 Kategoriyalar")
async def admin_manage_categories(message: Message):
    if not await is_admin(message.from_user.id): return
    company_id = await db.get_company_id_for_admin(message.from_user.id)
    cats = await db.get_categories(company_id=company_id)
    text = "🏷 <b>Mavjud Kategoriyalar:</b>\n\n"
    keyboard = []
    for c in cats:
        text += f"▪️ {c}\n"
        keyboard.append([InlineKeyboardButton(text=f"❌ {c} ni o'chirish", callback_data=f"delcat_{c}")])
    keyboard.insert(0, [InlineKeyboardButton(text="➕ Kategoriya qo'shish", callback_data="add_cat_start")])
    await message.answer(text or "Kategoriyalar yo'q.", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

@dp.callback_query(F.data == "add_cat_start")
async def add_cat_start(call: CallbackQuery, state: FSMContext):
    if not await is_admin(call.from_user.id): return
    await call.message.answer("Yangi kategoriya nomini kiriting:", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Asosiy menyu")]], resize_keyboard=True))
    await state.set_state(CategoryManage.waiting_for_new_category)
    await call.answer()

@dp.message(CategoryManage.waiting_for_new_category)
async def add_cat_finish(message: Message, state: FSMContext):
    if message.text == "🔙 Asosiy menyu": return await back_to_main(message, state)
    company_id = await db.get_company_id_for_admin(message.from_user.id)
    await db.add_category(message.text, company_id=company_id)
    await state.clear()
    is_super = await db.is_superadmin_session(message.from_user.id)
    await message.answer(f"✅ Kategoriya qo'shildi: {message.text}", reply_markup=get_admin_keyboard(is_superadmin=is_super))

@dp.callback_query(F.data.startswith("delcat_"))
async def delete_cat(call: CallbackQuery):
    if not await is_admin(call.from_user.id): return
    cat = call.data.split("_", 1)[1]
    company_id = await db.get_company_id_for_admin(call.from_user.id)
    await db.remove_category(cat, company_id=company_id)
    await call.answer("Kategoriya o'chirildi.")
    await admin_manage_categories(call.message)

# =================== PRODUCTS ===================
@dp.message(F.text == "➕ MENU qo'shish")
async def admin_add_product_start(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    await message.answer("🍔 Yangi mahsulot nomini kiriting:", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Asosiy menyu")]], resize_keyboard=True))
    await state.set_state(AddProduct.waiting_for_name)

@dp.message(AddProduct.waiting_for_name)
async def add_product_name(message: Message, state: FSMContext):
    if message.text == "🔙 Asosiy menyu": return await back_to_main(message, state)
    await state.update_data(name=message.text)
    company_id = await db.get_company_id_for_admin(message.from_user.id)
    categories = await db.get_categories(company_id=company_id)
    kb_buttons = []
    row = []
    for cat in categories:
        row.append(KeyboardButton(text=cat))
        if len(row) == 2:
            kb_buttons.append(row)
            row = []
    if row: kb_buttons.append(row)
    kb_buttons.append([KeyboardButton(text="🔙 Asosiy menyu")])
    await message.answer("Kategoriyani tanlang:", reply_markup=ReplyKeyboardMarkup(keyboard=kb_buttons, resize_keyboard=True))
    await state.set_state(AddProduct.waiting_for_category)

@dp.message(AddProduct.waiting_for_category)
async def add_product_category(message: Message, state: FSMContext):
    if message.text == "🔙 Asosiy menyu": return await back_to_main(message, state)
    await state.update_data(category=message.text)
    await message.answer("📝 Mahsulot tavsifini yozing:", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Asosiy menyu")]], resize_keyboard=True))
    await state.set_state(AddProduct.waiting_for_desc)

@dp.message(AddProduct.waiting_for_desc)
async def add_product_desc(message: Message, state: FSMContext):
    if message.text == "🔙 Asosiy menyu": return await back_to_main(message, state)
    await state.update_data(desc=message.text)
    await message.answer("💰 Narxini kiriting (raqamda):")
    await state.set_state(AddProduct.waiting_for_price)

@dp.message(AddProduct.waiting_for_price)
async def add_product_price(message: Message, state: FSMContext):
    if message.text == "🔙 Asosiy menyu": return await back_to_main(message, state)
    price_text = message.text.replace(" ", "").replace(",", "").replace(".", "")
    if not price_text.isdigit(): return await message.answer("Faqat raqam kiriting!")
    await state.update_data(price=int(price_text))
    await message.answer("🖼 Mahsulot rasmini yuboring (yoki URL link bering):")
    await state.set_state(AddProduct.waiting_for_image)

@dp.message(AddProduct.waiting_for_image)
async def add_product_image(message: Message, state: FSMContext):
    if message.text == "🔙 Asosiy menyu": return await back_to_main(message, state)
    data = await state.get_data()
    import os
    image_url = ""
    if message.photo:
        file_id = message.photo[-1].file_id
        file = await bot.get_file(file_id)
        os.makedirs("images", exist_ok=True)
        file_path = f"images/{file_id}.jpg"
        await bot.download_file(file.file_path, file_path)
        image_url = f"images/{file_id}.jpg"
    elif message.document:
        ext = os.path.splitext(message.document.file_name)[1].lower() if message.document.file_name else ".png"
        if message.document.mime_type and message.document.mime_type.startswith("image/") or ext in [".jpg",".jpeg",".png",".webp"]:
            file_id = message.document.file_id
            file = await bot.get_file(file_id)
            os.makedirs("images", exist_ok=True)
            file_path = f"images/{file_id}{ext}"
            await bot.download_file(file.file_path, file_path)
            image_url = f"images/{file_id}{ext}"
        else:
            return await message.answer("Noto'g'ri rasm formati!")
    elif message.text and message.text.startswith("http"):
        image_url = message.text
    else:
        return await message.answer("Rasm yoki URL link bering!")
    company_id = await db.get_company_id_for_admin(message.from_user.id)
    await db.add_product(data["name"], data["desc"], data["price"], category=data["category"], image=image_url, company_id=company_id)
    await state.clear()
    is_super = await db.is_superadmin_session(message.from_user.id)
    await message.answer("✅ Mahsulot qo'shildi!", reply_markup=get_admin_keyboard(is_superadmin=is_super))

@dp.message(F.text == "📝 O'chirish / Tahrirlash")
async def admin_edit_products(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    await state.update_data(edited_products=[])
    company_id = await db.get_company_id_for_admin(message.from_user.id)
    cats = await db.get_categories(company_id=company_id)
    keyboard = [[InlineKeyboardButton(text="📋 Barchasi", callback_data="editcat_all")]]
    for c in cats:
        keyboard.append([InlineKeyboardButton(text=f"📂 {c}", callback_data=f"editcat_{c}")])
    await message.answer("Kategoriyani tanlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

@dp.callback_query(F.data == "editcats_back")
async def admin_edit_cats_back(call: CallbackQuery, state: FSMContext):
    if not await is_admin(call.from_user.id): return
    company_id = await db.get_company_id_for_admin(call.from_user.id)
    cats = await db.get_categories(company_id=company_id)
    keyboard = [[InlineKeyboardButton(text="📋 Barchasi", callback_data="editcat_all")]]
    for c in cats: keyboard.append([InlineKeyboardButton(text=f"📂 {c}", callback_data=f"editcat_{c}")])
    await call.message.edit_text("Kategoriyani tanlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

@dp.callback_query(F.data.startswith("editcat_"))
async def admin_show_category_products(call: CallbackQuery, state: FSMContext):
    if not await is_admin(call.from_user.id): return
    cat = call.data.split("_", 1)[1]
    await state.update_data(current_edit_cat=cat)
    company_id = await db.get_company_id_for_admin(call.from_user.id)
    if company_id:
        company = await db.get_company(company_id)
        all_products = company.get("products", []) if company else []
    else:
        all_products = getattr(db, "products", [])
    cat_products = all_products if cat == "all" else [p for p in all_products if p.get("category") == cat]
    display_cat_name = "Barchasi" if cat == "all" else cat
    if not cat_products:
        return await call.answer("Bu kategoriyada mahsulotlar yo'q!", show_alert=True)
    data = await state.get_data()
    edited_products = data.get("edited_products", [])
    keyboard = []
    for p in cat_products:
        status = "✅" if p.get("is_active", 1) else "❌"
        edit_mark = "✏️ " if p["id"] in edited_products else ""
        keyboard.append([InlineKeyboardButton(text=f"{edit_mark}{status} {p['name']}", callback_data=f"prodmanage_{p['id']}")])
    keyboard.append([InlineKeyboardButton(text="🔙 Kategoriyalarga qaytish", callback_data="editcats_back")])
    await call.message.edit_text(f"📂 <b>{display_cat_name}</b> bo'limidagi mahsulotlar:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

@dp.callback_query(F.data.startswith("prodmanage_"))
async def admin_manage_product_options(call: CallbackQuery, state: FSMContext):
    if not await is_admin(call.from_user.id): return
    product_id = int(call.data.split("_")[1])
    company_id = await db.get_company_id_for_admin(call.from_user.id)
    if company_id:
        company = await db.get_company(company_id)
        products = company.get("products", []) if company else []
    else:
        products = db.products
    product = next((p for p in products if p["id"] == product_id), None)
    if not product: return await call.answer("Mahsulot topilmadi!")
    data = await state.get_data()
    back_cat = data.get("current_edit_cat", product.get("category", "Boshqa"))
    status_text = "Vaqtinchalik O'chirish" if product.get("is_active", 1) else "Vaqtinchalik Yoqish"
    keyboard = [
        [InlineKeyboardButton(text=f"👁 {status_text}", callback_data=f"del_{product_id}")],
        [InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"editprod_{product_id}")],
        [InlineKeyboardButton(text="🗑 Butunlay o'chirish", callback_data=f"harddel_{product_id}")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"editcat_{back_cat}")]
    ]
    status_display = "✅ Faol" if product.get("is_active", 1) else "❌ O'chirilgan"
    price_val = product.get("price") or 0
    await call.message.edit_text(f"🍔 <b>{product['name']}</b>\n💰 {price_val:,} so'm\n📊 {status_display}".replace(",", " "), reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

@dp.callback_query(F.data.startswith("del_"))
async def admin_toggle_product(call: CallbackQuery, state: FSMContext):
    if not await is_admin(call.from_user.id): return
    product_id = int(call.data.split("_")[1])
    company_id = await db.get_company_id_for_admin(call.from_user.id)
    await db.toggle_product(product_id, company_id=company_id)
    await call.answer("Holati o'zgartirildi!")
    await admin_manage_product_options(call, state)

@dp.callback_query(F.data.startswith("harddel_"))
async def admin_hard_delete_product(call: CallbackQuery):
    if not await is_admin(call.from_user.id): return
    product_id = int(call.data.split("_")[1])
    company_id = await db.get_company_id_for_admin(call.from_user.id)
    await db.delete_product(product_id, company_id=company_id)
    await call.answer("Butunlay o'chirildi!")
    await call.message.delete()

@dp.callback_query(F.data.startswith("editprod_"))
async def admin_edit_product_start(call: CallbackQuery, state: FSMContext):
    if not await is_admin(call.from_user.id): return
    product_id = int(call.data.split("_")[1])
    await state.update_data(edit_product_id=product_id)
    await call.message.answer("📝 Yangi tavsif yozing (o'zgartirmaslik uchun 'O'tkazib yuborish'):", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="⏩ O'tkazib yuborish")], [KeyboardButton(text="🔙 Asosiy menyu")]], resize_keyboard=True))
    await state.set_state(EditProduct.waiting_for_desc)

@dp.message(EditProduct.waiting_for_desc)
async def admin_edit_product_desc(message: Message, state: FSMContext):
    if message.text == "🔙 Asosiy menyu": return await back_to_main(message, state)
    await state.update_data(edit_desc=None if message.text == "⏩ O'tkazib yuborish" else message.text)
    await message.answer("✏️ Yangi narxni kiriting (yoki 'O'tkazib yuborish'):", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="⏩ O'tkazib yuborish")], [KeyboardButton(text="🔙 Asosiy menyu")]], resize_keyboard=True))
    await state.set_state(EditProduct.waiting_for_price)

@dp.message(EditProduct.waiting_for_price)
async def admin_edit_product_price(message: Message, state: FSMContext):
    if message.text == "🔙 Asosiy menyu": return await back_to_main(message, state)
    if message.text != "⏩ O'tkazib yuborish":
        price_text = message.text.replace(" ", "").replace(",", "").replace(".", "")
        if not price_text.isdigit(): return await message.answer("Faqat raqam kiriting!")
        await state.update_data(edit_price=int(price_text))
    else:
        await state.update_data(edit_price=None)
    await message.answer("🖼 Yangi rasmni yuboring (yoki 'O'tkazib yuborish'):", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="⏩ O'tkazib yuborish")], [KeyboardButton(text="🔙 Asosiy menyu")]], resize_keyboard=True))
    await state.set_state(EditProduct.waiting_for_image)

@dp.message(EditProduct.waiting_for_image)
async def admin_edit_product_image(message: Message, state: FSMContext):
    if message.text == "🔙 Asosiy menyu": return await back_to_main(message, state)
    data = await state.get_data()
    product_id = data["edit_product_id"]
    new_price = data.get("edit_price")
    new_desc = data.get("edit_desc")
    import os
    image_url = ""
    if message.text == "⏩ O'tkazib yuborish": pass
    elif message.photo:
        file_id = message.photo[-1].file_id
        file = await bot.get_file(file_id)
        os.makedirs("images", exist_ok=True)
        await bot.download_file(file.file_path, f"images/{file_id}.jpg")
        image_url = f"images/{file_id}.jpg"
    elif message.document:
        ext = os.path.splitext(message.document.file_name)[1].lower() if message.document.file_name else ".png"
        if message.document.mime_type and message.document.mime_type.startswith("image/") or ext in [".jpg",".jpeg",".png",".webp"]:
            file_id = message.document.file_id
            file = await bot.get_file(file_id)
            os.makedirs("images", exist_ok=True)
            await bot.download_file(file.file_path, f"images/{file_id}{ext}")
            image_url = f"images/{file_id}{ext}"
    elif message.text and message.text.startswith("http"):
        image_url = message.text
    else:
        return await message.answer("Noto'g'ri! Rasm yoki URL bering, yoki 'O'tkazib yuborish'.")
    company_id = await db.get_company_id_for_admin(message.from_user.id)
    await db.edit_product(product_id, new_price=new_price, new_image=image_url, new_desc=new_desc, company_id=company_id)
    await state.set_state(None)
    is_super = await db.is_superadmin_session(message.from_user.id)
    await message.answer("✅ Mahsulot tahrirlandi!", reply_markup=get_admin_keyboard(is_superadmin=is_super))

# =================== BROADCAST ===================
@dp.message(F.text == "📢 Reklama tarqatish")
async def admin_broadcast_start(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    await message.answer("Reklama materialini yuboring (Matn, Rasm, Video yoki Audio - hammasi qo'llab-quvvatlanadi):")
    await state.set_state(Broadcast.waiting_for_message)

@dp.message(Broadcast.waiting_for_message)
async def admin_broadcast_send(message: Message, state: FSMContext):
    users = await db.get_all_users()
    count = 0
    for u in users:
        try:
            await bot.copy_message(chat_id=u.get("telegram_id"), from_chat_id=message.chat.id, message_id=message.message_id)
            count += 1
        except Exception: pass
    await state.clear()
    is_super = await db.is_superadmin_session(message.from_user.id)
    await message.answer(f"✅ {count} ta foydalanuvchiga yuborildi!", reply_markup=get_admin_keyboard(is_superadmin=is_super))

# =================== WEBSITE UPDATE ===================
@dp.message(F.text == "🔄 Saytni yangilash")
async def update_website_data(message: Message):
    if not await is_admin(message.from_user.id): return
    try:
        db.export_webapp_products()
        await message.answer("✅ Sayt ma'lumotlari yangilandi!")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")

# =================== ANALYTICS ===================
@dp.message(F.text == "📊 Analiz")
async def admin_analiz_start(message: Message):
    if not await is_admin(message.from_user.id): return
    months = ["Yanvar","Fevral","Mart","Aprel","May","Iyun","Iyul","Avgust","Sentabr","Oktabr","Noyabr","Dekabr"]
    keyboard = []
    row = []
    for i, m in enumerate(months):
        row.append(InlineKeyboardButton(text=m, callback_data=f"analiz_m_{i+1}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row: keyboard.append(row)
    await message.answer("📊 Qaysi oyni analiz qilmoqchisiz?", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

@dp.callback_query(F.data.startswith("analiz_m_"))
async def admin_analiz_month(call: CallbackQuery):
    if not await is_admin(call.from_user.id): return
    month = int(call.data.split("_")[2])
    months = ["Yanvar","Fevral","Mart","Aprel","May","Iyun","Iyul","Avgust","Sentabr","Oktabr","Noyabr","Dekabr"]
    month_name = months[month-1]
    keyboard = [
        [InlineKeyboardButton(text="1-hafta (1-7)", callback_data=f"analiz_p_{month}_w1"), InlineKeyboardButton(text="2-hafta (8-14)", callback_data=f"analiz_p_{month}_w2")],
        [InlineKeyboardButton(text="3-hafta (15-21)", callback_data=f"analiz_p_{month}_w3"), InlineKeyboardButton(text="4-hafta (22+)", callback_data=f"analiz_p_{month}_w4")],
        [InlineKeyboardButton(text="1-10 kunlik", callback_data=f"analiz_p_{month}_t1")],
        [InlineKeyboardButton(text="11-20 kunlik", callback_data=f"analiz_p_{month}_t2")],
        [InlineKeyboardButton(text="21+ kunlik", callback_data=f"analiz_p_{month}_t3")],
        [InlineKeyboardButton(text="🔙 Oylarga qaytish", callback_data="analiz_back_m")]
    ]
    await call.message.edit_text(f"📊 <b>{month_name}</b> uchun davr tanlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

@dp.callback_query(F.data == "analiz_back_m")
async def admin_analiz_back(call: CallbackQuery):
    if not await is_admin(call.from_user.id): return
    months = ["Yanvar","Fevral","Mart","Aprel","May","Iyun","Iyul","Avgust","Sentabr","Oktabr","Noyabr","Dekabr"]
    keyboard = []
    row = []
    for i, m in enumerate(months):
        row.append(InlineKeyboardButton(text=m, callback_data=f"analiz_m_{i+1}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row: keyboard.append(row)
    await call.message.edit_text("📊 Qaysi oyni analiz qilmoqchisiz?", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

@dp.callback_query(F.data.startswith("analiz_p_"))
async def admin_analiz_result(call: CallbackQuery):
    if not await is_admin(call.from_user.id): return
    parts = call.data.split("_")
    month = int(parts[2])
    period = parts[3]
    months = ["Yanvar","Fevral","Mart","Aprel","May","Iyun","Iyul","Avgust","Sentabr","Oktabr","Noyabr","Dekabr"]
    month_name = months[month-1]
    if period == "w1": p_text, p_func = "1-hafta", lambda d: 1<=d<=7
    elif period == "w2": p_text, p_func = "2-hafta", lambda d: 8<=d<=14
    elif period == "w3": p_text, p_func = "3-hafta", lambda d: 15<=d<=21
    elif period == "w4": p_text, p_func = "4-hafta", lambda d: d>=22
    elif period == "t1": p_text, p_func = "1-10 kun", lambda d: 1<=d<=10
    elif period == "t2": p_text, p_func = "11-20 kun", lambda d: 11<=d<=20
    elif period == "t3": p_text, p_func = "21+ kun", lambda d: d>=21
    else: return

    company_id = await db.get_company_id_for_admin(call.from_user.id)
    if company_id:
        company = await db.get_company(company_id)
        orders = company.get("orders", []) if company else []
    else:
        orders = db.orders

    from collections import defaultdict
    product_counts = defaultdict(int)
    for o in orders:
        if o.get("status") == "Bekor qilingan": continue
        date_str = o.get("created_at", "")
        if not date_str: continue
        try:
            d_str, m_str, _ = date_str.split(" ")[0].split(".")
            d, m = int(d_str), int(m_str)
            if m == month and p_func(d):
                for item in o.get("items", []):
                    product_counts[item["name"]] += int(item["quantity"])
        except Exception: continue

    if not product_counts:
        return await call.answer("Bunday davr uchun xaridlar topilmadi!", show_alert=True)

    sorted_products = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)
    text = f"📊 <b>Analiz: {month_name} / {p_text}</b>\n\n"
    text += "📈 <b>Eng ko'p sotilgan:</b>\n"
    for p_name, p_qty in sorted_products[:5]:
        text += f"▪️ {p_name} — {p_qty} ta\n"
    shown = set(p[0] for p in sorted_products[:5])
    bottom = [(n,q) for n,q in reversed(sorted_products) if n not in shown][:5]
    if bottom:
        text += "\n📉 <b>Eng kam sotilgan:</b>\n"
        for p_name, p_qty in reversed(bottom):
            text += f"▪️ {p_name} — {p_qty} ta\n"
    text += f"\n<i>Jami: {len(sorted_products)} xil mahsulot sotilgan.</i>"
    keyboard = [[InlineKeyboardButton(text="🔙 Oylarga qaytish", callback_data="analiz_back_m")]]
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

# =================== WEB SERVER ===================
async def start_webapp():
    from aiohttp import web
    import os

    webapp_dir = os.path.dirname(os.path.abspath(__file__))

    async def index_handler(request):
        index_file = os.path.join(webapp_dir, "index.html")
        if os.path.exists(index_file):
            return web.FileResponse(index_file)
        return web.Response(text="Bot is running!", content_type="text/html")

    async def health_handler(request):
        return web.Response(text="OK")

    async def static_file_handler(request):
        filename = request.match_info.get("filename", "")
        allowed_files = ["app.js", "style.css", "products.json"]
        if filename in allowed_files:
            file_path = os.path.join(webapp_dir, filename)
            if os.path.exists(file_path):
                return web.FileResponse(file_path)
        return web.Response(status=404)

    async def api_checkout_handler(request):
        pass # Not used directly like this since it conflicts with aiohttp routing if not correctly setup. 
             # We define it inline here.

    app = web.Application()
    app.router.add_get("/health", health_handler)
    app.router.add_get("/", index_handler)
    app.router.add_get("/{filename}", static_file_handler)
    
    images_dir = os.path.join(webapp_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    app.router.add_static("/images", images_dir)

    async def api_checkout(request):
        try:
            data = await request.json()
            user_id = int(data.get("user_id", 0))
            items = data.get("items", [])
            company_id = data.get("company_id")
            if company_id: company_id = int(company_id)
            if not items or not user_id:
                return web.json_response({"status": "error", "message": "Bo'sh savat yoki user topilmadi"})
            user = await db.get_user(user_id)
            lang = user.get("lang", "uz") if user else "uz"
            db_products = await db.get_products(company_id=company_id)
            product_dict = {p["id"]: p["price"] for p in db_products}
            total = 0
            for item in items:
                real_price = product_dict.get(int(item["id"]), item.get("price", 0))
                if real_price is None: real_price = 0
                item["price"] = real_price
                total += real_price * int(item["quantity"])
                
            from aiogram.fsm.storage.base import StorageKey
            state = FSMContext(
                storage=dp.storage,
                key=StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
            )
            await state.update_data(items=items, total=total, company_id=company_id)
            state_data = await state.get_data()
            order_type = state_data.get("order_type")
            
            if not order_type:
                await bot.send_message(user_id, get_text(lang, "cart_accepted"), reply_markup=ReplyKeyboardMarkup(
                    keyboard=[[KeyboardButton(text=get_text(lang, "masofaviy"))]],
                    resize_keyboard=True
                ))
                await state.set_state(OrderFlow.waiting_for_type_after_checkout)
            else:
                text = f"🛍 <b>{get_text(lang, 'you_selected')}</b>\n\n"
                for item in items:
                    text += f"▪️ {item['name']} x {item['quantity']} = {item['price'] * item['quantity']:,} so'm\n".replace(",", " ")
                text += f"\n💰 <b>{get_text(lang, 'total')}:</b> {total:,} so'm\n\n".replace(",", " ")
                text += get_text(lang, "phone_prompt")
                await bot.send_message(user_id, text, reply_markup=get_contact_keyboard(lang))
                await state.set_state(OrderFlow.waiting_for_phone)
                
            return web.json_response({"status": "ok"})
        except Exception as e:
            print("API Checkout Error:", e)
            return web.json_response({"status": "error", "message": str(e)}, status=500)

    app.router.add_post("/api/checkout", api_checkout)

    runner = web.AppRunner(app)
    await runner.setup()
    port_str = os.environ.get("PORT")
    if port_str:
        port = int(port_str)
    else:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            port = s.getsockname()[1]
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"[WEB] Server {port}-portda ishga tushdi")
    return runner, port

localtunnel_process = None

async def auto_start_localtunnel(port):
    global WEBAPP_URL, localtunnel_process
    print(f"\n[*] LocalTunnel ishga tushirilmoqda (Port: {port})...")
    try:
        localtunnel_process = await asyncio.create_subprocess_shell(
            f"npx localtunnel --port {port}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        while True:
            line = await localtunnel_process.stdout.readline()
            if not line: break
            text = line.decode("utf-8").strip()
            if "your url is:" in text:
                url = text.split("your url is:")[1].strip()
                print(f"✅ URL: {url}\n")
                WEBAPP_URL = url
                break
    except Exception as e:
        print(f"❌ LocalTunnel xatosi: {e}")

async def main():
    await db.connect()
    runner = None
    try:
        logging.info("Bot ishga tushmoqda...")
        await bot.delete_webhook(drop_pending_updates=True)
        runner, port = await start_webapp()
        if not os.environ.get("PORT"):
            await auto_start_localtunnel(port)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logging.error(f"Xatolik: {e}")
    finally:
        logging.info("Xavfsiz to'xtatish...")
        await bot.session.close()
        await db.close()
        if runner:
            await runner.cleanup()
        if localtunnel_process:
            try: localtunnel_process.terminate()
            except: pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi.")
