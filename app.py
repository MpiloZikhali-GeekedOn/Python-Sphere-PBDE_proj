from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime


from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.functions import current_user

# App Initialization
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database Initialization
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auth4.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Bcrypt for password hashing
bcrypt = Bcrypt(app)

# Admin Credentials
ADMIN_EMAIL = "admin@voting.com"
ADMIN_PASSWORD = "admin123"  # Should be hashed in production


# ------------------------- DATABASE MODELS -------------------------

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


# Candidate Model
class Candidate(db.Model):
    __tablename__ = 'candidates'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    votes = db.Column(db.Integer, default=0)
    department = db.Column(db.String(100), nullable=False)
    contribution = db.Column(db.String(100), nullable=False)
    position = db.Column(db.Enum('President', 'Vice', 'Treasurer', name="position_enum"), nullable=False)
    political_party = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


# Voting Event Model
class VotingEvent(db.Model):
    __tablename__ = 'voting_events'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Vote Model
class Vote(db.Model):
    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)
    voter_id = db.Column(db.Integer, nullable=False)
    event_id = db.Column(db.Integer, nullable=False)
    candidate_id = db.Column(db.Integer, nullable=False)


from flask import flash
# ------------------------- ROUTES -------------------------

# Index Route
@app.route('/')
def index():
    email = session.get('user_email')  # Check if a user is logged in
    return render_template('index.html', email=email)


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check Admin Login
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['user_email'] = ADMIN_EMAIL
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))

        # Check if the user is a student
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_name'] = user.name
            session['role'] = 'student'
            return redirect(url_for('menu'))

        return 'Invalid email or password!', 401

    return render_template('login.html')


# Logout Route
@app.route('/logout')
def logout():
    # Clear the session to log out the user
    session.clear()
    return redirect(url_for('login'))


# Admin Dashboard Route
@app.route('/admin')
def admin_dashboard():
    # Ensure the user is logged in as admin
    if 'user_email' in session and session.get('role') == 'admin':
        return render_template('admin_dashboard.html', email=session['user_email'])

    # Redirect unauthorized access to login
    return redirect(url_for('login'))


# Admin Add Candidates View
@app.route('/admin/add_candidates')
def add_candidates():
    if 'user_email' in session and session.get('role') == 'admin':
        return render_template('add_candidates.html')

    return redirect(url_for('login'))


# Add SRC Candidate
@app.route('/admin/add_src_candidate', methods=['GET', 'POST'])
def add_src_candidate():
    if 'user_email' in session and session.get('role') == 'admin':
        if request.method == 'POST':
            name = request.form['name']
            department = request.form['department']
            contribution = request.form['contribution']
            position = request.form['position']
            political_party = request.form['political_party']

            # Save the SRC candidate to the database
            new_candidate = Candidate(
                name=name,
                department=department,
                contribution=contribution,
                position=position,
                political_party=political_party
            )
            db.session.add(new_candidate)
            db.session.commit()

            # Redirect to the candidates overview page
            return redirect(url_for('view_candidates'))

        return render_template('add_src_candidate.html')

    return redirect(url_for('login'))


# View All SRC Candidates
@app.route('/admin/view_candidates')
def view_candidates():
    if 'user_email' in session and session.get('role') == 'admin':
        candidates = Candidate.query.all()
        return render_template('view_candidates.html', candidates=candidates)

    return redirect(url_for('login'))


@app.route('/admin/create_voting_event', methods=['GET', 'POST'])
def create_voting_event():
    # Ensure admin is logged in
    if 'user_email' in session and session.get('role') == 'admin':
        if request.method == 'POST':
            # Extract form data
            name = request.form['name']
            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%dT%H:%M')
            end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%dT%H:%M')
            description = request.form['description']

            # Create and save the new voting event
            new_event = VotingEvent(
                name=name,
                start_date=start_date,
                end_date=end_date,
                description=description,
            )
            db.session.add(new_event)
            db.session.commit()

            # Redirect to view voting events
            return redirect(url_for('view_voting_events'))

        return render_template('create_voting_event.html')

    return redirect(url_for('login'))



@app.route('/voting-events', methods=['GET'])
def view_voting_events():
    # Ensure the user is logged in
    if 'user_id' not in session:
        flash("Please log in to access voting events.", "error")
        return redirect(url_for('login'))

    # Query voting events from the database
    voting_events = VotingEvent.query.all()

    # Pass the user's name into the template for context
    user_name = session.get('user_name', 'User')  # 'User' is a fallback if user_name is not defined
    return render_template('view_voting_events.html', voting_events=voting_events, name=user_name)




# Student Menu Route
@app.route('/menu')
def menu():
    # Ensure the user is logged in as a student
    if 'user_email' in session and session.get('role') == 'student':
        email = session['user_email']
        name = session['user_name']
        return render_template('menu.html', name=name, email=email)

    # Redirect unauthorized access to login
    return redirect(url_for('login'))


# Adjusted vote function
@app.route('/vote/<int:event_id>', methods=['GET', 'POST'])
def vote(event_id):
    # Ensure the user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to vote.", "error")
        return redirect(url_for('login'))

    # Retrieve the logged-in user's details
    user = User.query.get(user_id)

    # Get the voting event
    event = VotingEvent.query.get_or_404(event_id)

    # Get user's votes for the event
    user_votes = Vote.query.filter_by(voter_id=user_id, event_id=event_id).all()
    voted_candidate_ids = [vote.candidate_id for vote in user_votes]

    # Group candidates by position
    candidates_by_position = {}
    candidates = Candidate.query.all()
    for candidate in candidates:
        if candidate.id not in voted_candidate_ids:  # Exclude already voted candidates
            if candidate.position not in candidates_by_position:
                candidates_by_position[candidate.position] = []
            candidates_by_position[candidate.position].append(candidate)

    if request.method == 'POST':
        # Handle voting logic
        for position, candidates in candidates_by_position.items():
            candidate_id = request.form.get(position)  # Get selected candidate ID for the position
            if candidate_id:
                new_vote = Vote(voter_id=user_id, event_id=event_id, candidate_id=candidate_id)
                db.session.add(new_vote)
        db.session.commit()
        flash("Your votes have been successfully recorded!", "success")
        return redirect(url_for('vote', event_id=event_id))

    # Render voting.html
    return render_template(
        'voting.html',
        event=event,
        user=user,
        candidates_by_position=candidates_by_position,
        user_votes=user_votes,
    )







@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Validate form data
        if not name or not email or not password:
            flash("All fields are required!", "error")
            return redirect(url_for('register'))

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create a new user and insert into the database
        try:
            new_user = User(name=name, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            if "UNIQUE constraint failed" in str(e):  # Unique constraint error for email
                flash("Email already exists. Please use a different email.", "error")
            else:
                flash("An unexpected error occurred.", "error")
            return redirect(url_for('register'))
    return render_template('register.html')



# ------------------------- DATABASE INITIALIZATION -------------------------

with app.app_context():
    db.create_all()

# Run the App
if __name__ == '__main__':
    app.run()
