import sqlite3
from config import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

class DB_Map():
    def __init__(self, database):
        self.database = database

    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()

    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]  
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1
            else:
                return 0

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT cities.city 
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))

            cities = [row[0] for row in cursor.fetchall()]
            return cities

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT lat, lng
                            FROM cities  
                            WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates

    

        

    def draw_distance(self, city1, city2):
        pass
    def select_cities_by_country(self, country):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('SELECT city FROM cities WHERE country = ?', (country,))
            return [row[0] for row in cursor.fetchall()]

    def select_cities_by_density(self, min_density):
        
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('SELECT city FROM cities WHERE population_density >= ?', (min_density,))
            return [row[0] for row in cursor.fetchall()]

    def select_cities_by_country_and_density(self, country, min_density):
        
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('SELECT city FROM cities WHERE country = ? AND population_density >= ?', (country, min_density))
            return [row[0] for row in cursor.fetchall()]
    def get_city_time(self, city_name):
    
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('SELECT timezone_offset FROM cities WHERE city = ?', (city_name,))
            offset = cursor.fetchone()
            if offset:
                return f"UTC {offset[0]}"
            return "Часовой пояс не найден"
    def create_graph(self, path, cities):
        
        # Настройка карты
        fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})
        ax.set_global()
        ax.add_feature(cfeature.LAND, edgecolor='black')
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.COASTLINE)

        conn = sqlite3.connect(self.database)
        city_coordinates = []

        with conn:
            cursor = conn.cursor()
            for city in cities:
                cursor.execute('''SELECT lat, lng
                                FROM cities
                                WHERE city = ?''', (city,))
                coord = cursor.fetchone()
                if coord:
                    city_coordinates.append((city, coord[0], coord[1]))
        # Добавление точек на карту
        for city, lat, lng in city_coordinates:
            ax.plot(lng, lat, marker='o', color='red', markersize=5, transform=ccrs.PlateCarree())
            ax.text(lng + 0.5, lat + 0.5, city, fontsize=9, transform=ccrs.PlateCarree())
        
    
        plt.legend()
        plt.title("Города на карте")
        plt.xlabel("Долгота")
        plt.ylabel("Широта")
        plt.grid(True, linestyle='--', alpha=0.5)
        
        plt.savefig('graph.png')
        plt.close()
            

if __name__ == "__main__":
    m = DB_Map(DATABASE)
    m.create_user_table()
