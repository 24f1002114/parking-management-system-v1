from .database import db
from decimal import Decimal
from datetime import datetime
class User(db.Model):
    id = db.Column(db.Integer(),primary_key = True)
    username = db.Column(db.String(),unique=True,nullable = False)
    email = db.Column(db.String(),unique = True, nullable = False)
    password = db.Column(db.String(),nullable= False)
    full_name = db.Column(db.String(),nullable= False)
    address = db.Column(db.String(),nullable= False)
    pin_code = db.Column(db.Integer(),nullable= False)
    type = db.Column(db.String(),default ="general")

    #One to many relationship with Reserve_parking_spot
    #A user can have multiple reservations
    #A reservation belongs to one user
    #backref allows us to access the user from the reservation
    #cascade="all, delete" means if a user is deleted, all their reservations are also deleted

    reservations = db.relationship("Reserve_parking_spot", backref="user", cascade="all, delete")

    
class Parking_lot(db.Model):
        id = db.Column(db.Integer(),primary_key = True)
        prime_location_name = db.Column(db.String(),nullable = False)
        price = db.Column(db.Numeric(10, 2),nullable = False)
        address = db.Column(db.String(),nullable = False)
        pin_code = db.Column(db.Integer(),nullable= False)
        maximum_number_of_spots = db.Column(db.Integer(),nullable = False)

        # One-to-many relationship with Parking_spot
        # A parking lot can have multiple parking spots 
        # A parking spot belongs to one parking lot
        # backref allows us to access the parking lot from the parking spot
        # cascade="all, delete" means if a parking lot is deleted, all its parking spots are also deleted

        spots = db.relationship("Parking_spot", backref="parking_lot", cascade="all, delete")

class Parking_spot(db.Model):
        id = db.Column(db.Integer(),primary_key = True)
        lot_id = db.Column(db.Integer(),db.ForeignKey("parking_lot.id"),nullable = False)
        spot_number = db.Column(db.Integer(),nullable = False)
        status = db.Column(db.String(),nullable = False)

        # One-to-one relationship with Reserve_parking_spot
        # A parking spot can have one reservation
        # A reservation belongs to one parking spot
        # backref allows us to access the parking spot from the reservation
        # uselist=False means that this relationship is one-to-one
        # cascade="all, delete" means if a parking spot is deleted, its reservation is also deleted
        
        reservation = db.relationship("Reserve_parking_spot", backref="spot", uselist=False, cascade="all, delete")

class Reserve_parking_spot(db.Model):
    id = db.Column(db.Integer(),primary_key = True)
    spot_id = db.Column(db.Integer(),db.ForeignKey("parking_spot.id"),nullable = False)
    user_id = db.Column(db.Integer(),db.ForeignKey("user.id"),nullable = False)
    parking_timestamp = db.Column(db.DateTime(),nullable = True)
    leaving_timestamp = db.Column(db.DateTime(),nullable = True)
    parking_cost = db.Column(db.Numeric(10, 2),nullable = True)
    vehicle_no = db.Column(db.String(),nullable = False)

    def calculate_cost(self):
        # Get parking lot price through spot -> lot
        price_per_hour = self.spot.parking_lot.price
        duration = datetime.now() - self.parking_timestamp
        hours = Decimal(str(duration.total_seconds())) / Decimal("3600")

        return round(price_per_hour * hours, 2)
    
    def calculate_cost_temp(self,temp):
        # Get parking lot price through spot -> lot
        price_per_hour = self.spot.parking_lot.price
        duration = temp - self.parking_timestamp
        hours = Decimal(str(duration.total_seconds())) / Decimal("3600")
        return round(price_per_hour * hours, 2)
