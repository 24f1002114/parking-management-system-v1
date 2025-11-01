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
            return render_template("occupied_spot_details.html", spot=spot, reservation=latest_reservation)
    return redirect(url_for("admin.admin"))

@admin_bp.route("/registered_users")
def registered_users():
    this_user = User.query.filter_by(type='admin').first()
    users = User.query.filter(User.type != "admin").all()
    return render_template("registereduser.html",users=users,this_user=this_user)

@admin_bp.route("/search",methods=["GET","POST"])
def search():
    this_user = User.query.filter_by(type='admin').first()
    lots = []
    user_details = None
     # To hold a "no match" message

    if request.method == "POST":
        search_type = request.form.get("search")
        search_string = request.form.get("search_string")

        if search_type == "location":
            lots = Parking_lot.query.filter(
                Parking_lot.prime_location_name.ilike(f"%{search_string}%")).all()
            if not lots:
                flash("No parking lots found with that location.")

        elif search_type == "user_id":
            try:
                user_id = int(search_string)
                user_details = User.query.get(user_id)
                if not user_details:
                    message = "No user found with that ID."
            except ValueError:
                flash("Invalid User ID format.")

    return render_template(
        "search.html",
        this_user=this_user,
        lots=lots,
        user_details=user_details,
        
    )


@admin_bp.route("/summary")
def summary():
    this_user = User.query.filter_by(type='admin').first()
    lots = Parking_lot.query.all()
    revenue_data = []
    labels = []
    for lot in lots:
        total_revenue = 0
        for spot in lot.spots:
            if spot.reservation and spot.reservation.parking_cost:
                total_revenue += float(spot.reservation.parking_cost)
        revenue_data.append(total_revenue)
        labels.append(lot.prime_location_name)

    # Status of all spots
    occupied = Parking_spot.query.filter_by(status="O").count()
    available = Parking_spot.query.filter_by(status="A").count()

    # --- Generate Pie Chart: Revenue from Lots ---
    fig1, ax1 = plt.subplots()
    ax1.pie(revenue_data, labels=labels, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    pie_path = "static/revenue_pie.png"
    fig1.savefig(pie_path)
    plt.close(fig1)

    # --- Generate Bar Chart: Spot Status ---
    fig2, ax2 = plt.subplots()
    ax2.bar(["Occupied", "Available"], [occupied, available], color=['coral', 'skyblue'])
    ax2.set_ylabel("Spots")
    ax2.set_title("Spot Availability Summary")
    bar_path = "static/spot_bar.png"
    fig2.savefig(bar_path)
    plt.close(fig2)

    return render_template("summaryadmin.html", pie_chart=pie_path, bar_chart=bar_path,this_user=this_user)
    
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



