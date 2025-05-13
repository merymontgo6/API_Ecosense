from typing import List, Optional, Dict
from collections import defaultdict
from fastapi import FastAPI, HTTPException
import mysql.connector
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from client import db_client
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, field_validator
import re

app = FastAPI()
BASE_URL = "http://192.168.5.206:8000"
#BASE_URL = "http://192.168.17.240:8000"
#BASE_URL = "http://18.213.199.248:8000"
app.mount("/static", StaticFiles(directory="static"), name="static")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
    imagen_url: Optional[str] = None

class PlantaUpdate(BaseModel):
    nom: Optional[str] = None
    ubicacio: Optional[str] = None
    sensor_id: Optional[int] = None
    usuari_id: Optional[int] = None
    imagen_url: Optional[str] = None
    

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

    @field_validator('email')
    def validate_email(cls, v):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", v):
            raise ValueError("El email no tiene un formato válido")
        return v.lower()

    @field_validator('nom', 'cognom')
    def validate_names(cls, v):
        if len(v) < 2:
            raise ValueError("El nom i cognom han de tenir al menys 2 caracters")
        return v.title()

    @field_validator('contrasenya')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("La contrasenya ha de tenir al menys 6 caracters")
        return v

class SensorCreate(BaseModel):
    sensor_id: int
    estat: Optional[str] = "Actiu"
    usuari_id: Optional[int] = None

class PlantaCreate(BaseModel):
    nom: str
    ubicacio: str
    sensor_id: int
    usuari_id: Optional[int] = None
    imagen_url: Optional[str] = None

class LecturaCreate(BaseModel):
    sensor_id: int
    valor: float
    
class HumitatResponse(BaseModel):
    sensor_id: int
    valor: float
    timestamp: datetime
    
class HumitatValorResponse(BaseModel):
    valor: float
    
class RegistreResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    usuari_id: Optional[int] = None
    nom: Optional[str] = None
    email: Optional[str] = None

class LoginResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    usuari_id: Optional[int] = None
    nom: Optional[str] = None
    email: Optional[str] = None


# Endpoints
@app.get("/")
def read_root():
    return {"ECOSENSE API"}

# Usuarios Endpoints

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

@app.post("/usuaris/login", response_model=LoginResponse)
def login_usuario(login_data: dict):
    db = db_client()
    cursor = db.cursor(dictionary=True)
    try:
        email = login_data.get("email")
        contrasenya_plana = login_data.get("contrasenya")
        
        if not email or not contrasenya_plana:
            return {"success": False, "message": "Email y contraseña son requeridos"}
        
        cursor.execute("""SELECT id, nom, cognom, email, contrasenya FROM usuaris WHERE email = %s""", (email,))
        usuario = cursor.fetchone()
    
        if not usuario:
            return {"success": False, "message": "Usuario no encontrado"}
        
        # Intento 1: Verificar con contraseña hasheada
        try:
            if pwd_context.verify(contrasenya_plana, usuario['contrasenya']):
                return {"success": True, "usuari_id": usuario['id'], "nom": usuario['nom'], "email": usuario['email'] }
        except ValueError:
            pass
        
        # Intento 2: Comparación directa para contraseñas antiguas sin hash
        if contrasenya_plana == usuario['contrasenya']:
            # Actualizar la contraseña a formato hasheado
            hashed_password = pwd_context.hash(contrasenya_plana)
            cursor.execute("""UPDATE usuaris SET contrasenya = %s WHERE id = %s""", (hashed_password, usuario['id']))
            db.commit()
            
            return { "success": True, "usuari_id": usuario['id'], "nom": usuario['nom'], "email": usuario['email'] }
        
        # Si ambos intentos fallan
        return { "success": False, "message": "Contrasenya incorrecta" }
        
    except mysql.connector.Error as err:
        return {"success": False, "message": f"Error de base de datos: {str(err)}" }
    finally:
        cursor.close()
        db.close()

@app.post("/usuaris/registre", response_model=RegistreResponse)
def registrar_usuari(usuari: UsuariCreate):
    db = db_client()    
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM usuaris WHERE email = %s", (usuari.email,))
        if cursor.fetchone():
            return {"success": False, "message": "El correu ja existeix"}

        hashed_password = pwd_context.hash(usuari.contrasenya)

        query = """INSERT INTO usuaris (nom, cognom, email, contrasenya) VALUES (%s, %s, %s, %s)"""
        cursor.execute(query, ( usuari.nom, usuari.cognom, usuari.email, hashed_password))
        db.commit()
        
        user_id = cursor.lastrowid
        
        return {"success": True, "message": "Usuari registrat amb éxit", "usuari_id": user_id, "nom": usuari.nom, "email": usuari.email }
        
    except mysql.connector.Error as err:
        db.rollback()
        return {"success": False, "message": f"Error de base de datos: {str(err)}" }
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

