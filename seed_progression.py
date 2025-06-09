"""
Extended seeding script: Adds predefined tricks and simulates realistic practice progression for a demo user.

Run manually after migrations:
    python seed_progression.py
"""

from app import create_app
from app.models import db, Trick, UserTrick, PracticeLogEntry
from datetime import datetime, timedelta
import random

# Initialize Flask app and push context
app = create_app()
demo_user_id = "auth0|demo_user"  # Simulated Auth0 user ID

# Ordered list: beginner to advanced
TRICKS = [
    "Ollie",
    "Pop Shuvit",
    "Frontside 180",
    "Backside 180",
    "Manual",
    "Kickflip",
    "Heelflip",
    "Half Cab",
    "Varial Kickflip",
    "Varial Heelflip",
    "Tre Flip (360 Flip)",
    "Hardflip",
    "Full Cab",
]

# Simulated notes for flavor
NOTES = [
    "Felt solid today.",
    "Still working on consistency.",
    "Need more pop.",
    "Landing more than usual!",
    "Almost have it!",
    "Not my best day, but progress.",
    "Tried it at the park — better results.",
    "Struggled a bit with foot placement.",
    "🔥 Progress!",
]

def generate_practice_logs(user_trick, start_date):
    """
    Generate a time series of practice logs for a single trick,
    showing gradual improvement.
    """
    logs = []
    date = start_date
    sessions = random.randint(4, 10)

    # Track trick difficulty based on its position in the progression
    difficulty = TRICKS.index(user_trick.trick.name)

    for i in range(sessions):
        # Each session spaced out by about a week
        date += timedelta(days=random.randint(5, 10))

        # Simulate learning curve: easier tricks have higher landed ratios
        tries = random.randint(5, 15)
        base_success = max(0.2, 0.8 - (difficulty * 0.05))
        success_variation = random.uniform(-0.1, 0.2)
        landed_ratio = min(1.0, max(0.0, base_success + i * 0.05 + success_variation))
        landed = min(tries, int(tries * landed_ratio))

        logs.append(PracticeLogEntry(
            user_trick=user_trick,
            date=date.date(),
            time_logged=datetime.utcnow(),
            tries=tries,
            landed=landed,
            note=random.choice(NOTES)
        ))

    return logs


def seed_with_progression():
    with app.app_context():
        added_tricks = 0
        added_logs = 0

        # Ensure all tricks exist
        for trick_name in TRICKS:
            if not Trick.query.filter_by(name=trick_name).first():
                db.session.add(Trick(name=trick_name))
                added_tricks += 1
        db.session.commit()
        print(f"✅ {added_tricks} new tricks added.")

        # Start with a clean slate for demo user
        UserTrick.query.filter_by(user_id=demo_user_id).delete()
        db.session.commit()

        today = datetime.today()
        start_date = today - timedelta(days=365)

        # Assign each trick to the demo user with a sensible status
        for i, trick_name in enumerate(TRICKS):
            trick = Trick.query.filter_by(name=trick_name).first()

            # Pick a reasonable starting status depending on progression
            if i < 4:
                status = "mastered"
            elif i < 8:
                status = "in_progress"
            else:
                status = "to_learn"

            user_trick = UserTrick(
                user_id=demo_user_id,
                trick=trick,
                status=status
            )
            db.session.add(user_trick)
            db.session.commit()

            # Add realistic practice log entries
            logs = generate_practice_logs(user_trick, start_date)
            db.session.add_all(logs)
            added_logs += len(logs)

        db.session.commit()
        print(f"✅ Progression seeded: {len(TRICKS)} tricks with {added_logs} log entries for demo user.")

if __name__ == "__main__":
    seed_with_progression()
