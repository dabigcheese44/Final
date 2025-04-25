from flask import (
    current_app as app,
    render_template, redirect, request, session, url_for, json
)
from flask_socketio import emit, join_room
from .utils.database.database import database
from datetime import datetime
from . import socketio
import functools

# ---------------------------------------------------------------------------
#  Init
# ---------------------------------------------------------------------------
db = database()

# ---------------------------------------------------------------------------
#  Helpers
# ---------------------------------------------------------------------------
def login_required(func):
    """Redirects to /login if the user is not logged in."""
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return secure_function


def get_current_user_email():
    enc = session.get("email")
    if not enc:
        return None
    try:
        return db.reversibleEncrypt("decrypt", enc)
    except Exception:
        return None


def get_current_user_id():
    email = get_current_user_email()
    if not email:
        return None
    res = db.query("SELECT user_id FROM users WHERE email=%s", (email,))
    return res[0]["user_id"] if res else None


# ---------------------------------------------------------------------------
#  Auth pages
# ---------------------------------------------------------------------------
@app.route("/")
def root():
    return redirect("/login")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------------------------------------------------------------------------
#  Auth actions
# ---------------------------------------------------------------------------
@app.route("/processsignup", methods=["POST"])
def process_signup():
    """Create a brand-new account or log in an existing one, and
       automatically attach the user to any events they were invited to
       before they signed up."""
    email    = request.form.get("email").strip().lower()
    password = request.form.get("password")

    existing = db.query("SELECT user_id, password FROM users WHERE email=%s", (email,))
    if existing:
        if db.onewayEncrypt(password) == existing[0]["password"]:
            session["email"] = db.reversibleEncrypt("encrypt", email)
            return json.dumps({"success": 1, "redirect": "/createevent"})
        return json.dumps({"success": 0,
                           "message": "User exists but password is incorrect"})

    create_res = db.createUser(email=email, password=password)
    if not create_res["success"]:
        return json.dumps({"success": 0, "message": create_res["message"]})

    # log them in
    session["email"] = db.reversibleEncrypt("encrypt", email)

    # obtain new user_id (createUser may return it; otherwise look it up)
    uid = create_res.get("user_id")
    if uid is None:
        uid = db.query("SELECT user_id FROM users WHERE email=%s", (email,))[0]["user_id"]

    pending = db.query("""
        SELECT event_id
          FROM event_invites
         WHERE email=%s AND user_id IS NULL
    """, (email,))

    for row in pending:
        eid = row["event_id"]
        db.addUserToEvent(uid, eid)
        db.query("""
            UPDATE event_invites
               SET user_id=%s
             WHERE event_id=%s AND email=%s
        """, (uid, eid, email))

    return json.dumps({"success": 1, "redirect": "/createevent"})



@app.route("/processlogin", methods=["POST"])
def process_login():
    email    = request.form.get("email")
    password = request.form.get("password")

    res = db.authenticate(email=email, password=password)
    if res["success"]:
        session["email"] = db.reversibleEncrypt("encrypt", email)
        return json.dumps({"success": 1, "redirect": "/createevent"})
    return json.dumps({"success": 0, "message": res["message"]})


# ---------------------------------------------------------------------------
#  Event creation / join pages
# ---------------------------------------------------------------------------
@app.route("/createevent")
@login_required
def create_event_page():
    return render_template("createevent.html",
                           user_email=get_current_user_email())


@app.route("/joinevent")
@login_required
def join_event_page():
    uid    = get_current_user_id()
    email  = get_current_user_email()          
    events = db.getUserEvents(uid, email)      
    return render_template(
        "joinevent.html",
        user_email=email,
        events=events
    )


