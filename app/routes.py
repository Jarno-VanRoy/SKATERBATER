import os
from functools import wraps
from flask import Blueprint, redirect, render_template, session, url_for, request, flash
from authlib.integrations.flask_client import OAuth
from . import db
from .models import Trick, Session as TrickSession

main = Blueprint('main', __name__)

# Auth0 configuration
oauth = OAuth()
auth0 = oauth.register(
    'auth0',
    client_id=os.getenv('AUTH0_CLIENT_ID'),
    client_secret=os.getenv('AUTH0_CLIENT_SECRET'),
    client_kwargs={'scope': 'openid profile email'},
    server_metadata_url=f'https://{os.getenv("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

@main.record_once
def on_load(state):
    oauth.init_app(state.app)

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=os.getenv('AUTH0_CALLBACK_URL'))

@main.route('/callback')
def callback():
    token = auth0.authorize_access_token()
    session['user'] = token['userinfo']
    return redirect('/dashboard')

@main.route('/logout')
def logout():
    session.clear()
    return redirect(
        f'https://{os.getenv("AUTH0_DOMAIN")}/v2/logout?'
        f'returnTo={url_for("main.home", _external=True)}&'
        f'client_id={os.getenv("AUTH0_CLIENT_ID")}'
    )

@main.route('/dashboard', methods=['GET', 'POST'])
@requires_auth
def dashboard():
    user = session.get('user')
    user_id = user['sub']

    if request.method == 'POST':
        trick_name = request.form.get('name', '').strip().lower()
        stance = request.form.get('stance')
        notes = request.form.get('notes')
        tries = request.form.get('tries', type=int)
        lands = request.form.get('lands', type=int)

        if not trick_name or tries is None or lands is None:
            flash("⚠️ All fields must be filled correctly.", "error")
            return redirect(url_for('main.dashboard'))

        if lands > tries:
            flash("⛔ You can't land more tricks than you tried.", "error")
            return redirect(url_for('main.dashboard'))

        trick = Trick.query.filter_by(user_id=user_id, name=trick_name).first()
        if not trick:
            trick = Trick(name=trick_name, stance=stance, user_id=user_id)
            db.session.add(trick)
            db.session.commit()

        session_log = TrickSession(
            trick_id=trick.id,
            tries=tries,
            lands=lands,
            notes=notes
        )
        db.session.add(session_log)
        db.session.commit()

        flash("✅ Session logged successfully!", "success")
        return redirect(url_for('main.dashboard'))

    tricks = Trick.query.filter_by(user_id=user_id).all()

    trick_data = []
    for trick in tricks:
        total_tries = sum(s.tries for s in trick.sessions)
        total_lands = sum(s.lands for s in trick.sessions)
        trick_data.append({
            'trick': trick,
            'total_tries': total_tries,
            'total_lands': total_lands,
            'sessions': sorted(trick.sessions, key=lambda s: s.created_at, reverse=True)
        })

    return render_template('dashboard.html', user=user, trick_data=trick_data)
