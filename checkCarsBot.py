from telegram.ext import Updater, CommandHandler
import requests
from bs4 import BeautifulSoup as BS
import telebot

token = "5276253794:AAGgC9RfqOmlnTiiIwijpUaW9IK3X2RcNic"
bot = telebot.TeleBot(token)

LINK = "https://cars.av.by"
print("Бот запущен.")



@bot.message_handler(commands=['start'])
def start(message):
	keyboard = telebot.types.ReplyKeyboardMarkup(True)
	keyboard.row('Отслеживать', 'Инструкция')
	bot.send_message(message.chat.id, 'Привет, я Бот, который покажет тебе объявления о продаже интересующего автомобиля. Ознакомься с инструкцией по созданию фильтра, нажав на кнопку "Инструкция", а после нажми "Отслеживать" и отправь мне ссылку со своими фильтрами.', reply_markup=keyboard)
	print(message.chat.id, "started")


#@bot.message_handler(commands=['parse'])
def parse(message, URL):
#	URL ='https://cars.av.by/audi/90'
	HEADERS = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36 OPR/85.0.4341.47'
	}
	response = requests.get(URL, headers=HEADERS)
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
	if len(cars) == 0:
		bot.send_message(message.chat.id, 'Неверная ссылка, попробуйте снова')
		print(message.chat.id, 'parsing trouble')
	elif len(cars) != 0:
		#bot.send_message(message.chat.id, 'для просмотра следующего объвления введите next')
		printing(cars, message)



@bot.message_handler(content_types=['text'])
def send_text(message):
	if message.text == 'Отслеживать':
		bot.send_message(message.chat.id, 'Пришлите ссылку на интересующие вас фильтры')
	elif message.text == 'Инструкция':
		bot.send_message(message.chat.id, f'Для настройки фильтра выполните следующее:\n'
                              f'1. Зайдите на сайт av.by\n'
                              f'2. Настройте фильтр на сайте (не забудьте установить сортировку "По дате подачи")\n'
                              f'3. Нажмите кнопку "Показать"\n'
                              f'4. Скопируйте получившуюся ссылку из Вашего браузера\n'
                              f'5. Отправьте ссылку мне\n\n'
                              f'Сейчас у вас не установлен фильтр\n\n')
	elif 'cars.av.by' in message.text:
		checking_url(message, message.text)
	else:
		bot.send_message(message.chat.id, 'Неверная ссылка или неизвестная команда, попробуйте снова')

#https://cars.av.by/filter?brands[0][brand]=6&brands[0][model]=9&brands[0][generation]=34&sort=4
#@bot.message_handler()
def printing(cars, message):
	for car in cars:
#		if message.text == 'send' or 'next' or 'parse':
			print(f'{car["title"]} -> Price: {car["price"]} -> Location: {car["location"]} -> Params: {car["params"]} -> Link: {"cars.av.by" + car["link"]}')
			bot.send_message(message.chat.id, 'Рассылка включена. Я отправлю Вам новые объявления как только они появятся.')
			#bot.send_message(message.chat.id, f'{car["title"]} -> Price: {car["price"]} -> Location: {car["location"]} -> Params: {car["params"]} -> Link: {"cars.av.by" + car["link"]}')
			bot.send_message(message.chat.id, f'Новое объявление по Вашему фильтру:\n\n'
                             f'{car["title"]}\n\n'
                             f'Цена: {car["price"]}$\n'
                             f'Город: {car["location"]}\n'
                             f'Год: {car["params"]}\n'
                             #f'Коробра передач: {ads["transmission"]}\n'
                             #f'Объём двигателя: {ads["engine_capacity"]}\n'
                             #f'Тип двигателя: {ads["engines_type"]}\n'
                             #f'Тип кузова: {ads["body_type"]}\n'
                             #f'Пробег: {ads["mileage"]}\n\n'
                             f'<a href="{"cars.av.by" + car["link"]}">Смотреть объявление на сайте</a>\n\n',
							# f'[Смотреть объявление на сайте]({"cars.av.by" + car["link"]})\n\n',
                        disable_web_page_preview=True, parse_mode='html'
                    )
#		elif message.text == 'back':   [текст ссылки](http://example.com/url)
#			bot.send_message(message.chat.id, 'Вы вышли из просмотра объявлений')
#			break
@bot.message_handler(commands=['naebka'])
def naebka(message):
	bot.send_message(message.chat.id, f'Новое объявление по Вашему фильтру:\n\n'
                             f'Audi 90, B3\n\n'
                             f'Цена: 1300 $\n'
                             f'Город: Слуцк\n'
                             f'Год: 1987 г.\n'
                             f'Коробра передач: механика\n'
                             f'Объём двигателя: 2.2 л\n'
                             f'Тип двигателя: бензин\n'
                             f'Тип кузова: седан\n'
                             f'Пробег: 26832 км\n\n'
                             f'<a href="cars.av.by/audi/90/101071636">Смотреть объявление на сайте</a>\n\n',
                        disable_web_page_preview=True, parse_mode='html')

def checking_url(message, url):
#	url = ""  # тут должна быть твоя ссылка которая сгенерировалась
	v = 0
	try:
		requests.get(url, timeout=5)  # Кидаем запрос. timeout, что бы лишний раз не ждать
		v = 1  # Если всё прошло успешно, то valids будет равен 1
	except: pass
	if v == 1: parse(message, url)
	else: bot.send_message(message.chat.id, 'Неверная ссылка или неизвестная команда, попробуйте снова')







bot.polling(none_stop=True)
