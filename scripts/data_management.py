import sqlite3
import pandas as pd
import os

DB_PATH = r"D:\Internship_ICT\Final\automated_reminders\database\reminders.db"


def connect_db():
    return sqlite3.connect(DB_PATH)


def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        discord_id TEXT,
        course TEXT NOT NULL,
        batch_name TEXT,
        year INTEGER,
        mode TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS classes (
        class_id INTEGER PRIMARY KEY AUTOINCREMENT,
        course TEXT NOT NULL,
        batch_name TEXT,
        year INTEGER,
        session_name TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        mode TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assignments (
        assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        course TEXT NOT NULL,
        batch_name TEXT,
        year INTEGER,
        subject TEXT NOT NULL,
        due_date TEXT NOT NULL,
        mode TEXT
    );
    """)

    conn.commit()
    conn.close()
    print("✅ Tables verified or created successfully.")


def view_all():
    conn = connect_db()
    print("\n=== Students Table ===")
    print(pd.read_sql_query("SELECT * FROM students", conn))

    print("\n=== Classes Table ===")
    print(pd.read_sql_query("SELECT * FROM classes", conn))

    print("\n=== Assignments Table ===")
    print(pd.read_sql_query("SELECT * FROM assignments", conn))
    conn.close()


def view_by_course():
    course = input("Enter course name (e.g., DSA, CyberSecurity, FullStack): ")
    batch_name = input("Enter batch name (optional): ")
    year = input("Enter year (optional): ")
    mode = input("Enter mode (Online/Offline, optional): ")

    query = f"SELECT * FROM students WHERE course = '{course}'"
    if batch_name:
        query += f" AND batch_name = '{batch_name}'"
    if year:
        query += f" AND year = {year}"
    if mode:
        query += f" AND mode = '{mode}'"

    conn = connect_db()
    print(f"\n=== Students Enrolled in {course} ===")
    print(pd.read_sql_query(query, conn))

    print(f"\n=== Classes for {course} ===")
    print(pd.read_sql_query(query.replace("students", "classes"), conn))

    print(f"\n=== Assignments for {course} ===")
    print(pd.read_sql_query(query.replace("students", "assignments"), conn))
    conn.close()


def menu():
    create_tables()

    while True:
        print("\n🎓 Data Management Menu")
        print("1. View all data")
        print("2. View data by course/batch/year/mode")
        print("3. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            view_all()
        elif choice == "2":
            view_by_course()
        elif choice == "3":
            print("👋 Exiting... Goodbye!")
            break
        else:
            print("❌ Invalid choice, please try again!")


if __name__ == "__main__":
    menu()
