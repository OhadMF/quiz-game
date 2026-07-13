import sqlite3

connection = sqlite3.connect("quiz.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    option1 TEXT NOT NULL,
    option2 TEXT NOT NULL,
    option3 TEXT NOT NULL,
    option4 TEXT NOT NULL,
    answer INTEGER NOT NULL
)
""")

connection.commit()
connection.close()

print("Database Ready!")