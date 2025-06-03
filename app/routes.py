from flask import Blueprint, render_template, redirect, url_for, session, request
from functools import wraps
from app.models import db, Trick, UserTrick, PracticeSession

# Define the main blueprint
main_bp = Blueprint('main', __name__)

# Decorator to require login for protected routes
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("main.login"))
        return f(*args, **kwargs)
    return decorated


# Home page route — open to all users
@main_bp.route('/')
def index():
    return render_template('index.html')


# Dashboard view — requires user to be logged in
@main_bp.route('/dashboard')
@requires_auth
def dashboard():
    user_id = session.get('user', {}).get('sub')

    # Get all UserTricks for this user
    user_tricks = UserTrick.query.filter_by(user_id=user_id).all()

    # Separate them by status
    to_learn = [ut for ut in user_tricks if ut.status == 'to_learn']
    in_progress = [ut for ut in user_tricks if ut.status == 'in_progress']
    mastered = [ut for ut in user_tricks if ut.status == 'mastered']

    # 🧠 Add this line to fetch all available tricks for the dropdown
    all_tricks = Trick.query.order_by(Trick.name).all()

    return render_template(
        'dashboard.html',
        to_learn=to_learn,
        in_progress=in_progress,
        mastered=mastered,
        all_tricks=all_tricks  # 👈 Pass to template
    )

# Add a trick to a user's personal list
@main_bp.route('/add_trick', methods=['POST'])
@requires_auth
def add_trick():
    user_id = session["user"]["sub"]
    trick_id = request.form.get('trick_id')
    status = request.form.get('status')  # ✅ Get status from the form

    if not trick_id or status not in ['to_learn', 'in_progress', 'mastered']:
        return redirect(url_for('main.dashboard'))

    # Prevent duplicates — only add if this user doesn’t already have it
    existing = UserTrick.query.filter_by(user_id=user_id, trick_id=trick_id).first()
    if not existing:
        new_user_trick = UserTrick(
            user_id=user_id,
            trick_id=trick_id,
            status=status  # ✅ Use the selected status
        )
        db.session.add(new_user_trick)
        db.session.commit()

    return redirect(url_for('main.dashboard'))



# View details of a specific user trick, including session logs
@main_bp.route('/trick/<int:user_trick_id>')
@requires_auth
def trick_detail(user_trick_id):
    user_id = session["user"]["sub"]
    user_trick = UserTrick.query.filter_by(id=user_trick_id, user_id=user_id).first_or_404()
    return render_template('trick_detail.html', user_trick=user_trick)


# Log a practice session for a given user trick
@main_bp.route('/log_session/<int:user_trick_id>', methods=['POST'])
@requires_auth
def log_session(user_trick_id):
    user_id = session["user"]["sub"]

    # Retrieve the correct UserTrick instance for the logged-in user
    user_trick = UserTrick.query.filter_by(id=user_trick_id, user_id=user_id).first_or_404()

    # Get submitted form values
    date_str = request.form.get('date')  # optional
    tries = request.form.get('tries', type=int)  # total number of attempts
    landed = request.form.get('landed', type=int)  # total successful landings
    notes = request.form.get('notes', '')  # optional notes

    # If no date is provided, fallback to today
    from datetime import datetime, date
    session_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()

    # ❗ Logical validation: can't land more times than attempted
    if landed > tries:
        # Return to the trick detail page with an error message
        error = "You can't land more times than you tried! 🤔"
        return render_template('trick_detail.html', user_trick=user_trick, error=error)

    # Create a new PracticeSession record
    new_session = PracticeSession(
        user_trick_id=user_trick.id,
        date=session_date,
        tries=tries,
        landed=landed,
        notes=notes
    )

    # Add and commit to the database
    db.session.add(new_session)
    db.session.commit()

    # Redirect back to the trick detail page after logging
    return redirect(url_for('main.trick_detail', user_trick_id=user_trick.id))

# Change the status of a user trick (e.g. from in_progress to mastered)
@main_bp.route('/update_status/<int:user_trick_id>', methods=['POST'])
@requires_auth
def update_status(user_trick_id):
    user_id = session["user"]["sub"]
    new_status = request.form.get('status')
    user_trick = UserTrick.query.filter_by(id=user_trick_id, user_id=user_id).first_or_404()

    if new_status in ['to_learn', 'in_progress', 'mastered']:
        user_trick.status = new_status
        db.session.commit()

    return redirect(url_for('main.dashboard'))


# Login and logout routes for Auth0
@main_bp.route('/login')
def login():
    return redirect(url_for("auth0.login"))  # Handled by Auth0 blueprint


@main_bp.route('/logout')
def logout():
    return redirect(url_for("auth0.logout"))  # Handled by Auth0 blueprint
