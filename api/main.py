from flask import Flask, render_template, request, redirect, send_file, session
from flask_sqlalchemy import SQLAlchemy
from PyPDF2 import PdfReader
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
import joblib
import os

import matplotlib
matplotlib.use('Agg')

# =========================
# BASE PATH (IMPORTANT FOR VERCEL)
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =========================
# FLASK APP (ONLY ONCE)
# =========================
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "../templates"),
    static_folder=os.path.join(BASE_DIR, "../static")
)

app.secret_key = "placement_secret_key"

# =========================
# DATABASE CONFIG (Vercel safe)
# =========================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# =========================
# MODELS
# =========================
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    regno = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100))
    prediction = db.Column(db.String(200))

with app.app_context():
    db.create_all()

# =========================
# LOAD MODEL
# =========================
model = joblib.load("model.pkl")

latest_report = {}

# =========================
# COMPANY DATA
# =========================
companies = {
    "Google": {"requirements": [8.5, 3, 8, 0], "logo": "google.png"},
    "Microsoft": {"requirements": [8.0, 2, 7, 0], "logo": "microsoft.png"},
    "Amazon": {"requirements": [7.5, 2, 7, 0], "logo": "amazon.png"},
    "Infosys": {"requirements": [6.0, 1, 5, 0], "logo": "infosys.png"},
    "TCS": {"requirements": [6.0, 1, 5, 0], "logo": "tcs.png"},
    "Wipro": {"requirements": [6.0, 1, 5, 0], "logo": "wipro.png"},
    "IBM": {"requirements": [7.0, 2, 6, 0], "logo": "ibm.png"},
    "Accenture": {"requirements": [6.5, 1, 6, 0], "logo": "accenture.png"},
    "Capgemini": {"requirements": [6.0, 1, 5, 0], "logo": "capgemini.jpg"},
    "Deloitte": {"requirements": [7.0, 2, 6, 0], "logo": "deloitte.png"}
}

# =========================
# ROUTES
# =========================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        student = Student.query.filter_by(email=email, password=password).first()

        if student:
            session["student"] = student.regno
            return render_template("dashboard.html")

        return "Invalid Login"
    return render_template("login.html")


# =========================
# FIXED SIGNUP ROUTE (INDENTATION FIXED)
# =========================
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":

        fullname = request.form.get("fullname")
        email = request.form.get("email")
        regno = request.form.get("regno")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not fullname or not email or not regno or not password:
            return "Missing fields"

        if password != confirm_password:
            return "Passwords do not match"

        existing = Student.query.filter_by(email=email).first()
        if existing:
            return "User already exists"

        student = Student(email=email, regno=regno, password=password)
        db.session.add(student)
        db.session.commit()

        return redirect("/login")

    return render_template("signup.html")


@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    return render_template("forgot.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    global latest_report

    name = request.form["name"]
    cgpa = float(request.form["cgpa"])
    projects = int(request.form["projects"])
    communication = int(request.form["communication"])
    internships = int(request.form["internships"])
    backlogs = int(request.form["backlogs"])
    skills = request.form["skills"]

    prediction = model.predict([[cgpa, projects, communication, internships]])[0]

    ai_message = "High Placement Probability 🚀" if prediction == 1 else "Need Improvement ⚠"

    latest_report = {
        "name": name,
        "cgpa": cgpa,
        "projects": projects,
        "communication": communication,
        "internships": internships,
        "backlogs": backlogs,
        "skills": skills,
        "prediction": ai_message
    }

    return render_template(
        "result.html",
        name=name,
        ai_message=ai_message,
        results=[],
        suggestions=[]
    )


@app.route("/download")
def download():
    pdf_path = "/tmp/report.pdf"
    c = canvas.Canvas(pdf_path)
    c.drawString(100, 800, "Placement Report")
    c.save()

    return send_file(pdf_path, as_attachment=True)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# =========================
# VERCEL ENTRYPOINT (IMPORTANT FIX)
# =========================
app = app