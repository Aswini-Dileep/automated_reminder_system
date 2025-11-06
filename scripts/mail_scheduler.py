import os
import time
import sqlite3
import pytz
import smtplib
import pandas as pd
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# ============================================================
# Load environment variables
# ============================================================
load_dotenv()

DB_PATH = os.getenv("DB_PATH", r"D:\Internship_ICT\Final\automated_reminders\database\reminders.db")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASS = os.getenv("SENDER_PASS")

if not SENDER_EMAIL or not SENDER_PASS:
    raise ValueError("❌ Missing SENDER_EMAIL or SENDER_PASS in .env file!")

IST = pytz.timezone("Asia/Kolkata")
sent_reminders = set()

# ============================================================
# EMAIL FUNCTION
# ============================================================
def send_email(recipient, subject, body):
    """Send an email using SMTP."""
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASS)
            server.send_message(msg)
        print(f"✅ Email sent to {recipient}")
    except Exception as e:
        print(f"❌ Error sending email to {recipient}: {e}")

# ============================================================
# DATABASE READERS
# ============================================================
def get_students():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT name, email, course, batch_name, year, mode FROM students", conn)
    conn.close()
    return df

def get_classes():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT course, batch_name, year, session_name, date, time, mode FROM classes", conn)
    conn.close()
    return df

def get_assignments():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT course, batch_name, year, subject, due_date, mode FROM assignments", conn)
    conn.close()
    return df

# ============================================================
# REMINDER LOGIC
# ============================================================
def send_reminders():
    global sent_reminders
    now = datetime.now(IST)
    print(f"\n⏰ Checking reminders at {now.strftime('%Y-%m-%d %H:%M:%S')} IST")

    students_df = get_students()
    classes_df = get_classes()
    assignments_df = get_assignments()

    # -------------------------------
    # CLASS REMINDERS
    # -------------------------------
    for _, row in classes_df.iterrows():
        course, batch_name, year, mode = (
            row["course"],
            row["batch_name"],
            row["year"],
            str(row.get("mode", "Offline")).strip(),
        )
        session_name, date_str, time_str = row["session_name"], row["date"], row["time"]

        try:
            class_time = IST.localize(datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M"))
        except ValueError:
            print(f"⚠️ Invalid datetime for class '{session_name}' ({course})")
            continue

        for hours_before in [24, 1]:
            reminder_time = class_time - timedelta(hours=hours_before)
            key = f"class-{course}-{batch_name}-{year}-{mode}-{session_name}-{hours_before}"

            if 0 <= (now - reminder_time).total_seconds() < 600 and key not in sent_reminders:
                recipients = students_df[
                    (students_df["course"].str.lower() == course.lower()) &
                    (students_df["batch_name"].str.lower() == str(batch_name).lower()) &
                    (students_df["year"] == year) &
                    (students_df["mode"].str.lower() == mode.lower())
                ]

                if recipients.empty:
                    print(f"⚠️ No students found for {course} {batch_name} {year} ({mode})")
                    continue

                for _, stu in recipients.iterrows():
                    body = (
                        f"Hi {stu['name']},\n\n"
                        f"📚 Reminder: Your class '{session_name}' for {course} - {batch_name} ({mode}) "
                        f"is scheduled at {class_time.strftime('%I:%M %p on %d-%b-%Y')}.\n"
                        f"This is your {hours_before}-hour reminder.\n\n"
                        f"— Automated Reminder System"
                    )
                    send_email(
                        stu["email"],
                        f"Class Reminder: {session_name} ({hours_before}h before)",
                        body,
                    )

                sent_reminders.add(key)

    # -------------------------------
    # ASSIGNMENT REMINDERS
    # -------------------------------
    for _, row in assignments_df.iterrows():
        course, batch_name, year, mode = (
            row["course"],
            row["batch_name"],
            row["year"],
            str(row.get("mode", "Offline")).strip(),
        )
        subject, due_str = row["subject"], str(row["due_date"])

        # Default time if only date is given
        if len(due_str.strip()) == 10:
            due_str += " 09:00"

        try:
            due_time = IST.localize(datetime.strptime(due_str, "%Y-%m-%d %H:%M"))
        except ValueError:
            print(f"⚠️ Invalid due date for assignment '{subject}' ({course})")
            continue

        for hours_before in [24, 1]:
            reminder_time = due_time - timedelta(hours=hours_before)
            key = f"assignment-{course}-{batch_name}-{year}-{mode}-{subject}-{hours_before}"

            if 0 <= (now - reminder_time).total_seconds() < 600 and key not in sent_reminders:
                recipients = students_df[
                    (students_df["course"].str.lower() == course.lower()) &
                    (students_df["batch_name"].str.lower() == str(batch_name).lower()) &
                    (students_df["year"] == year) &
                    (students_df["mode"].str.lower() == mode.lower())
                ]

                if recipients.empty:
                    print(f"⚠️ No students found for {course} {batch_name} {year} ({mode})")
                    continue

                for _, stu in recipients.iterrows():
                    body = (
                        f"Hi {stu['name']},\n\n"
                        f"📝 Reminder: Your assignment '{subject}' for {course} - {batch_name} ({mode}) "
                        f"is due at {due_time.strftime('%I:%M %p on %d-%b-%Y')}.\n"
                        f"This is your {hours_before}-hour reminder.\n\n"
                        f"— Automated Reminder System"
                    )
                    send_email(
                        stu["email"],
                        f"Assignment Reminder: {subject} ({hours_before}h before)",
                        body,
                    )

                sent_reminders.add(key)

# ============================================================
# MAIN LOOP
# ============================================================
if __name__ == "__main__":
    print("📧 Email Reminder Scheduler Started... (Checks every minute)")
    while True:
        try:
            send_reminders()
        except Exception as e:
            print(f"❌ Error in reminder loop: {e}")
        time.sleep(60)
