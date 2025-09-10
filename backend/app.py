import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes

def get_db_connection():
    conn = "psql 'postgresql://neondb_owner:npg_z4K3VEavmUYo@ep-morning-leaf-ab3ldqxu-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require'"
    return conn

# Initialize the database table
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id SERIAL PRIMARY KEY,
            text VARCHAR(255) NOT NULL,
            completed BOOLEAN DEFAULT FALSE
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

init_db()

@app.route('/todos', methods=['GET'])
def get_todos():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM todos ORDER BY id')
    todos = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{'id': todo[0], 'text': todo[1], 'completed': todo[2]} for todo in todos])

@app.route('/todos', methods=['POST'])
def add_todo():
    data = request.json
    text = data.get('text')
    if not text:
        return jsonify({'error': 'Text is required'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO todos (text) VALUES (%s) RETURNING *', (text,))
    new_todo = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'id': new_todo[0], 'text': new_todo[1], 'completed': new_todo[2]}), 201

if __name__ == '__main__':
    app.run(debug=True)
