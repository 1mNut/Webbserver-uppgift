from functools import *
from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template, flash
import mysql.connector
from mysql.connector import Error
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

# SELECT * from topics where header like "%hej%"

# Skapa en blueprint för forumet
forum_bp = Blueprint('forum', __name__)

# Använd samma DB_CONFIG som i app.py (importera från app.py eller definiera här)
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

@forum_bp.route('/create', methods=['GET'])
def create_topic_page():
    return render_template('create_topic.html')

@forum_bp.route('/create', methods=['POST'])
def create_topic():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    header = request.form['header']
    description = request.form['description']
    user_id = session['user_id']
    date = datetime.now().date()
    
    connection = get_db_connection()
    if connection is None:
        flash("Database connection failed", "fail")
        return redirect(url_for('home'))
    
    cursor = None
    try:
        cursor = connection.cursor()
        sql = "INSERT INTO topics (user_id, header, description, date) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (user_id, header, description, date))
        connection.commit()
        flash("Tråd skapad!", "success")
        return redirect(url_for('home'))
    except Error as e:
        flash(f"Error: {e}", "fail")
        return redirect(url_for('home'))
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@forum_bp.route('/topics', methods=['GET'])
def list_topics():
    connection = get_db_connection()
    if connection is None:
        return "Database error", 500
    
    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT topics.*, users.username FROM topics JOIN users ON topics.user_id = users.id ORDER BY date DESC")
        topics = cursor.fetchall()
        return render_template('topics.html', topics=topics)
    except Error as e:
        return f"Error: {e}", 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@forum_bp.route('/topic/<int:topic_id>', methods=['GET'])
def view_topic(topic_id): 
    connection = get_db_connection()
    if connection is None:
        return "Database error", 500
    
    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT topics.*, users.username FROM topics JOIN users ON topics.user_id = users.id WHERE topics.id = %s", (topic_id,))
        topic = cursor.fetchone()
        if topic is None:
            return jsonify({"error": "Topic not found"}), 404
        
        # Hämta kommentarer för tråden
        cursor.execute("SELECT comments.*, users.username FROM comments JOIN users ON comments.user_id = users.id WHERE comments.topic_id = %s ORDER BY date ASC", (topic_id,))
        comments = cursor.fetchall()
        
        return render_template('topic.html', topic=topic, comments=comments)
    except Error as e:
        return f"Error: {e}", 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@forum_bp.route('/topic/<int:topic_id>', methods=['POST'])
def add_comment(topic_id):
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    content = request.form['comment']
    user_id = session['user_id']
    date = datetime.now().date()
    
    connection = get_db_connection()
    if connection is None:
        flash("Database connection failed", "fail")
        return redirect(url_for('home'))
    
    cursor = None
    try:
        cursor = connection.cursor()
        sql = "INSERT INTO comments (topic_id, user_id, content, date) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (topic_id, user_id, content, date))
        connection.commit()
        flash("Kommentar tillagd!", "success")
        return redirect(url_for('view_topic', topic_id=topic_id))
    except Error as e:
        flash(f"Error: {e}", "fail")
        return redirect(url_for('view_topic', topic_id=topic_id))
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()