"""Обработчики команд и callback"""

import os
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode

from . import texts, keyboards

router = Router()
logger = logging.getLogger(__name__)

ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        texts.WELCOME,
        reply_markup=keyboards.main_menu()
    )


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


# Ловим все остальные callback для отладки
@router.callback_query()
async def cb_unknown(callback: CallbackQuery):
    """Неизвестный callback"""
    logger.warning(f"Unknown callback: {callback.data}")
    await callback.answer("Что-то пошло не так")


@router.message(F.text)
async def forward_text_to_admin(message: Message, bot: Bot):
    """Пересылка текстовых сообщений организаторам"""
    if not ADMIN_CHAT_ID:
        return
    
    user = message.from_user
    user_info = f"От: {user.full_name}"
    if user.username:
        user_info += f" (@{user.username})"
    user_info += f"\nID: {user.id}"
    
    await bot.send_message(
        int(ADMIN_CHAT_ID),
        f"💬 Новое сообщение\n\n{user_info}\n\n{message.text}"
    )
    await message.answer(texts.MESSAGE_RECEIVED, reply_markup=keyboards.main_menu())


@router.message(F.photo | F.voice | F.video_note | F.document)
async def forward_media_to_admin(message: Message, bot: Bot):
    """Пересылка медиа организаторам"""
    if not ADMIN_CHAT_ID:
        return
    
    user = message.from_user
    user_info = f"От: {user.full_name}"
    if user.username:
        user_info += f" (@{user.username})"
    user_info += f"\nID: {user.id}"
    
    await bot.send_message(int(ADMIN_CHAT_ID), f"📎 Новое сообщение с медиа\n\n{user_info}")
    await message.forward(int(ADMIN_CHAT_ID))
    await message.answer(texts.MESSAGE_RECEIVED, reply_markup=keyboards.main_menu())
