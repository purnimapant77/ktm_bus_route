# KTM Bus Route Finder 🚌

A web application to help people in Kathmandu Valley find the right public bus for their journey.

## About This Project

This is my personal project that I built to solve a real problem — finding the right bus in Kathmandu is confusing, especially for new people. There is no proper online platform that tells you which bus to take, where to board, and where to get off. So I decided to build one myself.

This project is currently in early stage. The route and stop data is very limited right now (only 2 routes and 13 stops as sample data) but the system is fully functional and more routes and stops will be added gradually as the project grows.

## Features

- 🔍 **Route Finder** — Select your starting stop and destination stop and the system tells you which bus to take, where to board and where to exit
- 🗺️ **Map View** — See all bus stops and routes on an interactive map using OpenStreetMap
- 🚌 **Yatayat Directory** — Browse all available Yatayat services and their complete routes
- 💰 **Fare Calculation** — Automatically calculates bus fare based on distance using official Bagmati Province fare slabs
- 🎓 **Student Discount** — 45% student discount option for students with valid ID card or uniform
- 👤 **User Accounts** — Login, signup and logout functionality
- ⭐ **Favorite Routes** — Logged in users can save their frequent routes for quick access
- 📍 **Stops List** — View all available bus stops in one place

## Tech Stack

- **Backend** — Python, Django
- **Database** — SQLite
- **Frontend** — HTML, CSS, Bootstrap 5, JavaScript
- **Map** — Leaflet.js with OpenStreetMap and CartoCDN tiles
- **Data Import** — Pandas, OdfPy (for reading ODS files)

## Fare Structure

As per Bagmati Province official fare list:

| Distance | Fare |
|---|---|
| 0 - 5 km | Rs. 24 (charged Rs. 25) |
| 5 - 10 km | Rs. 33 (charged Rs. 35) |
| 10 - 15 km | Rs. 39 (charged Rs. 40) |
| 15 - 20 km | Rs. 44 (charged Rs. 45) |
| 20+ km | Rs. 50 |

Fares are rounded up to the nearest Rs. 5 as conductors charge in multiples of 5.
Student discount of 45% is applied before rounding.

## Project Structure

```
ktm_bus_route/
├── bus/                        # Main app
│   ├── models.py               # Stop, Route, RouteStop, FavoriteRoute models
│   ├── views.py                # All views including search and fare logic
│   ├── urls.py                 # URL routing
│   ├── admin.py                # Admin panel setup
│   ├── templates/bus/          # HTML templates
│   ├── static/bus/images/      # Static files and images
│   └── management/commands/    # Custom import command
│       └── import_data.py      # Imports stops and routes from ODS files
├── accounts/                   # Authentication app
│   ├── views.py                # Login, signup, logout, profile views
│   ├── urls.py                 # Auth URL routing
│   └── templates/accounts/     # Login, signup, profile templates
├── config/                     # Project settings
│   ├── settings.py
│   └── urls.py
├── data/                       # ODS data files (not pushed to GitHub)
│   ├── stops.ods
│   └── routes.ods
└── manage.py
```

## How to Run Locally

1. Clone the repository
```bash
git clone https://github.com/purnimapant77/ktm-bus-route-finder.git
cd ktm-bus-route-finder
```

2. Create and activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies
```bash
pip install django pillow odfpy openpyxl pandas
```

4. Run migrations
```bash
python manage.py migrate
```

5. Add your data files inside `data/` folder and import
```bash
python manage.py import_data
```

6. Create admin account
```bash
python manage.py createsuperuser
```

7. Run the server
```bash
python manage.py runserver
```

8. Open browser and go to `http://127.0.0.1:8000`

## Data Format

**stops.ods** columns:
`StopID, Name, AltNames, Latitude, Longitude, Notes`

**routes.ods** columns:
`RouteID, RouteNumber, RouteName, YatayatID, YatayatName, VehicleType, StopSequence, StopID, Direction, Color`

## Current Data Status

> ⚠️ **Note:** The current data is very minimal and only for testing purposes.
> - **Stops:** 13 stops (Samakhusi area and nearby)
> - **Routes:** 2 routes (1A and 2A)
> 
> More routes and stops covering all of Kathmandu Valley will be added in future updates.

## Future Plans

- Add more routes and stops covering full Kathmandu Valley
- Add bus schedule and frequency information
- Mobile responsive improvements
- Deploy online so anyone can access it
- Add feature to report wrong information

## Developer

**Purnima** — BSc CSIT Student, Padmakanya Multiple Campus, Tribhuvan University, Kathmandu

This project was built as a personal project to practice Django web development and solve a real problem for Kathmandu commuters.

---

*If you know any bus routes or stops that are missing, feel free to contact through the website!*
