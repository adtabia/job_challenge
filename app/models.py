from datetime import datetime
from app import db

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(50), nullable=False)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job = db.Column(db.String(50), nullable=False)

class HiredEmployee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    datetime = db.Column(db.String(50), default=datetime.utcnow)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))