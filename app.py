from flask import Flask, render_template, g, request
import sqlite3

app = Flask(__name__)

def connect_db():
    sql = sqlite3.connect('food_log.db')
    sql.row_factory = sqlite3.Row
    return sql

def get_db():
    if not hasattr(g, 'sqlite3_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/view')
def view():
    return render_template('day.html')

@app.route('/food', methods=['POST', 'GET'])
def food():
    if request.method == 'POST':
        names = request.form['food-name']
        protein = int(request.form['protein'])
        carbohydrates = int(request.form['carbohydrates'])
        fat = int(request.form['fat'])

        calories = protein*4 + carbohydrates*4 + fat*9
        db = get_db()
        db.execute('insert into food (names, protein, fat, carbohydrates, calories) values(?,?,?,?,?)',\
                   [names, protein, carbohydrates, fat, calories])
        db.commit()
        return '<h1>Name: {} Protein: {} Carbs: {} Fat: {}</h1>'.format(request.form['food-name'],\
                                                                        request.form['protein'], request.form['carbohydrates'], request.form['fat'])
    return render_template('add_food.html')

if __name__ == '__main__':
    app.run(debug=True)