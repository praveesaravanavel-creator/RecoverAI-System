from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

# Temporary latest patient data
patient_data = {}


# ---------------- DATABASE ----------------

def create_database():
    conn = sqlite3.connect("recoverai.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pain INTEGER,
            sleep TEXT,
            energy TEXT,
            symptoms TEXT,
            medication TEXT,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()


create_database()


# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- PATIENT DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# ---------------- DAILY CHECK-IN ----------------

@app.route("/checkin")
def checkin():
    return render_template("checkin.html")


# ---------------- AI PREDICTION ----------------

@app.route("/prediction", methods=["GET", "POST"])
def prediction():

    if request.method == "POST":

        pain = int(request.form["pain"])
        sleep = request.form["sleep"]
        energy = request.form["energy"]
        symptoms = request.form["symptoms"]
        medication = request.form["medication"]

        # Risk prediction logic
        if pain >= 7 or sleep == "Poor" or energy == "Low":
            status = "High Risk"

        elif pain >= 4 or sleep == "Average" or energy == "Medium":
            status = "Needs Attention"

        else:
            status = "Normal Recovery"

        # Store latest patient data
        patient_data["pain"] = pain
        patient_data["sleep"] = sleep
        patient_data["energy"] = energy
        patient_data["symptoms"] = symptoms
        patient_data["medication"] = medication
        patient_data["status"] = status

        # Save check-in to SQLite
        conn = sqlite3.connect("recoverai.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO checkins
            (pain, sleep, energy, symptoms, medication, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            pain,
            sleep,
            energy,
            symptoms,
            medication,
            status
        ))

        conn.commit()
        conn.close()

        return render_template(
            "prediction.html",
            status=status
        )

    return render_template("prediction.html")


# ---------------- DOCTOR DASHBOARD ----------------

@app.route("/doctor")
def doctor():

    conn = sqlite3.connect("recoverai.db")
    cursor = conn.cursor()

    # Get all previous check-ins
    cursor.execute("""
        SELECT id, pain, sleep, energy, symptoms, medication, status
        FROM checkins
        ORDER BY id ASC
    """)

    history = cursor.fetchall()

    conn.close()

    return render_template(
        "doctor.html",
        patient=patient_data,
        history=history
    )


# ---------------- RUN APP ----------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )