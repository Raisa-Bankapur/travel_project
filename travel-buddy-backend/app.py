import json
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATA_FILE = Path(__file__).with_name("users.json")
trips = []

BUDGET_MULTIPLIERS = {
    "low": 0.75,
    "medium": 1.0,
    "high": 1.8,
}

DESTINATION_DATA = {
    "goa": {
        "hotels": [
            {"name": "Calangute Beach Stay", "base_price": 2200},
            {"name": "Anjuna Coast Resort", "base_price": 3200},
            {"name": "Panjim Harbor Hotel", "base_price": 4200},
            {"name": "Candolim Sunset Suites", "base_price": 5200},
            {"name": "Morjim Palm Retreat", "base_price": 6200},
        ],
        "restaurants": [
            "Fisherman's Wharf",
            "Pousada by the Beach",
            "Mum's Kitchen",
            "Gunpowder Goa",
            "Thalassa",
        ],
        "activities": [
            "Relax at the beach and enjoy a sunset walk",
            "Visit a Portuguese heritage street and local cafes",
            "Take an evening cruise with live music",
            "Explore flea markets and coastal viewpoints",
            "Keep one half-day for water sports or a quiet beach hop",
        ],
    },
    "jaipur": {
        "hotels": [
            {"name": "Pink City Haveli", "base_price": 2100},
            {"name": "Amber Courtyard Inn", "base_price": 3000},
            {"name": "Raj Mahal Residency", "base_price": 4100},
            {"name": "City Palace View Hotel", "base_price": 5200},
            {"name": "Nahargarh Heritage Retreat", "base_price": 6400},
        ],
        "restaurants": [
            "Spice Court",
            "Rawat Mishthan Bhandar",
            "Bar Palladio",
            "Laxmi Misthan Bhandar",
            "Tapri Central",
        ],
        "activities": [
            "Start with Amber Fort and city viewpoints",
            "Explore bazaars for handicrafts and textiles",
            "Spend the evening at a rooftop restaurant",
            "Visit heritage courtyards and photo spots",
            "Keep one block for shopping and local sweets",
        ],
    },
    "manali": {
        "hotels": [
            {"name": "Pine Trail Lodge", "base_price": 2000},
            {"name": "Old Manali Valley Stay", "base_price": 3100},
            {"name": "Snow Peak Retreat", "base_price": 4300},
            {"name": "Beas River Resort", "base_price": 5600},
            {"name": "Solang Heights Hotel", "base_price": 6900},
        ],
        "restaurants": [
            "Johnson's Cafe",
            "Cafe 1947",
            "The Lazy Dog",
            "Chopsticks Manali",
            "Drifters' Cafe",
        ],
        "activities": [
            "Visit mountain viewpoints and pine trails",
            "Explore Old Manali cafes and local shops",
            "Keep the evening for a bonfire-style dinner",
            "Add a scenic river walk and slow photography stop",
            "Reserve time for nearby adventure activities",
        ],
    },
    "dharwad": {
        "hotels": [
            {"name": "Dharwad Comfort Inn", "base_price": 1800},
            {"name": "Hubli-Dharwad Residency", "base_price": 2600},
            {"name": "Kittur Heritage Stay", "base_price": 3600},
            {"name": "Green Campus Hotel", "base_price": 4300},
            {"name": "North Karnataka Retreat", "base_price": 5200},
        ],
        "restaurants": [
            "Dharwad Tiffin Corner",
            "North Karnataka Oota House",
            "Basaveshwar Khanavali",
            "Campus Cafe",
            "Malnad Spice Table",
        ],
        "activities": [
            "Visit local heritage spots and explore calm neighborhood streets",
            "Spend time in green campus areas and try popular Dharwad snacks",
            "Wrap up the day with a relaxed evening at a well-known local cafe",
            "Explore bookstores, markets, and everyday city culture",
            "Keep one half-day for nearby viewpoints or a local food trail",
        ],
    },
    "delhi": {
        "hotels": [
            {"name": "Connaught Comfort Hotel", "base_price": 2400},
            {"name": "Karol Bagh Residency", "base_price": 3200},
            {"name": "India Gate View Stay", "base_price": 4500},
            {"name": "Aerocity Metro Suites", "base_price": 5600},
            {"name": "Capital Luxe Hotel", "base_price": 7200},
        ],
        "restaurants": [
            "Saravana Bhavan",
            "Karim's",
            "Indian Accent",
            "Cafe Lota",
            "Bukhara",
        ],
        "activities": [
            "Start with a major monument and a walk through a historic district",
            "Visit markets for street food and shopping",
            "Plan an evening around lights, food, and city views",
            "Explore museums or cultural centers in the afternoon",
            "Keep one slot for old and new city contrast photography",
        ],
    },
    "mumbai": {
        "hotels": [
            {"name": "Marine Drive Stay", "base_price": 2500},
            {"name": "Colaba Harbor Inn", "base_price": 3500},
            {"name": "Bandra City Suites", "base_price": 4700},
            {"name": "Juhu Palm Residency", "base_price": 5900},
            {"name": "Skyline Bay Hotel", "base_price": 7600},
        ],
        "restaurants": [
            "Leopold Cafe",
            "Bademiya",
            "The Table",
            "Britannia & Co.",
            "Khyber",
        ],
        "activities": [
            "See the waterfront and iconic city landmarks",
            "Explore art, shopping, and neighborhood cafes",
            "End the day with sea-facing dinner plans",
            "Keep time for local train-accessible city highlights",
            "Add a sunset stop and a late-evening food trail",
        ],
    },
    "bangalore": {
        "hotels": [
            {"name": "Garden City Inn", "base_price": 2300},
            {"name": "Indiranagar Suites", "base_price": 3300},
            {"name": "MG Road Residency", "base_price": 4300},
            {"name": "Cubbon Park Hotel", "base_price": 5400},
            {"name": "Skydeck Premium Stay", "base_price": 6800},
        ],
        "restaurants": [
            "MTR",
            "Toit",
            "Vidyarthi Bhavan",
            "CTR",
            "The Only Place",
        ],
        "activities": [
            "Visit gardens and a popular city landmark",
            "Explore cafes, bookstores, and tech district hangouts",
            "Spend the evening in a lively food street or brewery area",
            "Reserve one block for parks and slow city walks",
            "Keep a flexible slot for shopping and coffee stops",
        ],
    },
    "punjab": {
        "hotels": [
            {"name": "Amritsar Heritage Inn", "base_price": 2100},
            {"name": "Ludhiana Grand Stay", "base_price": 3200},
            {"name": "Patiala Palace Residency", "base_price": 4300},
            {"name": "Punjab Courtyard Hotel", "base_price": 5400},
            {"name": "Golden Fields Retreat", "base_price": 6700},
        ],
        "restaurants": [
            "Kesar Da Dhaba",
            "Bharawan Da Dhaba",
            "Brothers Dhaba",
            "Pal Dhaba",
            "Kulcha Land",
        ],
        "activities": [
            "Begin with the best-known attractions and landmarks in Punjab",
            "Explore local food spots, shopping streets, and culture in Punjab",
            "Keep the evening free for scenic views, relaxed dining, and photos in Punjab",
            "Reserve time for local markets, sweets, and street photography",
            "Add a flexible stop for heritage, music, or a food trail",
        ],
    },
}


