from flask import request
from app import app, db
from app.models import model_cols, Department, HiredEmployee, Job
import csv
import os
import io
import pandas as pd
import dateutil

@app.route('/batch-insert', methods=['POST'])
def upload_and_batch_insert():

    # File and table name
    file = request.files['file']
    table_name = request.form['table_name']

    # Checking if the file is correct
    if (file.filename == '') & ('.csv' in file.filename):
        return {"error": "No file selected or incorrect file"}, 400
    
    # Checking if the table name is correct
    if not table_name:
        return {"error": "Table name missing"}, 400
        
    rows_to_insert = []
    skipped_rows = 0
    invalid_rows = 0

    # Read the CSV content using pandas
    df = pd.read_csv(file.stream, names=model_cols[table_name])

    for index, row in df.iterrows():
    
        # Batch insert of departments data
        if table_name == 'department':
            # Data type validation
            try:
                id_val = int(row['id'])
                department_val = str(row['department'])
            except ValueError:
                invalid_rows += 1
                continue

            existing_ids = {row[0] for row in db.session.query(Department.id).all()}
            if id_val not in existing_ids:
                new_entry = Department(id=id_val, department=department_val)
                rows_to_insert.append(new_entry)
                existing_ids.add(id_val)
            else:
                skipped_rows += 1

            if len(rows_to_insert) == 1000:
                db.session.bulk_save_objects(rows_to_insert)
                rows_to_insert = []

        
        # Batch insert of jobs data
        if table_name == 'job':
            # Data type validation
            try:
                id_val = int(row['id'])
                job_val = str(row['job'])
            except ValueError:
                invalid_rows += 1
                continue

            existing_ids = {row[0] for row in db.session.query(Job.id).all()}
            if id_val not in existing_ids:
                new_entry = Job(id=id_val, job=job_val)
                rows_to_insert.append(new_entry)
                existing_ids.add(id_val)
            else:
                skipped_rows += 1

            if len(rows_to_insert) == 1000:
                db.session.bulk_save_objects(rows_to_insert)
                rows_to_insert = []
                

        # Batch insert of hired employees data
        if table_name == 'employees':
            # Data type validation
            try:
                id_val = int(row['id'])
                name_val = str(row['name'])
                # datetime_val = dateutil.parser.parse(row['datetime'])
                datetime_val = str(row['datetime'])
                department_id_val = int(row['department_id'])
                job_id_val = int(row['job_id'])
            except ValueError:
                invalid_rows += 1
                continue
            
            existing_ids = {row[0] for row in db.session.query(HiredEmployee.id).all()}
            if id_val not in existing_ids:
                new_entry = HiredEmployee(id=id_val, name=name_val, datetime=datetime_val, department_id=department_id_val, job_id=job_id_val)
                rows_to_insert.append(new_entry)
                existing_ids.add(id_val)
            else:
                skipped_rows += 1

            if len(rows_to_insert) == 1000:
                db.session.bulk_save_objects(rows_to_insert)
                rows_to_insert = []

    # Save any remaining rows
    if rows_to_insert:
        db.session.bulk_save_objects(rows_to_insert)

    db.session.commit()

    message = "Data inserted successfully."
    if skipped_rows:
        message += " {skipped_rows} rows were skipped due to existing IDs.".format(skipped_rows=skipped_rows)
    if invalid_rows:
        message += " {invalid_rows} rows were skipped due to invalid data types.".format(invalid_rows=invalid_rows)

    return {"message": message}, 200



if __name__ == '__main__':
    app.run(debug=True)