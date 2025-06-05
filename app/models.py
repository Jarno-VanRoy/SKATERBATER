from datetime import date, datetime
from app import db
from sqlalchemy.dialects.sqlite import JSON

class Trick(db.Model):
    """
    Represents a predefined skate trick.
    These tricks are seeded into the database and available for all users to add to their personal trick list.
    """
    id = db.Column(db.Integer, primary_key=True)

    # The name of the trick (e.g., "Kickflip", "Heelflip")
    name = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return f"<Trick {self.name}>"


class UserTrick(db.Model):
    """
    Associates a specific Trick with a user, and tracks their individual learning status.
    This relationship allows multiple users to track their own status for the same trick independently.
    """
    id = db.Column(db.Integer, primary_key=True)

    # Auth0 user ID (string, not numeric)
    user_id = db.Column(db.String(255), nullable=False)

    # ForeignKey to the shared Trick definition
    trick_id = db.Column(db.Integer, db.ForeignKey('trick.id'), nullable=False)

    # User's learning status for this trick: 'to_learn', 'in_progress', or 'mastered'
    status = db.Column(db.String(20), nullable=False, default='to_learn')

    # Relationship: each user-trick can have multiple daily logs
    log_entries = db.relationship(
        'PracticeLogEntry',
        backref='user_trick',
        cascade='all, delete-orphan',
        lazy=True
    )

    # Relationship to the base trick info (name, etc.)
    trick = db.relationship('Trick', backref='user_tricks', lazy=True)

    def __repr__(self):
        return f"<UserTrick user={self.user_id} trick={self.trick.name} status={self.status}>"


class PracticeLogEntry(db.Model):
    """
    Represents a single practice session log for a specific user-trick.

    - Each row is one submitted form: a single set of tries/landed/note.
    - Use the `date` field to group entries visually in the UI.
    """
    id = db.Column(db.Integer, primary_key=True)

    # Date when the session occurred (grouping key in UI)
    date = db.Column(db.Date, default=date.today, nullable=False)

    # Timestamp when the log was created
    time_logged = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Number of attempts for this log
    tries = db.Column(db.Integer, default=0, nullable=False)

    # Number of landed attempts for this log
    landed = db.Column(db.Integer, default=0, nullable=False)

    # Optional note for this session
    note = db.Column(db.Text, default='', nullable=True)

    # Link to the user-trick
    user_trick_id = db.Column(
        db.Integer,
        db.ForeignKey('user_trick.id', name='fk_logentry_usertrick'),
        nullable=False
    )

    def __repr__(self):
        return f"<PracticeLogEntry {self.date} ({self.tries} tries)>"
