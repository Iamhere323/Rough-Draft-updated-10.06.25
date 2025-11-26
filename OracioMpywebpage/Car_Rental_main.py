import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import json
import webview
from datetime import datetime, timedelta
from Car_class import Car
from CarInventory_class import CarInventory
from Rental_class import Rental
from user_class import User



def get_data_folder():
    folder = os.path.join(os.getenv('LOCALAPPDATA'), 'CarRentalApp')
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder

def save_json(filename, data):
    path = os.path.join(get_data_folder(), filename)
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

def load_json(filename, default=None):
    path = os.path.join(get_data_folder(), filename)
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return default if default is not None else []
    return default if default is not None else []


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class CarRentalAPI:
    def __init__(self):
        self.inventory = CarInventory()
        self.users = self.load_users()
        self.load_inventory_from_file(resource_path("List_of_Rental_Cars.txt"))

    
    def load_inventory_from_file(self, filename):
        try:
            with open(filename, 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line or line.lower().startswith("car_id"):
                        continue
                    parts = line.split(',')
                    if len(parts) != 6:
                        continue
                    car_id, make, model, year, car_type, is_available = parts
                    try:
                        car = Car(
                            car_id=int(car_id),
                            make=make,
                            model=model,
                            year=int(year),
                            car_type=car_type,
                            is_available=is_available.strip().lower() == 'true'
                        )
                        self.inventory.add_car(car)
                    except ValueError:
                        continue
        except FileNotFoundError:
            print(f"File not found: {filename}")

    
    def load_users(self):
        data = load_json("users.json", [])
        users = {}
        for u in data:
            user = User(u["name"], u["email"], u["password"], u.get("user_id", 0))
            user.rentals = []  # Load rentals if you want
            users[u["email"]] = user
        return users

    def save_users(self):
        data = []
        for user in self.users.values():
            data.append({
                "name": user.name,
                "email": user.email,
				"password": user.password,
                "user_id": user.user_id
            })
        save_json("users.json", data)

    def register(self, name, password, email):
        email = email.lower()
        if email in self.users:
            return {"success": False, "message": "User already exists. Please login."}

        user_id = len(self.users) + 1
        user = User(name, email, password, user_id)
        self.users[email] = user
        self.save_users()
        return {"success": True, "message": f"User {name} registered successfully."}

    
    def login(self, email, password):
	    email = email.lower()
	    if email in self.users:
	        user = self.users[email]
	        if user.password == password:
	            return {"success": True, "name": user.name}
	        else:
	            return {"success": False, "message": "Incorrect password."}
	    return {"success": False, "message": "User not found. Please register."}

    
    def get_available_cars(self):
        cars = []
        for car in self.inventory.cars.values():
            if car.is_available:
                cars.append({
                    "id": car.car_id,
                    "make": car.make,
                    "model": car.model,
                    "year": car.year,
                    "type": car.car_type
                })
        return cars

    
    def rent_car(self, car_id, email, duration_days):
        email = email.lower()
        if email not in self.users:
            return {"success": False, "message": "User not found."}

        try:
            car_id = int(car_id)
            duration_days = int(duration_days)
        except ValueError:
            return {"success": False, "message": "Invalid input."}

        car = self.inventory.rent_car(car_id)
        if not car:
            return {"success": False, "message": "Car not available."}

        user = self.users[email]
        rental = Rental(car_id, user, car, duration_days)
        user.add_rental(rental)
        return {"success": True, "message": f"You successfully rented {car.make} {car.model} for {duration_days} days."}

    
    def get_rentals(self, email):
        email = email.lower()
        if email not in self.users:
            return []
        user = self.users[email]
        rentals = []
        for rental in user.rentals:
            rentals.append({
                "car": f"{rental.car.make} {rental.car.model}",
                "duration": rental.duration_days,
                "from": rental.start_date.strftime("%Y-%m-%d"),
                "to": rental.return_date.strftime("%Y-%m-%d")
            })
        return rentals


if __name__ == "__main__":
    api = CarRentalAPI()
    window = webview.create_window(
        "Car Rental System",
        resource_path("index.html"),
        width=1000,
        height=700,
        resizable=True,
        js_api=api
    )
    webview.start()
