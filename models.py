from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Student(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    applications = db.relationship('Candidate', backref='student', lazy=True)

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    student_number = db.Column(db.String(20), unique=True, nullable=False)
    achievements = db.Column(db.Text, nullable=False)
    certificate = db.Column(db.String(200), nullable=True)
    motivation = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="Pending")

    image = db.Column(db.String(200), nullable=True)
    party = db.Column(db.String(50), nullable=False, default="Independent")
    position = db.Column(db.String(100), nullable=False, default="Member")

    # Link to Student who applied
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)

    def __repr__(self):
        return f"Candidate({self.name}, {self.surname}, {self.student_number}, {self.party}, {self.position})"