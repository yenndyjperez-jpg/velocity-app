import os
import sqlite3
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='templates')

# Configuración de carpetas
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

try:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
except Exception as e:
    print(f"Aviso carpetas: {e}")

DB_NAME = 'velocity.db'

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    try:
        with get_db() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS pasajeros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cedula TEXT UNIQUE NOT NULL,
                    nombre TEXT NOT NULL,
                    fecha_nacimiento TEXT NOT NULL,
                    telefono TEXT NOT NULL,
                    sexo TEXT NOT NULL
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS conductores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cedula TEXT UNIQUE NOT NULL,
                    nombre TEXT NOT NULL,
                    telefono TEXT NOT NULL,
                    tipo_vehiculo TEXT NOT NULL,
                    foto_vehiculo TEXT NOT NULL
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS solicitudes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pasajero_id INTEGER,
                    tipo_servicio TEXT NOT NULL,
                    origen_direccion TEXT NOT NULL,
                    origen_lat REAL NOT NULL,
                    origen_lon REAL NOT NULL,
                    destino_direccion TEXT NOT NULL,
                    destino_lat REAL NOT NULL,
                    destino_lon REAL NOT NULL,
                    detalles_adicionales TEXT,
                    estado TEXT DEFAULT 'pendiente',
                    conductor_id INTEGER
                )
            ''')
            conn.commit()
    except Exception as e:
        print(f"Error BD: {e}")

init_db()

# --- RUTAS DE NAVEGACIÓN ---

@app.route('/')
def inicio():
    try:
        return render_template('pasajero.html')
    except Exception as e:
        return f"<h3>Error de plantilla:</h3><p>{e}</p><p>Verifica que 'pasajero.html' esté dentro de la carpeta 'templates' en GitHub.</p>"

@app.route('/pasajero')
def vista_pasajero():
    return render_template('pasajero.html')

@app.route('/conductor')
def vista_conductor():
    return render_template('conductor.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)