from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    adress = db.Column(db.String(120), nullable=True)
    pin_code = db.Column(db.String(10), nullable=False)


    isUser = db.Column(db.Boolean, default=True)
    isAdmin = db.Column(db.Boolean, default=False)

    reservations = db.relationship('Reserve_parking_spot', backref='user', lazy=True)

class Parking_lot(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    prime_location_name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    adress = db.Column(db.String(120), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    maximum_number_of_spots = db.Column(db.Integer, nullable=False)

    spots = db.relationship('Parking_spot', backref='lot', lazy=True, cascade='all, delete-orphan')


class Parking_spot(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    lot_id = db.Column(db.Integer(), db.ForeignKey('parking_lot.id'), nullable=False)
    status = db.Column(db.String(1), nullable=False)  # 'A' and 'O' only, 'A' for available, 'O' for occupied

    reservations = db.relationship('Reserve_parking_spot', backref='spot', lazy=True)


class Reserve_parking_spot(db.Model):
    id= db.Column(db.Integer(), primary_key=True)
    spot_id = db.Column(db.Integer(), db.ForeignKey('parking_spot.id'), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    parking_timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    parking_cost = db.Column(db.Float, nullable=True)


def create_default_admin():
    admin = User.query.filter_by(email='admin@spotfinder.com').first()
    if not admin:
        admin = User(

            name='Admin',
            email='admin@spotfinder.com',
            password='admin123',
            adress='Chennai',
            pin_code='600001',
            isUser=False,
            isAdmin=True
        )
        db.session.add(admin)
        db.session.commit()
        print('Default admin created: admin@spotfinder.com / admin123')