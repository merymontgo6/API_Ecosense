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
        "id": sensor[0],
        "ubicacio": sensor[1],
        "planta": sensor[2],
        "estat": sensor[3],
        "limit_humitat": sensor[4]
    }

def humitat_sol_schema(humitat) -> dict:
    return {
        "id": humitat[0],
        "sensor_id": humitat[1],
        "valor": humitat[2],
        "timestamp": humitat[3]
    }
    
def alerta_schema(alerta) -> dict:
    return {
        "id": alerta[0],
        "sensor_id": alerta[1],
        "timestamp": alerta[2],
        "valor": alerta[3],
        "tipus": alerta[4]
    }

def usuaris_schema(usuaris) -> list[dict]:
    return [usuari_schema(usuari) for usuari in usuaris]

def sensors_schema(sensors) -> list[dict]:
    return [sensor_schema(sensor) for sensor in sensors]

def humitats_sol_schema(humitats) -> list[dict]:
    return [humitat_sol_schema(humitat) for humitat in humitats]

def alertes_schema(alertes) -> list[dict]:
    return [alerta_schema(alerta) for alerta in alertes]