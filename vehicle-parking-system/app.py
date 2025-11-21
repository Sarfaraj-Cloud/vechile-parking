from flask import Flask, request, render_template, redirect, url_for, session, flash
from models.models import db, User, Parking_lot, Parking_spot, Reserve_parking_spot, create_default_admin

app = Flask(__name__)  #Object of Flask class

#Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///udata.sqlite3'
app.config['SECRET_KEY'] = 'AaBbCcDd'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Connect to the database and make in context adn create the database
db.init_app(app)
app.app_context().push()
db.create_all()  #Create or update the database schema

create_default_admin()

def get_current_user():
    id=session.get('id')
    if id:
        return User.query.get(id)
    return None

@app.route('/')
def index():
    total_lots = Parking_lot.query.count()
    parking_lots = Parking_lot.query.all()
    
    # Calculate stats for each parking lot
    for lot in parking_lots:
        spots = Parking_spot.query.filter_by(lot_id=lot.id).all()
        lot.available_count = len([spot for spot in spots if spot.status == 'A'])
        lot.occupied_count = len([spot for spot in spots if spot.status == 'O'])
    
    # Calculate overall stats
    all_spots = Parking_spot.query.all()
    total_spots = len(all_spots)
    occupied_spots = len([spot for spot in all_spots if spot.status == 'O'])
    available_spots = total_spots - occupied_spots
    
    return render_template('index.html', 
                         total_lots=total_lots,
                         total_spots=total_spots,
                         occupied_spots=occupied_spots,
                         available_spots=available_spots,
                         parking_lots=parking_lots)
    

@app.route('/accesslogin')
def accesslogin():
    return render_template('accesslogin.html')

@app.route('/accessregister')
def accessregister():
    return render_template('accessregister.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    u = User.query.filter_by(email=email, password=password).first()
    
    if u:
        session['id'] = u.id
        if u.isAdmin:
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))

    flash('Invalid Email or Password!')
    return redirect(url_for('accesslogin'))

@app.route('/register', methods=['POST'])
def register():
    name=request.form.get('name')
    email=request.form.get('email')
    password1=request.form.get('password1')
    password2=request.form.get('password2')
    adress=request.form.get('adress')
    pin_code=request.form.get('pin_code')

    #check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash('User with this email already exists!')
        return redirect(url_for('accesslogin'))
    
    #check if password match
    if password1 != password2:
        flash('Passwords do not match!')
        return redirect(url_for('accessregister'))
    
    #create new user
    new_user = User(name=name, email=email, password=password1, adress=adress, pin_code=pin_code, isUser=True, isAdmin=False)
    db.session.add(new_user)
    db.session.commit()

    flash('Registration successful! Please login.')
    return redirect(url_for('accessregister'))

@app.route('/admin_dashboard')
def admin_dashboard():
    user=get_current_user()
    if not user or not user.isAdmin:
        flash('Access denied!')
        return redirect(url_for('accesslogin'))
    
    parking_lots = Parking_lot.query.all()
    
    # Calculate stats for each parking lot
    for lot in parking_lots:
        spots = Parking_spot.query.filter_by(lot_id=lot.id).all()
        lot.available_count = len([spot for spot in spots if spot.status == 'A'])
        lot.occupied_count = len([spot for spot in spots if spot.status == 'O'])
    
    # Calculate overall stats
    all_spots = Parking_spot.query.all()
    total_spots = len(all_spots)
    occupied_spots = len([spot for spot in all_spots if spot.status == 'O'])
    available_spots = total_spots - occupied_spots

    all_users = user.query.all()
    
    return render_template('admin_dashboard.html', 
                         user=user, 
                         parking_lots=parking_lots,
                         total_spots=total_spots,
                         occupied_spots=occupied_spots,
                         available_spots=available_spots,
                         all_users=all_users)

@app.route('/user_dashboard')
def user_dashboard():
    user=get_current_user()
    if not user or not user.isUser:
        flash('Access denied!')
        return redirect(url_for('accesslogin'))
    
    parking_lots = Parking_lot.query.all()
    
    # Calculate stats for each parking lot
    for lot in parking_lots:
        spots = Parking_spot.query.filter_by(lot_id=lot.id).all()
        lot.available_count = len([spot for spot in spots if spot.status == 'A'])
        lot.occupied_count = len([spot for spot in spots if spot.status == 'O'])
    
    # Get current booking (if any)
    current_booking = Reserve_parking_spot.query.filter_by(
        user_id=user.id, 
        leaving_timestamp=None
    ).first()
    
    # Get booking history
    booking_history = Reserve_parking_spot.query.filter_by(user_id=user.id).order_by(
        Reserve_parking_spot.parking_timestamp.desc()
    ).all()
    
    return render_template('user_dashboard.html', 
                         user=user, 
                         parking_lots=parking_lots,
                         current_booking=current_booking,
                         booking_history=booking_history)

