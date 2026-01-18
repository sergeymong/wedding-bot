"""Inline-клавиатуры бота"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu() -> InlineKeyboardMarkup:
    """Главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📍 Как добраться", callback_data="location"),
            InlineKeyboardButton(text="🕐 Расписание", callback_data="schedule"),
        ],
        [
            InlineKeyboardButton(text="👗 Что надеть", callback_data="dresscode"),
            InlineKeyboardButton(text="🍽 Еда и напитки", callback_data="menu"),
        ],
        [
            InlineKeyboardButton(text="❓ Вопросы", callback_data="questions"),
            InlineKeyboardButton(text="📞 Связаться", callback_data="contact"),
        ],
    ])


def back_button() -> InlineKeyboardMarkup:
    """Кнопка 'Назад'"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="← Назад в меню", callback_data="back")]
    ])


def location_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для раздела 'Как добраться'"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗺 Открыть в Яндекс Картах", url="https://yandex.ru/maps/-/CLhzMN9F")],
        [InlineKeyboardButton(text="← Назад в меню", callback_data="back")]
    ])


def questions_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для вопросов"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✉️ Ещё вопросы? Напиши нам", callback_data="contact")],
        [InlineKeyboardButton(text="← Назад в меню", callback_data="back")]
    ])


def contact_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для контактов"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="← Назад в меню", callback_data="back")]
    ])
