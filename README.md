# Vehicle Parking Management System
A Flask-based full-stack web app that streamlines parking lot management for admins and users, featuring real-time booking, analytics.

## Author
**Name:** Anshul Shakya  
**Email:** 24f1002114@ds.study.iitm.ac.in  

---

## 🧩 Project Description
This project is a **multi-user vehicle parking management system** built using **Flask**, **SQLite**, and **Bootstrap**.  
It allows:
- **Admins** to manage parking lots, view spot statuses, and generate reports.
- **Users** to register, book, and release parking spots.  

The application integrates backend logic with a clean frontend UI and proper database management, ensuring a seamless experience.

---

## 🧠 Technologies Used

| SN | Technology | Purpose |
|----|-------------|----------|
| 1 | Flask | Server-side logic, routing, and request handling |
| 2 | Jinja2 | Dynamic HTML rendering |
| 3 | HTML, CSS, Bootstrap | Frontend design and responsiveness |
| 4 | SQLite, SQLAlchemy | Database and ORM handling |
| 5 | JavaScript | Form validation and dynamic actions |

## 📚 Libraries Used

| Library | Purpose |
|----------|----------|
| **Flask** | Core web framework handling routing, requests, and responses |
| **Flask-SQLAlchemy** | ORM for database operations with SQLite |
| **Flask-Migrate** | Handles database migrations using Alembic |
| **Jinja2** | Template engine for rendering dynamic HTML pages |
| **Matplotlib** | Generates charts and visual summaries for admin analytics |
| **SQLAlchemy** | Underlying ORM engine for data modeling |
| **Werkzeug** | Provides low-level utilities for WSGI, security, and debugging |
| **itsdangerous** | Safely signs data for session management |
| **Click** | Command-line interface support for Flask commands |
| **NumPy** | Supports numerical operations and chart data processing |
| **Pillow** | Image processing for chart generation and saving |

 

---

## 🧱 Database Schema
The system uses **SQLite** with ORM mapping through **SQLAlchemy**.  
It includes tables for:
- Users  
- Parking Lots  
- Parking Spots  
- Reservations  

Each model is linked using relationships to maintain data consistency.

---
![Database Schema](static/schema.png)

---

## 🧩 Architecture and Features

The project follows a **modular structure** using Flask **Blueprints**, ensuring scalability and maintainability.

- **app.py** – Initializes Flask and registers blueprints.  
- **controllers/** – Contains route logic:
  - `admin_controller.py` → Admin routes  
  - `user_controller.py` → User routes  
- **models/** – Defines database models and initialization.  
- **templates/** – Holds HTML templates for admin and user views.  
- **static/** – Contains CSS, JS, and chart files.  

---

## 🗂 Folder Structure
```
parking-management-system-v1/
│
├── app.py
│
├── controllers/
│ ├── admin_controller.py
│ └── user_controller.py
│
├── models/
│ ├── database.py
│ └── moddel.py
│
├── static/
│ ├── style.css
│ └── charts and graph/
│
├── templates/
│ ├── add_lot.html
│ ├── admin.html
│ ├── adminprofile.html
│ ├── bookspot.html
│ ├── edit_lot.html
│ ├── login.html
│ ├── occupied_spot_details.html
│ ├── registereduser.html
│ ├── releasespot.html
│ ├── search.html
│ ├── signup.html
│ ├── summaryadmin.html
│ ├── user.html
│ ├── userprofileuserprofile.html
│ ├── usersummary.html
│ └── viewspot.html
```

---


## ⚙️ Admin Features

| Feature | Route | Description |
|----------|--------|-------------|
| Login & Signup | `/login`, `/signup` | Handles authentication for users and admins |
| Dashboard | `/admin` | Displays all users and lots |
| Profile | `/adminprofile` | Manage admin profile |
| Add Lot | `/addlot` | Create new parking lot |
| Edit Lot | `/editlot/<lot_id>` | Modify lot details |
| Delete Lot | `/deletelot/<lot_id>` | Remove unoccupied lots |
| View Spot | `/spot/<spot_id>` | Spot details and deletion |
| Occupied Spot | `/occupiedspots/<spot_id>` | Reservation info |
| Registered Users | `/registered_users` | View all users |
| Search | `/search` | Search users or lots |
| Summary | `/summary` | Generate charts for revenue and occupancy |

---

## 👥 User Features

| Feature | Route | Description |
|----------|--------|-------------|
| Dashboard | `/user/<user_id>` | View reservations and search lots |
| Profile | `/profile/<user_id>` | Update profile info |
| Book Spot | `/book/<lot_id>` | Book available spots |
| Release Spot | `/release/<spot_id>` | Release booked spots and calculate cost |
| Summary | `/usersummary` | View booking statistics and charts |

---

## 🧰 Setup Instructions

1. **Clone the repository**
   ```bash
    git clone https://github.com/24f1002114/parking-management-system-v1.git
    cd parking-management-system-v1
2. **Create and activate virtual environment**  
    ```bash
    python3 -m venv venv
    source venv/bin/activate   # On Windows: venv\Scripts\activate
3. **Install dependencies**  
    ```bash
    pip install -r requirements.txt
4. **Run the application**  
    ```bash
    python3 app.py
5. **Access the app**  
    ```
    Open your browser and go to:
    http://127.0.0.1:5000/login  
    ```

   





---


