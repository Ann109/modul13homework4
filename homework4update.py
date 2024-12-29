from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

# Инициализация бота и диспетчера
bot = Bot(token='')
storage = MemoryStorage()
router = Router()
dp = Dispatcher(storage=storage)
dp.include_router(router)

class UserState(StatesGroup):
    age = State()  # состояния возраста
    growth = State()  # ...состояния роста
    weight = State()  # ...состояния веса


# Ответ на текстовое сообщение 'Calories'
@router.message(F.text.casefold().contains('calories'))  # F.text - ссылка на текст сообщения, используется
async def set_age(message: types.Message, state: FSMContext):
    await message.answer("Введите свой возраст:")  # бот отправляет сообщение с просьбой ввести возраст
    await state.set_state(UserState.age)  # устанавливаем состояние age, где бот ожидает ввода возраста


# Хендлер для обработки возраста
@router.message(UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
        await state.update_data(age=int(message.text)) # обновляет данные состояния, сохраняя возраст пользователя
        await message.answer("Введите свой рост (в см):")
        await state.set_state(UserState.growth) # устанавливаем состояние growth, где бот ожидает ввода роста


# Хендлер для обработки роста
@router.message(UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
        await state.update_data(growth=int(message.text)) # обновляет данные состояния, сохраняя рост пользователя
        await message.answer("Введите свой вес (в кг):")
        await state.set_state(UserState.weight) # устанавливаем состояние weight, где бот ожидает ввода вес


# Хендлер для обработки веса и вычисления нормы калорий
@router.message(UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
        await state.update_data(weight=int(message.text)) # обновляет данные состояния, сохраняя вес пользователя
        data = await state.get_data() # извлекаем все данные введенные пользователем (возраст, рост, вес)

        age = data['age']
        growth = data['growth']
        weight = data['weight']

        # Формула Миффлина - Сан Жеора для мужчин
        calories = 10 * weight + 6.25 * growth - 5 * age + 5

        await message.answer(f"Ваша норма калорий: {calories:.2f} ккал в день.")

        await state.clear()  # Завершение машины состояний
 

# Команда start
@dp.message(Command("start"))
async def start_form(message: Message):
    await message.answer("Привет! Я бот, помогающий твоему здоровью., "
                         "Напиши слово 'Calories'.")

# Хендлер для перенаправления всех остальных сообщений на start
@router.message(~F.text.casefold().contains('calories') and ~F.state(UserState.age) and ~F.state(UserState.growth)
                and ~F.state(UserState.weight))
async def redirect_to_start(message: types.Message):
    await start_form(message)  # Перенаправляем сообщение на хендлер команды /start


# Основная функция запуска бота
async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
