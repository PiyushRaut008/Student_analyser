from flask import Flask, render_template, request ,redirect, url_for
from pymongo import MongoClient
import pandas as pd
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
client = MongoClient('mongodb://localhost:27017')
db = client['Student_data']
collection = db['Students']

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/data", methods=["POST"])
def datahandle():
    if request.method == "POST":
        roll_number = request.form["roll_number"]
        existing_student = collection.find_one({"roll_number": roll_number})
        
        if existing_student:
            return "Roll number already exists. Please use a different roll number.", 400
        
        student_data = {
            "name": request.form["name"],
            "class": request.form["class"],
            "roll_number": roll_number,
            "cgpa": {
                "1st_semester": request.form["cgpa1"],
                "2nd_semester": request.form["cgpa2"],
                "3rd_semester": request.form["cgpa3"],
                "4th_semester": request.form["cgpa4"],
                "5th_semester": request.form["cgpa5"],
                "6th_semester": request.form["cgpa6"],
                "7th_semester": request.form["cgpa7"],
                "8th_semester": request.form["cgpa8"]
            }
        }
        collection.insert_one(student_data)
        return "Data submitted successfully!"

@app.route('/dash_board', methods=["GET", "POST"])
def dash_board():
    return render_template("dash_board.html")


@app.route("/uploades", methods=["GET", "POST"])
def uploadss():
    return render_template("uploads.html")


@app.route("/uploaded_data", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if file and file.filename.endswith('.csv'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        process_csv(filepath)
        return "CSV data uploaded successfully!"
    return "Invalid file format", 400

def process_csv(filepath):
    data = pd.read_csv(filepath)
    payload = data.to_dict(orient='records')

    # Check for duplicate data
    duplicates = []
    for record in payload:
        if collection.find_one(record):
            duplicates.append(record)

    if duplicates:
        os.remove(filepath)
        return "Some data already exists in the database. No new data was inserted."

    collection.insert_many(payload)
    os.remove(filepath)