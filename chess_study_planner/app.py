from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_bcrypt import Bcrypt
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
bcrypt = Bcrypt(app)

# Database initialization
def init_db():
    conn = sqlite3.connect('chess_study.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Create weekly_plans table
    c.execute('''CREATE TABLE IF NOT EXISTS weekly_plans
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  week_start DATE NOT NULL,
                  weekly_goal TEXT,
                  efficiency_action TEXT,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    # Create daily_entries table
    c.execute('''CREATE TABLE IF NOT EXISTS daily_entries
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  weekly_plan_id INTEGER NOT NULL,
                  entry_date DATE NOT NULL,
                  study_time INTEGER,
                  learning_summary TEXT,
                  focus_score INTEGER,
                  suggestion TEXT,
                  FOREIGN KEY(weekly_plan_id) REFERENCES weekly_plans(id))''')
    
    conn.commit()
    conn.close()

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect('chess_study.db')
    conn.row_factory = sqlite3.Row
    return conn

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash('Username and password are required!', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                         (username, hashed_password))
            conn.commit()
            conn.close()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get current week's plan
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    
    conn = get_db_connection()
    weekly_plan = conn.execute('''
        SELECT * FROM weekly_plans 
        WHERE user_id = ? AND week_start = ?
    ''', (session['user_id'], week_start)).fetchone()
    
    daily_entries = []
    if weekly_plan:
        daily_entries = conn.execute('''
            SELECT * FROM daily_entries 
            WHERE weekly_plan_id = ?
            ORDER BY entry_date
        ''', (weekly_plan['id'],)).fetchall()
    
    conn.close()
    
    # Create days of the week
    days = []
    for i in range(7):
        day_date = week_start + timedelta(days=i)
        day_entry = next((entry for entry in daily_entries if entry['entry_date'] == str(day_date)), None)
        days.append({
            'date': day_date,
            'entry': day_entry
        })
    
    return render_template('dashboard.html', 
                         weekly_plan=weekly_plan,
                         days=days,
                         week_start=week_start)

@app.route('/save_weekly_plan', methods=['POST'])
def save_weekly_plan():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    week_start = request.form['week_start']
    weekly_goal = request.form['weekly_goal']
    efficiency_action = request.form['efficiency_action']
    
    conn = get_db_connection()
    
    # Check if weekly plan exists
    existing_plan = conn.execute('''
        SELECT id FROM weekly_plans 
        WHERE user_id = ? AND week_start = ?
    ''', (session['user_id'], week_start)).fetchone()
    
    if existing_plan:
        # Update existing plan
        conn.execute('''
            UPDATE weekly_plans 
            SET weekly_goal = ?, efficiency_action = ?
            WHERE id = ?
        ''', (weekly_goal, efficiency_action, existing_plan['id']))
    else:
        # Create new plan
        conn.execute('''
            INSERT INTO weekly_plans (user_id, week_start, weekly_goal, efficiency_action)
            VALUES (?, ?, ?, ?)
        ''', (session['user_id'], week_start, weekly_goal, efficiency_action))
    
    conn.commit()
    conn.close()
    
    flash('Weekly plan saved successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/save_daily_entry', methods=['POST'])
def save_daily_entry():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    entry_date = request.form['entry_date']
    study_time = request.form['study_time']
    learning_summary = request.form['learning_summary']
    focus_score = request.form['focus_score']
    suggestion = request.form['suggestion']
    
    # Get the weekly plan for this date
    entry_date_obj = datetime.strptime(entry_date, '%Y-%m-%d').date()
    week_start = entry_date_obj - timedelta(days=entry_date_obj.weekday())
    
    conn = get_db_connection()
    
    # Get or create weekly plan
    weekly_plan = conn.execute('''
        SELECT id FROM weekly_plans 
        WHERE user_id = ? AND week_start = ?
    ''', (session['user_id'], week_start)).fetchone()
    
    if not weekly_plan:
        conn.execute('''
            INSERT INTO weekly_plans (user_id, week_start)
            VALUES (?, ?)
        ''', (session['user_id'], week_start))
        weekly_plan_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    else:
        weekly_plan_id = weekly_plan['id']
    
    # Check if daily entry exists
    existing_entry = conn.execute('''
        SELECT id FROM daily_entries 
        WHERE weekly_plan_id = ? AND entry_date = ?
    ''', (weekly_plan_id, entry_date)).fetchone()
    
    if existing_entry:
        # Update existing entry
        conn.execute('''
            UPDATE daily_entries 
            SET study_time = ?, learning_summary = ?, focus_score = ?, suggestion = ?
            WHERE id = ?
        ''', (study_time, learning_summary, focus_score, suggestion, existing_entry['id']))
    else:
        # Create new entry
        conn.execute('''
            INSERT INTO daily_entries (weekly_plan_id, entry_date, study_time, learning_summary, focus_score, suggestion)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (weekly_plan_id, entry_date, study_time, learning_summary, focus_score, suggestion))
    
    conn.commit()
    conn.close()
    
    flash('Daily entry saved successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    weekly_plans = conn.execute('''
        SELECT * FROM weekly_plans 
        WHERE user_id = ?
        ORDER BY week_start DESC
    ''', (session['user_id'],)).fetchall()
    
    # Get daily entries for each week
    weeks_with_entries = []
    for plan in weekly_plans:
        entries = conn.execute('''
            SELECT * FROM daily_entries 
            WHERE weekly_plan_id = ?
            ORDER BY entry_date
        ''', (plan['id'],)).fetchall()
        weeks_with_entries.append({
            'plan': plan,
            'entries': entries
        })
    
    conn.close()
    
    return render_template('history.html', weeks=weeks_with_entries)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)