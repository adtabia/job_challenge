from flask import request
from app import app, db
from app.models import Department, Job, HiredEmployee
import csv
import os

@app.route('/upload-csv', methods=['POST'])
def upload_csv():
    file = request.files['file']
    table_name = request.form['table_name']

    if not file or not table_name:
        return {"error": "File or table name missing"}, 400

    # Save the file temporarily
    # filepath = os.path.join("/tmp", file.filename)
    filepath = "tmp\\" + file.filename
    file.save(filepath)

    with open(filepath, 'r') as f:
        reader = csv.reader(f)

        if table_name == "departments":
            for row in reader:
                department = Department(id=row[0], department=row[1])
                db.session.add(department)
        elif table_name == "jobs":
            for row in reader:
                job = Job(id=row[0], title=row[1])
                db.session.add(job)
        elif table_name == "employees":
            for row in reader:
                employee = HiredEmployee(id=row[0], name=row[1], datetime=row[2], department_id=row[3], job_id=row[4])
                db.session.add(employee)
        else:
            return {"error": "Invalid table name"}, 400

        db.session.commit()

    os.remove(filepath)
    return {"message": "Data uploaded successfully"}, 200