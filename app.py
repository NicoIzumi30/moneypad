from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify
from flask_themer import Themer
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from functools import wraps
from datetime import datetime, timedelta

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
def get_user_data(user_id):
    cursor = conn.cursor()
    sql_query = "SELECT name, username FROM users WHERE id = %s"
    cursor.execute(sql_query, (user_id,))
    result = cursor.fetchone()

    cursor.close()
    return result 
@app.context_processor
def inject_user_data():
    user_id = session.get("user_id", None)
    user_data = get_user_data(user_id)

    return dict(user_id=user_id, user_data=user_data)

class User:
    def __init__(self, id, name, username):
        self.id = id
        self.name = name
        self.username = username

    def update(self):
        cursor = conn.cursor()
        sql_update_income = """UPDATE users SET name=%s, username=%s WHERE id=%s"""
        cursor.execute(sql_update_income, (self.name, self.username, self.id))
        conn.commit()

        cursor.close()

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
        sql_insert_income = """INSERT INTO income (user_id, nominal, source_type, note, date) VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql_insert_income, (self.user_id, self.nominal, self.source_type, self.note, self.date))
        conn.commit()

        sql_update_saldo = """UPDATE users SET saldo = saldo + %s WHERE id = %s"""
        cursor.execute(sql_update_saldo, (self.nominal, self.user_id))
        conn.commit()

        cursor.close()

        
    def update(self):
        cursor = conn.cursor()
        sql_get_initial_nominal = """SELECT nominal, user_id FROM income WHERE id=%s"""
        cursor.execute(sql_get_initial_nominal, (self.id,))
        result = cursor.fetchone()

        if result:
            initial_nominal = int(result[0])  # Convert to int
            user_id = result[1]

            new_nominal = int(self.nominal) if isinstance(self.nominal, str) else self.nominal
            sql_update_income = """UPDATE income SET user_id=%s, nominal=%s, source_type=%s, note=%s, date=%s WHERE id=%s"""
            cursor.execute(sql_update_income, (self.user_id, new_nominal, self.source_type, self.note, self.date, self.id))
            conn.commit()

            nominal_difference = new_nominal - initial_nominal

            sql_update_saldo = """UPDATE users SET saldo = saldo + %s WHERE id = %s"""
            cursor.execute(sql_update_saldo, (nominal_difference, user_id))
            conn.commit()
        else:
            print("Income data not found")

        cursor.close()



    def delete(self, id):
        cursor = conn.cursor()
        sql_get_nominal = """SELECT nominal, user_id FROM income WHERE id=%s"""
        cursor.execute(sql_get_nominal, (id,))
        result = cursor.fetchone()

        if result:
            nominal = result[0]
            user_id = result[1]

            # Delete income data
            sql_delete_income = """DELETE FROM income WHERE id=%s"""
            cursor.execute(sql_delete_income, (id,))
            conn.commit()

            # Update user saldo
            sql_update_saldo = """UPDATE users SET saldo = saldo - %s WHERE id = %s"""
            cursor.execute(sql_update_saldo, (nominal, user_id))
            conn.commit()
        else:
            print("Income data not found")

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

        sql_update_saldo = """UPDATE users SET saldo = saldo - %s WHERE id = %s"""
        cursor.execute(sql_update_saldo, (self.nominal, self.user_id))
        conn.commit()
        cursor.close()
        
    def update(self):
        cursor = conn.cursor()
        sql_get_initial_nominal = """SELECT nominal, user_id FROM outcome WHERE id=%s"""
        cursor.execute(sql_get_initial_nominal, (self.id,))
        result = cursor.fetchone()

        if result:
            initial_nominal = int(result[0])  # Convert to int
            user_id = result[1]

            new_nominal = int(self.nominal) if isinstance(self.nominal, str) else self.nominal
            sql = """UPDATE outcome SET user_id=%s, nominal=%s, used_type=%s, note=%s, date=%s WHERE id=%s"""
            cursor.execute(sql, (self.user_id, self.nominal, self.used_type, self.note, self.date, self.id))
            conn.commit()
            nominal_difference = new_nominal - initial_nominal

            sql_update_saldo = """UPDATE users SET saldo = saldo - %s WHERE id = %s"""
            cursor.execute(sql_update_saldo, (nominal_difference, user_id))
            conn.commit()
        else:
            print("Outcome data not found")

        cursor.close()

    def delete(self, id):
        cursor = conn.cursor()
        sql_get_nominal = """SELECT nominal, user_id FROM outcome WHERE id=%s"""
        cursor.execute(sql_get_nominal, (id,))
        result = cursor.fetchone()

        if result:
            nominal = result[0]
            user_id = result[1]

            sql_delete_outcome = """DELETE FROM outcome WHERE id=%s"""
            cursor.execute(sql_delete_outcome, (id,))
            conn.commit()

            sql_update_saldo = """UPDATE users SET saldo = saldo + %s WHERE id = %s"""
            cursor.execute(sql_update_saldo, (nominal, user_id))
            conn.commit()
        else:
            print("outcome data not found")

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

    sql_query = """ SELECT users.id, users.username, users.saldo,( SELECT COALESCE(SUM(nominal), 0) FROM income WHERE user_id = users.id) AS total_income,( SELECT COALESCE(SUM(nominal), 0) FROM outcome WHERE user_id = users.id) AS total_outcome FROM users WHERE users.id = %s """

    cursor.execute(sql_query, (user_id,))
    result = cursor.fetchone()

    if result:
        dict_data = dict(zip([column[0] for column in cursor.description], result))
        return render_template('dashboard.html', data=dict_data)
    
    
 
@app.route('/query_data_bulan/')
def query_bulan():
    try:
        cursor = conn.cursor()
        current_year = datetime.now().year

        # Query untuk total pendapatan per bulan pada tahun saat ini
        income_query = """
        SELECT
            DATE_FORMAT(date, '%m-%Y') AS bulan,
            COALESCE(SUM(nominal), 0) AS total_income
        FROM
            income
        WHERE
            YEAR(date) = %s
        GROUP BY
            bulan;
        """

        # Query untuk total pengeluaran per bulan pada tahun saat ini
        outcome_query = """
        SELECT
            DATE_FORMAT(date, '%m-%Y') AS bulan,
            COALESCE(SUM(nominal), 0) AS total_outcome
        FROM
            outcome
        WHERE
            YEAR(date) = %s
        GROUP BY
            bulan;
        """

        # Eksekusi query untuk pendapatan
        cursor.execute(income_query, (current_year,))
        income_data = cursor.fetchall()

        # Eksekusi query untuk pengeluaran
        cursor.execute(outcome_query, (current_year,))
        outcome_data = cursor.fetchall()

        # Membuat dictionary untuk setiap bulan dalam tahun saat ini, jika tidak ada data pada bulan tersebut, total diatur ke 0
        result = [{'bulan': month.strftime('%m-%Y'), 'total_income': 0, 'total_outcome': 0} for month in (datetime(current_year, month, 1) for month in range(1, 13))]

        # Mengisi data yang ada dari hasil query
        for data in income_data:
            result_entry = next((entry for entry in result if entry['bulan'] == data[0]), None)
            if result_entry:
                result_entry['total_income'] = data[1]

        for data in outcome_data:
            result_entry = next((entry for entry in result if entry['bulan'] == data[0]), None)
            if result_entry:
                result_entry['total_outcome'] = data[1]

        return jsonify(result)

    finally:
        # Tutup kursor dan koneksi
        cursor.close()

@app.route('/query_data_income/')
def query_data():
    bulan_saat_ini = datetime.now().month
    tahun_saat_ini = datetime.now().year
    user_id = session["user_id"]
    try:
        cursor = conn.cursor()
         # Buat rentang tanggal untuk satu bulan
        start_date = datetime(tahun_saat_ini, bulan_saat_ini, 1)
        end_date = start_date + timedelta(days=31)  # Menambah 31 hari untuk memastikan rentang mencakup seluruh bulan
        dates = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]  # Perubahan di sini

        # Format tanggal ke dalam string
        formatted_dates = [date.strftime('%Y-%m-%d') for date in dates]

        # Query untuk mendapatkan data pada rentang tanggal
        query = """SELECT DATE_FORMAT(date, '%Y-%m-%d') AS tanggal, user_id, IFNULL(SUM(nominal), 0) AS total_nominal FROM income WHERE user_id = %s AND DATE(date) BETWEEN %s AND %s GROUP BY DATE_FORMAT(date, '%Y-%m-%d')
        """

        cursor.execute(query, (user_id,formatted_dates[0], formatted_dates[-1]))
        results = cursor.fetchall()
        data = []
        for date in formatted_dates:
            data_for_date = next((result for result in results if result[0] == date), None)
            if data_for_date is not None:
                data.append({'tanggal': date, 'user_id': data_for_date[1], 'total_nominal': float(data_for_date[2])})
            else:
                data.append({'tanggal': date, 'user_id': None, 'total_nominal': 0.0})

        return jsonify(data)

        # return jsonify(results)

    finally:
        cursor.close()
@app.route('/query_data_outcome/')
def query_data_outcome():
    bulan_saat_ini = datetime.now().month
    tahun_saat_ini = datetime.now().year
    user_id = session["user_id"]
    try:
        cursor = conn.cursor()
         # Buat rentang tanggal untuk satu bulan
        start_date = datetime(tahun_saat_ini, bulan_saat_ini, 1)
        end_date = start_date + timedelta(days=31)  # Menambah 31 hari untuk memastikan rentang mencakup seluruh bulan
        dates = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]  # Perubahan di sini

        # Format tanggal ke dalam string
        formatted_dates = [date.strftime('%Y-%m-%d') for date in dates]

        # Query untuk mendapatkan data pada rentang tanggal
        query = """SELECT DATE_FORMAT(date, '%Y-%m-%d') AS tanggal, user_id, IFNULL(SUM(nominal), 0) AS total_nominal FROM outcome WHERE user_id = %s AND DATE(date) BETWEEN %s AND %s GROUP BY DATE_FORMAT(date, '%Y-%m-%d')
        """

        cursor.execute(query, (user_id,formatted_dates[0], formatted_dates[-1]))
        results = cursor.fetchall()
        data = []
        for date in formatted_dates:
            data_for_date = next((result for result in results if result[0] == date), None)
            if data_for_date is not None:
                data.append({'tanggal': date, 'user_id': data_for_date[1], 'total_nominal': float(data_for_date[2])})
            else:
                data.append({'tanggal': date, 'user_id': None, 'total_nominal': 0.0})

        return jsonify(data)

        # return jsonify(results)

    finally:
        cursor.close()

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
        try :
            user_id = session["user_id"]
            nominal = request.form["nominal"]
            source_type = request.form["source_type"]
            note = request.form["note"]
            date = request.form["date"]

            income = Income(user_id=user_id, nominal=nominal, source_type=source_type, note=note, date=date)
            income.save()
            flash('Data added successfully', 'success')
            return redirect(url_for('income'))
        except Exception as e:
            print(f"Error added data: {e}")
            flash('Error added data', 'error')
    return render_template('income.html')

@app.route("/income/update", methods=['GET', 'POST'])
def update_income():
    if request.method == "POST":
        try :
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
        except Exception as e:
            print(f"Error updating data: {e}")
            flash('Error updating data', 'error')
    return render_template('income.html')

@app.route("/income/<income_id>/delete", methods=['GET', 'POST'])
def delete_income(income_id):
    print(income_id)   
    if request.method == 'GET':
        try :
            income = Income(None, None, None, None, None, None)
            income.delete(income_id)
        
            flash('Data deleted successfully', 'success')
            return redirect(url_for('income'))
        except Exception as e:
            print(f"Error deleted data: {e}")
            flash('Error deleted data', 'error')
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
        try :
            user_id = session["user_id"]
            nominal = request.form["nominal"]
            used_type = request.form["used_type"]
            note = request.form["note"]
            date = request.form["date"]

            outcome = Outcome(user_id=user_id, nominal=nominal, used_type=used_type, note=note, date=date)
            outcome.save()
            flash('Data added successfully', 'success')
            return redirect(url_for('outcome'))
        except Exception as e:
            print(f"Error added data: {e}")
            flash('Error added data', 'error')
            
    return render_template('outcome.html')

@app.route("/outcome/update", methods=['GET', 'POST'])
def update_outcome():
    if request.method == "POST":
        try:
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
        except Exception as e:
            print(f"Error update data: {e}")
            flash('Error update data', 'error')
    return render_template('outcome.html')

@app.route("/outcome/<outcome_id>/delete", methods=['GET', 'POST'])
def delete_outcome(outcome_id):
    print(outcome_id)   
    if request.method == 'GET':
        try :
            outcome = Outcome(None, None, None, None, None, None)
            outcome.delete(outcome_id)
            
            flash('Data deleted successfully', 'success')
            return redirect(url_for('outcome'))
        except Exception as e:
            print(f"Error deleted data: {e}")
            flash('Error deleted data', 'error')
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
    return render_template('setting.html', data=dict_data)
@app.route("/setting/update", methods=['GET', 'POST'])
def update_user():
    if request.method == "POST":
        try:
            user_id = session["user_id"]
            name = request.form["name"]
            username = request.form["username"]

            user = User(id=user_id, name=name,username=username)
            user.update()

            flash('Data update successfully', 'success')
            return redirect(url_for('setting'))
        except Exception as e:
            print(f"Error update data: {e}")
            flash('Error update data', 'error')
    return render_template('setting.html')

@app.route("/setting/update_password", methods=['GET', 'POST'])
def update_password():
    if request.method == "POST":
        try:
            user_id = session["user_id"]
            current_password = request.form["current_password"]
            new_password = request.form["new_password"]
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()

            if user and check_password_hash(user[3], current_password):
                hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
                sql_update_income = """UPDATE users SET password=%s WHERE id=%s"""
                cursor.execute(sql_update_income, (hashed_password, user_id))
                conn.commit()
                flash('Data update successfully', 'success')
                # flash('Data update successfully', 'success')
                return redirect(url_for('setting'))
            else:      
                flash('The current password is incorrect', 'error')
                return redirect(url_for('setting'))
        except Exception as e:
            print(f"Error update data: {e}")
            flash('Error update data', 'error')
    return render_template('setting.html')
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
            session['name'] = user[1]
            return redirect(url_for('index'))
        else:
            flash('Incorrect username or password', 'error')

    return render_template('login.html')

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash('Logout successful!', 'success')
    return redirect(url_for("login"))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(debug=True)