@app.route('/book_spot/<int:lot_id>')
def book_spot(lot_id):
    user = get_current_user()
    if not user or not user.isUser:
        flash('Access denied!')
        return redirect(url_for('accesslogin'))
    
    # Check if user already has an active booking
    existing_booking = Reserve_parking_spot.query.filter_by(
        user_id=user.id, 
        leaving_timestamp=None
    ).first()
    
    if existing_booking:
        flash('You already have an active booking! Please release it first.')
        return redirect(url_for('user_dashboard'))
    
    # Find first available spot in the lot
    available_spot = Parking_spot.query.filter_by(
        lot_id=lot_id, 
        status='A'
    ).first()
    
    if not available_spot:
        flash('No available spots in this parking lot!')
        return redirect(url_for('user_dashboard'))
    
    # Create booking
    from datetime import datetime
    new_booking = Reserve_parking_spot(
        spot_id=available_spot.id,
        user_id=user.id,
        parking_timestamp=datetime.utcnow()
    )
    
    # Mark spot as occupied
    available_spot.status = 'O'
    
    db.session.add(new_booking)
    db.session.commit()
    
    lot = Parking_lot.query.get(lot_id)
    flash(f'Spot booked successfully at {lot.prime_location_name}! Your spot ID is {available_spot.id}.')
    return redirect(url_for('user_dashboard'))

@app.route('/release_spot/<int:booking_id>')
def release_spot(booking_id):
    user = get_current_user()
    if not user or not user.isUser:
        flash('Access denied!')
        return redirect(url_for('accesslogin'))
    
    # Get the booking
    booking = Reserve_parking_spot.query.filter_by(
        id=booking_id, 
        user_id=user.id,
        leaving_timestamp=None
    ).first()
    
    if not booking:
        flash('Booking not found or already released!')
        return redirect(url_for('user_dashboard'))
    
    # Calculate parking cost
    from datetime import datetime
    leaving_time = datetime.utcnow()
    parking_duration = (leaving_time - booking.parking_timestamp).total_seconds() / 3600  # hours
    lot = booking.spot.lot
    parking_cost = parking_duration * lot.price
    
    # Update booking
    booking.leaving_timestamp = leaving_time
    booking.parking_cost = round(parking_cost, 2)
    
    # Mark spot as available
    booking.spot.status = 'A'
    
    db.session.commit()
    
    flash(f'Spot released successfully! Parking duration: {parking_duration:.2f} hours. Total cost: ₹{parking_cost:.2f}')
    return redirect(url_for('user_dashboard'))

@app.route('/create_lot', methods=['POST'])
def create_lot():
    user = get_current_user()
    if not user or not user.isAdmin:
        flash('Access denied!')
        return redirect(url_for('accesslogin'))
    
    prime_location_name = request.form.get('prime_location_name')
    adress = request.form.get('adress')
    pin_code = request.form.get('pin_code')
    price = float(request.form.get('price'))
    maximum_number_of_spots = int(request.form.get('maximum_number_of_spots'))
    
    # Create parking lot
    new_lot = Parking_lot(
        prime_location_name=prime_location_name,
        adress=adress,
        pin_code=pin_code,
        price=price,
        maximum_number_of_spots=maximum_number_of_spots
    )
    db.session.add(new_lot)
    db.session.commit()
    
    # Create parking spots for this lot
    for i in range(maximum_number_of_spots):
        spot = Parking_spot(lot_id=new_lot.id, status='A')
        db.session.add(spot)
    
    db.session.commit()
    flash(f'Parking lot "{prime_location_name}" created successfully with {maximum_number_of_spots} spots!')
    return redirect(url_for('admin_dashboard'))

