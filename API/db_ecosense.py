from ast import Dict, List
from fastapi import Query
from client import db_client
from typing import Any, Optional

# Consulta de todos los usuarios
def fetch_all_usuaris() -> List[Dict[str, Any]]:
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
def fetch_usuari_by_id(id_usuari: int) -> Dict[str, Any]:
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

def create_usuari(usuari: Dict[str, Any]) -> Dict[str, Any]:
    try:
        conn = db_client()
        cur = conn.cursor()
        
        query = """
            INSERT INTO usuaris (nom, cognom, email, contrasenya)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        cur.execute(query, (usuari['nom'], usuari['cognom'], usuari['email'], usuari['contrasenya']))
        usuari_id = cur.fetchone()[0]
        conn.commit()
        
        return {**usuari, "id": usuari_id}
    except pymysql.err.IntegrityError as e:
        return {"status": -1, "message": "Email ya registrado"}
    except Exception as e:
        return {"status": -1, "message": f"Error de conexión: {e}"}
    finally:
        conn.close()
        
def fetch_sensor_data(sensor_id: int) -> Dict[str, Any]:
    try:
        conn = db_client()
        cur = conn.cursor()
        
        # Obtener información del sensor
        sensor_query = """
        SELECT id, ubicacio, planta, estat 
        FROM sensors 
        WHERE id = %s
        """
        cur.execute(sensor_query, (sensor_id,))
        sensor = cur.fetchone()
        
        if sensor is None:
            return {"status": -1, "message": "Sensor no encontrado"}
        
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
        
        # Obtener planta asociada
        planta_query = """
        SELECT id, nom 
        FROM planta 
        WHERE sensor_id = %s
        """
        cur.execute(planta_query, (sensor_id,))
        planta = cur.fetchone()
        
        response = {
            "sensor": {
                "id": sensor[0],
                "ubicacion": sensor[1],
                "planta": sensor[2],
                "estado": sensor[3]
            },
            "lecturas": [{
                "id": l[0],
                "valor": l[1],
                "timestamp": l[2].isoformat()
            } for l in lecturas],
            "planta": {
                "id": planta[0],
                "nom": planta[1]
            } if planta else None
        }
        
    except Exception as e:
        return {"status": -1, "message": f"Error de conexión: {e}"}
    finally:
        conn.close()
    return response

def create_lectura(lectura: Dict[str, Any]) -> Dict[str, Any]:
    try:
        conn = db_client()
        cur = conn.cursor()
        
        query = """
            INSERT INTO humitat_sol (sensor_id, valor)
            VALUES (%s, %s)
            RETURNING id, timestamp
        """
        cur.execute(query, (lectura['sensor_id'], lectura['valor']))
        lectura_id, timestamp = cur.fetchone()
        conn.commit()
        
        return {
            "id": lectura_id,
            "sensor_id": lectura['sensor_id'],
            "valor": lectura['valor'],
            "timestamp": timestamp.isoformat()
        }
    except Exception as e:
        return {"status": -1, "message": f"Error de conexión: {e}"}
    finally:
        conn.close()
        
def fetch_plantes() -> List[Dict[str, Any]]:
    try:
        conn = db_client()
        cur = conn.cursor()
        
        query = "SELECT id, nom, sensor_id FROM planta"
        cur.execute(query)
        plantes = cur.fetchall()
        
        return [{
            "id": p[0],
            "nom": p[1],
            "sensor_id": p[2]
        } for p in plantes]
    except Exception as e:
        return {"status": -1, "message": f"Error de conexión: {e}"}
    finally:
        conn.close()
        
def create_planta(planta: Dict[str, Any]) -> Dict[str, Any]:
    try:
        conn = db_client()
        cur = conn.cursor()
        
        query = """
            INSERT INTO planta (nom, sensor_id)
            VALUES (%s, %s)
            RETURNING id
        """
        cur.execute(query, (planta['nom'], planta['sensor_id']))
        planta_id = cur.fetchone()[0]
        conn.commit()
        
        return {**planta, "id": planta_id}
    except pymysql.err.IntegrityError as e:
        return {"status": -1, "message": "Sensor ya asociado a otra planta"}
    except Exception as e:
        return {"status": -1, "message": f"Error de conexión: {e}"}
    finally:
        conn.close()