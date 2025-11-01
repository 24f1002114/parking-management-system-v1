
from flask import flash,render_template,redirect,request,Blueprint,url_for,session
from models.model import *
from datetime import datetime
import matplotlib.pyplot as plt
from collections import Counter
import os

user_bp = Blueprint('user', __name__) # Create a Blueprint for admin-related routes, allowing modular organization of the app

@user_bp.route("/user/<int:user_id>", methods=['GET', 'POST'])
def user(user_id):
    this_user = User.query.get(user_id)
    if session.get('user_id') != user_id:
      flash("Unauthorized access")
      return redirect(url_for("admin.login"))
    if not this_user:
        return "User not found", 404
    raw_reservations = Reserve_parking_spot.query.filter_by(user_id=this_user.id).order_by(Reserve_parking_spot.parking_timestamp.desc()).all()
    latest_reservation = {}
    for r in raw_reservations:
    # Only keep the latest reservation per spot *for this user only*
     if r.spot_id not in latest_reservation:
        latest_reservation[r.spot_id] = r
    reservation = list(latest_reservation.values())
    prime_locations = [l[0] for l in Parking_lot.query.with_entities(Parking_lot.prime_location_name).distinct()]
    parking_lots = []
    query = None        
    if request.method == "POST":
            query = request.form.get("search")
            if query:
                parking_lots = Parking_lot.query.filter_by(prime_location_name=query).all()
            return render_template("user.html",this_user=this_user,prime_locations=prime_locations,parking_lots=parking_lots,query=query,  reservation=reservation,user_id=this_user.id)
    return render_template("user.html", this_user=this_user, reservation=reservation,prime_locations=prime_locations,user_id=this_user.id)

@user_bp.route("/release/<int:spot_id>", methods = ["GET","POST"])
def release(spot_id):
    spot = Parking_spot.query.get_or_404(spot_id)
    user_id = session.get('user_id')
    reservation = Reserve_parking_spot.query.filter_by(
        spot_id=spot.id, user_id=user_id, leaving_timestamp=None).first_or_404()
    temp_leaving_time = datetime.now()
    Estimated_cost = Reserve_parking_spot.calculate_cost_temp(reservation,temp_leaving_time)
    if request.method == "POST":
        # Save leaving time and cost
        Estimated_cost = Reserve_parking_spot.calculate_cost(reservation)
         # Update existing reservation
        reservation.leaving_timestamp = datetime.now()
        reservation.parking_cost = Estimated_cost
        spot.status = "A"
        db.session.commit()
        flash(f"Spot released successfully. Total cost ₹{Estimated_cost}")
        return redirect(url_for("user.user", user_id=reservation.user_id))
    return render_template("releasespot.html", spot=spot, reservation=reservation,temp_leaving_time=temp_leaving_time,estimated_cost=Estimated_cost,user_id=reservation.user_id)

@user_bp.route("/book/<int:lot_id>",methods=["GET","POST"])
def book_spot(lot_id):
    lot = Parking_lot.query.filter_by(id=lot_id).first()
    user_id = session.get('user_id')
    if not lot:
        flash("Parking lot not found")
        return redirect("/")
    available_spot = None
    for spot in lot.spots:
        if spot.status == 'A':
            available_spot = spot
            break
    if request.method == 'POST':
        if available_spot:
            vehicle_no = request.form.get("vehicle_no")
            if user_id is None:
                return "User not logged in", 403 
            reservation = Reserve_parking_spot(user_id=user_id,  
                                      spot_id=available_spot.id,
                                      vehicle_no=vehicle_no,
                                      parking_timestamp=datetime.now()
                                      )
            available_spot.status = 'O'
            db.session.add(reservation)
            db.session.commit()
            flash("Spot reserved successfully!")
            return redirect(url_for("user.user", user_id=user_id))
        else:
            flash("Lot is full")
    return render_template("bookspot.html", spot=available_spot,user_id=user_id)

@user_bp.route("/usersummary")
def summary():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
    this_user = User.query.get(user_id)
    if not this_user:
        return redirect(url_for("login"))
    # Get all reservations by this user
    reservations = Reserve_parking_spot.query.filter_by(user_id=user_id).all()
    # Extract parking lot names
    lot_names = []
    for r in reservations:
        if r.spot and r.spot.parking_lot:
            lot_names.append(r.spot.parking_lot.prime_location_name)
        else:
            lot_names.append("Unknown")
    # Count usage
    lot_counts = dict(Counter(lot_names))
    # Extract keys and values for plotting
    location_names = list(lot_counts.keys())
    reservation_counts = list(lot_counts.values())
    # Plot bar chart
    location_names = [
    r.spot.parking_lot.prime_location_name
    if r.spot and r.spot.parking_lot else "Unknown"
    for r in reservations]
    # Count how many times each location was used
    location_counts = Counter(location_names)
    # Prepare data
    x_labels = list(location_counts.keys())
    y_values = list(location_counts.values())
    # Plot
    plt.figure(figsize=(6, 4), dpi=100)
    plt.bar(x_labels, y_values, color='mediumseagreen', edgecolor='black', width =0.3)
    plt.title("Total Reservations per Location")
    plt.xlabel("Location")
    plt.ylabel("Number of Reservations")
    plt.tight_layout()
    chart_path = os.path.join("static", f"summary_chart_user{this_user.id}.png")
    plt.savefig(chart_path, bbox_inches='tight')
    plt.close()
    return render_template(
        "usersummary.html",
        this_user=this_user,
        chart_path=chart_path,
        reservations=reservations)

@user_bp.route("/profile/<int:user_id>", methods=["GET", "POST"])
def profile(user_id):
    this_user = User.query.get_or_404(user_id)

    if session.get("user_id") != user_id:
        flash("Unauthorized access")
        return redirect(url_for("admin.login"))

    if request.method == "POST":
        this_user.full_name = request.form.get("full_name")
        this_user.email = request.form.get("email")
        this_user.address = request.form.get("address")
        this_user.pin_code = request.form.get("pin_code")
        db.session.commit()
        flash("Profile updated successfully!")

    return render_template("userprofile.html", this_user=this_user)
