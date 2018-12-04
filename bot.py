import asyncio
import json
import logging

import requests
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.utils.emoji import emojize
from aiogram.dispatcher import Dispatcher
from aiogram.types.message import ContentType
from aiogram.utils.markdown import text, bold, italic, code, pre
from aiogram.types import ParseMode, InputMediaPhoto, InputMediaVideo, ChatActions

from config import TOKEN

logging.basicConfig(
    format=u'%(filename)s [ LINE:%(lineno)+3s ]#%(levelname)+8s [%(asctime)s]  %(message)s',
    level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    msg = text('Привет!\nЭто поисковик по фильмам. Используй', bold('/help'), 'чтобы узнать больше')
    await message.reply(msg)


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    msg = text(
        'Поиск по фильмам из базы IMDb.',
        'Просто введи часть названия фильма или сериала, который тебя интересует.',
        sep='\n')
    await message.reply(msg, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler()
async def move_message(msg: types.Message):
    imdb = 'http://sg.media-imdb.com/suggests/'
    query = msg.text.lower().strip()
    if not query:
        return
    req = requests.get(f'{imdb}{query[0]}/{query}.json')
    if not req.ok:
        return
    data = req.text[len('imdb$') + len(query) + 1:-1]
    data = json.loads(data)
    if 'd' not in data:
        return

    for info in data['d']:
        if 'q' not in info:
            continue
        if 'i' not in info:
            continue
        if 'l' not in info:
            continue

        if info['q'] not in ['feature', 'TV series']:
            continue

        link = f'https://www.imdb.com/title/{info["id"]}/'
        head = info['l']
        imag = info['i'][0]

        await bot.send_message(msg.from_user.id, '\n'.join([head, link]))
        await bot.send_photo(msg.from_user.id, imag)


@dp.message_handler()
async def echo_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, msg.text)


@dp.message_handler(content_types=ContentType.ANY)
async def unknown_message(msg: types.Message):
    message_text = text(emojize('Я не знаю, что с этим делать :astonished:'),
                        italic('\nЯ просто напомню,'), 'что есть',
                        code('команда'), '/help')
    await msg.reply(message_text, parse_mode=ParseMode.MARKDOWN)


if __name__ == '__main__':
    executor.start_polling(dp)
