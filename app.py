from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
from forms import CandidateForm
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_bcrypt import Bcrypt
from flask_login import login_required
from flask_login import LoginManager
from flask_login import login_user
from flask_login import current_user
from flask_login import login_required, current_user
from flask_login import logout_user
from flask_migrate import Migrate  # Added Flask-Migrate
import os
import json

# Create Flask App
app = Flask(__name__)
# Configure Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///candidates.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey123'
app.config['UPLOAD_FOLDER'] = 'uploads/'


bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'student_login'


# Import db from models.py
from models import db, Candidate

# Initialize db and Migrate
db.init_app(app)
migrate = Migrate(app, db)  # Added Migrate

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    form = CandidateForm()

    if form.validate_on_submit():
        # Handle file upload
        file = form.certificate.data
        filename = None
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Save to database with student_id
        new_candidate = Candidate(
            name=form.name.data,
            surname=form.surname.data,
            student_number=form.student_number.data,
            achievements=form.achievements.data,
            certificate=filename,
            motivation=form.motivation.data,
            image=None,  # Optional: handle image later
            party=form.party.data,
            position=form.position.data,
            student_id=current_user.id  # ✅ This line fixes the error
        )

        db.session.add(new_candidate)
        db.session.commit()
        flash('Application submitted successfully!', 'success')
        return redirect(url_for('student_dashboard'))

    return render_template('apply.html', form=form)

# Initialize Flask-Admin
admin = Admin(app, name="Admin Panel", template_mode="bootstrap4")

# Create an admin view for Candidate model
class CandidateAdmin(ModelView):
    column_list = ['id', 'name', 'surname', 'student_number', 'status']
    form_columns = ['name', 'surname', 'student_number', 'achievements', 'certificate', 'motivation', 'status']
    column_searchable_list = ['name', 'surname', 'student_number']
    column_filters = ['status']

admin.add_view(CandidateAdmin(Candidate, db.session))

# API for Dashboard Data
@app.route('/admin/stats')
def admin_stats():
    total_candidates = Candidate.query.count()
    approved = Candidate.query.filter_by(status="Approved").count()
    rejected = Candidate.query.filter_by(status="Rejected").count()
    pending = Candidate.query.filter_by(status="Pending").count()

    return jsonify({
        "total": total_candidates,
        "approved": approved,
        "rejected": rejected,
        "pending": pending
    })

@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/candidates/<status>')
def filter_candidates(status):
    if status not in ["Pending", "Approved", "Rejected"]:
        flash("Invalid status!", "danger")
        return redirect(url_for('admin_dashboard'))
    
    candidates = Candidate.query.filter_by(status=status).all()
    return render_template('candidate_list.html', candidates=candidates, status=status)

@app.route('/admin')
def admin():
    candidates = Candidate.query.all()
    return render_template('admin.html', candidates=candidates)

@app.route('/download/<filename>')
def download_certificate(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/approve/<int:candidate_id>')
def approve_candidate(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    candidate.status = "Approved"
    db.session.commit()
    flash('Candidate Approved!', 'success')
    return redirect(url_for('admin'))

@app.route('/reject/<int:candidate_id>')
def reject_candidate(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    candidate.status = "Rejected"
    db.session.commit()
    flash('Candidate Rejected!', 'danger')
    return redirect(url_for('admin'))

@app.route('/delete/<int:candidate_id>')
def delete_candidate(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    db.session.delete(candidate)
    db.session.commit()
    flash('Candidate Deleted!', 'danger')
    return redirect(url_for('admin'))

@app.route('/')  
def home():
    return render_template('home.html')

from models import db, Student, Candidate
from forms import StudentRegistrationForm, StudentLoginForm

@login_manager.user_loader
def load_user(user_id):
    return Student.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = StudentRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        student = Student(email=form.email.data, password=hashed_password)
        db.session.add(student)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('student_login'))
    
    # Print form errors if validation fails
    print(form.errors)  
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def student_login():
    form = StudentLoginForm()
    if form.validate_on_submit():
        student = Student.query.filter_by(email=form.email.data).first()
        if student and bcrypt.check_password_hash(student.password, form.password.data):
            login_user(student)  # This line logs in the user
            flash('Login successful!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Login failed. Check email and password.', 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))  # Or wherever you want to redirect after logout
    
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    applications = Candidate.query.filter_by(student_id=current_user.id).all() # Use current_user here
    return render_template('student_dashboard.html', applications=applications)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))


