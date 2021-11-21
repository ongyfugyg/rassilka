import re, configparser, time
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import BoundFilter
import db
import keyboards as kb

config = configparser.ConfigParser()
config.read("settings.ini")
TOKEN = config["tgbot"]["token"]
admin_id = int(config["tgbot"]["admin_id"])
class IsPrivate(BoundFilter):
    async def check(self, message: types.Message):
        return message.chat.type == types.ChatType.PRIVATE

class Info(StatesGroup):
    adminka = State()
    rassilka = State()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

@dp.message_handler(IsPrivate(), commands=['start'])
async def start_command(message: types.Message):
	if db.get_users_exist(message.chat.id) == False:
		db.add_user_to_db(message.chat.id)
		if message.chat.id == admin_id:
			await bot.send_message(chat_id=message.chat.id, text='Привет, админ.', reply_markup = kb.admin_menu())
			await Info.adminka.set()
		else:
			await bot.send_message(chat_id=message.chat.id, text='Привет, тебя нету в бд я добавил тебя туда.')
	else:
		if message.chat.id == admin_id:
			await bot.send_message(chat_id=message.chat.id, text='Привет, админ.', reply_markup = kb.admin_menu())
			await Info.adminka.set()
		else:
			await bot.send_message(chat_id=message.chat.id, text='Ку. ты есть в бд.')

@dp.message_handler(text="Админка")
async def create_post(message: types.Message):
	if db.get_users_exist(message.chat.id) == True:
		if message.chat.id == admin_id:
			await bot.send_message(chat_id=message.chat.id, text='Вот ваше админ меню.', reply_markup = kb.admin_menu())
			await Info.adminka.set()

@dp.message_handler(state=Info.adminka, content_types=types.ContentTypes.TEXT)
async def adminka(message: types.Message, state: FSMContext):
	if message.text.lower() == 'назад':
		await bot.send_message(chat_id=message.chat.id, text='Ты вернулся в главное меню.', reply_markup=kb.admin_kb())
		await state.finish()
	elif message.text.lower() == 'рассылка':
		await bot.send_message(chat_id=message.chat.id, text='Введи текст для рассылки.', reply_markup=kb.back_2())
		await state.finish()
		await Info.rassilka.set()

@dp.message_handler(state=Info.rassilka, content_types=types.ContentTypes.TEXT)
async def rassilka2(message: types.Message, state: FSMContext):
	if message.text.lower() == 'отмена':
		await bot.send_message(chat_id=message.chat.id, text='Ты вернулся в админ меню.', reply_markup=kb.admin_kb())
		await state.finish()
	else:
		text = message.text
		start_time = time.time()
		users = db.get_all_users()
		for user in users:
			try:
				await bot.send_message(chat_id=user[0], text=text)
				time.sleep(0.1)
			except:
				pass
		end_time = time.time()
		await bot.send_message(message.from_user.id, f"✔️ Рассылка успешно завершена за {round(end_time-start_time, 1)} сек. \n 》 Все пользователи получили ваше сообщение. 《", reply_markup=kb.admin_menu())
		await state.finish()


if __name__ == "__main__":
	db.check_db()
	# Запускаем бота
	executor.start_polling(dp, skip_updates=True)