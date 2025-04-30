from typing import List, Optional, Dict
from collections import defaultdict
from fastapi import FastAPI, HTTPException
import mysql.connector
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from client import db_client

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class Usuari(BaseModel):
    id: int
    nom: str
    cognom: str
    email: str
    contrasenya: Optional[str] = None

class Sensor(BaseModel):
    sensor_id: int
    estat: str = "Actiu"
    usuari_id: Optional[int] = None

class Planta(BaseModel):
    id: int
    nom: str
    ubicacio: str
    sensor_id: int
    usuari_id: Optional[int] = None
    
class Lectura(BaseModel):
    id: Optional[int] = None
    sensor_id: int
    valor: float
    timestamp: Optional[datetime] = None

class UsuariCreate(BaseModel):
    nom: str
    cognom: str
    email: str
    contrasenya: str

class SensorCreate(BaseModel):
    sensor_id: int
    estat: Optional[str] = "Actiu"
    usuari_id: Optional[int] = None

class PlantaCreate(BaseModel):
    id: int
    nom: str
    ubicacio: str
    sensor_id: int
    usuari_id: Optional[int] = None

class LecturaCreate(BaseModel):
    sensor_id: int
    valor: float

# Endpoints
@app.get("/")
def read_root():
    return {"ECOSENSE API"}

# Usuarios Endpoints
@app.post("/usuaris/", response_model=Usuari)
def crear_usuari(usuari: UsuariCreate):
    db = db_client()    
    cursor = db.cursor(dictionary=True)
    try:
        query = """
        INSERT INTO usuaris (nom, cognom, email, contrasenya)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (usuari.nom, usuari.cognom, usuari.email, usuari.contrasenya))
        db.commit()
        user_id = cursor.lastrowid
        cursor.execute("SELECT * FROM usuaris WHERE id = %s", (user_id,))
        return cursor.fetchone()
    except mysql.connector.Error as err:
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        cursor.close()
        db.close()

@app.get("/usuaris/", response_model=List[Usuari])
def listar_usuaris():
    db = db_client()    
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, nom, cognom, email FROM usuaris")
        return cursor.fetchall()
    finally:
        cursor.close()
        db.close()

@app.get("/usuaris/{usuari_id}", response_model=Usuari)
def obtenir_usuari(usuari_id: int):
    db = db_client()    
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, nom, cognom, email FROM usuaris WHERE id = %s", (usuari_id,))
        usuari = cursor.fetchone()
        if not usuari:
            raise HTTPException(status_code=404, detail="Usuari no trobat")
        return usuari
    finally:
        cursor.close()
        db.close()

# Sensores Endpoints
@app.post("/sensors/", response_model=Sensor)
def crear_sensor(sensor: SensorCreate):
    db = db_client()    
    cursor = db.cursor(dictionary=True)
    try:
        query = """
        INSERT INTO sensors (sensor_id, estat, usuari_id)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (sensor.sensor_id, sensor.estat, sensor.usuari_id))
        db.commit()
        cursor.execute("SELECT * FROM sensors WHERE sensor_id = %s", (sensor.sensor_id,))
        return cursor.fetchone()
    except mysql.connector.Error as err:
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        cursor.close()
        db.close()

@app.get("/sensors/{sensor_id}", response_model=Sensor)
def get_sensor_data(sensor_id: int):
    db = db_client()    
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM sensors WHERE sensor_id = %s", (sensor_id,))
        sensor = cursor.fetchone()
        if not sensor:
            raise HTTPException(status_code=404, detail="Sensor no encontrado")
        return sensor
    finally:
        cursor.close()
        db.close()

@app.get("/sensors/")
def get_sensors():
    db = db_client()
    if isinstance(db, dict):  # Si hay error
        raise HTTPException(status_code=500, detail=db["message"])
        
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM sensors")
        return cursor.fetchall()
    finally:
        cursor.close()
        db.close()

@app.put("/sensors/{sensor_id}", response_model=Sensor)
def actualitzar_sensor(sensor_id: int, sensor: SensorCreate):
    db = db_client()    
    cursor = db.cursor(dictionary=True)
    try:
        query = """
        UPDATE sensors 
        SET estat = %s, usuari_id = %s 
        WHERE sensor_id = %s
        """
        cursor.execute(query, (sensor.estat, sensor.usuari_id, sensor_id))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Sensor no encontrado")
        db.commit()
        cursor.execute("SELECT * FROM sensors WHERE sensor_id = %s", (sensor_id,))
        return cursor.fetchone()
    except mysql.connector.Error as err:
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        cursor.close()
        db.close()

