from datetime import datetime
from app import db

class Departments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(50), nullable=False)

class Jobs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job = db.Column(db.String(50), nullable=False)

class HiredEmployees(db.Model):    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    datetime = db.Column(db.DateTime)
    # datetime = db.Column(db.String(50))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'))

model_cols = {
    'departments': ['id', 'department'],
    'jobs': ['id', 'job'],
    'hired_employees': ['id', 'name', 'datetime', 'department_id', 'job_id']
}