# seed_tricks.py

"""
Script to populate the database with a predefined list of skateboarding tricks.
Run this manually after initializing your database and applying migrations.

Usage:
    python seed_tricks.py
"""

from app import create_app
from app.models import db, Trick

# Create the Flask app context
app = create_app()

# Define your starter trick list here
TRICKS = [
    "Ollie",
    "Kickflip",
    "Heelflip",
    "Pop Shuvit",
    "Frontside 180",
    "Backside 180",
    "Varial Kickflip",
    "Hardflip",
    "Tre Flip (360 Flip)",
    "Nollie",
    "Switch Ollie",
    "Fakie Bigspin",
    "Manual",
    "Nose Manual",
    "Board Slide",
    "50-50 Grind",
    "5-0 Grind",
    "Crooked Grind",
    "Smith Grind",
    "Feeble Grind"
]

def seed_tricks():
    with app.app_context():
        added_count = 0

        for trick_name in TRICKS:
            # Avoid duplicate trick entries
            existing = Trick.query.filter_by(name=trick_name).first()
            if not existing:
                new_trick = Trick(name=trick_name)
                db.session.add(new_trick)
                added_count += 1

        db.session.commit()
        print(f"✅ {added_count} new tricks added to the database.")

if __name__ == "__main__":
    seed_tricks()
