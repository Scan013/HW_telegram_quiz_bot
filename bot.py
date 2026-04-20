import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from config import API_TOKEN
from database import (
    create_tables, update_quiz_state, get_quiz_state,
    save_final_result, get_last_result
)
from quiz_data import quiz_data
from keyboards import generate_options_keyboard

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ---------- Хэндлеры ----------
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(F.text == "Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer("Давайте начнем квиз!")
    await new_quiz(message)

async def new_quiz(message: types.Message):
    user_id = message.from_user.id
    await update_quiz_state(user_id, 0, 0)
    await get_question(message, user_id)

async def get_question(message: types.Message, user_id: int):
    current_index, current_score = await get_quiz_state(user_id)
    if current_index >= len(quiz_data):
        await save_final_result(user_id, current_score, len(quiz_data))
        await message.answer(f"Квиз окончен! Вы ответили правильно на {current_score} из {len(quiz_data)}.\n/stats — посмотреть результат.")
        return

    q = quiz_data[current_index]
    kb = generate_options_keyboard(q['options'], q['options'][q['correct_option']])
    await message.answer(q['question'], reply_markup=kb)

@dp.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    user_id = callback.from_user.id
    current_index, current_score = await get_quiz_state(user_id)
    new_score = current_score + 1
    new_index = current_index + 1
    await update_quiz_state(user_id, new_index, new_score)
    await callback.message.answer("✅ Верно!")

    if new_index < len(quiz_data):
        await get_question(callback.message, user_id)
    else:
        await save_final_result(user_id, new_score, len(quiz_data))
        await callback.message.answer(f"🏁 Квиз завершён! Правильных ответов: {new_score} из {len(quiz_data)}.\n/stats — посмотреть результат.")

@dp.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    user_id = callback.from_user.id
    current_index, current_score = await get_quiz_state(user_id)
    correct_option_index = quiz_data[current_index]['correct_option']
    correct_text = quiz_data[current_index]['options'][correct_option_index]
    await callback.message.answer(f"❌ Неправильно. Правильный ответ: {correct_text}")

    new_index = current_index + 1
    await update_quiz_state(user_id, new_index, current_score)

    if new_index < len(quiz_data):
        await get_question(callback.message, user_id)
    else:
        await save_final_result(user_id, current_score, len(quiz_data))
        await callback.message.answer(f"🏁 Квиз завершён! Правильных ответов: {current_score} из {len(quiz_data)}.\n/stats — посмотреть результат.")

@dp.message(Command("stats"))
async def show_stats(message: types.Message):
    user_id = message.from_user.id
    last_score, total = await get_last_result(user_id)
    if last_score is None:
        await message.answer("Вы ещё не проходили квиз. Напишите /quiz, чтобы начать.")
    else:
        await message.answer(f"📊 Ваш последний результат: {last_score} из {total} правильных ответов.")

# ---------- Запуск ----------
async def main():
    await create_tables()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())