"""Обработчики команд и callback"""

import os
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode

from . import texts, keyboards, database

router = Router()
logger = logging.getLogger(__name__)

ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

# ID кружочка для приветствия (заполнить после загрузки)
WELCOME_VIDEO_NOTE_ID = os.getenv("WELCOME_VIDEO_NOTE_ID", "")


# ==================== Команды для гостей ====================

@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    """Обработчик команды /start"""
    user = message.from_user
    is_first = database.is_first_visit(user.id)
    
    # Сохраняем пользователя
    database.save_user(user.id, user.username, user.full_name, first_visit=is_first)
    
    if is_first and WELCOME_VIDEO_NOTE_ID:
        # Первый визит — отправляем кружочек
        try:
            await bot.send_video_note(message.chat.id, WELCOME_VIDEO_NOTE_ID)
        except Exception as e:
            logger.error(f"Failed to send video note: {e}")
        
        await message.answer(
            texts.WELCOME_FIRST,
            reply_markup=keyboards.main_menu()
        )
    elif is_first:
        # Первый визит, но кружочка нет
        await message.answer(
            texts.WELCOME_FIRST,
            reply_markup=keyboards.main_menu()
        )
    else:
        # Повторный визит
        await message.answer(
            texts.WELCOME_RETURNING,
            reply_markup=keyboards.main_menu()
        )


# ==================== Команды для админов ====================

@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, bot: Bot):
    """Рассылка всем гостям. Reply на сообщение + /broadcast"""
    if not ADMIN_CHAT_ID or str(message.chat.id) != ADMIN_CHAT_ID:
        return
    
    if not message.reply_to_message:
        await message.reply("❗ Ответьте на сообщение, которое хотите разослать")
        return
    
    users = database.get_all_users()
    if not users:
        await message.reply("Пока нет пользователей для рассылки")
        return
    
    source = message.reply_to_message
    success = 0
    failed = 0
    
    await message.reply(f"📤 Начинаю рассылку {len(users)} пользователям...")
    
    for user_id in users:
        try:
            await source.copy_to(user_id)
            success += 1
        except Exception as e:
            logger.error(f"Failed to send to {user_id}: {e}")
            failed += 1
    
    await message.reply(f"✅ Рассылка завершена\nУспешно: {success}\nОшибок: {failed}")


@router.message(Command("morning"))
async def cmd_morning(message: Message, bot: Bot):
    """Утренняя рассылка в день свадьбы"""
    if not ADMIN_CHAT_ID or str(message.chat.id) != ADMIN_CHAT_ID:
        return
    
    users = database.get_confirmed_users()
    if not users:
        # Если нет подтверждённых, шлём всем
        users = database.get_all_users()
    
    if not users:
        await message.reply("Пока нет пользователей для рассылки")
        return
    
    success = 0
    failed = 0
    
    await message.reply(f"☀️ Отправляю утреннее сообщение {len(users)} гостям...")
    
    for user_id in users:
        try:
            await bot.send_message(user_id, texts.MORNING_MESSAGE)
            success += 1
        except Exception as e:
            logger.error(f"Failed to send morning to {user_id}: {e}")
            failed += 1
    
    await message.reply(f"✅ Утренняя рассылка завершена\nУспешно: {success}\nОшибок: {failed}")


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Статистика бота"""
    if not ADMIN_CHAT_ID or str(message.chat.id) != ADMIN_CHAT_ID:
        return
    
    stats = database.get_stats()
    text = f"""📊 <b>Статистика</b>

👥 Всего в боте: {stats['total']}
✅ Подтвердили: {stats['confirmed']}
❌ Отказались: {stats['declined']}
⏳ Не ответили: {stats['pending']}
➕ С парой: {stats['plus_ones']}