@app.route('/view_lot_details/<int:lot_id>')
def view_lot_details(lot_id):
    user = get_current_user()
    if not user or not user.isAdmin:
        flash('Access denied!')
        return redirect(url_for('accesslogin'))
    
    lot = Parking_lot.query.get_or_404(lot_id)
    spots = Parking_spot.query.filter_by(lot_id=lot_id).all()
    
    from datetime import datetime
    current_time = datetime.utcnow()

    # Get reservation details for occupied spots
    for spot in spots:
        if spot.status == 'O':
            reservation = Reserve_parking_spot.query.filter_by(spot_id=spot.id, leaving_timestamp=None).first()
            if reservation:
                spot.reservation = reservation
                duration_seconds = (current_time - reservation.parking_timestamp).total_seconds()
                duration_hours = duration_seconds / 3600
                spot.duration_hours = round(duration_hours, 2)
                spot.current_cost = round(duration_hours * lot.price, 2)
    
    
    return render_template('lot_details.html', user=user, lot=lot, spots=spots)

@app.route('/edit_lot/<int:lot_id>')
def edit_lot(lot_id):
    user = get_current_user()
    if not user or not user.isAdmin:
        flash('Access denied!')
        return redirect(url_for('accesslogin'))
    
    lot = Parking_lot.query.get_or_404(lot_id)
    return render_template('edit_lot.html', user=user, lot=lot)

@app.route('/update_lot/<int:lot_id>', methods=['POST'])
def update_lot(lot_id):
    user = get_current_user()
    if not user or not user.isAdmin:
        flash('Access denied!')
        return redirect(url_for('accesslogin'))
    
    lot = Parking_lot.query.get_or_404(lot_id)
    
    lot.prime_location_name = request.form.get('prime_location_name')
    lot.adress = request.form.get('adress')
    lot.pin_code = request.form.get('pin_code')
    lot.price = float(request.form.get('price'))
    
    new_max_spots = int(request.form.get('maximum_number_of_spots'))
    current_spots = Parking_spot.query.filter_by(lot_id=lot_id).count()
    
    if new_max_spots > current_spots:
        # Add new spots
        for i in range(new_max_spots - current_spots):
            spot = Parking_spot(lot_id=lot_id, status='A')
            db.session.add(spot)
    elif new_max_spots < current_spots:
        # Remove spots (only available ones)
        spots_to_remove = current_spots - new_max_spots
        available_spots = Parking_spot.query.filter_by(lot_id=lot_id, status='A').limit(spots_to_remove).all()
        
        if len(available_spots) < spots_to_remove:
            flash('Cannot reduce spots: Some spots are currently occupied!')
            return redirect(url_for('edit_lot', lot_id=lot_id))
        
        for spot in available_spots:
            db.session.delete(spot)
    
    lot.maximum_number_of_spots = new_max_spots
    db.session.commit()
    
    flash(f'Parking lot "{lot.prime_location_name}" updated successfully!')
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_lot/<int:lot_id>')
def delete_lot(lot_id):
    user = get_current_user()
    if not user or not user.isAdmin:
        flash('Access denied!')
        return redirect(url_for('accesslogin'))
    
    lot = Parking_lot.query.get_or_404(lot_id)
    
    # Check if any spots are occupied
    occupied_spots = Parking_spot.query.filter_by(lot_id=lot_id, status='O').count()
    if occupied_spots > 0:
        flash('Cannot delete parking lot: Some spots are currently occupied!')
        return redirect(url_for('admin_dashboard'))
    
    # Delete all spots and the lot
    Parking_spot.query.filter_by(lot_id=lot_id).delete()
    db.session.delete(lot)
    db.session.commit()
    
    flash(f'Parking lot "{lot.prime_location_name}" deleted successfully!')
    return redirect(url_for('admin_dashboard'))

@app.route('/get_spot_details/<int:spot_id>')
def get_spot_details(spot_id):
    """Get detailed information about a specific parking spot"""
    user = get_current_user()
    if not user or not user.isAdmin:
        return {'error': 'Access denied'}, 403
    
    spot = Parking_spot.query.get_or_404(spot_id)
    lot = spot.lot
    
    result = {
        'spot_id': spot.id,
        'status': spot.status,
        'lot_name': lot.prime_location_name,
        'lot_price': lot.price,
        'reservation': None
    }
    
    # If spot is occupied, get reservation details
    if spot.status == 'O':
        reservation = Reserve_parking_spot.query.filter_by(
            spot_id=spot_id, 
            leaving_timestamp=None
        ).first()
        
        if reservation:
            result['reservation'] = {
                'user_name': reservation.user.name,
                'parking_time': reservation.parking_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'user_email': reservation.user.email
            }
    
    return result



@app.route('/logout')
def logout():
    session.pop('id', None)
    return redirect(url_for('accesslogin'))

if __name__ == '__main__':
    app.run(debug=True)
        

