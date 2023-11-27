from flask import Flask, render_template, request, redirect, url_for, flash
from flask_themer import Themer

app = Flask(__name__)
themer = Themer(app)

# Simpan konfigurasi Flask-Themer di sini jika diperlukan

# Konfigurasi untuk menyimpan data pengguna sementara (secara nyata Anda akan menggunakan database)
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
        username = request.form['username']
        password = request.form['password']

        if username in users:
            flash('Username sudah digunakan. Silakan pilih username lain.', 'danger')
        else:
            users[username] = password
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            flash('Login berhasil!', 'success')
            # Di sini Anda dapat melakukan tindakan setelah login, seperti menyimpan sesi pengguna
            return redirect(url_for('index'))
        else:
            flash('Username atau password salah. Silakan coba lagi.', 'danger')

    return render_template('login.html')


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(debug=True)
