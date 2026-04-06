from flask import Flask, request, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Crear conexión a la base de datos
def get_db_connection():
    conn = sqlite3.connect('citas.db')
    conn.row_factory = sqlite3.Row
    return conn

# Crear tabla si no existe
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Registro
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    hashed_password = generate_password_hash(password)

    try:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO users (username, password) VALUES (?, ?)',
            (username, hashed_password)
        )
        conn.commit()
        conn.close()

        return jsonify({'message': 'Usuario registrado correctamente'}), 201

    except sqlite3.IntegrityError:
        return jsonify({'message': 'El usuario ya existe'}), 400

# Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ?',
        (username,)
    ).fetchone()
    conn.close()

    if user is None or not check_password_hash(user['password'], password):
        return jsonify({'message': 'Credenciales inválidas'}), 401

    return jsonify({
        'message': 'Login exitoso',
        'user': {
            'id': user['id'],
            'username': user['username']
        }
    }), 200

# Ruta de prueba
@app.route('/')
def home():
    return jsonify({'message': 'API funcionando correctamente'}), 200

if __name__ == '__main__':
    app.run(debug=True)