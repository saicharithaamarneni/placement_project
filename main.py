from flask import (
    Flask,
    render_template,
    request,
    redirect,
    send_file,
    session
)

from flask_sqlalchemy import SQLAlchemy

import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader

import joblib
import os

# =========================================
# FLASK APP
# =========================================

app = Flask(__name__)

app.secret_key = "placement_secret_key"

# =========================================
# DATABASE CONFIG
# =========================================

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# =========================================
# DATABASE
# =========================================

db = SQLAlchemy(app)

# =========================================
# LOAD ML MODEL
# =========================================

model = joblib.load("model.pkl")

# =========================================
# GLOBAL REPORT DATA
# =========================================

latest_report = {}

# =========================================
# STUDENT TABLE
# =========================================

class Student(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    regno = db.Column(
        db.String(100),
        unique=True
    )

    email = db.Column(
        db.String(100)
    )

    password = db.Column(
        db.String(100)
    )

# =========================================
# HISTORY TABLE
# =========================================

class History(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_name = db.Column(
        db.String(100)
    )

    prediction = db.Column(
        db.String(200)
    )

# =========================================
# CREATE DATABASE
# =========================================

with app.app_context():

    db.create_all()

# =========================================
# COMPANY DATA
# =========================================

companies = {

    "Google": {
        "requirements": [8.5, 3, 8, 0],
        "logo": "google.png"
    },

    "Microsoft": {
        "requirements": [8.0, 2, 7, 0],
        "logo": "microsoft.png"
    },

    "Amazon": {
        "requirements": [7.5, 2, 7, 0],
        "logo": "amazon.png"
    },

    "Infosys": {
        "requirements": [6.0, 1, 5, 0],
        "logo": "infosys.png"
    },

    "TCS": {
        "requirements": [6.0, 1, 5, 0],
        "logo": "tcs.png"
    },

    "Wipro": {
        "requirements": [6.0, 1, 5, 0],
        "logo": "wipro.png"
    },

    "IBM": {
        "requirements": [7.0, 2, 6, 0],
        "logo": "ibm.png"
    },

    "Accenture": {
        "requirements": [6.5, 1, 6, 0],
        "logo": "accenture.png"
    },

    "Capgemini": {
        "requirements": [6.0, 1, 5, 0],
        "logo": "capgemini.jpg"
    },

    "Deloitte": {
        "requirements": [7.0, 2, 6, 0],
        "logo": "deloitte.png"
    }
}

# =========================================
# HOME PAGE
# =========================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )

# =========================================
# LOGIN PAGE
# =========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]

        password = request.form["password"]

        student = Student.query.filter_by(
            email=email,
            password=password
        ).first()

        if student:

            session["student"] = student.regno

            return render_template(
                "dashboard.html"
            )

        else:

            return """

<h2>Invalid Login</h2>

<a href='/login'>
Try Again
</a>

"""

    return render_template(
        "login.html"
    )

# =========================================
# SIGNUP PAGE
# =========================================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        email = request.form["email"]

        regno = request.form["regno"]

        password = request.form["password"]

        existing = Student.query.filter_by(
            email=email
        ).first()

        if existing:

            return """

<h2>Email Already Exists</h2>

<a href='/signup'>
Try Again
</a>

"""

        student = Student(

            email=email,

            regno=regno,

            password=password
        )

        db.session.add(student)

        db.session.commit()

        return redirect("/login")

    return render_template(
        "signup.html"
    )

# =========================================
# FORGOT PASSWORD
# =========================================

@app.route("/forgot", methods=["GET", "POST"])
def forgot():

    if request.method == "POST":

        email = request.form["email"]

        new_password = request.form["password"]

        student = Student.query.filter_by(
            email=email
        ).first()

        if student:

            student.password = new_password

            db.session.commit()

            return """

<h2>Password Updated Successfully</h2>

<a href='/login'>
Go To Login
</a>

"""

        else:

            return """

<h2>Email Not Found</h2>

<a href='/forgot'>
Try Again
</a>

"""

    return render_template(
        "forgot.html"
    )

# =========================================
# ANALYZE PAGE
# =========================================

@app.route("/analyze", methods=["POST"])
def analyze():

    global latest_report

    name = request.form["name"]

    cgpa = float(
        request.form["cgpa"]
    )

    projects = int(
        request.form["projects"]
    )

    communication = int(
        request.form["communication"]
    )

    internships = int(
        request.form["internships"]
    )

    backlogs = int(
        request.form["backlogs"]
    )

    skills = request.form["skills"]

    # =====================================
    # ML PREDICTION
    # =====================================

    prediction = model.predict([[

        cgpa,
        projects,
        communication,
        internships

    ]])[0]

    if prediction == 1:

        ai_message = (
            "High Placement Probability 🚀"
        )

    else:

        ai_message = (
            "Need Improvement ⚠"
        )

    # =====================================
    # IMPROVEMENT SUGGESTIONS
    # =====================================

    suggestions = []

    if cgpa < 7:

        suggestions.append(
            "Improve academic performance and maintain CGPA above 7.5"
        )

    if projects < 2:

        suggestions.append(
            "Build real-time projects using Python, Java or Web Development"
        )

    if communication < 7:

        suggestions.append(
            "Practice communication and aptitude regularly"
        )

    if internships < 1:

        suggestions.append(
            "Apply for internships to gain industry experience"
        )

    if backlogs > 0:

        suggestions.append(
            "Clear all active backlogs immediately"
        )

    if "python" not in skills.lower():

        suggestions.append(
            "Learn Python programming for better placement opportunities"
        )

    if len(suggestions) == 0:

        suggestions.append(
            "Excellent profile. Keep improving advanced technical skills"
        )

    # =====================================
    # PIE CHART
    # =====================================

    labels = [

        "CGPA",
        "Projects",
        "Communication",
        "Internships"
    ]

    sizes = [

        cgpa,
        projects,
        communication,
        internships
    ]

    colors = [

        '#00c6ff',
        '#2563eb',
        '#7c3aed',
        '#06b6d4'
    ]

    plt.figure(figsize=(6, 6))

    plt.pie(

        sizes,

        labels=labels,

        autopct='%1.1f%%',

        colors=colors
    )

    plt.title(
        "Skill Analysis"
    )

    plt.savefig(
        "static/chart.png"
    )

    plt.close()

    # =====================================
    # COMPANY ANALYSIS
    # =====================================

    results = []

    for company, data in companies.items():

        req = data["requirements"]

        reasons = []

        recommendations = []

        eligible = True

        # CGPA CHECK

        if cgpa < req[0]:

            eligible = False

            reasons.append(
                f"Required CGPA is {req[0]}"
            )

            recommendations.append(
                "Improve CGPA"
            )

        # PROJECT CHECK

        if projects < req[1]:

            eligible = False

            reasons.append(
                f"Minimum {req[1]} projects required"
            )

            recommendations.append(
                "Build More Projects"
            )

        # COMMUNICATION CHECK

        if communication < req[2]:

            eligible = False

            reasons.append(
                "Communication skills are low"
            )

            recommendations.append(
                "Improve Communication"
            )

        # BACKLOG CHECK

        if backlogs > req[3]:

            eligible = False

            reasons.append(
                "Active backlogs not allowed"
            )

            recommendations.append(
                "Clear Backlogs"
            )

        # INTERNSHIP CHECK

        if internships < 1:

            recommendations.append(
                "Try Internships"
            )

        status = (

            "Eligible ✅"

            if eligible

            else

            "Not Eligible ❌"
        )

        results.append({

            "company": company,

            "logo": data["logo"],

            "status": status,

            "reasons": reasons,

            "recommendations": recommendations
        })

    # =====================================
    # SAVE HISTORY
    # =====================================

    history = History(

        student_name=name,

        prediction=ai_message
    )

    db.session.add(history)

    db.session.commit()

    # =====================================
    # SAVE REPORT DATA
    # =====================================

    latest_report = {

        "name": name,
        "cgpa": cgpa,
        "projects": projects,
        "communication": communication,
        "internships": internships,
        "backlogs": backlogs,
        "skills": skills,
        "prediction": ai_message,
        "suggestions": suggestions
    }

    # =====================================
    # RETURN RESULT PAGE
    # =====================================

    return render_template(

        "result.html",

        results=results,

        name=name,

        ai_message=ai_message,

        chart_path="chart.png",

        suggestions=suggestions
    )

# =========================================
# RESUME ANALYZER
# =========================================

@app.route("/resume", methods=["POST"])
def resume():

    file = request.files["resume"]

    upload_folder = "uploads"

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    path = os.path.join(

        upload_folder,

        file.filename
    )

    file.save(path)

    reader = PdfReader(path)

    text = ""

    for page in reader.pages:

        extracted = page.extract_text()

        if extracted:

            text += extracted

    skills = [

        "Python",
        "Java",
        "DSA",
        "Flask",
        "SQL",
        "Machine Learning"
    ]

    found = []

    for skill in skills:

        if skill.lower() in text.lower():

            found.append(skill)

    return f"""

Resume Uploaded Successfully

Skills Found:
{found}

"""

# =========================================
# CHATBOT PAGE
# =========================================

@app.route("/chatbot")
def chatbot():

    return render_template(
        "chatbot.html"
    )

# =========================================
# INTERVIEW PAGE
# =========================================

@app.route("/interview")
def interview():

    return render_template(
        "interview.html"
    )

# =========================================
# ADMIN DASHBOARD
# =========================================

@app.route("/admin")
def admin():

    students = Student.query.all()

    history = History.query.all()

    return render_template(

        "admin.html",

        students=students,

        history=history
    )

# =========================================
# PDF DOWNLOAD
# =========================================

@app.route("/download")
def download():

    global latest_report

    pdf_path = "placement_report.pdf"

    c = canvas.Canvas(pdf_path)

    # TITLE

    c.setFont(
        "Helvetica-Bold",
        22
    )

    c.drawString(
        150,
        800,
        "AI Placement Report"
    )

    # STUDENT DETAILS

    c.setFont(
        "Helvetica",
        14
    )

    c.drawString(
        50,
        760,
        f"Student Name: {latest_report.get('name')}"
    )

    c.drawString(
        50,
        735,
        f"CGPA: {latest_report.get('cgpa')}"
    )

    c.drawString(
        50,
        710,
        f"Projects: {latest_report.get('projects')}"
    )

    c.drawString(
        50,
        685,
        f"Communication: {latest_report.get('communication')}"
    )

    c.drawString(
        50,
        660,
        f"Internships: {latest_report.get('internships')}"
    )

    c.drawString(
        50,
        635,
        f"Backlogs: {latest_report.get('backlogs')}"
    )

    c.drawString(
        50,
        610,
        f"Skills: {latest_report.get('skills')}"
    )

    c.drawString(
        50,
        575,
        f"Prediction: {latest_report.get('prediction')}"
    )

    # SUGGESTIONS

    c.setFont(
        "Helvetica-Bold",
        16
    )

    c.drawString(
        50,
        530,
        "Suggestions To Improve"
    )

    c.setFont(
        "Helvetica",
        13
    )

    y = 500

    for suggestion in latest_report.get("suggestions", []):

        c.drawString(
            60,
            y,
            f"- {suggestion}"
        )

        y -= 25

    c.save()

    return send_file(

        pdf_path,

        as_attachment=True
    )

# =========================================
# LOGOUT
# =========================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# =========================================
# RUN APP
# =========================================

if __name__ == "__main__":

    app.run(debug=True)