@app.delete("/sensors/{sensor_id}")
def eliminar_sensor(sensor_id: int):
    db = db_client()    
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("DELETE FROM sensors WHERE sensor_id = %s", (sensor_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Sensor no encontrado")
        db.commit()
        return {"message": "Sensor eliminat correctament"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        cursor.close()
        db.close()

# Lecturas Endpoints
@app.post("/lectures/", response_model=Lectura)
def crear_lectura(lectura: LecturaCreate):
    db = db_client()    
    cursor = db.cursor(dictionary=True)
    try:
        query = """
        INSERT INTO humitat_sol (sensor_id, valor)
        VALUES (%s, %s)
        """
        cursor.execute(query, (lectura.sensor_id, lectura.valor))
        db.commit()
        lectura_id = cursor.lastrowid
        cursor.execute("SELECT * FROM humitat_sol WHERE id = %s", (lectura_id,))
        return cursor.fetchone()
    except mysql.connector.Error as err:
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        cursor.close()
        db.close()

@app.get("/lectures/", response_model=List[Lectura])
def listar_lectures(
    sensor_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100
):
    db = db_client()    
    cursor = db.cursor(dictionary=True)
    try:
        query = "SELECT * FROM humitat_sol"
        params = []
        conditions = []
        
        if sensor_id:
            conditions.append("sensor_id = %s")
            params.append(sensor_id)
        
        if start_date:
            conditions.append("timestamp >= %s")
            params.append(start_date)
        
        if end_date:
            conditions.append("timestamp <= %s")
            params.append(end_date)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY timestamp DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    finally:
        cursor.close()
        db.close()

# Plantas Endpoints
@app.post("/plantes/", response_model=Planta)
def crear_planta(planta: PlantaCreate):
    db = db_client()    
    cursor = db.cursor(dictionary=True)
    try:
        query = """
        INSERT INTO planta (id, nom, ubicacio, sensor_id, usuari_id)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            planta.id, 
            planta.nom, 
            planta.ubicacio,
            planta.sensor_id,
            planta.usuari_id
        ))
        db.commit()
        cursor.execute("SELECT * FROM planta WHERE id = %s", (planta.id,))
        return cursor.fetchone()
    except mysql.connector.Error as err:
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        cursor.close()
        db.close()

@app.get("/plantes/", response_model=List[Planta])
def listar_plantes():
    db = db_client()    
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM planta")
        return cursor.fetchall()
    finally:
        cursor.close()
        db.close()
        
class PlantasPorZonaResponse(BaseModel):
    zona: str
    plantas: List[Planta]

@app.get("/plantes/por-zones", response_model=List[PlantasPorZonaResponse])
def get_plantas_agrupadas_por_zones(usuari_id: int):
    db = db_client()
    if isinstance(db, dict):
        raise HTTPException(status_code=500, detail=db["message"])
    
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id, nom, ubicacio, sensor_id, usuari_id 
            FROM planta
            WHERE usuari_id = %s
            ORDER BY ubicacio, nom
        """, (usuari_id,))
        
        plantas = cursor.fetchall()
        
        # Agrupar por zona
        plantas_por_zona = defaultdict(list)
        for planta in plantas:
            plantas_por_zona[planta['ubicacio']].append(planta)
            
        # Convertir a la estructura de respuesta
        return [
            {"zona": zona, "plantas": plantas}
            for zona, plantas in plantas_por_zona.items()
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()

@app.get("/plantes/{planta_id}", response_model=Planta)
def obtenir_planta(planta_id: int):
    db = db_client()    
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM planta WHERE id = %s", (planta_id,))
        planta = cursor.fetchone()
        if not planta:
            raise HTTPException(status_code=404, detail="Planta no trobada")
        return planta
    finally:
        cursor.close()
        db.close()

@app.put("/plantes/{planta_id}", response_model=Planta)
def actualitzar_planta(planta_id: int, planta: PlantaCreate):
    db = db_client()    
    cursor = db.cursor(dictionary=True)
    try:
        query = """
        UPDATE planta 
        SET nom = %s, ubicacio = %s, sensor_id = %s, usuari_id = %s
        WHERE id = %s
        """
        cursor.execute(query, (
            planta.nom,
            planta.ubicacio,
            planta.sensor_id,
            planta.usuari_id,
            planta_id
        ))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Planta no encontrada")
        db.commit()
        cursor.execute("SELECT * FROM planta WHERE id = %s", (planta_id,))
        return cursor.fetchone()
    except mysql.connector.Error as err:
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        cursor.close()
        db.close()

@app.delete("/plantes/{planta_id}")
def eliminar_planta(planta_id: int):
    db = db_client()    
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("DELETE FROM planta WHERE id = %s", (planta_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Planta no encontrada")
        db.commit()
        return {"message": "Planta eliminada correctament"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        cursor.close()
        db.close()
        