import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

BOT_TOKEN = "8217609395:AAHjIfMTf9P_uo2KK-swfqECzI61Rq5eLCw"

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


class CreatePost(StatesGroup):
    waiting_for_chat_id = State()
    waiting_for_text = State()
    waiting_for_format = State()
    waiting_for_photo = State()
    waiting_for_button_count = State()
    waiting_for_button_text = State()
    waiting_for_button_url = State()
    waiting_for_confirm = State()


@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Создать сообщение", callback_data="create")],
        [InlineKeyboardButton(text="Отменить создание", callback_data="cancel")]
    ])
    
    await message.answer(
        "👋 <b>Привет! Я бот для создания кастомных переходников.</b>\n\n"
        "Нажми кнопку ниже чтобы начать создание сообщения.",
        reply_markup=keyboard
    )


@dp.message(Command("create"))
async def cmd_create(message: Message, state: FSMContext):
    await message.answer(
        "📝 <b>Начинаем создание сообщения!</b>\n\n"
        "Шаг 1/7: Введи ID канала куда отправить сообщение.\n\n"
        "Примеры:\n"
        "• <code>-1001234567890</code> (для каналов)\n"
        "• <code>@username</code> (если канал публичный)\n\n"
        "💡 ID канала можно узнать через @myidbot - добавь бота в канал и он покажет ID."
    )
    await state.set_state(CreatePost.waiting_for_chat_id)


@dp.callback_query(F.data == "create")
async def callback_create(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        "📝 <b>Начинаем создание сообщения!</b>\n\n"
        "Шаг 1/7: Введи ID канала куда отправить сообщение.\n\n"
        "Примеры:\n"
        "• <code>-1001234567890</code> (для каналов)\n"
        "• <code>@username</code> (если канал публичный)\n\n"
        "💡 ID канала можно узнать через @myidbot - добавь бота в канал и он покажет ID."
    )
    await state.set_state(CreatePost.waiting_for_chat_id)


@dp.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нечего отменять.")
        return
    
    await state.clear()
    await message.answer("✅ Создание сообщения отменено.")


@dp.callback_query(F.data == "cancel")
async def callback_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    current_state = await state.get_state()
    if current_state is None:
        await callback.message.answer("Нечего отменять.")
        return
    
    await state.clear()
    await callback.message.answer("✅ Создание сообщения отменено.")


@dp.message(CreatePost.waiting_for_chat_id)
async def process_chat_id(message: Message, state: FSMContext):
    chat_id = message.text.strip()
    

    if not (chat_id.startswith('-') or chat_id.startswith('@')):
        await message.answer(
            "❌ Неверный формат ID!\n\n"
            "ID должен начинаться с '-' (например: -1001234567890)\n"
            "или с '@' (например: @channel_name)"
        )
        return
    
    await state.update_data(chat_id=chat_id)
    

    skip_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пропустить", callback_data="skip_text")]
    ])
    
    await message.answer(
        "✅ ID канала сохранен!\n\n"
        "Шаг 2/7: Теперь отправь текст сообщения.\n\n"
        "Просто напиши текст который будет в сообщении.\n\n"
        "Или нажми кнопку ниже если текст не нужен.",
        reply_markup=skip_keyboard
    )
    await state.set_state(CreatePost.waiting_for_text)


@dp.message(CreatePost.waiting_for_text)
async def process_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer(
        "✅ Текст сохранен!\n\n"
        "Шаг 3/7: Выбери оформление текста.\n\n"
        "Варианты:\n"
        "1️⃣ - Только жирный шрифт\n"
        "2️⃣ - Жирный шрифт + цитата\n"
        "3️⃣ - Обычный текст (без форматирования)\n\n"
        "Отправь номер (1, 2 или 3)"
    )
    await state.set_state(CreatePost.waiting_for_format)



