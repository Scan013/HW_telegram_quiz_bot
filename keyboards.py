from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

def generate_options_keyboard(answer_options: list, right_answer: str):
    builder = InlineKeyboardBuilder()
    for option in answer_options:
        builder.add(InlineKeyboardButton(
            text=option,
            callback_data="right_answer" if option == right_answer else "wrong_answer"
        ))
    builder.adjust(1)
    return builder.as_markup()