def load_users():
    if not DATA_FILE.exists():
        return []

    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def save_users(users):
    DATA_FILE.write_text(json.dumps(users, indent=2), encoding="utf-8")


users = load_users()


def normalize_budget(value):
    text = str(value or "").strip().lower()

    if "low" in text or "budget" in text or "cheap" in text:
        return "low"

    if "high" in text or "luxury" in text or "premium" in text:
        return "high"

    digits = "".join(ch for ch in text if ch.isdigit())
    if digits:
        amount = int(digits)
        if amount < 5000:
            return "low"
        if amount > 15000:
            return "high"

    return "medium"


def generic_destination_data(destination):
    safe_destination = destination.title()
    return {
        "hotels": [
            {"name": f"{safe_destination} Budget Inn", "base_price": 1800},
            {"name": f"{safe_destination} Comfort Stay", "base_price": 2800},
            {"name": f"{safe_destination} Central Residency", "base_price": 3800},
            {"name": f"{safe_destination} Grand Hotel", "base_price": 5000},
            {"name": f"{safe_destination} Premium Retreat", "base_price": 6500},
        ],
        "restaurants": [
            f"{safe_destination} Food Court",
            f"{safe_destination} Spice House",
            f"{safe_destination} Heritage Kitchen",
            f"{safe_destination} Market Cafe",
            f"{safe_destination} Skyline Dining",
        ],
        "activities": [
            f"Begin with the best-known attractions and landmarks in {destination}",
            f"Explore local food spots, shopping streets, and culture in {destination}",
            f"Keep the evening free for scenic views, relaxed dining, and photos in {destination}",
            f"Add a flexible half-day to discover hidden gems in {destination}",
            f"Reserve time for a neighborhood walk and local market stop in {destination}",
        ],
    }


