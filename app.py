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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json(silent=True)  # Hämta data från requesten.
    if not is_valid_user_data(data):
        return jsonify({"error": "Missing or invalid required fields (username, email, password)"}), 422

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    hashed_password = generate_password_hash(password)  # Hasha lösenordet

    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = None
    try:
        cursor = connection.cursor()
        sql = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        cursor.execute(sql, (username, email, hashed_password))
        connection.commit()
        user_id = cursor.lastrowid

        user = {
            'id': user_id,
            'username': username,
            'email': email,
            'password': hashed_password
        }
        return jsonify(user), 201
    except Error as e:
        print(f"Error executing insert: {e}")
        return jsonify({"error": "Insert failed"}), 500
    finally:
        if cursor:
            try:
                cursor.close()
                connection.close()
            except Exception:
                pass


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