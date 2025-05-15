import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__, template_folder="template")
app.secret_key = 'your_secret_key'

# Database connection
def get_db_connection():
    db_path = 'data/students.db'
    
    # Ensure the 'data' directory exists
    if not os.path.exists('data'):
        os.makedirs('data')  # Create the 'data' directory if it doesn't exist
    
    # Ensure the database exists and create it if not
    if not os.path.exists(db_path):
        create_db()  # Create the database and tables if they don't exist
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn

# Function to create the database if it doesn't exist
def create_db():
    db_path = 'data/students.db'
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rollno TEXT NOT NULL,
        name TEXT NOT NULL,
        class_name TEXT NOT NULL,
        sports TEXT NOT NULL,
        scores TEXT NOT NULL,
        attendance TEXT NOT NULL,
        review TEXT NOT NULL,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

# Admin Login
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    # Admin login check
    if username == 'admin' and password == 'admin@123':
        session['user'] = 'admin'
        return redirect(url_for('admin_dashboard'))
    
    # Student login check
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE username = ? AND password = ?', (username, password)).fetchone()
    conn.close()
    
    if student:
        session['user'] = 'student'
        session['student_id'] = student['id']
        return redirect(url_for('student_dashboard'))
    
    return "Invalid credentials"

# Admin Dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('home'))
    
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    
    return render_template('admin_dashboard.html', students=students)

# Add Student
@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        rollno = request.form['rollno']
        name = request.form['name']
        class_name = request.form['class']
        sports = request.form['sports']
        scores = request.form['scores']
        attendance = request.form['attendance']
        review = request.form['review']
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO students (rollno, name, class_name, sports, scores, attendance, review, username, password) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                     (rollno, name, class_name, sports, scores, attendance, review, username, password))
        conn.commit()
        conn.close()
        
        return redirect(url_for('admin_dashboard'))
    
    return render_template('add_student.html')

# Edit Student
@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('home'))
    
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (id,)).fetchone()
    
    if request.method == 'POST':
        rollno = request.form['rollno']
        name = request.form['name']
        class_name = request.form['class']
        sports = request.form['sports']
        scores = request.form['scores']
        attendance = request.form['attendance']
        review = request.form['review']
        username = request.form['username']
        password = request.form['password']
        
        conn.execute('UPDATE students SET rollno = ?, name = ?, class_name = ?, sports = ?, scores = ?, attendance = ?, review = ?, username = ?, password = ? WHERE id = ?',
                     (rollno, name, class_name, sports, scores, attendance, review, username, password, id))
        conn.commit()
        conn.close()
        
        return redirect(url_for('admin_dashboard'))
    
    conn.close()
    return render_template('edit_student.html', student=student)

# Delete Student
@app.route('/delete_student/<int:id>')
def delete_student(id):
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('home'))
    
    conn = get_db_connection()
    conn.execute('DELETE FROM students WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_dashboard'))

# In your student_dashboard route:
# Updated student_dashboard route in Flask:
@app.route('/student_dashboard')
def student_dashboard():
    if 'user' not in session or session['user'] != 'student':
        return redirect(url_for('home'))
    
    student_id = session['student_id']
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    
    # Get sports and scores
    sports = student['sports'].split(',') if student['sports'] else []
    scores = student['scores'].split(',') if student['scores'] else []
    
    # Convert scores to integers
    scores = [int(score) for score in scores]
    
    # Combine sports and scores into a list of tuples
    sports_scores = list(zip(sports, scores))
    
    conn.close()
    
    # Pass sports_scores to the template
    return render_template('student_dashboard.html', student=student, sports_scores=sports_scores, sports=sports, scores=scores)

   
@app.route('/logout')
def logout():
    session.clear()  # Clear the session to log out
    return redirect(url_for('home'))  # Redirect to login page


if __name__ == '__main__':
    app.run(debug=True)
