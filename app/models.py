from . import db

# One trick per user, e.g. "Tre Flip"
class Trick(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    stance = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Link to all sessions for this trick
    sessions = db.relationship('Session', backref='trick', lazy=True, cascade="all, delete-orphan")

# Each practice session for a trick
class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trick_id = db.Column(db.Integer, db.ForeignKey('trick.id'), nullable=False)
    tries = db.Column(db.Integer, default=0)
    lands = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
