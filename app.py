from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_themer import Themer
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

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

users = {}

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/income', methods=['GET', 'POST'])
def income():
    return render_template('income.html')

@app.route('/outcome', methods=['GET', 'POST'])
def outcome():
    return render_template('outcome.html')

@app.route('/setting', methods=['GET', 'POST'])
def setting():
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
            cursor.execute("INSERT INTO users (name,username, password,saldo) VALUES (%s, %s,%s,%s)", (name,username, hashed_password,0))
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
            flash('Login berhasil!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Username atau password salah', 'danger')

    return render_template('login.html')
    
    # if request.method == 'POST':
    #     username = request.form['username']
    #     password = request.form['password']

    #     if username in users and users[username] == password:
    #         flash('Login berhasil!', 'success')
    #         # Di sini Anda dapat melakukan tindakan setelah login, seperti menyimpan sesi pengguna
    #         return redirect(url_for('index'))
    #     else:
    #         flash('Username atau password salah. Silakan coba lagi.', 'danger')

    # return render_template('login.html')


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(debug=True)
