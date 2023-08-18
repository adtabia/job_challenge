# Challenge - RESTful API Documentation

This document provides an overview of the API structure and guides you on how to use the available endpoints.

## API Structure

The API is organized around three main resources:

- **Employees**: Represents individual employees.
- **Departments**: Represents the various departments within the organization.
- **Jobs**: Represents the different job roles.

The data is stored in a SQLite database.

## Getting Started

### Prerequisites

- Python 3.8+
- Required Python packages: See `requirements.txt`
- SQLite3

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/adtabia/job_challenge.git
2. Navigate to the project directory and install the required packages:
    ```bash
   cd job_challenge
   pip3 install -r requirements.txt
3. Run the API:
   ```bash
   python3 run.py

The API should now be running on http://localhost:5000/.

## Endpoints

### POST `/batch-insert`

Uploads data from CSV files to the database. The request's form needs the path to the file and the table name.

**Request Example**:
```bash
curl -X POST -F "file=@data\departments.csv" -F "table_name=departments" http://localhost:5000/batch-insert
```

- **Response**:
- `200 OK` on success.
- `400 Bad Request` if there's an error with the uploaded file.

### GET `/hires-quater-2021`

Fetches the number of employees hired for each job and department in 2021, divided by quarter.

- **Response**:
    - `200 OK` on success.
    - Returns a JSON object with the data.


### GET `/hires-upper-mean`

Fetches a list of departments that hired more employees than the mean of employees hired in 2021 for all the departments.

- **Response**:
    - `200 OK` on success.
    - Returns a JSON object with the data.
