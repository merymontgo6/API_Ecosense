from ast import List
from fastapi import FastAPI, HTTPException
import db_assistencia
from typing import Optional
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Usuari(BaseModel):
    id: int
    nom: str
    cognom: str
    email: str
    contrasenya: str
class Sensor(BaseModel):
    id: int
    ubicacio: str
    planta: str
    estat: str
class Planta(BaseModel):
    id: int
    nom: str
    sensor_id: int
    
class Lectura(BaseModel):
    id: int
    sensor_id: int
    valor: float
    timestamp: str



@app.get("/")
def read_root():
    return {"ECOSENSE API"}

@app.post("/usuaris/", response_model=Usuari)
def crear_usuari(usuari: Usuari):
    try:
        new_usuari = db_assistencia.create_usuari(usuari)
        return new_usuari
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/usuaris/", response_model=List[Usuari])
def listar_usuaris():
    return db_assistencia.fetch_usuaris()

@app.get("/usuaris/{usuari_id}", response_model=Usuari)
def obtenir_usuari(usuari_id: int):
    usuari = db_assistencia.fetch_usuari_by_id(usuari_id)
    if not usuari:
        raise HTTPException(status_code=404, detail="Usuari no trobat")
    return usuari

@app.post("/sensors/", response_model=Sensor)
def crear_sensor(sensor: Sensor):
    try:
        new_sensor = db_assistencia.create_sensor(sensor)
        return new_sensor
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/sensors/{sensor_id}")
def get_sensor_data(sensor_id: int):
    sensor_data = db_assistencia.fetch_sensor_data(sensor_id)
    if not sensor_data or "status" in sensor_data:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    return sensor_data

@app.get("/sensors/", response_model=List[Sensor])
def listar_sensors(planta: Optional[str] = None):
    return db_assistencia.fetch_sensors(planta)

@app.put("/sensors/{sensor_id}", response_model=Sensor)
def actualitzar_sensor(sensor_id: int, sensor: Sensor):
    try:
        updated_sensor = db_assistencia.update_sensor(sensor_id, sensor)
        return updated_sensor
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/sensors/{sensor_id}")
def eliminar_sensor(sensor_id: int):
    try:
        db_assistencia.delete_sensor(sensor_id)
        return {"message": "Sensor eliminat correctament"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
        
@app.post("/lectures/", response_model=Lectura)
def crear_lectura(lectura: Lectura):
    try:
        new_lectura = db_assistencia.create_lectura(lectura)
        return new_lectura
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/lectures/", response_model=List[Lectura])
def listar_lectures(
    sensor_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100
):
    return db_assistencia.fetch_lectures(sensor_id, start_date, end_date, limit)

@app.post("/plantes/", response_model=Planta)
def crear_planta(planta: Planta):
    try:
        new_planta = db_assistencia.create_planta(planta)
        return new_planta
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/plantes/", response_model=List[Planta])
def listar_plantes():
    return db_assistencia.fetch_plantes()

@app.get("/plantes/{planta_id}", response_model=Planta)
def obtenir_planta(planta_id: int):
    planta = db_assistencia.fetch_planta_by_id(planta_id)
    if not planta:
        raise HTTPException(status_code=404, detail="Planta no trobada")
    return planta

@app.put("/plantes/{planta_id}", response_model=Planta)
def actualitzar_planta(planta_id: int, planta: Planta):
    try:
        updated_planta = db_assistencia.update_planta(planta_id, planta)
        return updated_planta
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/plantes/{planta_id}")
def eliminar_planta(planta_id: int):
    try:
        db_assistencia.delete_planta(planta_id)
        return {"message": "Planta eliminada correctament"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# Funciones de base de datos (db_assistencia.py)
"""
def create_usuari(usuari: Usuari) -> Usuari:
    # Implementar inserción en base de datos
    pass

def fetch_usuaris() -> List[Usuari]:
    # Implementar consulta de todos los usuarios
    pass

def fetch_usuari_by_id(usuari_id: int) -> Optional[Usuari]:
    # Implementar consulta de usuario por ID
    pass

def create_sensor(sensor: Sensor) -> Sensor:
    # Implementar inserción en base de datos
    pass

def fetch_sensors(planta: Optional[str] = None) -> List[Sensor]:
    # Implementar consulta con filtro opcional por planta
    pass

def update_sensor(sensor_id: int, sensor: Sensor) -> Sensor:
    # Implementar actualización de sensor
    pass

def delete_sensor(sensor_id: int):
    # Implementar eliminación de sensor
    pass

def create_lectura(lectura: Lectura) -> Lectura:
    # Implementar inserción de nueva lectura
    pass

def fetch_lectures(sensor_id, start_date, end_date, limit) -> List[Lectura]:
    # Implementar consulta de lecturas con filtros
    pass

def create_planta(planta: Planta) -> Planta:
    # Implementar inserción de nueva planta
    pass

def fetch_plantes() -> List[Planta]:
    # Implementar consulta de todas las plantas
    pass

def fetch_planta_by_id(planta_id: int) -> Optional[Planta]:
    # Implementar consulta de planta por ID
    pass

def update_planta(planta_id: int, planta: Planta) -> Planta:
    # Implementar actualización de planta
    pass

def delete_planta(planta_id: int):
    # Implementar eliminación de planta
    pass
"""