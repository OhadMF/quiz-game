from flask import Flask, render_template, redirect, url_for, session, request, Response
import sqlite3

app = Flask(__name__)
app.secret_key = "quiz_secret"

USERNAME = "admin"
PASSWORD = "1234"


def get_db():
    connection = sqlite3.connect("quiz.db")
    connection.row_factory = sqlite3.Row
    return connection


def check_auth(username, password):
    return username == USERNAME and password == PASSWORD


def authenticate():
    return Response(
        "Authentication Required",
        401,
        {
            "WWW-Authenticate": 'Basic realm="Quiz Admin"'
        }
    )


@app.route("/")
def home():
    session.clear()
    session["score"] = 0
    session["q_id"] = 1
    return render_template("index.html")


@app.route("/quiz")
def quiz():

    q_id = session.get("q_id", 1)

    connection = get_db()

    question = connection.execute(
        "SELECT * FROM questions ORDER BY id LIMIT 1 OFFSET ?",
        (q_id - 1,)
    ).fetchone()

    connection.close()


    if not question:
        return redirect(url_for("result"))


    return render_template(
        "quiz.html",
        question=question
    )


@app.route("/answer/<int:option>")
def answer(option):
    q_id = session.get("q_id", 1)

    connection = get_db()

    question = connection.execute(
    "SELECT * FROM questions ORDER BY id LIMIT 1 OFFSET ?",
    (q_id - 1,)
    ).fetchone()

    connection.close()

    if "score" not in session:
        session["score"] = 0

    if question and question["answer"] == option:
        session["score"] += 1

    session["q_id"] += 1

    return redirect(url_for("quiz"))


@app.route("/result")
def result():
    return render_template(
        "result.html",
        score=session.get("score", 0)
    )


@app.route("/admin")
def admin():

    auth = request.authorization

    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()


    connection = get_db()

    questions = connection.execute(
        "SELECT * FROM questions"
    ).fetchall()

    connection.close()


    return render_template(
        "admin.html",
        questions=questions
    )


@app.route("/admin/add", methods=["GET", "POST"])
def add_question():

    auth = request.authorization

    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()

    if request.method == "POST":

        connection = get_db()

        connection.execute(
            """
            INSERT INTO questions
            (question, option1, option2, option3, option4, answer)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                request.form["question"],
                request.form["option1"],
                request.form["option2"],
                request.form["option3"],
                request.form["option4"],
                request.form["answer"]
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("admin"))

    return render_template("add_question.html")

@app.route("/admin/delete/<int:id>")
def delete_question(id):

    auth = request.authorization

    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()


    connection = get_db()

    connection.execute(
        "DELETE FROM questions WHERE id = ?",
        (id,)
    )

    connection.commit()


    connection.close()


    return redirect(url_for("admin"))

@app.route("/admin/update/<int:id>", methods=["POST"])
def update_question(id):

    auth = request.authorization

    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()

    connection = get_db()

    connection.execute(
        """
        UPDATE questions
        SET
            question = ?,
            option1 = ?,
            option2 = ?,
            option3 = ?,
            option4 = ?,
            answer = ?
        WHERE id = ?
        """,
        (
            request.form["question"],
            request.form["option1"],
            request.form["option2"],
            request.form["option3"],
            request.form["option4"],
            request.form["answer"],
            id
        )
    )

    connection.commit()

    connection.close()

    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True)