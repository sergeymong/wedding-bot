"""Обработчики команд и callback"""

import os
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode

from . import texts, keyboards

router = Router()

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
    await callback.message.edit_text(
        texts.LOCATION,
        reply_markup=keyboards.location_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "schedule")
async def cb_schedule(callback: CallbackQuery):
    """Расписание"""
    await callback.message.edit_text(
        texts.SCHEDULE,
        reply_markup=keyboards.back_button()
    )
    await callback.answer()


@router.callback_query(F.data == "dresscode")
async def cb_dresscode(callback: CallbackQuery):
    """Дресс-код"""
    await callback.message.edit_text(
        texts.DRESSCODE,
        reply_markup=keyboards.back_button()
    )
    await callback.answer()


@router.callback_query(F.data == "menu")
async def cb_menu(callback: CallbackQuery):
    """Меню"""
    await callback.message.edit_text(
        texts.MENU,
        reply_markup=keyboards.back_button()
    )
    await callback.answer()


@router.callback_query(F.data == "faq")
async def cb_faq(callback: CallbackQuery):
    """FAQ"""
    await callback.message.edit_text(
        texts.FAQ,
        reply_markup=keyboards.faq_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


@router.callback_query(F.data == "contact")
async def cb_contact(callback: CallbackQuery):
    """Связаться"""
    await callback.message.edit_text(
        texts.CONTACT,
        reply_markup=keyboards.contact_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "back")
async def cb_back(callback: CallbackQuery):
    """Назад в главное меню"""
    await callback.message.edit_text(
        texts.BACK_TO_MENU,
        reply_markup=keyboards.main_menu()
    )
    await callback.answer()


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
        ADMIN_CHAT_ID,
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
    
    await bot.send_message(ADMIN_CHAT_ID, f"📎 Новое сообщение с медиа\n\n{user_info}")
    await message.forward(ADMIN_CHAT_ID)
    await message.answer(texts.MESSAGE_RECEIVED, reply_markup=keyboards.main_menu())
