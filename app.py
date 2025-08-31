# Importar los módulos necesarios
import os
import psycopg2
from flask import Flask, jsonify, request
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Inicializar la aplicación Flask
app = Flask(__name__)

# Función para obtener una conexión a la base de datos
def get_db_connection():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        return conn
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None

# Endpoint de prueba para verificar que el servicio está funcionando
@app.route('/api/saludo', methods=['GET'])
def saludo():
    """Devuelve un mensaje de saludo y la fecha actual."""
    import datetime
    return jsonify({
        "mensaje": "¡Hola! Mi web service con Python está funcionando en Render.",
        "fecha": datetime.datetime.now().isoformat()
    })

# Endpoint GET para obtener todos los usuarios
@app.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    """Obtiene y devuelve una lista de usuarios de la base de datos."""
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id_usuario, nombre, correo, fecha_reg FROM usuarios;")
            usuarios = cur.fetchall()
            
            # Convertir los resultados a una lista de diccionarios
            usuarios_list = []
            for usuario in usuarios:
                usuarios_list.append({
                    "id_usuario": usuario[0],
                    "nombre": usuario[1],
                    "correo": usuario[2],
                    "fecha_reg": usuario[3].isoformat()
                })
            
            return jsonify(usuarios_list)
    except Exception as e:
        print(f"Error al obtener usuarios: {e}")
        return jsonify({"error": "Error al obtener los usuarios"}), 500
    finally:
        conn.close()

# Endpoint POST para agregar un nuevo usuario
@app.route('/api/usuarios', methods=['POST'])
def add_usuario():
    """Agrega un nuevo usuario a la base de datos."""
    data = request.json
    nombre = data.get('nombre')
    correo = data.get('correo')
    password = data.get('password')

    # Validar que los datos requeridos estén presentes
    if not nombre or not correo or not password:
        return jsonify({"error": "Nombre, correo y password son campos obligatorios."}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO usuarios(nombre, correo, password) VALUES(%s, %s, %s) RETURNING id_usuario, nombre, correo, fecha_reg;",
                (nombre, correo, password)
            )
            nuevo_usuario = cur.fetchone()
            conn.commit()

            # Convertir el resultado a un diccionario
            usuario_dict = {
                "id_usuario": nuevo_usuario[0],
                "nombre": nuevo_usuario[1],
                "correo": nuevo_usuario[2],
                "fecha_reg": nuevo_usuario[3].isoformat()
            }
            
            return jsonify({"mensaje": "Usuario creado exitosamente", "usuario": usuario_dict}), 201
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return jsonify({"error": "Error al crear el usuario. El correo ya existe."}), 409
    except Exception as e:
        conn.rollback()
        print(f"Error al crear el usuario: {e}")
        return jsonify({"error": "Error al crear el usuario."}), 500
    finally:
        conn.close()

# Esto solo se ejecutará cuando corras el script localmente
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.getenv('PORT', 5000))