🎉 <b>Итого гостей:</b> {stats['total_guests']}"""
    
    await message.reply(text, parse_mode=ParseMode.HTML)


@router.message(Command("getvideoid"))
async def cmd_get_video_id(message: Message):
    """Получить file_id кружочка. Reply на кружочек + /getvideoid"""
    if not ADMIN_CHAT_ID or str(message.chat.id) != ADMIN_CHAT_ID:
        return
    
    if not message.reply_to_message:
        await message.reply("❗ Ответьте на кружочек, чтобы получить его ID")
        return
    
    reply = message.reply_to_message
    if reply.video_note:
        await message.reply(f"🎬 <b>Video Note ID:</b>\n<code>{reply.video_note.file_id}</code>", parse_mode=ParseMode.HTML)
    elif reply.video:
        await message.reply(f"🎬 <b>Video ID:</b>\n<code>{reply.video.file_id}</code>", parse_mode=ParseMode.HTML)
    else:
        await message.reply("❌ Это не видео и не кружочек")


# ==================== Callback-кнопки ====================

@router.callback_query(F.data == "location")
async def cb_location(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
            texts.LOCATION,
            reply_markup=keyboards.location_keyboard(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Error in location: {e}")
        await callback.message.answer(
            texts.LOCATION,
            reply_markup=keyboards.location_keyboard(),
            parse_mode=ParseMode.HTML
        )
    await callback.answer()


@router.callback_query(F.data == "dresscode")
async def cb_dresscode(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
            texts.DRESSCODE,
            reply_markup=keyboards.back_button(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Error in dresscode: {e}")
        await callback.message.answer(
            texts.DRESSCODE,
            reply_markup=keyboards.back_button(),
            parse_mode=ParseMode.HTML
        )
    await callback.answer()


@router.callback_query(F.data == "menu")
async def cb_menu(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
            texts.MENU,
            reply_markup=keyboards.back_button(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Error in menu: {e}")
        await callback.message.answer(
            texts.MENU,
            reply_markup=keyboards.back_button(),
            parse_mode=ParseMode.HTML
        )
    await callback.answer()


@router.callback_query(F.data == "wishlist")
async def cb_wishlist(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
            texts.WISHLIST,
            reply_markup=keyboards.back_button(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Error in wishlist: {e}")
        await callback.message.answer(
            texts.WISHLIST,
            reply_markup=keyboards.back_button(),
            parse_mode=ParseMode.HTML
        )
    await callback.answer()


@router.callback_query(F.data == "questions")
async def cb_questions(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
            texts.QUESTIONS,
            reply_markup=keyboards.questions_keyboard(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Error in questions: {e}")
        await callback.message.answer(
            texts.QUESTIONS,
            reply_markup=keyboards.questions_keyboard(),
            parse_mode=ParseMode.HTML
        )
    await callback.answer()


@router.callback_query(F.data == "contact")
async def cb_contact(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
            texts.CONTACT,
            reply_markup=keyboards.contact_keyboard(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Error in contact: {e}")
        await callback.message.answer(
            texts.CONTACT,
            reply_markup=keyboards.contact_keyboard(),
            parse_mode=ParseMode.HTML
        )
    await callback.answer()


@router.callback_query(F.data == "sos")
async def cb_sos(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
            texts.SOS,
            reply_markup=keyboards.sos_keyboard(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Error in sos: {e}")
        await callback.message.answer(
            texts.SOS,
            reply_markup=keyboards.sos_keyboard(),
            parse_mode=ParseMode.HTML
        )
    await callback.answer()


@router.callback_query(F.data == "back")
async def cb_back(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
            texts.BACK_TO_MENU,
            reply_markup=keyboards.main_menu()
        )
    except Exception as e:
        logger.error(f"Error in back: {e}")
        await callback.message.answer(
            texts.BACK_TO_MENU,
            reply_markup=keyboards.main_menu()
        )
    await callback.answer()


@router.callback_query()
async def cb_unknown(callback: CallbackQuery):
    logger.warning(f"Unknown callback: {callback.data}")
    await callback.answer("Что-то пошло не так")


# ==================== Сообщения от гостей ====================

@router.message(F.chat.type == "private", F.text)
async def forward_text_to_admin(message: Message, bot: Bot):
    if not ADMIN_CHAT_ID:
        return
    
    user = message.from_user
    database.save_user(user.id, user.username, user.full_name)
    
    user_info = f"💬 <b>Новое сообщение</b>\n\n"
    user_info += f"От: {user.full_name}"
    if user.username:
        user_info += f" (@{user.username})"
    user_info += f"\n\n{message.text}"
    
    sent = await bot.send_message(
        int(ADMIN_CHAT_ID),
        user_info,
        parse_mode=ParseMode.HTML
    )
    
    database.save_message_link(sent.message_id, user.id)
    await message.answer(texts.MESSAGE_RECEIVED, reply_markup=keyboards.main_menu())


@router.message(F.chat.type == "private", F.photo | F.voice | F.video_note | F.document | F.video)
async def forward_media_to_admin(message: Message, bot: Bot):
    if not ADMIN_CHAT_ID:
        return
    
    user = message.from_user
    database.save_user(user.id, user.username, user.full_name)
    
    user_info = f"📎 <b>Новое сообщение</b>\n\n"
    user_info += f"От: {user.full_name}"
    if user.username:
        user_info += f" (@{user.username})"
    
    await bot.send_message(
        int(ADMIN_CHAT_ID),
        user_info,
        parse_mode=ParseMode.HTML
    )
    
    sent = await message.forward(int(ADMIN_CHAT_ID))
    database.save_message_link(sent.message_id, user.id)
    
    await message.answer(texts.MESSAGE_RECEIVED, reply_markup=keyboards.main_menu())


# ==================== Ответы админов ====================

@router.message(F.chat.type.in_({"group", "supergroup"}), F.reply_to_message)
async def admin_reply_to_guest(message: Message, bot: Bot):
    if not ADMIN_CHAT_ID or str(message.chat.id) != ADMIN_CHAT_ID:
        return
    
    # Игнорируем команды
    if message.text and message.text.startswith('/'):
        return
    
    reply_msg_id = message.reply_to_message.message_id
    user_id = database.get_user_by_message(reply_msg_id)
    
    if not user_id:
        return
    
    try:
        await message.copy_to(user_id)
        await message.reply("✅ Отправлено")
    except Exception as e:
        logger.error(f"Failed to reply to user {user_id}: {e}")
        await message.reply(f"❌ Не удалось отправить: {e}")
