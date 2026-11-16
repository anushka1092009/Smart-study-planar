
import sqlite3
from datetime import date

# Connect to database
conn = sqlite3.connect("smart_study_planner.db")
cursor = conn.cursor()

# Create database tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER,
    task TEXT,
    due_date TEXT,
    status TEXT DEFAULT 'Pending'
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER,
    minutes INTEGER,
    study_date TEXT
)
""")

conn.commit()


def add_subject():
    name = input("Enter subject name: ").strip()

    if name:
        try:
            cursor.execute(
                "INSERT INTO subjects (name) VALUES (?)",
                (name,)
            )
            conn.commit()
            print("Subject added successfully!")
        except sqlite3.IntegrityError:
            print("Subject already exists!")
    else:
        print("Subject name cannot be empty!")


def view_subjects():
    cursor.execute("SELECT * FROM subjects")
    records = cursor.fetchall()

    if records:
        print("\n--- YOUR SUBJECTS ---")
        for record in records:
            print(record[0], ".", record[1])
    else:
        print("No subjects added yet.")


def search_subject():
    name = input("Enter subject to search: ").strip()

    cursor.execute(
        "SELECT * FROM subjects WHERE name LIKE ?",
        ('%' + name + '%',)
    )

    records = cursor.fetchall()

    if records:
        for record in records:
            print("Found:", record[1])
    else:
        print("Subject not found.")


def choose_subject():
    view_subjects()

    try:
        subject_id = int(input("Enter subject ID: "))
        cursor.execute(
            "SELECT id FROM subjects WHERE id = ?",
            (subject_id,)
        )

        if cursor.fetchone():
            return subject_id

    except ValueError:
        pass

    print("Invalid subject ID!")
    return None


def add_task():
    subject_id = choose_subject()

    if subject_id is None:
        return

    task = input("Enter study task: ").strip()
    due = input("Enter due date (YYYY-MM-DD): ").strip()

    if not task:
        print("Task cannot be empty!")
        return

    cursor.execute(
        "INSERT INTO tasks (subject_id, task, due_date) VALUES (?, ?, ?)",
        (subject_id, task, due)
    )

    conn.commit()
    print("Study task added successfully!")


def view_tasks():
    cursor.execute("""
    SELECT tasks.id, subjects.name, tasks.task,
           tasks.due_date, tasks.status
    FROM tasks
    JOIN subjects ON tasks.subject_id = subjects.id
    """)

    records = cursor.fetchall()

    if records:
        print("\n--- STUDY TASKS ---")

        for record in records:
            print("\nTask ID:", record[0])
            print("Subject:", record[1])
            print("Task:", record[2])
            print("Due date:", record[3])
            print("Status:", record[4])
    else:
        print("No study tasks available.")
  
def mark_task_completed():
    view_tasks()
    task_id = input("Enter the Task ID to mark as completed: ")

    conn = sqlite3.connect("smart_study_planner.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE tasks SET status = 'Completed' WHERE id = ?",
        (task_id,)
    )

    if cursor.rowcount > 0:
        print("Task marked as completed!")
    else:
        print("Task ID not found.")

    conn.commit()
    conn.close()

def record_session():
    subject_id = choose_subject()

    if subject_id is None:
        return

    try:
        minutes = int(input("Enter study time in minutes: "))

        if minutes <= 0:
            print("Enter a positive number!")
            return

        cursor.execute("""
        INSERT INTO sessions (subject_id, minutes, study_date)
        VALUES (?, ?, ?)
        """, (subject_id, minutes, str(date.today())))

        conn.commit()
        print("Study session recorded successfully!")

    except ValueError:
        print("Please enter a valid number!")


def progress_report():
    cursor.execute("SELECT COUNT(*) FROM subjects")
    total_subjects = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tasks")
    total_tasks = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tasks WHERE status = 'Pending'"
    )
    pending_tasks = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(minutes) FROM sessions")
    total_minutes = cursor.fetchone()[0] or 0

    print("\n======= PROGRESS REPORT =======")
    print("Total subjects:", total_subjects)
    print("Total study tasks:", total_tasks)
    print("Pending tasks:", pending_tasks)
    print("Completed tasks:", total_tasks - pending_tasks)
    print("Total study time:", total_minutes, "minutes")
    print("===============================")


# Main menu
while True:

    print("\n================================")
    print("       SMART STUDY PLANNER")
    print("================================")
    print("1. Add Subject")
    print("2. View Subjects")
    print("3. Search Subject")
    print("4. Add Study Task")
    print("5. View Study Tasks")
    print("6. Record Study Session")
    print("7. Progress Report")
    print("8. Exit")
    print("9. Mark Task as Completed")  
    print("================================")

    choice = input("Enter your choice (1-9): ")

    if choice == "1":
        add_subject()

    elif choice == "2":
        view_subjects()

    elif choice == "3":
        search_subject()

    elif choice == "4":
        add_task()

    elif choice == "5":
        view_tasks()

    elif choice == "6":
        record_session()

    elif choice == "7":
        progress_report()
   
    elif choice == "9":
        mark_task_completed()
   
    elif choice == "8":
        print("Thank you for using Smart Study Planner!")
        break

    else:
        print("Invalid choice! Please try again.")

conn.close()

