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
    'database': 'database'
}

# def login_required(func):
#     @wraps(func)
#     def decorated_function(*args, **kwargs):
#         if 'user' not in session:
#             return redirect(url_for('login'))
#         return func(*args, **kwargs)
#     return decorated_function

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
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
                return redirect(url_for('login'))
            
            session['user'] = user['username']
            flash("Inloggad!", "success")
            return redirect(url_for('home'))

        except mysql.connector.Error as e:
            print(e)
            flash("Databasfel", "fail")
            return redirect(url_for('login'))

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    return render_template('login.html')

# @app.route('/settings')
# @login_required
# def settings():
#     return render_template('settings.html')

if __name__ == '__main__':
    app.run(debug=True)