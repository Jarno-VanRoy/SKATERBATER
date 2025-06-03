from datetime import date
from app import db

class Trick(db.Model):
    """
    Represents a predefined skate trick.
    These are seeded and available to all users to select from.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return f"<Trick {self.name}>"


class UserTrick(db.Model):
    """
    Associates a Trick with a specific user and tracks their learning status.
    This allows each user to have their own progress per trick.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), nullable=False)  # Auth0 user ID
    trick_id = db.Column(db.Integer, db.ForeignKey('trick.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='to_learn')  # 'to_learn', 'in_progress', 'mastered'

    # Relationships
    trick = db.relationship('Trick', backref='user_tricks', lazy=True)
    sessions = db.relationship('PracticeSession', backref='user_trick', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f"<UserTrick user={self.user_id} trick={self.trick.name} status={self.status}>"


class PracticeSession(db.Model):
    """
    Represents a single practice session for a user-trick.
    """
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=date.today, nullable=False)
    tries = db.Column(db.Integer, default=0)
    landed = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text, default='')

    # Link to the user's specific trick progress
    user_trick_id = db.Column(
        db.Integer,
        db.ForeignKey('user_trick.id', name='fk_practice_usertrick'),
        nullable=False
    )

    def __repr__(self):
        return f"<PracticeSession {self.date} for UserTrick ID {self.user_trick_id}>"
