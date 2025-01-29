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

def create_map(filename, cities, coordinates, color='red'):
    plt.figure(figsize=(10, 5))
    plt.xlim(-180, 180)
    plt.ylim(-90, 90)
    
    # Отображение точек городов
    for city, coord in zip(cities, coordinates):
        if coord:
            plt.scatter(coord[1], coord[0], c=color, label=city, edgecolors='black', s=100)
    
    plt.legend()
    plt.title("Города на карте")
    plt.xlabel("Долгота")
    plt.ylabel("Широта")
    plt.grid(True, linestyle='--', alpha=0.5)
    
    plt.savefig(filename)
    plt.close()

if __name__ == "__main__":
    manager = DB_Map(DATABASE)
    bot.polling()
