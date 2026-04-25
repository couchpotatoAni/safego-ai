from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
import sqlite3
import os
import threading
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# 🔥 IMPORT DETECTION
from detection import start_detection

app = Flask(__name__)
app.secret_key = 'supersecretkey'

app.config['UPLOAD_FOLDER'] = 'known_faces'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# ================= ROUTES ================= #

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if 'photo' not in request.files:
            flash('No photo uploaded', 'error')
            return redirect(request.url)

        file = request.files['photo']

        if file.filename == '':
            flash('No selected photo', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            name = request.form['name']
            safe_name = secure_filename(name).replace(' ', '_')
            extension = filename.rsplit('.', 1)[1].lower()
            new_filename = f"{safe_name}.{extension}"

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))

            email = request.form['email']
            password = generate_password_hash(request.form['password'])
            phone = request.form['phone']
            emergency_contact1 = request.form['emergency_contact1']
            emergency_contact2 = request.form.get('emergency_contact2', '')
            address = request.form['address']

            conn = get_db_connection()
            try:
                conn.execute(
                    'INSERT INTO users (name, email, password, phone, emergency_contact1, emergency_contact2, address, photo_filename) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                    (name, email, password, phone, emergency_contact1, emergency_contact2, address, new_filename)
                )
                conn.commit()
                conn.close()
                return redirect(url_for('success'))

            except sqlite3.IntegrityError:
                flash('Email already registered.', 'error')
                return redirect(url_for('register'))

        else:
            flash('Invalid file type', 'error')
            return redirect(request.url)

    return render_template('register.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()

    return render_template('profile.html', user=user)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    phone = request.form['phone']
    emergency_contact1 = request.form['emergency_contact1']
    emergency_contact2 = request.form['emergency_contact2']
    address = request.form['address']

    conn = get_db_connection()
    conn.execute(
        'UPDATE users SET phone=?, emergency_contact1=?, emergency_contact2=?, address=? WHERE id=?',
        (phone, emergency_contact1, emergency_contact2, address, session['user_id'])
    )
    conn.commit()
    conn.close()

    flash('Profile updated!', 'success')
    return redirect(url_for('profile'))

@app.route('/success')
def success():
    return render_template('success.html')

# 🚀 NEW ROUTE: START DETECTION
@app.route('/start_detection')
def start_detection_route():
    if 'user_id' not in session:
        flash('Login first!', 'error')
        return redirect(url_for('login'))
    start_detection()
    return "Detection Stopped"

    # Run detection in background thread
    threading.Thread(target=start_detection).start()

    flash('Detection started! Camera will open.', 'success')
    return redirect(url_for('profile'))

# ================= RUN ================= #

if __name__ == '__main__':
    app.run(debug=True)