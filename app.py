from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
DATABASE = 'college.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            status TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        )
    ''')

    cursor.execute(
        "INSERT OR IGNORE INTO admins (email, password) VALUES (?, ?)",
        ('admin@example.com', 'admin123')
    )

    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM students WHERE email=? AND password=?",
            (email, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session['student_id'] = user[0]
            return redirect(url_for('home'))

        return render_template('student/login.html', error='Invalid Credentials')

    return render_template('student/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO students (name, email, password, status) VALUES (?, ?, ?, ?)",
            (name, email, password, 'Pending')
        )
        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template('student/register.html')

@app.route('/admission')
def admission():
    return render_template('student/admission.html')

@app.route('/status')
def status():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, status FROM students WHERE id=?", (session['student_id'],))
    student = cursor.fetchone()
    conn.close()
    
    if not student:
        return redirect(url_for('login'))
    
    return render_template('student/status.html', student=student)

@app.route('/logout')
def logout():
    session.pop('student_id', None)
    return redirect(url_for('home'))

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
            
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM admins WHERE email=? AND password=?",
            (email, password)
        )
        admin = cursor.fetchone()
        conn.close()

        if admin:
            session['admin_id'] = admin[0]
            return redirect(url_for('admin_dashboard'))

        return render_template('admin/admin_login.html', error='Invalid admin credentials')

    return render_template('admin/admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, status FROM students ORDER BY id")
    students = cursor.fetchall()
    conn.close()
    
    return render_template('admin/admin_dashboard.html', students=students)

@app.route('/admin/approve/<int:student_id>', methods=['POST'])
def approve_student(student_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET status=? WHERE id=?", ('Approved', student_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject/<int:student_id>', methods=['POST'])
def reject_student(student_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET status=? WHERE id=?", ('Rejected', student_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/course')
def manage_course():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin/manage_course.html')

@app.route('/check')
def check():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()
    conn.close()
    return str(data)

if __name__ == '__main__':
    app.run(debug=True)