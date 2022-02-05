import telebot
import requests
import sqlite3
from config import tg_bot_token, open_weather_token


bot = telebot.TeleBot(tg_bot_token)
city = ''
user_id = 0

@bot.message_handler(commands=['start'])
def start(message):
    global user_id
    user_id = message.chat.id
    #Creating a SQL Table if not created
    msg = bot.send_message(message.chat.id, 'Привет, для использования бота, введите город, в котором вы хотите видеть погоду\n Для смены города используйте команду /change_town')
    connect = sqlite3.connect('accounts.db')
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users_info(
        user_id INTEGER PRIMARY KEY, 
        town TEXT)
    """)
    connect.commit()
    bot.register_next_step_handler(msg, remember_town)



def remember_town(message):
    global city, user_id

    connect = sqlite3.connect('accounts.db')
    cursor = connect.cursor()
    city = message.text
    print("Твой город:", city)
    print("User_id", user_id)
    # Регистрация пользователя
    cursor.execute("SELECT user_id FROM users_info")
    if cursor.fetchone() is None:
        cursor.execute(f"INSERT INTO users_info VALUES (?, ?)", (user_id, city))
        connect.commit()
    else:
        pass



'''Изменение города'''
@bot.message_handler(commands=['change_town'])
def change_town(message):
    connect = sqlite3.connect('accounts.db')
    cursor = connect.cursor()
    cursor.execute("SELECT town from users_info")

    if cursor.fetchone() is None:
        bot.send_message(message.chat.id, 'Вы не указали город')


    else:
        msg = bot.send_message(message.chat.id, "Укажите новый город: ")
        bot.register_next_step_handler(msg, change_town_2)
        connect.commit()


def change_town_2(message):
    connection = sqlite3.connect('accounts.db')
    cursor = connection.cursor()

    city = message.text
    print(city)

    # Изменение города если он был указан
    sql = """UPDATE users_info SET town = ?"""
    cursor.execute(f'UPDATE users_info SET town = ?', (city,))
    connection.commit()



@bot.message_handler(commands=["show_weather"])
def weather(message):
    global open_weather_token
    connect = sqlite3.connect('accounts.db')
    cursor = connect.cursor()


    cursor.execute("SELECT town FROM users_info")
    city = cursor.fetchone()
    city = city[0]


    print('Ваш город: ', city)
    code_to_smile = {
        'Clear': 'Ясно \U00002600',
        'Clouds': 'Облачно \U00002601',
        'Rain': 'Дождь \U00002614',
        'Drizzle': 'Дождь \U00002614',
        'Thunderstorm': 'Гроза \U000026A1',
        'Snow': 'Снег \U0001F328',
        'Mist': 'Туман \U0001F32B',
    }

    try:
        r = requests.get(
            f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={open_weather_token}&units=metric'
        )

        data = r.json()

        city = data['name']
        cur_weather = data['main']['temp']

        weather_description = data['weather'][0]['main']
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = 'Посмотри в окно, не пойму что там за погода'

        humidity = data['main']['humidity']
        wind = data['wind']['speed']

        bot.send_message(message.chat.id, f'Погода в городе: {city}\nТемператруа: {cur_weather}C°')


    except Exception as ex:
        bot.message_handler(message.chat.id, ex)
        bot.message_handler(message.chat.id, 'Проверьте правильность введённых данных')



@bot.message_handler(commands=['help'])
def text(message):
    bot.send_message(message.chat.id, 'Доступные команды: /start, /save_weather')

bot.infinity_polling()