@dp.callback_query(F.data == "skip_text")
async def callback_skip_text(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(text=None, format='normal')
    await callback.message.answer(
        "✅ Текст пропущен!\n\n"
        "Шаг 4/7: Отправь фото для сообщения.\n\n"
        "Просто отправь фотографию файлом или картинкой."
    )
    await state.set_state(CreatePost.waiting_for_photo)


@dp.message(CreatePost.waiting_for_format)
async def process_format(message: Message, state: FSMContext):
    format_choice = message.text.strip()
    
    if format_choice not in ['1', '2', '3']:
        await message.answer("❌ Введи 1, 2 или 3!")
        return
    
    format_map = {
        '1': 'bold',
        '2': 'quote_bold',
        '3': 'normal'
    }
    
    await state.update_data(format=format_map[format_choice])
    await message.answer(
        "✅ Оформление выбрано!\n\n"
        "Шаг 4/7: Отправь фото для сообщения.\n\n"
        "Просто отправь фотографию файлом или картинкой."
    )
    await state.set_state(CreatePost.waiting_for_photo)


@dp.message(CreatePost.waiting_for_photo, F.photo)
async def process_photo(message: Message, state: FSMContext):

    photo_id = message.photo[-1].file_id
    await state.update_data(photo=photo_id)
    
    await message.answer(
        "✅ Фото сохранено!\n\n"
        "Шаг 5/7: Сколько кнопок нужно добавить?\n\n"
        "Выбери количество (от 1 до 4):\n"
        "1️⃣ - Одна кнопка\n"
        "2️⃣ - Две кнопки\n"
        "3️⃣ - Три кнопки\n"
        "4️⃣ - Четыре кнопки\n\n"
        "Отправь номер (1, 2, 3 или 4)"
    )
    await state.set_state(CreatePost.waiting_for_button_count)


@dp.message(CreatePost.waiting_for_photo)
async def process_photo_error(message: Message, state: FSMContext):
    await message.answer("❌ Пожалуйста, отправь фото!")


@dp.message(CreatePost.waiting_for_button_count)
async def process_button_count(message: Message, state: FSMContext):
    count = message.text.strip()
    
    if count not in ['1', '2', '3', '4']:
        await message.answer("❌ Введи число от 1 до 4!")
        return
    
    button_count = int(count)
    await state.update_data(button_count=button_count, buttons=[], current_button=1)
    
    await message.answer(
        f"✅ Будет создано кнопок: {button_count}\n\n"
        f"Шаг 6/7: Кнопка 1 из {button_count}\n\n"
        "Что должно быть написано на кнопке?\n\n"
        "Например: 'Перейти в канал' или '📢 Подписаться'"
    )
    await state.set_state(CreatePost.waiting_for_button_text)


@dp.message(CreatePost.waiting_for_button_text)
async def process_button_text(message: Message, state: FSMContext):
    data = await state.get_data()
    button_count = data['button_count']
    current_button = data['current_button']
    
    await state.update_data(current_button_text=message.text)
    
    await message.answer(
        f"✅ Текст кнопки {current_button} сохранен!\n\n"
        f"Теперь введи ссылку для кнопки {current_button}.\n\n"
        "Например: https://t.me/your_channel"
    )
    await state.set_state(CreatePost.waiting_for_button_url)


@dp.message(CreatePost.waiting_for_button_url)
async def process_button_url(message: Message, state: FSMContext):
    url = message.text.strip()
    

    if not url.startswith('http://') and not url.startswith('https://'):
        await message.answer(
            "❌ Ссылка должна начинаться с http:// или https://\n\n"
            "Например: https://t.me/channel"
        )
        return
    
    data = await state.get_data()
    buttons = data.get('buttons', [])
    current_button = data['current_button']
    button_count = data['button_count']
    current_button_text = data['current_button_text']
    
    buttons.append({'text': current_button_text, 'url': url})
    

    if current_button < button_count:
        next_button = current_button + 1
        await state.update_data(buttons=buttons, current_button=next_button)
        
        await message.answer(
            f"✅ Кнопка {current_button} сохранена!\n\n"
            f"Шаг 6/7: Кнопка {next_button} из {button_count}\n\n"
            "Что должно быть написано на кнопке?\n\n"
            "Например: 'Перейти в канал' или '📢 Подписаться'"
        )
        await state.set_state(CreatePost.waiting_for_button_text)
    else:

        await state.update_data(buttons=buttons)
        

        data = await state.get_data()
        
  
        buttons_preview = "\n".join([f"• <b>{btn['text']}</b> → {btn['url']}" for btn in buttons])
        
        text_info = f"<b>Текст:</b> {data.get('text', 'Без текста')}\n<b>Оформление:</b> {data.get('format', 'normal')}\n" if data.get('text') else "<b>Текст:</b> Без текста\n"
        
        preview_text = (
            "📋 <b>Предварительный просмотр:</b>\n\n"
            f"<b>Канал:</b> <code>{data['chat_id']}</code>\n"
            f"{text_info}"
            f"<b>Количество кнопок:</b> {button_count}\n\n"
            f"<b>Кнопки:</b>\n{buttons_preview}\n\n"
            "Отправить сообщение?\n"
            "Напиши <b>да</b> для отправки или <b>нет</b> для отмены."
        )
        
        await message.answer(preview_text)
        await state.set_state(CreatePost.waiting_for_confirm)


@dp.message(CreatePost.waiting_for_confirm)
async def process_confirm(message: Message, state: FSMContext):
    answer = message.text.strip().lower()
    
    if answer not in ['да', 'yes', 'lf']:
        await state.clear()
        await message.answer("❌ Отправка отменена. Используй /create для создания нового сообщения.")
        return
    
    data = await state.get_data()
    
    text = data.get('text')
    if text:
        format_type = data['format']
        
        if format_type == 'bold':
            formatted_text = f"<b>{text}</b>"
        elif format_type == 'quote_bold':
            formatted_text = f"<blockquote><b>{text}</b></blockquote>"
        else:
            formatted_text = text
    else:
        formatted_text = None
    
    buttons = data['buttons']
    keyboard_buttons = [[InlineKeyboardButton(text=btn['text'], url=btn['url'])] for btn in buttons]
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    try:
 
        if formatted_text:
            await bot.send_photo(
                chat_id=data['chat_id'],
                photo=data['photo'],
                caption=formatted_text,
                reply_markup=keyboard
            )
        else:
            await bot.send_photo(
                chat_id=data['chat_id'],
                photo=data['photo'],
                reply_markup=keyboard
            )
        
        await message.answer("✅ Сообщение успешно отправлено!\n\nИспользуй /create для создания нового сообщения.")
        await state.clear()
        
    except Exception as e:
        await message.answer(
            f"❌ Ошибка при отправке:\n<code>{e}</code>\n\n"
            "Возможные причины:\n"
            "• Бот не является администратором канала\n"
            "• Неверный ID канала\n"
            "• Нет прав на отправку сообщений\n\n"
            "Используй /create чтобы попробовать снова."
        )
        await state.clear()


async def main():
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())