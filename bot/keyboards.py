"""Клавиатуры бота"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu() -> InlineKeyboardMarkup:
    """Главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📍 Где и когда", callback_data="location"),
            InlineKeyboardButton(text="👗 Что надеть", callback_data="dresscode"),
        ],
        [
            InlineKeyboardButton(text="🍽 Еда и напитки", callback_data="menu"),
            InlineKeyboardButton(text="🎁 Подарки", callback_data="wishlist"),
        ],
        [
            InlineKeyboardButton(text="❓ Вопросы", callback_data="questions"),
            InlineKeyboardButton(text="📞 Связаться", callback_data="contact"),
        ],
        [
            InlineKeyboardButton(text="🆘 Срочная связь", callback_data="sos"),
        ],
    ])


def back_button() -> InlineKeyboardMarkup:
    """Кнопка 'Назад'"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="← Назад в меню", callback_data="back")]
    ])


def location_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для локации"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗺 Открыть в Яндекс Картах", url="https://yandex.ru/maps/-/CLhzMN9F")],
        [InlineKeyboardButton(text="← Назад в меню", callback_data="back")]
    ])


def questions_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для вопросов"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✉️ Ещё вопросы? Напишите нам", callback_data="contact")],
        [InlineKeyboardButton(text="← Назад в меню", callback_data="back")]
    ])


def contact_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для контактов"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 Позвонить Сергею", url="tel:+79991621492")],
        [InlineKeyboardButton(text="← Назад в меню", callback_data="back")]
    ])


def sos_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для SOS"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 Позвонить Сергею", url="tel:+79991621492")],
        [InlineKeyboardButton(text="✉️ Написать в Телеграм", url="https://t.me/sergeymong")],
        [InlineKeyboardButton(text="← Назад в меню", callback_data="back")]
    ])
