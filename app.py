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

# Initialize database and table
try:
    connection = mysql.connector.connect(host='localhost', user='root', password='')
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS ourforms")
    cursor.execute("USE ourforms")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE,
            email VARCHAR(255),
            password VARCHAR(255)
        )
    """)
    cursor.close()
    connection.close()
except mysql.connector.Error as e:
    print(f"Database initialization error: {e}")

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/')
def home():
    return render_template('index.html')

# @app.route('/users', methods=['POST'])
# def create_user():
#     data = request.get_json(silent=True)  # Hämta data från requesten.
#     if not is_valid_user_data(data):
#         return jsonify({"error": "Missing or invalid required fields (username, email, password)"}), 422

#     username = data.get('username')
#     email = data.get('email')
#     password = data.get('password')
#     hashed_password = generate_password_hash(password)  # Hasha lösenordet

#     connection = get_db_connection()
#     if connection is None:
#         return jsonify({"error": "Database connection failed"}), 500

#     cursor = None
#     try:
#         cursor = connection.cursor()
#         sql = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
#         cursor.execute(sql, (username, email, hashed_password))
#         connection.commit()
#         user_id = cursor.lastrowid

#         user = {
#             'id': user_id,
#             'username': username,
#             'email': email,
#             'password': hashed_password
#         }
#         return jsonify(user), 201
#     except Error as e:
#         print(f"Error executing insert: {e}")
#         return jsonify({"error": "Insert failed"}), 500
#     finally:
#         if cursor:
#             try:
#                 cursor.close()
#                 connection.close()
#             except Exception:
#                 pass

@app.route('/users', methods=['POST'])
def create_user():

    cursor = None
    connection = None

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Incorrect Json format'}), 400

    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username:
        return jsonify({'error': 'username required'}), 400
    if not password:
        return jsonify({'error': 'password required'}), 400
    if not email:
        return jsonify({'error': 'email required'}), 400

    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'database connection failed'}), 500
        cursor = connection.cursor()
        hashed_password = generate_password_hash(password)
        sql = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        cursor.execute(sql, (username, email, hashed_password))
                
        connection.commit()
        user_id = cursor.lastrowid

        user = {
            'id': user_id,
            'username': username,
            'email': email
        }
        return jsonify({'message': 'user created', 'user': user}), 201
    except IntegrityError:
        return jsonify({'error': 'username already exists'}), 400
    except Error:
        return jsonify({'error': 'something went wrong'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# def is_valid_user_data(data):
#     if not data or not isinstance(data, dict):
#         return False

#     username = data.get('username')
#     if not isinstance(username, str) or not username.strip():
#         return False

#     if 'email' in data and data.get('email') is not None:
#         try:
#             email = int(data.get('email'))
#             if email < 0:
#                 return False
#         except (TypeError, ValueError):
#             return False

#     return True

def is_valid_user_data(data):
    return data and 'username' in data

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
        
        session['user'] = user['username']
        flash("Inloggad!", "success")
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