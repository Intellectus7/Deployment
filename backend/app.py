import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes

def get_db_connection():
    # Use the DATABASE_URL environment variable for the connection string
    conn = psycopg2.connect(os.environ['URL'])
    return conn

# Initialize the database table
def init_db():
    conn = get_db_connection()
    # Use a context manager to ensure the connection and cursor are closed properly
    with conn:
        with conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS todos (
                    id SERIAL PRIMARY KEY,
                    text VARCHAR(255) NOT NULL,
                    completed BOOLEAN DEFAULT FALSE
                );
            ''')
        # conn.commit() is automatically called by the context manager on success
    # conn.close() is also automatically handled

init_db()

@app.route('/todos', methods=['GET'])
def get_todos():
    conn = get_db_connection()
    with conn:
        # Use RealDictCursor to fetch results as a dictionary
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('SELECT * FROM todos ORDER BY id')
            todos = cur.fetchall()
            return jsonify(todos)
    # The context manager automatically closes the connection and cursor

@app.route('/todos', methods=['POST'])
def add_todo():
    data = request.json
    text = data.get('text')
    if not text:
        return jsonify({'error': 'Text is required'}), 400

    conn = get_db_connection()
    with conn:
        # Use RealDictCursor to return the new row as a dictionary
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('INSERT INTO todos (text) VALUES (%s) RETURNING *', (text,))
            new_todo = cur.fetchone()
            return jsonify(new_todo), 201
#