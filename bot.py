import telebot
from config import *
from logic import *
import random
import matplotlib.pyplot as plt
import numpy as np

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, "Доступные команды:\n"
                                  "/remember_city [название_города] - Запомнить город.\n"
                                  "/show_city [название_города] [цвет] - Показать город на карте с выбранным цветом.\n"
                                  "/show_my_cities - Показать карту с вашими городами.")

@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    parts = message.text.split()
    city_name = ' '.join(parts[1:-1]) if len(parts) > 2 else ' '.join(parts[1:])
    color = parts[-1] if len(parts) > 2 else 'red'  # Цвет по умолчанию
    
    coordinates = manager.get_coordinates(city_name)
    
    if coordinates:
        path = f"{city_name}_map.png"
        create_map(path, [city_name], [coordinates], color=color)  # Передаем цвет
        with open(path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
    else:
        bot.send_message(message.chat.id, 'Такого города я не знаю. Убедись, что он написан на английском!')

@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    user_id = message.chat.id
    city_name = ' '.join(message.text.split()[1:])
    
    if manager.add_city(user_id, city_name):
        bot.send_message(message.chat.id, f'Город {city_name} успешно сохранен!')
    else:
        bot.send_message(message.chat.id, 'Такого города я не знаю. Убедись, что он написан на английском!')

@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    user_id = message.chat.id
    cities = manager.select_cities(user_id)
    coordinates = [manager.get_coordinates(city) for city in cities]
    
    if cities:
        path = f"user_{user_id}_cities_map.png"
        create_map(path, cities, coordinates, color='blue')  # Цвет по умолчанию
        with open(path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
    else:
        bot.send_message(message.chat.id, 'Вы еще не добавили ни одного города.')
@bot.message_handler(commands=['cities_by_country'])
def handle_cities_by_country(message):
    country = ' '.join(message.text.split()[1:])
    cities = manager.select_cities_by_country(country)
    if cities:
        bot.send_message(message.chat.id, f"Города в {country}: {', '.join(cities)}")
    else:
        bot.send_message(message.chat.id, "Нет данных по этой стране.")

@bot.message_handler(commands=['cities_by_density'])
def handle_cities_by_density(message):
    try:
        min_density = int(message.text.split()[1])
        cities = manager.select_cities_by_density(min_density)
        if cities:
            bot.send_message(message.chat.id, f"Города с плотностью выше {min_density}: {', '.join(cities)}")
        else:
            bot.send_message(message.chat.id, "Нет данных.")
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "Введите число после команды.")

@bot.message_handler(commands=['time'])
def handle_time(message):
    city_name = ' '.join(message.text.split()[1:])
    city_time = manager.get_city_time(city_name)
    bot.send_message(message.chat.id, f"Время в {city_name}: {city_time}")

def create_map(filename, cities, coordinates, color='red'):
    plt.figure(figsize=(10, 5))
    plt.xlim(-180, 180)
    plt.ylim(-90, 90)
    
    

if __name__ == "__main__":
    manager = DB_Map(DATABASE)
    bot.polling()
