import logging
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

from config import TOKEN
PATH = getcwd()
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

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


@dp.message_handler(commands=['start','help'])
async def start_procces(msg:types.Message):
    await bot.send_message(msg.chat.id, "Test")
    f = open("test.txt","rb")
    await bot.send_document(msg.chat.id,f)

@dp.message_handler(commands=['sm'])
async def recv_message(message: types.Message):
    await Form.name.set()
    await message.reply("Выберите название папки для проекта (без пробелов кавычек и прочего)")

@dp.message_handler(state=Form.name)
async def process_test(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
        if make_dir('files/'+data['name']):
            await bot.send_message(message.chat.id, "Directory was created successfuly!")
        else:
            await bot.send_message(message.chat.id, "Directory name is invalid!")

        global active_dir_path
        active_dir_path = PATH+'/'+'files/'+data['name']

        await Form.next()
        await message.reply("Send me a SAM file :^)")

@dp.message_handler(lambda message: message.document.file_name == "SAM",content_types=['document'], state=Form.SAM)
async def process_SAM(message: types.Message, state:FSMContext):
    async with state.proxy() as data:
        data['SAM'] = True
        document_id = message.document.file_id
        file_info = await bot.get_file(document_id)
        fi = file_info.file_path
        name = message.document.file_name
        urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{TOKEN}/{fi}',f'{active_dir_path}/{name}')
        await bot.send_message(message.from_user.id, f'DEBUG: Файл SAM успешно сохранён {active_dir_path}/{name}')

    await Form.next()
    await message.reply("Ok, SAM was uploaded\nNext, send me a SYSTEM file :^)")

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
        system(f'python3 secretsdump.py -sam {active_dir_path}/SAM -system {active_dir_path}/SYSTEM LOCAL >> {active_dir_path}/hashes_out')
        with open(f"{active_dir_path}/hashes_out","rb") as f:
            await bot.send_document(message.chat.id,f)
            await bot.send_message(message.chat.id,"Отправьте 1 хеш с файла")

    await Form.next()

@dp.message_handler(state=Form.HASH)
async def process_test(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['HASH'] = message.text
        print(data['HASH'])
        await bot.send_message(message.chat.id, "Brute force started!")
        system(f"./cracken.sh {data['HASH']} {active_dir_path}/result.txt")

        await bot.send_message(message.chat.id, "Check result!")
        with open(f"{active_dir_path}/result.txt", "r") as r:
            text = r.readlines()
            await bot.send_message(message.chat.id, text[0])
 
    await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp)
