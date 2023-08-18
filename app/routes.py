from flask import request, jsonify
from app import app, db
from app.models import model_cols, Departments, HiredEmployees, Jobs
import csv
import os
import io
import pandas as pd
import dateutil
from sqlalchemy import text

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
    if not table_name in model_cols.keys():
        return {"error": "Table name incorrect"}, 400
        
    rows_to_insert = []
    skipped_rows = 0
    invalid_rows = 0

    # Read the CSV content using pandas
    df = pd.read_csv(file.stream, names=model_cols[table_name])

    for index, row in df.iterrows():
    
        # Batch insert of departments data
        if table_name == 'departments':
            # Data type validation
            try:
                id_val = int(row['id'])
                department_val = str(row['department'])
            except ValueError:
                invalid_rows += 1
                continue

            existing_ids = {row[0] for row in db.session.query(Departments.id).all()}
            if id_val not in existing_ids:
                new_entry = Departments(id=id_val, department=department_val)
                rows_to_insert.append(new_entry)
                existing_ids.add(id_val)
            else:
                skipped_rows += 1

            if len(rows_to_insert) == 1000:
                db.session.bulk_save_objects(rows_to_insert)
                rows_to_insert = []

        
        # Batch insert of jobs data
        elif table_name == 'jobs':
            # Data type validation
            try:
                id_val = int(row['id'])
                job_val = str(row['job'])
            except ValueError:
                invalid_rows += 1
                continue

            existing_ids = {row[0] for row in db.session.query(Jobs.id).all()}
            if id_val not in existing_ids:
                new_entry = Jobs(id=id_val, job=job_val)
                rows_to_insert.append(new_entry)
                existing_ids.add(id_val)
            else:
                skipped_rows += 1

            if len(rows_to_insert) == 1000:
                db.session.bulk_save_objects(rows_to_insert)
                rows_to_insert = []
                

        # Batch insert of hired employees data
        elif table_name == 'hired_employees':
            # Data type validation
            try:
                id_val = int(row['id'])
                name_val = str(row['name'])
                datetime_val = dateutil.parser.parse(str(row['datetime']))
                department_id_val = int(row['department_id'])
                job_id_val = int(row['job_id'])
            except ValueError:
                invalid_rows += 1
                continue
            
            existing_ids = {row[0] for row in db.session.query(HiredEmployees.id).all()}
            if id_val not in existing_ids:
                new_entry = HiredEmployees(id=id_val, name=name_val, datetime=datetime_val, department_id=department_id_val, job_id=job_id_val)
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



@app.route('/hires-quater-2021', methods=['GET'])
def hires_by_quarter_2021_sql():
    sql = text("""
    SELECT 
    d.department,
    j.job,
    CASE 
        WHEN strftime('%m', e.datetime) BETWEEN '01' AND '03' THEN 'Q1'
        WHEN strftime('%m', e.datetime) BETWEEN '04' AND '06' THEN 'Q2'
        WHEN strftime('%m', e.datetime) BETWEEN '07' AND '09' THEN 'Q3'
        WHEN strftime('%m', e.datetime) BETWEEN '10' AND '12' THEN 'Q4'
    END AS quarter,
    COUNT(e.id) AS num_hires
FROM 
    hired_employees e
JOIN 
    departments d ON e.department_id = d.id
JOIN 
    jobs j ON e.job_id = j.id
WHERE 
    strftime('%Y', e.datetime) = '2021'
GROUP BY 
    d.department, j.job, quarter
ORDER BY 
    d.department, j.job;
    """)
    # Get a connection and execute the SQL
    with db.engine.connect() as connection:
        result = connection.execute(sql)
        rows = result.fetchall()

    # Convert results to a table structure
    table_header = ["Department", "Job", "Quarter", "Number of Hires"]
    table_data = [list(row) for row in rows]

    table = {
        "header": table_header,
        "data": table_data
    }

    return jsonify(table)



@app.route('/hires-upper-avg', methods=['GET'])
def hires_upper_average():
    sql = text("""
    WITH MeanHires AS (
    SELECT AVG(hire_count) AS mean_hires
    FROM (
        SELECT department_id, COUNT(id) AS hire_count
        FROM hired_employees
        WHERE strftime('%Y', datetime) = '2021'
        GROUP BY department_id
    )
)

SELECT d.id, d.department AS name, COUNT(e.id) AS num_hires
FROM departments d
JOIN hired_employees e ON d.id = e.department_id
WHERE strftime('%Y', e.datetime) = '2021'
GROUP BY d.id, d.department
HAVING COUNT(e.id) > (SELECT mean_hires FROM MeanHires)
ORDER BY num_hires DESC;
    """)
    # Get a connection and execute the SQL
    with db.engine.connect() as connection:
        result = connection.execute(sql)
        rows = result.fetchall()

    # Convert results to a table structure
    table_header = ["Id", "Department", "Number of Hires"]
    table_data = [list(row) for row in rows]

    table = {
        "header": table_header,
        "data": table_data
    }

    return jsonify(table)



if __name__ == '__main__':
    app.run(debug=True)