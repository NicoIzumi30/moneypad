from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_themer import Themer
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from functools import wraps

app = Flask(__name__)
themer = Themer(app)
app.secret_key = 'your_secret_key'

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'moneypad'
}
def get_db():
    return mysql.connector.connect(**db_config)
conn = get_db()

users = {}


class User:
    def __init__(self, id, name, username):
        self.id = id
        self.name = name
        self.username = username

class Income:
    def __init__(self, user_id, nominal, source_type, note, date, id=None):
        self.user_id = user_id
        self.nominal = nominal
        self.source_type = source_type
        self.note = note
        self.date = date
        self.id = id

    def save(self):
        cursor = conn.cursor()
        sql = """INSERT INTO income (user_id, nominal, source_type, note, date) VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql, (self.user_id, self.nominal, self.source_type, self.note, self.date))
        conn.commit()
        
    def update(self):
        cursor = conn.cursor()
        sql = """UPDATE income SET user_id=%s, nominal=%s, source_type=%s, note=%s, date=%s WHERE id=%s"""
        cursor.execute(sql, (self.user_id, self.nominal, self.source_type, self.note, self.date, self.id))
        conn.commit()

    def delete(self, id):
        cursor = conn.cursor()
        sql = """DELETE FROM income WHERE id=%s"""
        cursor.execute(sql, (id,))
        conn.commit()
        cursor.close()
    

class Outcome:
    def __init__(self, user_id, nominal, used_type, note, date, id=None):
        self.user_id = user_id
        self.nominal = nominal
        self.used_type = used_type
        self.note = note
        self.date = date
        self.id = id

    def save(self):
        cursor = conn.cursor()
        sql = """INSERT INTO outcome (user_id, nominal, used_type, note, date) VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql, (self.user_id, self.nominal, self.used_type, self.note, self.date))
        conn.commit()
        
    def update(self):
        cursor = conn.cursor()
        sql = """UPDATE outcome SET user_id=%s, nominal=%s, used_type=%s, note=%s, date=%s WHERE id=%s"""
        cursor.execute(sql, (self.user_id, self.nominal, self.used_type, self.note, self.date, self.id))
        conn.commit()

    def delete(self, id):
        cursor = conn.cursor()
        sql = """DELETE FROM outcome WHERE id=%s"""
        cursor.execute(sql, (id,))
        conn.commit()
        cursor.close()
    
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper

@app.route('/')
@login_required
def index():
    conn = get_db()
    cursor = conn.cursor()
    user_id = session["user_id"]
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    dict_data = dict(zip([column[0] for column in cursor.description], user))
    return render_template('dashboard.html', data=dict_data)

# INCOME ROUTE

@app.route('/income', methods=['GET', 'POST'])
@login_required
def income():
    cursor = conn.cursor(dictionary=True)
    user_id = session["user_id"]
    sql = """SELECT * FROM income WHERE user_id=%s"""
    cursor.execute(sql,(user_id,))
    income = cursor.fetchall()
    return render_template('income.html', data = income)

@app.route('/income/create', methods=['GET', 'POST'])
@login_required
def create_income():
    if request.method == "POST":
        user_id = session["user_id"]
        nominal = request.form["nominal"]
        source_type = request.form["source_type"]
        note = request.form["note"]
        date = request.form["date"]

        income = Income(user_id=user_id, nominal=nominal, source_type=source_type, note=note, date=date)
        income.save()

        # flash('Data added successfully', 'success')
        return redirect(url_for('income'))
    return render_template('income.html')

@app.route("/income/update", methods=['GET', 'POST'])
def update_income():
    if request.method == "POST":
        user_id = session["user_id"]
        nominal = request.form["nominal"]
        source_type = request.form["source_type"]
        note = request.form["note"]
        date = request.form["date"]
        id = request.form["id"]

        income = Income(user_id=user_id, nominal=nominal, source_type=source_type, note=note, date=date, id=id)
        income.update()

        flash('Data update successfully', 'success')
        return redirect(url_for('income'))
    return render_template('income.html')

@app.route("/income/<income_id>/delete", methods=['GET', 'POST'])
def delete_income(income_id):
    print(income_id)   
    if request.method == 'GET':
        income = Income(None, None, None, None, None, None)
        income.delete(income_id)
        
        flash('Data deleted successfully', 'success')
        return redirect(url_for('income'))
    return render_template('income.html')

# OUTCOME ROUTE

@app.route('/outcome', methods=['GET', 'POST'])
@login_required
def outcome():
    cursor = conn.cursor(dictionary=True)
    user_id = session["user_id"]
    sql = """SELECT * FROM outcome WHERE user_id=%s"""
    cursor.execute(sql,(user_id,))
    outcome = cursor.fetchall()
    return render_template('outcome.html', data = outcome)
    # return render_template('outcome.html')

@app.route('/outcome/create', methods=['GET', 'POST'])
@login_required
def create_outcome():
    if request.method == "POST":
        user_id = session["user_id"]
        nominal = request.form["nominal"]
        used_type = request.form["used_type"]
        note = request.form["note"]
        date = request.form["date"]

        outcome = Outcome(user_id=user_id, nominal=nominal, used_type=used_type, note=note, date=date)
        outcome.save()

        # flash('Data added successfully', 'success')
        return redirect(url_for('outcome'))
    return render_template('outcome.html')

@app.route("/outcome/update", methods=['GET', 'POST'])
def update_outcome():
    if request.method == "POST":
        print("data =.",{
        "session" : session["user_id"],
        "nominal" : request.form["nominal"],
        "used_type" : request.form["used_type"],
        "note" : request.form["note"],
        "date" : request.form["date"],
        "id" : request.form["id"]
    })
        user_id = session["user_id"]
        nominal = request.form["nominal"]
        used_type = request.form["used_type"]
        note = request.form["note"]
        date = request.form["date"]
        id = request.form["id"]

        outcome = Outcome(user_id=user_id, nominal=nominal, used_type=used_type, note=note, date=date, id=id)
        outcome.update()

        flash('Data update successfully', 'success')
        return redirect(url_for('outcome'))
    return render_template('outcome.html')

@app.route("/outcome/<outcome_id>/delete", methods=['GET', 'POST'])
def delete_outcome(outcome_id):
    print(outcome_id)   
    if request.method == 'GET':
        outcome = Outcome(None, None, None, None, None, None)
        outcome.delete(outcome_id)
        
        flash('Data deleted successfully', 'success')
        return redirect(url_for('outcome'))
    return render_template('outcome.html')


@app.route('/setting', methods=['GET', 'POST'])
@login_required 
def setting():
    conn = get_db()
    cursor = conn.cursor()
    user_id = session["user_id"]
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    dict_data = dict(zip([column[0] for column in cursor.description], user))
    # return render_template('dashboard.html', data=dict_data)
    return render_template('setting.html', data=dict_data)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (name,username,password,saldo) VALUES (%s, %s,%s,%s)", (name,username, hashed_password,0))
            conn.commit()
            flash('Registrasi berhasil!', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        finally:
            conn.close()
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            # flash('Login berhasil!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Username atau password salah', 'danger')

    return render_template('login.html')

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash('Logout berhasil!', 'success')
    return redirect(url_for("login"))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(debug=True)
