def usuari_schema(usuari) -> dict:
    return {
        "id": usuari[0],
        "nom": usuari[1],
        "cognom": usuari[2],
        "email": usuari[3],
        "contrasenya": usuari[4]
    }
    
def sensor_schema(sensor) -> dict:
    return {
        "sensor_id": sensor[0],
        "estat": sensor[1],
        "usuari_id": sensor[2] if len(sensor) > 2 else None
    }

def humitat_sol_schema(humitat) -> dict:
    return {
        "id": humitat[0],
        "sensor_id": humitat[1],
        "valor": humitat[2],
        "timestamp": humitat[3]
    }

def planta_schema(planta) -> dict:
    return {
        "id": planta[0],
        "nom": planta[1],
        "ubicacio": planta[2],
        "sensor_id": planta[3],
        "usuari_id": planta[4] if len(planta) > 4 else None
    }

def usuaris_schema(usuaris) -> list[dict]:
    return [usuari_schema(usuari) for usuari in usuaris]

def sensors_schema(sensors) -> list[dict]:
    return [sensor_schema(sensor) for sensor in sensors]

def humitats_sol_schema(humitats) -> list[dict]:
    return [humitat_sol_schema(humitat) for humitat in humitats]

def plantes_schema(plantes) -> list[dict]:
    return [planta_schema(planta) for planta in plantes]