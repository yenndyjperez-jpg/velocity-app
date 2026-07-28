import os
import sqlite3
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuración para guardar las fotos de los vehículos
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Máximo 16MB

# Crear carpeta de fotos si no existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DB_NAME = 'velocity.db'

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Inicialización de la base de datos SQLite
def init_db():
    with get_db() as conn:
        # Tabla Pasajeros
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
        # Tabla Conductores
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
        # Tabla Solicitudes de Viaje / Delivery
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
                conductor_id INTEGER,
                FOREIGN KEY (pasajero_id) REFERENCES pasajeros (id),
                FOREIGN KEY (conductor_id) REFERENCES conductores (id)
            )
        ''')
        conn.commit()

# Crear tablas al iniciar la aplicación
init_db()


# =========================================================
# RUTAS PARA CARGAR LAS VISTAS HTML
# =========================================================

@app.route('/')
@app.route('/pasajero')
def vista_pasajero():
    return render_template('pasajero.html')

@app.route('/conductor')
def vista_conductor():
    return render_template('conductor.html')


# =========================================================
# RUTAS DE API / BACKEND
# =========================================================

# 1. Registro de Pasajero
@app.route('/registro/pasajero', methods=['POST'])
def registro_pasajero():
    data = request.form
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO pasajeros (cedula, nombre, fecha_nacimiento, telefono, sexo)
                VALUES (?, ?, ?, ?, ?)
            ''', (data['cedula'], data['nombre'], data['fecha_nacimiento'], data['telefono'], data['sexo']))
            conn.commit()
            pasajero_id = cursor.lastrowid
        return jsonify({"status": "success", "pasajero_id": pasajero_id, "mensaje": "Pasajero registrado con éxito"})
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "mensaje": "La cédula ya está registrada"}), 400

# 2. Registro de Conductor (con foto de vehículo)
@app.route('/registro/conductor', methods=['POST'])
def registro_conductor():
    data = request.form
    file = request.files.get('foto_vehiculo')
    
    if not file:
        return jsonify({"status": "error", "mensaje": "La foto del vehículo es obligatoria"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    foto_url = f"/static/uploads/{filename}"

    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO conductores (cedula, nombre, telefono, tipo_vehiculo, foto_vehiculo)
                VALUES (?, ?, ?, ?, ?)
            ''', (data['cedula'], data['nombre'], data['telefono'], data['tipo_vehiculo'], foto_url))
            conn.commit()
            conductor_id = cursor.lastrowid
        return jsonify({"status": "success", "conductor_id": conductor_id, "mensaje": "Conductor registrado con éxito"})
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "mensaje": "La cédula ya está registrada"}), 400

# 3. Solicitar Servicio (Viaje propio, para otro o Delivery)
@app.route('/solicitar_servicio', methods=['POST'])
def solicitar_servicio():
    data = request.json
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO solicitudes 
            (pasajero_id, tipo_servicio, origen_direccion, origen_lat, origen_lon, destino_direccion, destino_lat, destino_lon, detalles_adicionales)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['pasajero_id'], data['tipo_servicio'],
            data['origen_direccion'], data['origen_lat'], data['origen_lon'],
            data['destino_direccion'], data['destino_lat'], data['destino_lon'],
            data.get('detalles_adicionales', '')
        ))
        conn.commit()
        solicitud_id = cursor.lastrowid
    return jsonify({"status": "success", "solicitud_id": solicitud_id, "mensaje": "Solicitud enviada"})

# 4. Obtener Solicitudes Pendientes para Conductores (con Enlaces Google Maps)
@app.route('/conductor/solicitudes_pendientes', methods=['GET'])
def solicitudes_pendientes():
    with get_db() as conn:
        solicitudes = conn.execute('''
            SELECT s.*, p.nombre as nombre_pasajero, p.telefono as telefono_pasajero 
            FROM solicitudes s
            JOIN pasajeros p ON s.pasajero_id = p.id
            WHERE s.estado = 'pendiente'
        ''').fetchall()
    
    lista = []
    for s in solicitudes:
        link_origen = f"https://www.google.com/maps?q={s['origen_lat']},{s['origen_lon']}"
        link_destino = f"https://www.google.com/maps?q={s['destino_lat']},{s['destino_lon']}"
        
        lista.append({
            "id": s['id'],
            "pasajero": s['nombre_pasajero'],
            "telefono": s['telefono_pasajero'],
            "tipo_servicio": s['tipo_servicio'],
            "origen": s['origen_direccion'],
            "origen_maps": link_origen,
            "destino": s['destino_direccion'],
            "destino_maps": link_destino,
            "detalles": s['detalles_adicionales']
        })
    return jsonify({"solicitudes": lista})

# 5. Obtener Info del Conductor Asignado
@app.route('/pasajero/info_conductor/<int:conductor_id>', methods=['GET'])
def info_conductor(conductor_id):
    with get_db() as conn:
        conductor = conn.execute('SELECT nombre, telefono, tipo_vehiculo, foto_vehiculo FROM conductores WHERE id = ?', (conductor_id,)).fetchone()
    if conductor:
        return jsonify(dict(conductor))
    return jsonify({"error": "Conductor no encontrado"}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)