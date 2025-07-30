from flask import flash,render_template,redirect,request,Blueprint, url_for,session
from models.model import *
import matplotlib.pyplot as plt

admin_bp = Blueprint('admin', __name__) # Create a Blueprint for admin-related routes, allowing modular organization of the app

@admin_bp.route("/login",methods=["GET","POST"]) 
def login():
    if request.method == "POST":
        username = request.form.get("username")
        pwd = request.form.get("pwd")
        this_user = User.query.filter_by(username=username).first() 
        if this_user:
            if this_user.password == pwd:
                if this_user.type == "admin":
                    return redirect(url_for('admin.admin')) # Redirect to admin dashboard
                else:
                    session['user_id'] = this_user.id
                    return redirect(url_for('user.user', user_id=this_user.id)) # Redirect to user dashboard
            else:
                 flash("Incorrect Password")             
        else:
            flash("User does not exist")        
    return render_template("login.html")

@admin_bp.route("/signup",methods=["GET","POST"]) 
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email= request.form.get("email")
        pwd = request.form.get("pwd")
        fullname = request.form.get("fullname")
        address = request.form.get("address")
        pin_code = request.form.get("pin")
        user_name = User.query.filter_by(username=username).first()
        user_email = User.query.filter_by(email=email).first()
        if user_name or user_email:
            flash("User already exists")
        else:
            new_user = User(username=username, email=email, password=pwd, full_name=fullname, address=address, pin_code=pin_code) #LHS attribute name in table, RHS is data fetched from form
            db.session.add(new_user)
            db.session.commit()
            return redirect("/login")    
    return render_template("signup.html")

@admin_bp.route("/admin")
def admin():
    this_user = User.query.filter_by(type="admin").first()  
    users = User.query.all()
    parking_lots = Parking_lot.query.all()
    return render_template("admin.html", users=users, parking_lots=parking_lots, this_user=this_user)

@admin_bp.route("/addlot", methods=["GET", "POST"])
def add_lot():
    if request.method == "POST":
        prime_location_name = request.form.get("prime_location_name")
        price = request.form.get("price")
        address = request.form.get("address")
        pin_code = request.form.get("pin")
        maximum_number_of_spots = int(request.form.get("maximum_number_of_spots"))
        spots = []
        for i in range(maximum_number_of_spots):
            spot = Parking_spot(spot_number=i+1, status='A')
            spots.append(spot)
        new_lot = Parking_lot(prime_location_name=prime_location_name, price=price, address=address, pin_code=pin_code, maximum_number_of_spots=maximum_number_of_spots, spots=spots)
        db.session.add(new_lot)
        db.session.commit()
        return redirect(url_for('admin.admin'))
    return render_template("add_lot.html")

@admin_bp.route("/editlot/<int:lot_id>", methods=["GET", "POST"])
def edit_lot(lot_id):
    lot= Parking_lot.query.filter_by(id=lot_id).first()
    if request.method == "POST":
        lot.prime_location_name = request.form.get("prime_location_name")
        lot.price = request.form.get("price")
        lot.address = request.form.get("address")
        lot.pin_code = request.form.get("pin")
        new_max = int(request.form.get("maximum_number_of_spots"))
        old_max = lot.maximum_number_of_spots
        if new_max > old_max:  # Add new spots
            for i in range(old_max + 1, new_max + 1):
                lot.spots.append(Parking_spot(spot_number=i, status='A'))
        elif new_max < old_max: # Find highest occupied spot number
            occupied_spots = [spot.spot_number for spot in lot.spots if spot.status == 'O']
            if occupied_spots:
                highest_occupied = max(occupied_spots)
            else:
                highest_occupied = -1  # No occupied spots
            if new_max <= highest_occupied:
                flash(f"Cannot reduce spots below occupied spot number {highest_occupied}.")
                return redirect(url_for("admin.edit_lot",lot_id))        
            for spot in lot.spots:
                if spot.spot_number > new_max and spot.status == 'A':
                    db.session.delete(spot)   # Safe to delete unoccupied spots
        lot.maximum_number_of_spots = new_max    
        db.session.commit()
        return redirect(url_for("admin.admin"))
    return render_template("edit_lot.html", lot=lot)

@admin_bp.route("/deletelot/<int:lot_id>")
def delete_lot(lot_id): 
    lot = Parking_lot.query.filter_by(id=lot_id).first()
    if lot and all(spot.status == 'A' for spot in lot.spots):  # check for AVAILABLE spots only
        db.session.delete(lot)  # This will also delete related spots due to cascade
        db.session.commit()
        flash("Parking lot deleted successfully.")
    else:
        flash("Cannot delete lot: some spots are still occupied.")
    return redirect(url_for("admin.admin"))

@admin_bp.route("/spot/<int:spot_id>", methods=["GET", "POST"])
def view_spot(spot_id):
    spot = Parking_spot.query.get(spot_id)
    if not spot:
        flash("Spot not found.")
        return redirect("/admin")
    if request.method == "POST":
        if spot.status == 'A':
            lot_id = spot.lot_id
            db.session.delete(spot)
            db.session.commit()
            # Renumber remaining spots for the same lot
            remaining_spots = Parking_spot.query.filter_by(lot_id=lot_id).order_by(Parking_spot.spot_number).all()
            for index, s in enumerate(remaining_spots, start=1):
                s.spot_number = index
            db.session.commit()
            flash("Spot deleted and spots renumbered.")
            return redirect("/admin")
        else:
            flash("Cannot delete: Spot is occupied.")
    return render_template("viewspot.html", spot=spot)

@admin_bp.route("/occupiedspots/<int:spot_id>")
def occupied_spot(spot_id):
    spot = Parking_spot.query.get(spot_id)
    if spot and spot.status == 'O':
        # Fetch latest reservation for the spot
        latest_reservation = Reserve_parking_spot.query.filter_by(spot_id=spot_id,leaving_timestamp=None).order_by(Reserve_parking_spot.parking_timestamp.desc()).first()
        if latest_reservation:
            return render_template("Occupied_spot_details.html", spot=spot, reservation=latest_reservation)
    return redirect(url_for("admin.admin"))

@admin_bp.route("/registered_users")
def registered_users():
    this_user = User.query.filter_by(type='admin').first()
    users = User.query.filter(User.type != "admin").all()
    return render_template("registereduser.html",users=users,this_user=this_user)

@admin_bp.route("/adminprofile", methods=["GET", "POST"])
def profile():
    admin = User.query.filter_by(type="admin").first()
    if request.method == "POST":
        admin.full_name = request.form.get("full_name")
        admin.email = request.form.get("email")
        admin.address = request.form.get("address")
        admin.pin_code = int(request.form.get("pin_code") or 0)
        db.session.commit()
        flash("Admin profile updated successfully!")

    return render_template("adminprofile.html", admin=admin,this_user=admin)



