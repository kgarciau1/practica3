from flask import Flask, jsonify, request
from dotenv import load_dotenv
import os
import psycopg2
import psycopg2.extras
from flask.views import MethodView
from flask_smorest import Blueprint, Api
from flask_smorest import abort

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

# Configuración de la API con Swagger
app.config["API_TITLE"] = "Web Service UMG"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.2"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/docs"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

api = Api(app)
blp = Blueprint("usuarios", __name__, url_prefix="/api", description="Operaciones con usuarios")

@blp.route("/usuarios")
class UsuarioList(MethodView):

    def get(self):
        """Lista todos los usuarios."""
        conn = get_db_connection()
        if conn is None:
            abort(500, message="Error de conexión a la base de datos")
        try:
            cur.execute("SELECT id_usuario, nombre, correo, fecha_reg FROM usuarios ORDER BY id_usuario DESC")
            usuarios = cur.fetchall()
            return jsonify(usuarios)
        except Exception as e:
            abort(500, message=f"Error al obtener usuarios: {e}")

    def post(self):
        """Crea un nuevo usuario."""
        conn = get_db_connection()
        if conn is None:
            abort(500, message="Error de conexión a la base de datos")
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
            abort(400, message=f"Error al crear usuario: {e}")

@blp.route("/saludo")
class Saludo(MethodView):
    def get(self):
        """Devuelve un mensaje de saludo."""
        return jsonify({"mensaje": "¡Hola desde mi Web Service en Render!"})

api.register_blueprint(blp)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)