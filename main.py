#import logging
from aiogram import Bot, types
from aiogram.utils.helper import Helper
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from os import mkdir, getcwd, system
import urllib
from loguru import logger
import sqlite3 as sq


from config import TOKEN
PATH = getcwd()
#logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logger.add("debug.json", format="{time} {level} {message}", level="INFO", rotation="5 MB", compression="zip", serialize=True)

def db_checker(id):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        select = f"SELECT id FROM users WHERE id == {id}"
        cur.execute(select)
        res = cur.fetchall()
        if res != []:
            return True
        else:
            return False


def add_user(id):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        insert = f"INSERT INTO users VALUES({id},datetime('now','localtime'))"
        cur.execute(insert)


def make_dir(dirname):
    try:
        mkdir(dirname)
    except OSError as e:
        return False
    else:
        return True


class Form(StatesGroup):
    name = State()
    SAM = State()
    SYSTEM = State()
    HASH = State()


class Users(StatesGroup):
    user_id = State()

@dp.message_handler(commands=['start','help'])
async def start_procces(msg:types.Message):
    await bot.send_message(msg.chat.id, "Hello, this bot was created for automatic brutforce Windows hashes")

@dp.message_handler(commands=['add_user'])
async def process_add(message: types.Message):
    if message.chat.id == 450047498:
        await Users.user_id.set()
        await bot.send_message(message.chat.id, "Кого будем добавлять? (Только ID)")
    else:
        await bot.send_message(message.chat.id, "Ты не админ, кыш")


@dp.message_handler(state=Users.user_id)
async def process_test(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_id'] = message.text
        id = int(data['user_id'])
        add_user(id)
        await state.finish()

@dp.message_handler(commands=['brute'])
async def recv_message(message: types.Message):
    await Form.name.set()
    await message.reply("Выберите название папки для проекта (без пробелов кавычек и прочего)")

@dp.message_handler(state=Form.name)
async def process_test(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if db_checker(message.chat.id) == False:
            await bot.send_message(message.chat.id, "I didn`t know who are u...\n-_-")
            logger.error("ILLEGAL ACCES:"+str(message.chat.id)+'\n'+str(message.chat.username)+'\n')
            await state.finish()
        else:
            data['name'] = message.text
            if make_dir('files/'+data['name']):
                await bot.send_message(message.chat.id, "Папка была создана успешно!")
            else:
                await bot.send_message(message.chat.id, "Название папки не подходит.\nHапишите /brute и попробуйте ещё раз")

            global active_dir_path
            active_dir_path = PATH+'/'+'files/'+data['name']
            logger.info("WHOIS DIR : "+str(message.chat.id)+'\n'+str(message.chat.username)+'\n'+active_dir_path)

            await Form.next()
            await message.reply("Пришлите SAM файл :^)\n!!! Имена файлов должны быть в верхнем регистре !!!")

@dp.message_handler(lambda message: message.document.file_name == "SAM",content_types=['document'], state=Form.SAM)
async def process_SAM(message: types.Message, state:FSMContext):
    async with state.proxy() as data:
        data['SAM'] = True
        document_id = message.document.file_id
        file_info = await bot.get_file(document_id)
        fi = file_info.file_path
        name = message.document.file_name
        urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{TOKEN}/{fi}',f'{active_dir_path}/{name}')
        await bot.send_message(message.from_user.id, f'DEBUG: Файл SAM успешно сохранён в {active_dir_path}/{name}')

    await Form.next()
    await message.reply("Хорошо, SAM загружен\nТеперь скиньте файл SYSTEM :^)")

@dp.message_handler(lambda message: message.document.file_name == "SYSTEM",content_types=['document'], state=Form.SYSTEM)
async def process_SYSTEM(message: types.Message, state:FSMContext):
    async with state.proxy() as data:
        data['SYSTEM'] = True
        document_id = message.document.file_id
        file_info = await bot.get_file(document_id)
        fi = file_info.file_path
        name = message.document.file_name
        urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{TOKEN}/{fi}',f'{active_dir_path}/{name}')
        await bot.send_message(message.from_user.id, f'Файл SYSTEM успешно сохранён {active_dir_path}/{name}')
        await bot.send_message(message.from_user.id, "Вынятые хеши с файлов:")
        system(f'python3 secretsdump.py -sam {active_dir_path}/SAM -system {active_dir_path}/SYSTEM LOCAL >> {active_dir_path}/hashes_out.txt')
        with open(f"{active_dir_path}/hashes_out.txt", "r",encoding="utf-8") as f:
            for line in f:
                lines = line.split(":")
                name = lines[0]
                ha = lines[3]
                await bot.send_message(message.chat.id, name)
                await bot.send_message(message.chat.id, ha)
                #with open(f"{active_dir_path}/hashes_out.txt","rb") as f:
            #await bot.send_document(message.chat.id,f)
            await bot.send_message(message.chat.id,"Отправьте 1 хеш")

    await Form.next()

@dp.message_handler(state=Form.HASH)
async def process_test(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['HASH'] = message.text
        print(data['HASH'])
        await bot.send_message(message.chat.id, "Brute force started!")
        info = [data['name'], data['SAM'], data['SYSTEM'], data['HASH']]
        logger.info("WHOIS : "+str(info)+'\n'+active_dir_path)
        system(f"./cracken.sh {data['HASH']} {active_dir_path}/result.txt")

        await bot.send_message(message.chat.id, "Check result!")
        with open(f"{active_dir_path}/result.txt", "r") as r:
            try:
                text = r.readlines()
                await bot.send_message(message.chat.id, text[0])
            except Exception as e:
                await bot.send_message(message.chat.id, "Хеш не найден :(")
 
    await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp)
