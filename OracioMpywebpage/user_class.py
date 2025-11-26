class User:
    """Class to represent a user account in the car rental system"""
    
    def __init__(self, name, email, user_id=None):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password
        self.rentals = []
    
    def add_rental(self, rental):
        """Add a rental to user's rental history"""
        self.rentals.append(rental)
        print(f"Rental added for {self.name}")
    
    def view_rentals(self):
        """Display all rentals for this user"""
        if not self.rentals:
            print(f"{self.name} has no rentals yet.")
        else:
            print(f"\nRentals for {self.name}:")
            for i, rental in enumerate(self.rentals, 1):
                print(f"  {i}. {rental}")
    
    def __str__(self):
        return f"User: {self.name} (Email: {self.email})"
