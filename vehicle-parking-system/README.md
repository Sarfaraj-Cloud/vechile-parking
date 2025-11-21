# vehicle-parking-system
This is a dummy project that allows users to book parking lot for their vehicles.
# SpotFinder - Smart Parking Management System

A comprehensive web-based parking management system built with Flask that allows users to find, book, and manage parking spots while providing administrators with powerful tools to manage parking lots and monitor occupancy.

## Features

### For Users
- **User Registration & Authentication** - Secure account creation and login system
- **Real-time Spot Availability** - View live parking spot availability across all locations
- **Instant Booking** - Book available parking spots with one click
- **Booking Management** - View current bookings and release spots when done
- **Booking History** - Complete history of past parking sessions with costs
- **Automatic Cost Calculation** - Transparent pricing based on hourly rates and duration

### For Administrators
- **Admin Dashboard** - Comprehensive overview of all parking operations
- **Parking Lot Management** - Create, edit, and delete parking lots
- **Spot Monitoring** - Real-time monitoring of all parking spots and their status
- **Detailed Analytics** - View occupancy statistics and revenue data
- **User Management** - Monitor user bookings and system usage

### System Features
- **Responsive Design** - Works seamlessly on desktop and mobile devices
- **Real-time Updates** - Live status updates for parking availability
- **Secure Sessions** - Session-based authentication and authorization
- **Data Persistence** - SQLite database for reliable data storage
- **Bootstrap UI** - Modern, clean, and intuitive user interface

## 🛠 Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Authentication**: Flask Sessions
- **Templating**: Jinja2

## Default Admin Account

When you first run the application, a default admin account is automatically created:

- **Email**: `admin@spotfinder.com`
- **Password**: `admin123`

**Important**: Change these credentials after your first login for security purposes.

## Project Structure

parking-system/
│
├── app.py                 # Main Flask application
├── models/
│   └── models.py         # Database models and schema
├── templates/
│   ├── layouts/
│   │   └── bootstrap.html # Base template
│   ├── BasicComponents/
│   │   └── navbar.html   # Navigation component
│   ├── home.html         # Landing page
│   ├── access.html       # Access selection page
│   ├── accesslogin.html  # Login page
│   ├── accessregister.html # Registration page
│   ├── admin_dashboard.html # Admin dashboard
│   ├── user_dashboard.html  # User dashboard
│   ├── edit_lot.html     # Edit parking lot page
│   └── lot_details.html  # Parking lot details page
└── udata.sqlite3        # SQLite database (created automatically)


## 🗄 Database Schema

The system uses four main database tables:

### Users
- User information and authentication
- Role-based access (User/Admin)

### Parking Lots
- Location details and pricing
- Maximum capacity information

### Parking Spots
- Individual spot status (Available/Occupied)
- Linked to specific parking lots

### Reservations
- Booking records with timestamps
- Cost calculations and parking duration

## Security Features

- **Session-based Authentication** - Secure user sessions
- **Role-based Access Control** - Separate admin and user interfaces
- **Input Validation** - Server-side validation for all forms
- **Password Protection** - Secure password handling
- **Access Restrictions** - Protected admin routes

## User Guide

### For Regular Users:

1. **Registration**: Create an account with your details
2. **Login**: Access your dashboard with your credentials
3. **Browse Locations**: View available parking lots and their real-time availability
4. **Book a Spot**: Select a parking lot and book an available spot instantly
5. **Manage Booking**: View your current booking details and release when done
6. **View History**: Check your complete parking history and costs

### For Administrators:

1. **Login**: Use admin credentials to access the admin dashboard
2. **Create Parking Lots**: Add new parking locations with pricing and capacity
3. **Manage Lots**: Edit existing lots or delete unused ones
4. **Monitor Usage**: View real-time occupancy and system statistics
5. **View Details**: Check individual lot details and current reservations

## Advanced Features

- **Automatic Cost Calculation**: System calculates parking costs based on duration and hourly rates
- **Real-time Availability**: Live updates of parking spot availability
- **Booking Validation**: Prevents double-booking and ensures data integrity
- **Responsive Design**: Optimized for all device sizes
- **Flash Messaging**: User-friendly notifications and error messages

## 🛠 Configuration

### Database Configuration
The application uses SQLite by default. To change the database:

app.config['SQLALCHEMY_DATABASE_URI'] = 'your-database-url'

This project is licensed under the MIT License - see the LICENSE file for details.
