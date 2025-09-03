from flask import Flask, jsonify, request
from dotenv import load_dotenv
import os
import psycopg2
import psycopg2.extras

# Cargar variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)

# Configuración de la base de datos
DB_URL = os.environ.get("DATABASE_URL")
conn = None
cur = None

def get_db_connection():
    global conn, cur
    if conn is None or conn.closed:
        try:
            conn = psycopg2.connect(DB_URL)
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        except Exception as e:
            print(f"Error al conectar con la base de datos: {e}")
            return None
    return conn

# Ruta principal que ahora devolverá un mensaje
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "message": "Bienvenido a mi Web Service de usuarios.",
        "endpoints": {
            "GET /api/saludo": "Devuelve un mensaje de saludo.",
            "GET /api/usuarios": "Obtiene la lista de todos los usuarios.",
            "POST /api/usuarios": "Crea un nuevo usuario."
        }
    })

# Ruta de saludo
@app.route('/api/saludo', methods=['GET'])
def saludo():
    return jsonify({"mensaje": "¡Hola desde mi Web Service en Render!"})

# Ruta para obtener todos los usuarios
@app.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    try:
        cur.execute("SELECT id_usuario, nombre, correo, fecha_reg FROM usuarios ORDER BY id_usuario DESC")
        usuarios = cur.fetchall()
        return jsonify(usuarios)
    except Exception as e:
        return jsonify({"error": f"Error al obtener usuarios: {e}"}), 500

# Ruta para crear un nuevo usuario (POST)
@app.route('/api/usuarios', methods=['POST'])
def create_usuario():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    try:
        data = request.get_json()
        nombre = data['nombre']
        correo = data['correo']
        password = data['password']
        
        cur.execute("INSERT INTO usuarios (nombre, correo, password) VALUES (%s, %s, %s) RETURNING id_usuario", (nombre, correo, password))
        conn.commit()
        
        nuevo_usuario_id = cur.fetchone()['id_usuario']
        
        return jsonify({"mensaje": "Usuario creado con éxito", "id_usuario": nuevo_usuario_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Error al crear usuario: {e}"}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)