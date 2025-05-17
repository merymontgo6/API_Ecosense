# API_Ecosense
## API per l'aplicació mòbil
## Fet per Karolayn Muñoz

### Endpoints de l'API
L’API proporciona els següents endpoints:

![alt text](images/image.png)

- GET /

Aquest es per saber ja de principi el funcionament d'un endpoint de prova.

![alt text](images/image2.png)

- GET /usuaris/

Aquest endpoint mostra tos els usuaris que hi ha a la base de dades. En aquest cas no es mostra la contrasenya ja que està hasheada a la base de dades.

![alt text](images/image3.png)

- GET /usuaris/{usuari_id}

Aquest endpoint mostra només l'usuari que es troba per l'id que es passa com a paràmetre.

![alt text](images/image4.png)

- POST /usuaris/login

Aquest és un endpoint d'ajuda per tal de processar un login més segur, llavors se l'ha de passar tota la informació, i si coincideixen é´s perquè existeix i es pot fer un inici de sessió. Torna missatge de SUCCESS = TRUE.

![alt text](images/image5.png)

- POST /usuaris/registre

Aquest endpoint crea un nou usuari i l'insereix a la base de dades, si tot és correcte mostra missatge de SUCCESS = TRUE.

![alt text](images/image6.png)

- GET /sensors/

Aquest endpoint mostra tots els sensors i el seu estat dins de la base de dades.

![alt text](images/image7.png)

- GET /sensors/{sensor_id}

Aquest endpoint mostra només el sensor que es va demanar pel seu id.

![alt text](images/image8.png)

- PUT /sensors/{sensor_id}

Abans de la modificació:

![alt text](images/image9.png)

Després de la modificació: 

![alt text](images/image10.png)

- DELETE /sensors/{sensor_id}

Abans d'eliminar:

![alt text](images/image11.png)

Després d'eliminar:

![alt text](images/image12.png)

- GET /lectures/

En aquest endpoint només és obligatori inserir l'id del sensor, pero les dades són opcionals ja que la informació apareix per id. Mostra les dades de les lectures de l'humetat del sensor.

![alt text](images/image13.png)

- GET /humitat/{sensor_id}

Aquest endpoint només mostra el valor de la humitat d'un sensor en especific. Es va afegir per fer el procés de recollida de dades essencials més ràpid i efectiu.

![alt text](images/image14.png)

- GET /plantes/

Aquest endpoint mostra totes les plantes que hi ha a la base de dades.

![alt text](images/image15.png)

- POST /plantes/

En aquest enpoint s'afegeix una planta a la base de dades, és obligatori inserir id d'usuari i sensor que ja existeixen, o s'han de crear per afegir-los.

![alt text](images/image16.png)

- GET /plantes/por-zones

Aquest endpoint és similar al de mostrar totes les plantes, però aquest les mostra agrupades per zones, és a dir, surten en conjunt per la seva ubicació.

Aquest és un endpoint pensat especificament per poder mostrar les plantes per usuari filtrades per zones a l'aplicació mòbil.

![alt text](images/image17.png)

- GET /plantes/{planta_id}

Aquest endpoint mostra totes les dades d'una planta per el seu id.

![alt text](images/image18.png)

- PUT /plantes/{planta_id}

En aquest endpoint es pot modificar les dades d'una planta pel seu id.

![alt text](images/image19.png)

- DELETE /plantes/{planta_id}

Aquest endpoint elimina una planta per el seu id, si s'elimina correctament torna un missatge de confirmació.

![alt text](images/image20.png)

- GET /plantes/complet/{planta_id}

Aquest endpoint retorna tota la informació relacionada a una planta, és a dir, no només els camps de la taula planta si no que també el seu sensor, la seva humitat que son d'altre taules diferents.

![alt text](images/image21.png)

A més, es van fer Schemas per a cada necessitat, estàn personalitzats per tal de poder mostrar i tornar només la informació que es desea a l'endpoint. Això es va fer per tal de fer mmillorar i que sigui més ràpida l'obtenció de dades.

![alt text](images/image22.png)