from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.utils.emoji import emojize
from aiogram.dispatcher import Dispatcher
from aiogram.types.message import ContentType
from aiogram.utils.markdown import text, bold, italic, code
from aiogram.types import ParseMode

from config import TOKEN
import logging

from search import search

logging.basicConfig(
    format=u'%(filename)s [ LINE:%(lineno)+3s ]#%(levelname)+8s [%(asctime)s]  %(message)s',
    level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    answer = text('Привет!\nЭто поисковик по фильмам. Используй',
                  bold('/help'), 'чтобы узнать больше')
    await message.reply(answer)


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    answer = text(
        'Поиск по фильмам из базы IMDb.',
        'Просто введи часть названия фильма или сериала, который тебя интересует.',
        sep='\n')
    logging.info(f'help for {message.from_user.id}')
    await message.reply(answer, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler()
async def find_film(message: types.Message):
    films = list(search(message.text))

    logging.info(f'found {len(films)} films')

    if not films:
        await bot.send_message(message.from_user.id, "Я ничего не нашел :(")

    for film in films:
        await bot.send_message(message.from_user.id, f'{film.title}\n{film.link}')
        await bot.send_photo(message.from_user.id, film.poster)


@dp.message_handler()
async def echo_message(message: types.Message):
    await bot.send_message(message.from_user.id, message.text)


@dp.message_handler(content_types=ContentType.ANY)
async def unknown_message(msg: types.Message):
    answer = text(emojize('Я не знаю, что с этим делать :astonished:'),
                  italic('\nЯ просто напомню,'), 'что есть',
                  code('команда'), '/help')
    await msg.reply(answer, parse_mode=ParseMode.MARKDOWN)


if __name__ == '__main__':
    executor.start_polling(dp)
