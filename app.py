from functools import wraps
from flask import Flask, request, jsonify, session, redirect, url_for, render_template, flash
import mysql.connector
from mysql.connector import Error
from werkzeug.security import check_password_hash, generate_password_hash




app = Flask(__name__)

app.secret_key = 'SUPER_SECRET_IMPOSSIBLE_TO_CRACK_KEY'

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'ourforms'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
    
def login_required(f):
    """Dekorator som kräver inloggning"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def home():
    return render_template('index.html')

@app.route('/sign_up', methods=['GET'])
def sign_up_page():
    return render_template('sign_up.html')

@app.route('/sign_up', methods=['POST'])
def create_user():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    hashed_password = generate_password_hash(password)

    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = None
    try:
        cursor = connection.cursor()
        sql = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        cursor.execute(sql, (username, email, hashed_password))
        connection.commit()
        return redirect(url_for('login_page'))
    except Error as e:
        flash(f"Error executing insert: {e}")
        return jsonify({"error": "Insert failed"}), 500
    finally:
        if cursor:
            try:
                cursor.close()
                connection.close()
            except Exception:
                pass
    

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    flash("Utloggad!", "success")
    return redirect(url_for('login_page'))

@app.route('/login', methods=['POST'])
def login():

    username = request.form['username']
    password = request.form['password']

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if not user or not check_password_hash(user['password'], password):
            flash("Fel användarnamn eller lösenord", "fail")
            return render_template('login.html')
        
        flash("Inloggad!", "success")
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['is_admin'] = user['is_admin']
        return redirect(url_for('home'))

    except Error:
        return render_template('login.html', error=True)

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Registrera blueprinten
from forum import forum_bp  # Importera blueprinten
app.register_blueprint(forum_bp)

if __name__ == '__main__':
    app.run(debug=True)