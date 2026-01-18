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
            InlineKeyboardButton(text="👗 Дресс-код", callback_data="dresscode"),
            InlineKeyboardButton(text="🍽 Меню", callback_data="menu"),
        ],
        [
            InlineKeyboardButton(text="❓ FAQ", callback_data="faq"),
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


def faq_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для FAQ"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✉️ Ещё вопросы? Напиши нам", callback_data="contact")],
        [InlineKeyboardButton(text="← Назад в меню", callback_data="back")]
    ])


def contact_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для контактов"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 Позвонить Сергею", url="tel:+79991621492")],
        [InlineKeyboardButton(text="← Назад в меню", callback_data="back")]
    ])
