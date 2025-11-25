#  Automated Class & Assignment Reminder System

###  Overview

**Automated Reminder System** is a Python-based automation tool designed for educational institutions and training programs.
It helps students stay on track by automatically sending **email** and **Discord reminders** for upcoming **classes** and **assignment deadlines**.
The system is fully automated — once set up, it runs continuously without manual intervention.

---

##  Features

*  **Automatic Class Reminders**
  Sends Discord and email notifications 1 hour before and 24 hours before each class.

*  **Assignment Alerts**
  Notifies students 24 hours and 1 hour before assignment deadlines.

*  **Excel-Based Data Import**
  Easily import class schedules and student lists from Excel files into an SQLite database.

*  **Continuous Automation**
  Runs as background scripts using Python’s `asyncio` and scheduling logic.

*  **Discord Bot Integration**
  Posts class and assignment reminders in a specific Discord channel.

*  **Email Notification System**
  Sends personalized email alerts to students in the relevant course and batch only.

---

##  Project Structure

```
automated_reminders/
│
├── data/
│   ├── DSA.xlsx
│   ├── cybersecurity.xlsx
│   ├── fullstack.xlsx
│   └── students.xlsx
│
├── database/
│   └── reminders.db
│
├── scripts/
│   ├── import_data.py          # Imports Excel data into SQLite
│   ├── data_management.py      # Handles DB operations
│   ├── discord_notifier.py     # Sends reminders via Discord
│   └── mail_scheduler.py       # Sends email reminders
│
├── .env                        # Stores API tokens, DB path, and config
└── requirements.txt             # Python dependencies
```

---

##  Technologies Used

* **Python 3.10+**
* **SQLite3** – Lightweight local database
* **Pandas** – Excel data handling
* **Discord.py** – Discord bot integration
* **smtplib** / **email.mime** – Email automation
* **dotenv** – Environment variable management
* **asyncio** – Asynchronous scheduling

---

##  How It Works

1. Excel files (`DSA.xlsx`, etc.) contain class and assignment schedules.
2. The data is imported into an SQLite database (`reminders.db`) using `import_data.py`.
3. Two automation scripts handle notifications:

   * `mail_scheduler.py` → Sends email reminders
   * `discord_notifier.py` → Sends Discord reminders
4. Both scripts check the database every minute for upcoming events.
5. Messages are sent only once at precise intervals (24h and 1h before).

---

##  Future Enhancements

* Integration with Google Calendar or Microsoft Teams
* Web dashboard for schedule management
* Support for SMS/WhatsApp notifications
* Docker support for easy cloud deployment

---

##  Author

**Aswini Dileep**
*Data Science Intern 
📧 [aswinidileep91@gmail.com](mailto:aswinidileep91@gmail.com)

**Jaiha Stanly S V**
*Data Science Intern 
📧 [jaihastanly018@gmail.com](mailto:jaihastanly018@gmail.com)

**Nandana Sajju Pillai**
*Data Science Intern 
📧 [nandanasajju@gmail.com](mailto:nandanasajju@gmail.com)

**Shadiya Hamza K P**
*Data Science Intern 
📧 [shadiyahamzakp7@gmail.com](mailto:shadiyahamzakp7@gmail.com)

---

