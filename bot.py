import asyncio

from aiogram import Bot, Dispatcher, executor, types
import logging
import requests
from aiogram.dispatcher.webhook import SendMessage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup as BS
from pymongo import MongoClient
import aioschedule

API_TOKEN = "5276253794:AAGgC9RfqOmlnTiiIwijpUaW9IK3X2RcNic"
delay = 900

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
loop = asyncio.get_event_loop()

client = MongoClient("mongodb://localhost:27017/")
db = client['tgbot']
userdata = db['userdata']
users = db['users']

choice = InlineKeyboardMarkup(row_width=2,
                              inline_keyboard=[
                                  [
                                      InlineKeyboardButton(
                                          text="Отписаться",
                                          callback_data="cancel"
                                      )
                                  ]
                              ])


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Пришли мне ссылку вида https://cars.av.by/acura/mdx чтобы я подобрал подходящие объявления")


@dp.callback_query_handler(lambda c: c.data.startswith('cancel'))
async def cancel(callback: types.CallbackQuery):
    remove_all_userdata(callback.from_user.id)
    await callback.message.answer('Вы успешно отписались!')
    await callback.answer()


@dp.message_handler()
async def return_car_data(message: types.Message):
    data = get_data(url=str(message.text))
    if len(data) == 0:
        await message.answer('Попробуйте еще')
    elif len(data) != 0:
        await message.answer('Найдено ' + str(len(data)) + ' объявлений')
        for car in data:
            save_userdata(message.from_user.id, car['link'], car['link'])
            await message.answer(get_car_str(car))


def get_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/99.0.4844.84 Safari/537.36 OPR/85.0.4341.47 '
    }
    response = requests.get(url, headers=headers)
    soup = BS(response.content, 'html.parser')
    items = soup.findAll('div', class_='listing-item__wrap')
    cars = []

    for item in items:
        cars.append({
            'title': item.find('a', class_='listing-item__link').get_text(strip=True),
            'price': item.find('div', class_='listing-item__priceusd').get_text(strip=True),
            'location': item.find('div', class_='listing-item__location').get_text(strip=True),
            'params': item.find('div', class_='listing-item__params').get_text(strip=True),
            'link': item.find('a', class_='listing-item__link').get('href')
        })
    return cars[:5]


def save_user(userid: str):
    users.insert_one({'userid': userid})


def save_userdata(userid: str, url: str, car_url: str):
    userdata.insert_one({'userid': userid, 'url': url, 'car_url': car_url})


def remove_all_userdata(userid: str):
    userdata.delete_many({'userid': userid})


async def check_updates():
    user_list = users.find({})
    for user in user_list:
        ud = userdata.find({'userid': user['userid']})
        cars = []
        urls = []
        for data in ud:
            cars.append(data['car_url'])
            if data['ulr'] not in urls:
                urls.append(data['url'])
        for url in urls:
            for car in get_data(url):
                if car['link'] not in cars:
                    userdata.insert_one({'userid': user['userid'], 'url': url, 'car_url': car['link']})
                    await notify_user(user['userid'], "Новое объявление! \n" + car['link'])


async def notify_user(userid: str, message: str):
    await bot.send_message(chat_id=userid, text=message, reply_markup=choice)


def get_car_str(car: dict):
    return car['title'] + '\n' + car['price'] + "\n" + car['location'] + "\n" + car[
        'params'] + '\n https://cars.av.by' + car['link']


async def my_func():
    await check_updates()
    when_to_call = loop.time() + delay
    loop.call_at(when_to_call, my_callback)


def my_callback():
    asyncio.ensure_future(my_func())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=my_callback())
