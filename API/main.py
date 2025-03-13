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

@app.get("/")
def read_root():
    return {"ECOSENSE API"}

@app.get("/usuaris/{id}", response_model=Usuari)
def read_usuari_id(id: int):
    usuari_data = db_assistencia.fetch_usuari_by_id(id)
    if not usuari_data or "status" in usuari_data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuari_data

# Nuevos endpoints para sensores
@app.get("/sensors/{sensor_id}")
def get_sensor_data(sensor_id: int):
    sensor_data = db_assistencia.fetch_sensor_data(sensor_id)
    if not sensor_data or "status" in sensor_data:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    return sensor_data

@app.get("/alertes")
def get_ultimes_alertes(limit: int = 10):
    return db_assistencia.fetch_recent_alertes(limit)

@app.get("/humitats")
def get_ultimes_lectures(limit: int = 10):
    return db_assistencia.fetch_recent_humitats(limit)