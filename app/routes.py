from flask import Blueprint, render_template, redirect, url_for, session, request, send_file
from functools import wraps
from app.models import db, Trick, UserTrick, PracticeLogEntry
from app.oauth import oauth
from urllib.parse import urlencode
from datetime import datetime, date
import os
import io
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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

    # ✅ Sort each list alphabetically by trick name
    to_learn.sort(key=lambda ut: ut.trick.name.lower())
    in_progress.sort(key=lambda ut: ut.trick.name.lower())
    mastered.sort(key=lambda ut: ut.trick.name.lower())

    # Load all available tricks for the dropdown (also sorted)
    all_tricks = Trick.query.order_by(Trick.name.asc()).all()

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

    # Parse the submitted date or default to today
    session_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()

    # Disallow future dates
    if session_date > date.today():
        error = "You can't log a session in the future! 🕒"
        return render_template('trick_detail.html', user_trick=user_trick,
                               log_entries=user_trick.log_entries, error=error)

    # Validate
    if tries is None or landed is None or tries < 0 or landed < 0:
        error = "Both 'tries' and 'landed' must be non-negative numbers! 🧮"
        return render_template('trick_detail.html', user_trick=user_trick,
                               log_entries=user_trick.log_entries, error=error, note=note)

    if landed > tries:
        error = "You can't land more times than you tried! 🤔"
        return render_template('trick_detail.html', user_trick=user_trick,
                               log_entries=user_trick.log_entries, error=error, note=note)

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

# -------------------------------
# Chart: Trick Progress Over Time
# -------------------------------
@main_bp.route('/trick_progress_chart/<int:user_trick_id>')
@requires_auth
def trick_progress_chart(user_trick_id):
    user_id = session["user"]["sub"]

    # Fetch the trick the user is working on, or return 404 if not found
    user_trick = UserTrick.query.filter_by(id=user_trick_id, user_id=user_id).first_or_404()

    # Get all practice logs for this user trick, sorted by date
    logs = PracticeLogEntry.query.filter_by(user_trick_id=user_trick.id).order_by(PracticeLogEntry.date).all()

    from collections import defaultdict
    from datetime import datetime

    # Group log data by date to calculate daily totals
    grouped = defaultdict(lambda: {'tries': 0, 'landed': 0})
    for log in logs:
        grouped[log.date]['tries'] += log.tries
        grouped[log.date]['landed'] += log.landed

    # Create a bytes buffer to store the image in memory
    buf = io.BytesIO()

    if not grouped:
        # If no data yet, display a placeholder message
        fig, ax = plt.subplots(figsize=(8, 3), facecolor='#222')  # smaller height
        ax.text(0.5, 0.5, "No data yet 🛹", ha='center', va='center', color='white', fontsize=14)
        ax.set_facecolor('#222')
        ax.axis('off')  # Hide axes
    else:
        # Sort dates and calculate values to plot
        dates = sorted(grouped.keys())
        landed_counts = [grouped[d]['landed'] for d in dates]
        tries_counts = [grouped[d]['tries'] for d in dates]

        # Calculate landing % for each day (0 if no tries that day)
        landing_percentages = [
            (landed / tries) * 100 if tries else 0
            for landed, tries in zip(landed_counts, tries_counts)
        ]

        # Create the figure with smaller height for a more streamlined layout
        fig, ax = plt.subplots(figsize=(8, 3), facecolor='#222')  # dark background
        ax.set_facecolor('#333')  # slightly lighter plot area

        # Plot the landing percentage over time
        ax.plot(dates, landing_percentages, marker='o', color='limegreen', linewidth=2, label='Landing %')

        # Title and axis labels
        ax.set_title(f"Landing % Over Time for {user_trick.trick.name}", color='white', fontsize=13, pad=12)
        ax.set_xlabel("Date", color='white', fontsize=10)
        ax.set_ylabel("Landing %", color='white', fontsize=10)
        ax.set_ylim(0, 100)  # Y-axis from 0 to 100%

        # Format dates: short month + day (e.g., Jun 05)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        fig.autofmt_xdate(rotation=40)  # tilt dates for readability

        # Tweak grid and axis appearance
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.tick_params(colors='white', labelsize=8)  # smaller ticks for cleaner look

        # Add legend
        ax.legend(
            facecolor='#444', edgecolor='none', loc='upper left',
            labelcolor='white', fontsize=9
        )

    # Final layout and save image to buffer
    fig.tight_layout(pad=2)
    plt.savefig(buf, format='png', facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)

    # Return chart as an inline image (PNG format)
    return send_file(buf, mimetype='image/png')

# -------------------------------
# Chart: Cumulative lands Over Time
# -------------------------------
@main_bp.route('/cumulative_lands_chart/<int:user_trick_id>')
@requires_auth
def cumulative_lands_chart(user_trick_id):
    user_id = session["user"]["sub"]

    # Fetch the trick only if it belongs to the current user
    user_trick = UserTrick.query.filter_by(id=user_trick_id, user_id=user_id).first_or_404()

    # Get all log entries for this trick, sorted by date
    logs = PracticeLogEntry.query.filter_by(user_trick_id=user_trick.id).order_by(PracticeLogEntry.date).all()

    # Group landed counts by date
    from collections import defaultdict
    from datetime import datetime

    grouped = defaultdict(int)
    for log in logs:
        grouped[log.date] += log.landed

    buf = io.BytesIO()

    if not grouped:
        # Fallback if there's no data yet
        fig, ax = plt.subplots(facecolor='#222')
        ax.text(0.5, 0.5, "No landings yet 🛹", ha='center', va='center', color='white', fontsize=14)
        ax.set_facecolor('#222')
    else:
        # Sort the dates to show progression
        dates = sorted(grouped.keys())
        daily_landed = [grouped[d] for d in dates]

        # Build the cumulative landed list (running total)
        cumulative_landed = []
        total = 0
        for landed in daily_landed:
            total += landed
            cumulative_landed.append(total)

        # Create the plot
        fig, ax = plt.subplots(figsize=(8, 3), facecolor='#222')  # Smaller vertical height for sleek look
        ax.set_facecolor('#333')

        # Plot cumulative landed tricks
        ax.plot(dates, cumulative_landed, marker='o', color='deepskyblue', linewidth=2, label='Total Lands')

        # Titles and labels
        ax.set_title(f"Cumulative Lands for {user_trick.trick.name}", color='white', fontsize=14, pad=15)
        ax.set_xlabel("Date", color='white')
        ax.set_ylabel("Total Lands", color='white')

        # Format x-axis with month + year
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
        fig.autofmt_xdate(rotation=45)

        # Grid, ticks, legend
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.tick_params(colors='white')
        ax.legend(facecolor='#444', edgecolor='none', loc='upper left', labelcolor='white')

    # Final layout and output
    fig.tight_layout()
    plt.savefig(buf, format='png', facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)

    return send_file(buf, mimetype='image/png')

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

# ---------------------------------------
# 404 PAGE
# ---------------------------------------
@main_bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# ---------------------------------------
# 500 Internal Server Error
# ---------------------------------------
@main_bp.app_errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500

# ---------------------------------------
# Quick healthcheck that returns 200 OK
# ---------------------------------------
@main_bp.route("/healthz")
def healthz():
    return "OK", 200
