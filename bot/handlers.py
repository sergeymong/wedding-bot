"""Обработчики команд и callback"""

import os
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode

from . import texts, keyboards, database

router = Router()
logger = logging.getLogger(__name__)

ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")


# ==================== Команды ====================

@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    # Сохраняем пользователя
    user = message.from_user
    database.save_user(user.id, user.username, user.full_name)
    
    await message.answer(
        texts.WELCOME,
        reply_markup=keyboards.main_menu()
    )


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, bot: Bot):
    """Рассылка всем гостям. Использовать как reply на сообщение."""
    # Только из группы админов
    if not ADMIN_CHAT_ID or str(message.chat.id) != ADMIN_CHAT_ID:
        return
    
    # Нужен reply на сообщение
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
            # Копируем сообщение (текст, фото, кружок и т.д.)
            await source.copy_to(user_id)
            success += 1
        except Exception as e:
            logger.error(f"Failed to send to {user_id}: {e}")
            failed += 1
    
    await message.reply(f"✅ Рассылка завершена\nУспешно: {success}\nОшибок: {failed}")


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Статистика бота"""
    # Только из группы админов
    if not ADMIN_CHAT_ID or str(message.chat.id) != ADMIN_CHAT_ID:
        return
    
    count = database.get_users_count()
    await message.reply(f"📊 Статистика\n\nГостей в боте: {count}")


# ==================== Callback-кнопки ====================

@router.callback_query(F.data == "location")
async def cb_location(callback: CallbackQuery):
    """Как добраться"""
    try:
        await callback.message.edit_text(
            texts.LOCATION,
            reply_markup=keyboards.location_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in location: {e}")
        await callback.message.answer(
            texts.LOCATION,
            reply_markup=keyboards.location_keyboard()
        )
    await callback.answer()


@router.callback_query(F.data == "schedule")
async def cb_schedule(callback: CallbackQuery):
    """Расписание"""
    try:
        await callback.message.edit_text(
            texts.SCHEDULE,
            reply_markup=keyboards.back_button()
        )
    except Exception as e:
        logger.error(f"Error in schedule: {e}")
        await callback.message.answer(
            texts.SCHEDULE,
            reply_markup=keyboards.back_button()
        )
    await callback.answer()


@router.callback_query(F.data == "dresscode")
async def cb_dresscode(callback: CallbackQuery):
    """Что надеть"""
    try:
        await callback.message.edit_text(
            texts.DRESSCODE,
            reply_markup=keyboards.back_button()
        )
    except Exception as e:
        logger.error(f"Error in dresscode: {e}")
        await callback.message.answer(
            texts.DRESSCODE,
            reply_markup=keyboards.back_button()
        )
    await callback.answer()


@router.callback_query(F.data == "menu")
async def cb_menu(callback: CallbackQuery):
    """Еда и напитки"""
    try:
        await callback.message.edit_text(
            texts.MENU,
            reply_markup=keyboards.back_button()
        )
    except Exception as e:
        logger.error(f"Error in menu: {e}")
        await callback.message.answer(
            texts.MENU,
            reply_markup=keyboards.back_button()
        )
    await callback.answer()


@router.callback_query(F.data == "questions")
async def cb_questions(callback: CallbackQuery):
    """Вопросы и ответы"""
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
    """Связаться"""
    try:
        await callback.message.edit_text(
            texts.CONTACT,
            reply_markup=keyboards.contact_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in contact: {e}")
        await callback.message.answer(
            texts.CONTACT,
            reply_markup=keyboards.contact_keyboard()
        )
    await callback.answer()


@router.callback_query(F.data == "back")
async def cb_back(callback: CallbackQuery):
    """Назад в главное меню"""
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
    """Неизвестный callback"""
    logger.warning(f"Unknown callback: {callback.data}")
    await callback.answer("Что-то пошло не так")


# ==================== Сообщения от гостей ====================

@router.message(F.chat.type == "private", F.text)
async def forward_text_to_admin(message: Message, bot: Bot):
    """Пересылка текстовых сообщений организаторам"""
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
    
    # Сохраняем связь для ответа
    database.save_message_link(sent.message_id, user.id)
    
    await message.answer(texts.MESSAGE_RECEIVED, reply_markup=keyboards.main_menu())


@router.message(F.chat.type == "private", F.photo | F.voice | F.video_note | F.document | F.video)
async def forward_media_to_admin(message: Message, bot: Bot):
    """Пересылка медиа организаторам"""
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


# ==================== Ответы админов гостям ====================

@router.message(F.chat.type.in_({"group", "supergroup"}), F.reply_to_message)
async def admin_reply_to_guest(message: Message, bot: Bot):
    """Ответ админа на сообщение гостя"""
    if not ADMIN_CHAT_ID or str(message.chat.id) != ADMIN_CHAT_ID:
        return
    
    # Игнорируем команды
    if message.text and message.text.startswith('/'):
        return
    
    # Находим user_id по сообщению, на которое отвечают
    reply_msg_id = message.reply_to_message.message_id
    user_id = database.get_user_by_message(reply_msg_id)
    
    if not user_id:
        # Может это ответ на своё сообщение для broadcast
        return
    
    try:
        # Отправляем ответ гостю
        await message.copy_to(user_id)
        await message.reply("✅ Отправлено")
    except Exception as e:
        logger.error(f"Failed to reply to user {user_id}: {e}")
        await message.reply(f"❌ Не удалось отправить: {e}")