# ---------------------------------------------------------------------------
#  Event creation action
# ---------------------------------------------------------------------------
@app.route("/processevent", methods=["POST"])
@login_required
def process_event():
    data = request.form.to_dict(flat=True)

    title          = data.get("title")
    start_date     = data.get("start_date")      # yyyy‑mm‑dd
    end_date       = data.get("end_date")
    day_start_time = data.get("day_start_time")  # hh:mm
    day_end_time   = data.get("day_end_time")
    invitees       = request.form.getlist("invitees[]")  # list of emails

    creator_id = get_current_user_id()
    if not creator_id:
        return json.dumps({'success':0, 'message':'Session expired – please log in again'})

    res = db.createEvent(title, creator_id,
                         start_date, end_date,
                         day_start_time, day_end_time)
    if not res["success"]:
        return json.dumps(res)

    event_id = res["event_id"]

    for email in invitees:
        # 1) always store the invitation
        db.query("""
            INSERT IGNORE INTO event_invites (event_id, email)
            VALUES (%s, %s)
        """, (event_id, email))

        # 2) if the account exists, associate right now
        row = db.query("SELECT user_id FROM users WHERE email=%s", (email,))
        if row:
            uid = row[0]["user_id"]
            db.addUserToEvent(uid, event_id)
            db.query("""
                UPDATE event_invites
                   SET user_id=%s
                 WHERE event_id=%s AND email=%s
            """, (uid, event_id, email))

    session["current_event_id"] = event_id
    return json.dumps({"success": 1, "redirect": f"/event?event_id={event_id}"})


# ---------------------------------------------------------------------------
#  Event page
# ---------------------------------------------------------------------------
@app.route("/event")
@login_required
def event_page():
    event_id = request.args.get("event_id") or session.get("current_event_id")
    if not event_id:
        return redirect("/joinevent")

    uid = get_current_user_id()

    # access control
    allowed = db.query(
        "SELECT 1 FROM event_users WHERE user_id=%s AND event_id=%s",
        (uid, event_id)
    )
    if not allowed:
        return "Access denied", 403

    session["current_event_id"] = event_id
    meta = db.getEventMeta(event_id)
    return render_template("event.html",
                           user_email=get_current_user_email(),
                           event=meta,
                           current_user_id=uid)


# ---------------------------------------------------------------------------
#  Availability API
# ---------------------------------------------------------------------------
@app.route("/setavailability", methods=["POST"])
@login_required
def set_availability():
    """
    JSON payload example:
    {
      "rows": [
        [event_id, user_id, "2025-04-25 14:00:00", "available"],
        ...
      ]
    }
    """
    rows = request.json.get("rows", [])
    if not rows:
        return json.dumps({"success": 0, "message": "No rows provided"})

    db.insertAvailabilities(rows)

    event_id = rows[0][0]
    avail    = db.getEventAvailabilities(event_id)

    # after you’ve called db.getEventAvailabilities(event_id)
    avail = db.getEventAvailabilities(event_id)

    # convert slot_start datetimes to ISO strings so JSON can handle them
    for row in avail:
        if isinstance(row['slot_start'], datetime):
            row['slot_start'] = row['slot_start'].isoformat(sep=' ', timespec='seconds')

    socketio.emit(
        "availability_updated",
        {"avail": avail},          # now serialisable
        room=f"event_{event_id}",
        namespace="/event"
    )

    return json.dumps({"success": 1})


@app.route('/geteventdata')
@login_required
def get_event_data():
    event_id = session.get('current_event_id')
    if not event_id:
        return json.dumps({'success': 0, 'message': 'No event selected'})

    avail = db.getEventAvailabilities(event_id)

    for row in avail:
        if isinstance(row['slot_start'], datetime):
            row['slot_start'] = row['slot_start'].isoformat(sep=' ', timespec='seconds')

    return json.dumps({'success': 1, 'avail': avail})



# ---------------------------------------------------------------------------
#  Socket.IO namespace
# ---------------------------------------------------------------------------
@socketio.on("join_event", namespace="/event")
def join_event_socket(data=None):
    event_id = session.get("current_event_id")
    if event_id:
        join_room(f"event_{event_id}")
        emit("status",
             {"msg": "User joined event"},
             room=f"event_{event_id}")