@app.get("/humitat/{sensor_id}", response_model=HumitatValorResponse)
def get_humitat_actual(sensor_id: int):
    db = db_client()
    cursor = db.cursor(dictionary=True)
    try:
        # First check if sensor exists
        cursor.execute("SELECT * FROM sensors WHERE sensor_id = %s", (sensor_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Sensor no encontrado")
            
        query = """
        SELECT sensor_id, valor, timestamp 
        FROM humitat_sol 
        WHERE sensor_id = %s 
        ORDER BY timestamp DESC 
        LIMIT 1
        """
        cursor.execute(query, (sensor_id,))
        result = cursor.fetchone()
        
        if not result:
            # Return default values when no data exists
            return {"valor": result["valor"]}
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()
        
# Plantas Endpoints
@app.get("/plantes/", response_model=List[Planta])
def listar_plantes():
    db = db_client()    
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM planta")
        plantas = cursor.fetchall()
        for planta in plantas:
            if not planta.get('imagen_url'):
                planta['imagen_url'] = f"{BASE_URL}/static/plantas/{planta['nom']}.jpg"
        return plantas
    finally:
        cursor.close()
        db.close()
        
@app.post("/plantes/", response_model=Planta)
def crear_planta(planta: PlantaCreate):
    db = db_client()    
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM sensors WHERE sensor_id = %s", (planta.sensor_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail="El sensor especificado no existe")
        
        if planta.usuari_id:
            cursor.execute("SELECT * FROM usuaris WHERE id = %s", (planta.usuari_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=400, detail="El usuario especificado no existe")
        
        query = """
        INSERT INTO planta (nom, ubicacio, sensor_id, usuari_id, imagen_url)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            planta.nom, 
            planta.ubicacio,
            planta.sensor_id,
            planta.usuari_id,
            planta.imagen_url
        ))
        db.commit()
        planta_id = cursor.lastrowid
        
        cursor.execute("SELECT * FROM planta WHERE id = %s", (planta_id,))
        new_planta = cursor.fetchone()
        if not new_planta:
            raise HTTPException(status_code=500, detail="Error al recuperar la planta creada")
            
        return new_planta
    except mysql.connector.Error as err:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(err))
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
            SELECT id, nom, ubicacio, sensor_id, usuari_id, imagen_url 
            FROM planta
            WHERE usuari_id = %s
            ORDER BY ubicacio, nom
        """, (usuari_id,))
        
        plantas = cursor.fetchall()
        
        for planta in plantas:
            if not planta.get('imagen_url'):
                planta['imagen_url'] = f"{BASE_URL}/static/plantas/{planta['nom']}.jpg"
        
        plantas_por_zona = defaultdict(list)
        for planta in plantas:
            plantas_por_zona[planta['ubicacio']].append(planta)
            
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
        
        if not planta.get('imagen_url'):
            planta["imagen_url"] = f"{BASE_URL}/static/plantas/{planta['nom']}.jpg"
        return planta
    finally:
        cursor.close()
        db.close()


@app.put("/plantes/{planta_id}", response_model=Planta)
def actualitzar_planta(planta_id: int, planta: PlantaUpdate):
    db = db_client()    
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM planta WHERE id = %s", (planta_id,))
        current_planta = cursor.fetchone()
        if not current_planta:
            raise HTTPException(status_code=404, detail="Planta no encontrada")
        
        update_data = {
            'nom': planta.nom if planta.nom is not None else current_planta['nom'],
            'ubicacio': planta.ubicacio if planta.ubicacio is not None else current_planta['ubicacio'],
            'sensor_id': planta.sensor_id if planta.sensor_id is not None else current_planta['sensor_id'],
            'usuari_id': planta.usuari_id if planta.usuari_id is not None else current_planta['usuari_id'],
            'imagen_url': planta.imagen_url if planta.imagen_url is not None else current_planta['imagen_url']
        }

        query = """
        UPDATE planta 
        SET nom = %s, ubicacio = %s, sensor_id = %s, usuari_id = %s, imagen_url = %s
        WHERE id = %s
        """
        cursor.execute(query, (
            update_data['nom'],
            update_data['ubicacio'],
            update_data['sensor_id'],
            update_data['usuari_id'],
            update_data['imagen_url'],
            planta_id
        ))
        db.commit()
        cursor.execute("SELECT * FROM planta WHERE id = %s", (planta_id,))
        updated_planta = cursor.fetchone()
        # Ensure image URL exists
        if not updated_planta.get('imagen_url'):
            updated_planta['imagen_url'] = f"{BASE_URL}/static/plantas/{updated_planta['nom']}.jpg"
        return updated_planta
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