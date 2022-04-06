from telegram.ext import Updater, CommandHandler
import requests
from bs4 import BeautifulSoup as BS
import telebot

token = "5276253794:AAGgC9RfqOmlnTiiIwijpUaW9IK3X2RcNic"
bot = telebot.TeleBot(token)


print("Бот запущен.")


#	items = soup.findAll('a', {'href': 'audi/90'}).text
#	print(items)


# with open ("https://cars.av.by/audi/90") as file:
#	src = file.read()

# soup = BS(src, lxml)

# page_all_h3 = soup.find_all("h3")
# print(page_all_h3)
@bot.message_handler(commands=['start'])
def start(message):
	bot.send_message(message.chat.id, 'Привет, я Бот, который покажет тебе объявления о продаже интересующей тачки.')
	print(message.chat.id, "started")


@bot.message_handler(commands=['parse'])
def parse(message):
	URL ='https://cars.av.by/audi/90'
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
		bot.send_message(message.chat.id, 'Попробуйте еще')
		print(message.chat.id, 'parsing trouble')
	elif len(cars) != 0:
		bot.send_message(message.chat.id, 'для просмотра следующего объвления введите next')
		printing(cars, message)

#		chat = update.effective_chat
#		context.bot.send_message(chat_id=chat.id,)
#def printing():
#		for car in cars:
#			print(f'{car["title"]} -> Price: {car["price"]} -> Location: {car["location"]} -> Params: {car["params"]} -> Link: {"cars.av.by"+car["link"]}')
#			bot.send_message(message.chat.id, f'{car["title"]} -> Price: {car["price"]} -> Location: {car["location"]} -> Params: {car["params"]} -> Link: {"cars.av.by"+car["link"]}')


@bot.message_handler()
def printing(cars, message):
	for car in cars:
		if message.text == 'send' or 'next' or 'parse':
			print(f'{car["title"]} -> Price: {car["price"]} -> Location: {car["location"]} -> Params: {car["params"]} -> Link: {"cars.av.by" + car["link"]}')
			bot.send_message(message.chat.id, f'{car["title"]} -> Price: {car["price"]} -> Location: {car["location"]} -> Params: {car["params"]} -> Link: {"cars.av.by" + car["link"]}')
		elif message.text == 'back':
			bot.send_message(message.chat.id, 'Вы вышли из просмотра объявлений')
			break







bot.polling(none_stop=True)
#def start(update, context):
#	chat = update.effective_chat
#	context.bot.send_message(chat_id=chat.id, text="Привет, я Бот, который покажет тебе объявления о продаже интересующей тачки.")
#	print(chat.id, "started")
#	parse()


#updater = Updater(token, use_context=True)

#dispatcher = updater.dispatcher
#dispatcher.add_handler(CommandHandler("start", start))
#dispatcher.add_handler(CommandHandler("parse", parse))
#dispatcher.add_handler(CommandHandler('next', printing))


#updater.start_polling()
#updater.idle()