def build_day_hotels(hotels, budget_key, day_index):
    multiplier = BUDGET_MULTIPLIERS[budget_key]
    day_hotels = []

    for hotel in hotels[day_index : day_index + 2]:
        adjusted_price = round(hotel["base_price"] * multiplier / 100) * 100
        day_hotels.append(
            {
                "name": hotel["name"],
                "price": f"Rs. {adjusted_price:,}/night",
            }
        )

    if len(day_hotels) < 2:
        for hotel in hotels[: 2 - len(day_hotels)]:
            adjusted_price = round(hotel["base_price"] * multiplier / 100) * 100
            day_hotels.append(
                {
                    "name": hotel["name"],
                    "price": f"Rs. {adjusted_price:,}/night",
                }
            )

    return day_hotels


def build_day_restaurants(restaurants, day_index):
    selection = restaurants[day_index : day_index + 2]
    if len(selection) < 2:
        selection += restaurants[: 2 - len(selection)]
    return selection


def build_days(destination, total_days, budget_key):
    normalized_destination = destination.strip().lower()
    destination_data = DESTINATION_DATA.get(
        normalized_destination,
        generic_destination_data(destination),
    )

    support_notes = [
        f"Keep some extra time for local travel inside {destination}",
        "Add one flexible stop based on weather and timing",
        "Reserve the evening for food, shopping, or a relaxed walk",
        "Capture photos and keep a short backup indoor activity",
        "Use one lighter slot for rest and spontaneous exploration",
    ]

    days = []
    for index in range(total_days):
        primary_activity = destination_data["activities"][
            index % len(destination_data["activities"])
        ]
        secondary_activity = support_notes[index % len(support_notes)]
        day_hotels = build_day_hotels(destination_data["hotels"], budget_key, index)
        day_restaurants = build_day_restaurants(destination_data["restaurants"], index)

        days.append(
            {
                "date": f"Day {index + 1}",
                "activities": [primary_activity, secondary_activity],
                "hotels": day_hotels,
                "restaurants": day_restaurants,
            }
        )

    return days


@app.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    email = str(data.get("email", "")).strip().lower()

    if not email or not data.get("password"):
        return jsonify({"message": "Email and password are required"}), 400

    for user in users:
        if user["email"].strip().lower() == email:
            return jsonify({"message": "User already exists"}), 409

    new_user = {
        "name": data.get("name", "Traveler"),
        "email": email,
        "password": data["password"],
    }
    users.append(new_user)
    save_users(users)
    return jsonify(
        {
            "message": "User registered",
            "user": {"name": new_user["name"], "email": new_user["email"]},
        }
    )


@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    email = str(data.get("email", "")).strip().lower()
    password = data.get("password", "")

    for user in users:
        if user["email"].strip().lower() == email and user["password"] == password:
            return jsonify(
                {
                    "message": "Login success",
                    "user": {
                        "name": user.get("name", "Traveler"),
                        "email": user["email"],
                    },
                }
            )

    return jsonify({"message": "Invalid credentials"}), 401


@app.route("/generate_itinerary", methods=["POST"])
def generate_itinerary():
    data = request.json or {}

    destination = data.get("destination", "your destination")
    total_days = int(data.get("days", 3) or 3)
    budget_key = normalize_budget(data.get("budget", "medium"))
    days = build_days(destination, max(total_days, 1), budget_key)

    payload = {
        "summary": f"{total_days}-day trip to {destination} with {budget_key} budget picks.",
        "days": days,
        "itinerary": "\n".join(
            [f"Trip to {destination}"]
            + [f"{day['date']}: {day['activities'][0]}" for day in days]
            + [f"Budget: {budget_key}"]
        ),
    }
    trips.append(payload)
    return jsonify(payload)


if __name__ == "__main__":
    app.run(debug=True)
