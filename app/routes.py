from flask import Blueprint, render_template, redirect, url_for, session, request
from functools import wraps
from app.models import db, Trick, UserTrick, PracticeLogEntry
from app.oauth import oauth
from urllib.parse import urlencode
from datetime import datetime, date
import os

main_bp = Blueprint('main', __name__)

# ---------------------------------------
# AUTH DECORATOR: restricts routes to logged-in users only
# ---------------------------------------
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("main.login"))
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------
# HOME PAGE
# ---------------------------------------
@main_bp.route('/')
def index():
    return render_template('index.html')


# ---------------------------------------
# DASHBOARD
# ---------------------------------------
@main_bp.route('/dashboard')
@requires_auth
def dashboard():
    user_id = session.get('user', {}).get('sub')

    # All tricks associated with this user
    user_tricks = UserTrick.query.filter_by(user_id=user_id).all()

    # Categorize user tricks by status
    to_learn = [ut for ut in user_tricks if ut.status == 'to_learn']
    in_progress = [ut for ut in user_tricks if ut.status == 'in_progress']
    mastered = [ut for ut in user_tricks if ut.status == 'mastered']

    # All available tricks for dropdown (pre-seeded list)
    all_tricks = Trick.query.order_by(Trick.name).all()

    return render_template(
        'dashboard.html',
        to_learn=to_learn,
        in_progress=in_progress,
        mastered=mastered,
        all_tricks=all_tricks
    )


# ---------------------------------------
# ADD TRICK TO USER'S PERSONAL LIST
# ---------------------------------------
@main_bp.route('/add_trick', methods=['POST'])
@requires_auth
def add_trick():
    user_id = session["user"]["sub"]
    trick_id = request.form.get('trick_id')
    status = request.form.get('status')

    # Ensure form inputs are valid
    if not trick_id or status not in ['to_learn', 'in_progress', 'mastered']:
        return redirect(url_for('main.dashboard'))

    # Prevent duplicate UserTrick entries
    existing = UserTrick.query.filter_by(user_id=user_id, trick_id=trick_id).first()
    if not existing:
        new_user_trick = UserTrick(user_id=user_id, trick_id=trick_id, status=status)
        db.session.add(new_user_trick)
        db.session.commit()

    return redirect(url_for('main.dashboard'))


# ---------------------------------------
# TRICK DETAIL PAGE (with all log entries)
# ---------------------------------------
@main_bp.route('/trick/<int:user_trick_id>')
@requires_auth
def trick_detail(user_trick_id):
    user_id = session["user"]["sub"]

    # Confirm trick belongs to logged-in user
    user_trick = UserTrick.query.filter_by(id=user_trick_id, user_id=user_id).first_or_404()

    # Show all log entries for this trick, newest first
    log_entries = PracticeLogEntry.query.filter_by(user_trick_id=user_trick.id).order_by(
        PracticeLogEntry.date.desc(),
        PracticeLogEntry.time_logged.desc()
    ).all()

    return render_template(
        'trick_detail.html',
        user_trick=user_trick,
        log_entries=log_entries,
        current_date=date.today().isoformat()
    )


# ---------------------------------------
# LOG A NEW PRACTICE SESSION ENTRY
# ---------------------------------------
@main_bp.route('/log_session/<int:user_trick_id>', methods=['POST'])
@requires_auth
def log_session(user_trick_id):
    user_id = session["user"]["sub"]

    user_trick = UserTrick.query.filter_by(id=user_trick_id, user_id=user_id).first_or_404()

    # Get form values
    date_str = request.form.get('date')
    tries = request.form.get('tries', type=int)
    landed = request.form.get('landed', type=int)
    note = request.form.get('notes', '')

    session_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()

    # Validate
    if tries is None or landed is None or tries < 0 or landed < 0:
        error = "Both 'tries' and 'landed' must be non-negative numbers! 🧮"
        return render_template('trick_detail.html', user_trick=user_trick,
                               log_entries=user_trick.log_entries, error=error)

    if landed > tries:
        error = "You can't land more times than you tried! 🤔"
        return render_template('trick_detail.html', user_trick=user_trick,
                               log_entries=user_trick.log_entries, error=error)

    # Create new row — no grouping, no JSON
    new_log = PracticeLogEntry(
        user_trick_id=user_trick.id,
        date=session_date,
        time_logged=datetime.utcnow(),
        tries=tries,
        landed=landed,
        note=note
    )

    db.session.add(new_log)
    db.session.commit()

    return redirect(url_for('main.trick_detail', user_trick_id=user_trick.id))

# ---------------------------------------
# DELETE A PRACTICE LOG ENTRY
# ---------------------------------------
@main_bp.route('/delete_log_entry/<int:entry_id>', methods=['POST'])
@requires_auth
def delete_log_entry(entry_id):
    user_id = session["user"]["sub"]

    # Look up entry and confirm ownership through UserTrick
    entry = PracticeLogEntry.query.get_or_404(entry_id)
    if entry.user_trick.user_id != user_id:
        return redirect(url_for('main.dashboard'))

    user_trick_id = entry.user_trick.id

    db.session.delete(entry)
    db.session.commit()

    return redirect(url_for('main.trick_detail', user_trick_id=user_trick_id))


# ---------------------------------------
# CHANGE STATUS OF A TRICK (e.g. from "in progress" to "mastered")
# ---------------------------------------
@main_bp.route('/update_status/<int:user_trick_id>', methods=['POST'])
@requires_auth
def update_status(user_trick_id):
    user_id = session["user"]["sub"]
    new_status = request.form.get('status')

    if new_status not in ['to_learn', 'in_progress', 'mastered']:
        return redirect(url_for('main.dashboard'))

    user_trick = UserTrick.query.filter_by(id=user_trick_id, user_id=user_id).first_or_404()
    user_trick.status = new_status
    db.session.commit()

    return redirect(url_for('main.dashboard'))


# ---------------------------------------
# AUTH: LOGIN via Auth0
# ---------------------------------------
@main_bp.route('/login')
def login():
    redirect_uri = url_for('main.callback', _external=True)
    return oauth.auth0.authorize_redirect(redirect_uri=redirect_uri)


# ---------------------------------------
# AUTH: CALLBACK HANDLER
# ---------------------------------------
@main_bp.route('/callback')
def callback():
    token = oauth.auth0.authorize_access_token()
    user_info = token.get('userinfo')
    session["user"] = user_info
    return redirect(url_for("main.dashboard"))


# ---------------------------------------
# AUTH: LOGOUT and return to index
# ---------------------------------------
@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(
        f'https://{os.getenv("AUTH0_DOMAIN")}/v2/logout?' + urlencode({
            'returnTo': url_for('main.index', _external=True),
            'client_id': os.getenv("AUTH0_CLIENT_ID")
        })
    )
