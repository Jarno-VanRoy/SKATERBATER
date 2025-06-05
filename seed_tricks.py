"""
Script to populate the database with a predefined list of flat/street skateboarding tricks.
Run manually after migrations are applied.

Usage:
    python seed_tricks.py
"""

from app import create_app
from app.models import db, Trick

# Initialize the app and push app context
app = create_app()

# ⚠️ Only flatground/street tricks — no grinds, slides, or ramp tricks
TRICKS = [
    "Ollie",
    "Nollie",
    "Fakie Ollie",
    "Switch Ollie",
    "Kickflip",
    "Heelflip",
    "Pop Shuvit",
    "Frontside Shuvit",
    "Backside Shuvit",
    "Frontside 180",
    "Backside 180",
    "Half Cab",
    "Full Cab",
    "Varial Kickflip",
    "Varial Heelflip",
    "Hardflip",
    "Inward Heelflip",
    "Tre Flip (360 Flip)",
    "360 Shuvit",
    "Bigspin",
    "Fakie Bigspin",
    "Manual",
    "Nose Manual",
    "Caveman",
    "No Comply",
    "Boneless",
    "Body Varial",
]

def seed_tricks():
    with app.app_context():
        added_count = 0

        for trick_name in TRICKS:
            # Avoid duplicates
            if not Trick.query.filter_by(name=trick_name).first():
                db.session.add(Trick(name=trick_name))
                added_count += 1

        db.session.commit()
        print(f"✅ {added_count} new flat/street tricks added to the database.")

if __name__ == "__main__":
    seed_tricks()
