import sqlite3
import os

DB_NAME = "velocity.db"

# =====================================================================
# 1. INICIALIZACIÓN Y ESTRUCTURA DE LA BASE DE DATOS
# =====================================================================
def inicializar_base_datos():
    """Crea la estructura de tablas para Usuarios, Conductores, Viajes y Chats."""
    with sqlite3.connect(DB_NAME) as conexion:
        cursor = conexion.cursor()
        
        # Tabla de Usuarios Normales (Pasajeros)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                telefono TEXT UNIQUE NOT NULL,
                correo TEXT
            )
        """)
        
        # Tabla de Conductores (Motos y Carros + 5 fotos/documentos)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conductores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                cedula TEXT UNIQUE NOT NULL,
                licencia TEXT NOT NULL,
                placa TEXT NOT NULL,
                tipo_vehiculo TEXT NOT NULL,
                localidad TEXT NOT NULL,
                foto_perfil TEXT,
                foto_vehiculo_ext TEXT,
                foto_vehiculo_int TEXT,
                foto_licencia TEXT,
                foto_documentos TEXT,
                estado TEXT DEFAULT 'DISPONIBLE'
            )
        """)
        
        # Tabla de Solicitudes de Viajes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS viajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_nombre TEXT NOT NULL,
                cliente_ubicacion TEXT NOT NULL,
                tipo_vehiculo_req TEXT NOT NULL,
                conductor_id INTEGER,
                estado TEXT DEFAULT 'BUSCANDO',
                FOREIGN KEY(conductor_id) REFERENCES conductores(id)
            )
        """)
        
        # Tabla de Mensajes del Chat en vivo
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                viaje_id INTEGER,
                remitente TEXT,
                mensaje TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(viaje_id) REFERENCES viajes(id)
            )
        """)

# =====================================================================
# 2. OPERACIONES DE USUARIOS Y CONDUCTORES
# =====================================================================
def registrar_usuario(nombre, telefono, correo):
    """Registra un pasajero/usuario normal en el sistema."""
    try:
        with sqlite3.connect(DB_NAME) as conexion:
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO usuarios (nombre, telefono, correo)
                VALUES (?, ?, ?)
            """, (nombre, telefono, correo))
            return True, "Usuario registrado exitosamente."
    except sqlite3.IntegrityError:
        return False, "El número de teléfono ya está registrado."
    except Exception as e:
        return False, f"Error en la base de datos: {str(e)}"

def registrar_conductor_completo(nombre, cedula, licencia, placa, tipo_vehiculo, localidad, fotos_dict):
    """Registra un conductor con sus datos personales y rutas de fotos."""
    try:
        with sqlite3.connect(DB_NAME) as conexion:
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO conductores (
                    nombre, cedula, licencia, placa, tipo_vehiculo, localidad,
                    foto_perfil, foto_vehiculo_ext, foto_vehiculo_int, foto_licencia, foto_documentos
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                nombre, cedula, licencia, placa, tipo_vehiculo, localidad,
                fotos_dict.get('perfil'), fotos_dict.get('ext'), 
                fotos_dict.get('int'), fotos_dict.get('licencia'), fotos_dict.get('docs')
            ))
            return True, "Conductor registrado exitosamente."
    except sqlite3.IntegrityError:
        return False, "La cédula de identidad ya se encuentra registrada."
    except Exception as e:
        return False, f"Error en la base de datos: {str(e)}"

# =====================================================================
# 3. MOTOR DE MATCHING Y VIAJES
# =====================================================================
def crear_solicitud_viaje(cliente_nombre, cliente_ubicacion, tipo_vehiculo_req):
    """Inserta una solicitud de viaje en la BD y retorna su ID asignado."""
    with sqlite3.connect(DB_NAME) as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO viajes (cliente_nombre, cliente_ubicacion, tipo_vehiculo_req)
            VALUES (?, ?, ?)
        """, (cliente_nombre, cliente_ubicacion, tipo_vehiculo_req))
        return cursor.lastrowid

def buscar_conductor_disponible(viaje_id, tipo_vehiculo_req):
    """Busca un conductor disponible que coincida con el tipo de vehículo."""
    with sqlite3.connect(DB_NAME) as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT id, nombre FROM conductores 
            WHERE tipo_vehiculo = ? AND estado = 'DISPONIBLE' 
            LIMIT 1
        """, (tipo_vehiculo_req,))
        conductor = cursor.fetchone()
        
        if conductor:
            cond_id, cond_nombre = conductor
            cursor.execute("UPDATE conductores SET estado = 'OCUPADO' WHERE id = ?", (cond_id,))
            cursor.execute("UPDATE viajes SET conductor_id = ?, estado = 'EN_PROCESO' WHERE id = ?", (cond_id, viaje_id))
            return cond_nombre
            
        return None

def finalizar_viaje(viaje_id):
    """Finaliza el viaje y libera al conductor asociado."""
    with sqlite3.connect(DB_NAME) as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT conductor_id FROM viajes WHERE id = ?", (viaje_id,))
        resultado = cursor.fetchone()
        
        if resultado and resultado[0]:
            cond_id = resultado[0]
            cursor.execute("UPDATE conductores SET estado = 'DISPONIBLE' WHERE id = ?", (cond_id,))
            
        cursor.execute("UPDATE viajes SET estado = 'FINALIZADO' WHERE id = ?", (viaje_id,))

# =====================================================================
# 4. CHAT EN TIEMPO REAL
# =====================================================================
def enviar_mensaje_chat(viaje_id, remitente, mensaje):
    """Guarda un mensaje enviado en la BD."""
    if not mensaje.strip():
        return
    with sqlite3.connect(DB_NAME) as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO chats (viaje_id, remitente, mensaje) 
            VALUES (?, ?, ?)
        """, (viaje_id, remitente, mensaje.strip()))

def obtener_mensajes_nuevos(viaje_id, ultimo_id_leido):
    """Obtiene mensajes del chat cuya clave id sea mayor al último leído."""
    with sqlite3.connect(DB_NAME) as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT id, remitente, mensaje FROM chats 
            WHERE viaje_id = ? AND id > ? 
            ORDER BY id ASC
        """, (viaje_id, ultimo_id_leido))
        return cursor.fetchall()