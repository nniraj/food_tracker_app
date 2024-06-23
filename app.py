from flask import Flask, render_template, g, request
import sqlite3
from datetime import datetime

app = Flask(__name__)


def connect_db():
    sql = sqlite3.connect("food_log.db")
    sql.row_factory = sqlite3.Row
    return sql


def get_db():
    if not hasattr(g, "sqlite3_db"):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()


@app.route("/", methods=["GET", "POST"])
def index():
    db = get_db()
    if request.method == "POST":
        date = request.form["date"]
        dt = datetime.strptime(date, "%Y-%m-%d")
        database_date = datetime.strftime(dt, "%Y%m%d")
        db.execute("Insert into log_date (entry_date) values (?)", [database_date])
        db.commit()
    cur = db.execute("SELECT entry_date from log_date order by entry_date desc")
    results = cur.fetchall()

    pretty_results = []
    for i in results:
        single_date = {}
        d = datetime.strptime(str(i["entry_date"]), "%Y%m%d")
        single_date["entry_date"] = datetime.strftime(d, "%B %d, %y")
        pretty_results.append(single_date)
    return render_template("home.html", results=pretty_results)


@app.route("/view/<date>", methods=["GET", "POST"])
def view(date):
    db = get_db()
    cur = db.execute("select id, entry_date from log_date where entry_date = ?", [date])
    date_result = cur.fetchone()

    if request.method == "POST":
        db.execute(
            "insert into food_date (food_id, log_date_id) values (?, ?)",
            [request.form["food-select"], date_result["id"]],
        )
        db.commit()

    d = datetime.strptime(str(date_result["entry_date"]), "%Y%m%d")
    pretty_date = datetime.strftime(d, "%B %d, %y")

    food_cur = db.execute("select id, names from food")
    food_results = food_cur.fetchall()

    log_cur = db.execute(
        "select food.names, food.protein, food.carbohydrates, food.fat, food.calories from log_date join food_date on food_date.log_date_id=log_date.id join food on food_id=food_date.food_id where log_date.entry_date = ?",
        [date],
    )
    log_results = log_cur.fetchall()
    return render_template("day.html", date=pretty_date, results=food_results, log_results=log_results)

@app.route("/food", methods=["POST", "GET"])
def food():
    db = get_db()
    if request.method == "POST":
        names = request.form["food-name"]
        protein = int(request.form["protein"])
        carbohydrates = int(request.form["carbohydrates"])
        fat = int(request.form["fat"])

        calories = protein * 4 + carbohydrates * 4 + fat * 9
        db.execute(
            "insert into food (names, protein, fat, carbohydrates, calories) values(?,?,?,?,?)",
            [names, protein, carbohydrates, fat, calories],
        )
        db.commit()
    cur = db.execute(
        "select names, protein, fat, carbohydrates, calories from food order by id desc"
    )
    results = cur.fetchall()
    return render_template("add_food.html", results=results)


if __name__ == "__main__":
    app.run(debug=True)
