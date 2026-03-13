from functools import *
from flask_socketio import *
import random as rand
from flask import Flask, request, jsonify, session, redirect, url_for, render_template, get_flashed_messages, flash
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error, IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta



app = Flask(__name__)
jwt = JWTManager(app)
socketio = SocketIO(app)

app.secret_key = 'SUPER_SECRET_IMPOSSIBLE_TO_CRACK_KEY'



DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'ourforms'
}



def get_db_connection():
    """Get a database connection"""
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

def is_valid_user_data(data):
    return data and 'username' in data

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
        return redirect(url_for('home'))

    except mysql.connector.Error:
        return render_template('login.html', error=True)

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()



# @app.route('/settings')
# @login_required
# def settings():
#     return render_template('settings.html')

if __name__ == '__main__':
    app.run(debug=True)