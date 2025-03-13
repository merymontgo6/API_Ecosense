from fastapi import Query
from client import db_client
from typing import Optional

# Consulta de todos los usuarios
def fetch_all_usuaris():
    try:
        conn = db_client()
        cur = conn.cursor()
        
        query = "SELECT * FROM usuaris"
        cur.execute(query)
        usuaris = cur.fetchall()

        usuaris_list = []
        for usuari in usuaris:
            usuaris_list.append({
                "id": usuari[0],
                "nom": usuari[1],
                "cognom": usuari[2],
                "email": usuari[3],
                "contrasenya": usuari[4]
            })
        
    except Exception as e:
        return {"status": -1, "message": f"Error de conexión: {e}"}
    finally:
        conn.close()
    return usuaris_list

# Consulta de usuario por ID
def fetch_usuari_by_id(id_usuari: int):
    try:
        conn = db_client()
        cur = conn.cursor()
        
        query = "SELECT * FROM usuaris WHERE id = %s"
        cur.execute(query, (id_usuari,))
        usuari = cur.fetchone()

        if usuari is None:
            return {"status": -1, "message": "Usuario no encontrado"}

        usuari_dict = {
            "id": usuari[0],
            "nom": usuari[1],
            "cognom": usuari[2],
            "email": usuari[3],
            "contrasenya": usuari[4]
        }
    except Exception as e:
        return {"status": -1, "message": f"Error de conexión: {e}"}
    finally:
        conn.close()
    return usuari_dict

# Consulta de sensor por ID con sus lecturas de humedad
def fetch_sensor_data(sensor_id: int):
    try:
        conn = db_client()
        cur = conn.cursor()
        
        # Obtener información del sensor
        sensor_query = """
        SELECT id, ubicacio, planta, estat, limit_humitat 
        FROM sensors 
        WHERE id = %s
        """
        cur.execute(sensor_query, (sensor_id,))
        sensor = cur.fetchone()
        
        if sensor is None:
            return {"status": -1, "message": "Sensor no encontrado"}
        
        # Obtener últimas lecturas de humedad
        humitat_query = """
        SELECT valor, timestamp 
        FROM humitat_sol 
        WHERE sensor_id = %s 
        ORDER BY timestamp DESC 
        LIMIT 10
        """
        cur.execute(humitat_query, (sensor_id,))
        lecturas = cur.fetchall()
        
        # Obtener alertas asociadas
        alertes_query = """
        SELECT timestamp, valor 
        FROM alertes 
        WHERE sensor_id = %s 
        ORDER BY timestamp DESC 
        LIMIT 10
        """
        cur.execute(alertes_query, (sensor_id,))
        alertas = cur.fetchall()
        
        response = {
            "sensor": {
                "id": sensor[0],
                "ubicacion": sensor[1],
                "planta": sensor[2],
                "estado": sensor[3],
                "limite_humedad": sensor[4]
            },
            "lecturas": [{"valor": l[0], "timestamp": l[1]} for l in lecturas],
            "alertas": [{"timestamp": a[0], "valor": a[1]} for a in alertas]
        }
        
    except Exception as e:
        return {"status": -1, "message": f"Error de conexión: {e}"}
    finally:
        conn.close()
    return response