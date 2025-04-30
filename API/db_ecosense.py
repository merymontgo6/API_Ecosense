from typing import Dict, List, Any, Optional
import pymysql
from datetime import datetime

# Consulta de todos los usuarios (sin sensor_id)
def fetch_all_usuaris() -> List[Dict[str, Any]]:
    conn = None
    try:
        conn = db_client()
        cur = conn.cursor()
        
        query = "SELECT id, nom, cognom, email FROM usuaris"  # Eliminado contrasenya y sensor_id
        cur.execute(query)
        usuaris = cur.fetchall()

        return [{
            "id": usuari[0],
            "nom": usuari[1],
            "cognom": usuari[2],
            "email": usuari[3]
        } for usuari in usuaris]
        
    except Exception as e:
        return {"status": -1, "message": f"Error de conexión: {e}"}
    finally:
        if conn:
            conn.close()

# Consulta de usuario por ID (sin sensor_id)
def fetch_usuari_by_id(id_usuari: int) -> Dict[str, Any]:
    conn = None
    try:
        conn = db_client()
        cur = conn.cursor()
        
        query = "SELECT id, nom, cognom, email FROM usuaris WHERE id = %s"  # Eliminado contrasenya y sensor_id
        cur.execute(query, (id_usuari,))
        usuari = cur.fetchone()

        if usuari is None:
            return {"status": -1, "message": "Usuario no encontrado"}

        return {
            "id": usuari[0],
            "nom": usuari[1],
            "cognom": usuari[2],
            "email": usuari[3]
        }
    except Exception as e:
        return {"status": -1, "message": f"Error de conexión: {e}"}
    finally:
        if conn:
            conn.close()

# Creación de usuario (sin sensor_id)
def create_usuari(usuari: Dict[str, Any]) -> Dict[str, Any]:
    conn = None
    try:
        conn = db_client()
        cur = conn.cursor()
        
        query = """
            INSERT INTO usuaris (nom, cognom, email, contrasenya)
            VALUES (%s, %s, %s, %s)
        """
        cur.execute(query, (
            usuari['nom'], 
            usuari['cognom'], 
            usuari['email'], 
            usuari['contrasenya']
        ))
        usuari_id = cur.lastrowid
        conn.commit()
        
        return {**usuari, "id": usuari_id, "contrasenya": None}  # No devolver la contraseña
    except pymysql.err.IntegrityError as e:
        return {"status": -1, "message": "Email ya registrado"}
    except Exception as e:
        return {"status": -1, "message": f"Error de conexión: {e}"}
    finally:
        if conn:
            conn.close()

# Consulta de datos del sensor (actualizada)
def fetch_sensor_data(sensor_id: int) -> Dict[str, Any]:
    conn = None
    try:
        conn = db_client()
        cur = conn.cursor()
        
        # Obtener información básica del sensor
        sensor_query = """
        SELECT sensor_id, estat, usuari_id 
        FROM sensors 
        WHERE sensor_id = %s
        """
        cur.execute(sensor_query, (sensor_id,))
        sensor = cur.fetchone()
        
        if sensor is None:
            return {"status": -1, "message": "Sensor no encontrado"}
        
        # Obtener planta asociada (con ubicación)
        planta_query = """
        SELECT id, nom, ubicacio 
        FROM planta 
        WHERE sensor_id = %s
        """
        cur.execute(planta_query, (sensor_id,))
        planta = cur.fetchone()
        
        # Obtener últimas lecturas de humedad
        humitat_query = """
        SELECT id, valor, timestamp 
        FROM humitat_sol 
        WHERE sensor_id = %s 
        ORDER BY timestamp DESC 
        LIMIT 10
        """
        cur.execute(humitat_query, (sensor_id,))
        lecturas = cur.fetchall()
        
        response = {
            "sensor": {
                "sensor_id": sensor[0],
                "estat": sensor[1],
                "usuari_id": sensor[2]
            },
            "planta": {
                "id": planta[0],
                "nom": planta[1],
                "ubicacio": planta[2]
            } if planta else None,
            "lecturas": [{
                "id": l[0],
                "valor": l[1],
                "timestamp": l[2].isoformat() if l[2] else None
            } for l in lecturas]
        }
        
        return response
        
    except Exception as e:
        return {"status": -1, "message": f"Error de conexión: {e}"}
    finally:
        if conn:
            conn.close()

# Creación de sensor
def create_sensor(sensor: Dict[str, Any]) -> Dict[str, Any]:
    conn = None
    try:
        conn = db_client()
        cur = conn.cursor()
        
        query = """
            INSERT INTO sensors (sensor_id, estat, usuari_id)
            VALUES (%s, %s, %s)
        """
        cur.execute(query, (
            sensor['sensor_id'],
            sensor.get('estat', 'Actiu'),
            sensor.get('usuari_id')
        ))
        conn.commit()
        
        return {
            "sensor_id": sensor['sensor_id'],
            "estat": sensor.get('estat', 'Actiu'),
            "usuari_id": sensor.get('usuari_id')
        }
    except pymysql.err.IntegrityError as e:
        return {"status": -1, "message": "Sensor ya existe o usuario no válido"}
    except Exception as e:
        return {"status": -1, "message": f"Error de conexión: {e}"}
    finally:
        if conn:
            conn.close()

# Consulta de plantas (actualizada con ubicación)
def fetch_plantes() -> List[Dict[str, Any]]:
    conn = None
    try:
        conn = db_client()
        cur = conn.cursor()
        
        query = "SELECT id, nom, ubicacio, sensor_id, usuari_id FROM planta"
        cur.execute(query)
        plantes = cur.fetchall()
        
        return [{
            "id": p[0],
            "nom": p[1],
            "ubicacio": p[2],
            "sensor_id": p[3],
            "usuari_id": p[4]
        } for p in plantes]
    except Exception as e:
        return {"status": -1, "message": f"Error de conexión: {e}"}
    finally:
        if conn:
            conn.close()

# Creación de planta (actualizada con ubicación y usuari_id)
def create_planta(planta: Dict[str, Any]) -> Dict[str, Any]:
    conn = None
    try:
        conn = db_client()
        cur = conn.cursor()
        
        query = """
            INSERT INTO planta (id, nom, ubicacio, sensor_id, usuari_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(query, (
            planta['id'],
            planta['nom'],
            planta['ubicacio'],
            planta['sensor_id'],
            planta.get('usuari_id')
        ))
        planta_id = cur.lastrowid
        conn.commit()
        
        return {
            "id": planta['id'],
            "nom": planta['nom'],
            "ubicacio": planta['ubicacio'],
            "sensor_id": planta['sensor_id'],
            "usuari_id": planta.get('usuari_id')
        }
    except pymysql.err.IntegrityError as e:
        if "sensor_id" in str(e):
            return {"status": -1, "message": "Sensor ya asociado a otra planta"}
        return {"status": -1, "message": "ID de planta ya existe o datos inválidos"}
    except Exception as e:
        return {"status": -1, "message": f"Error de conexión: {e}"}
    finally:
        if conn:
            conn.close()