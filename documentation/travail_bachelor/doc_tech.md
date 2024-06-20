# Documentation Technique

(Ce fichier est temporaire et sert à rédiger sans prendre en compte la forme)

## Architecture Générale

![architecture diagram](./Architecture.png)

## Composants

- Postgresql

### Base de données

#### Diagramme relationnel

Afin de pouvoir enregistrer les divers informations en lien avec des réservations, une base de données Postgresql est disponible.

![](../../projet/db/documentation/db.png)

Lors de l'initialisation du Bot, à l'aide d'un script fournit, il est possible de remplir aisément les tables nécessaires au fonctionnement de l'application : 

1. jour_horaire: Contient les heures de début-fin par tranches d'heure pour une ressource donnée
2. ressource: Un nom de ressource avec une description optionnellement
3. options_resource: Associe une option et description a une ressource
4. options_resource_choix: Associe un choix à une option

Par la suite, les tables suivantes sont régulièrement utilisées pour réserver une ressource :

1. reservation: Contient les informations du client ayant effectué une réservation
2. reservations_client_resource: Définit quelle ressource a été réservée, à quelle heure/date et associé à quelle réservation
3. reservations_client_choix: Enregistre, si la ressource choisie en possède, les choix effectués lors de la réservation par le client
4. temp_reservation: Lorsqu'un client est en train de réserver, la ressource à la date et heure donnée seront pré-réservées pendant un temps limité afin d'éviter des réservations simultanées

#### Script d'insertion de données



### API

- FastAPI
- Uvicorn
- SQLAlchemy

L'API est un des composants centraux avec lequel l'utilisateur va communiquer et qui permet de faire le lien entre la base de données, le chatbot Rasa et l'utilisateur. Pour se faire, une multitude de routes sont disponibles :



Afin de simplifier les interactions avec la base de donnée depuis l'API, SQLAlchemy est employé pour mettre en place une couche d'ORM (Object-relational-mapping) qui en quelques mots permet d'éviter de devoir rédiger chaque requête manuellement et de simplement utiliser des fonctions d'objet de manière chaînées pour les requêtes.

Un exemple : 
```python
query = session.query(Jour_Horaire.jour).where(Jour_Horaire.label.like(ressource_label)).where(Jour_Horaire.debut <= heure).where(Jour_Horaire.fin>=heure).distinct().all()
```

Serait équivalent à :

```sql
SELECT DISTINCT jour FROM Jour_Horaire WHERE label like ressource_label AND debut <= heure AND fin >= heure
```

Bien que la requête soit plus longue avec de l'ORM, elle est plus rapide à écrire et bien plus facilement modulable que de devoir changer manuellement un string contenant la requête SQL

De plus, si l'on souhaite ajouter un nouvel élément dans la table, on peut faire usage des classes créées au préalable pour ajouter très facilement une nouvelle réservation par exemple : 

```python
class Reservation(Base):
    __tablename__ = 'reservation'
    id = Column(Integer(),primary_key=True,autoincrement="auto")
    nom = Column(VARCHAR(),nullable=False)
    prenom = Column(VARCHAR(),nullable=False)
    numero_tel = Column(VARCHAR(),nullable=False)
    date_reservation = Column(TIMESTAMP(),nullable=False)
    
new_reservation = Reservation(nom=data.nom,prenom=data.prenom,numero_tel=data.numero_tel,date_reservation=datetime.datetime.now(ZoneInfo('Europe/Paris')),)
with Session.begin() as session:
    session.add(new_reservation)
    session.flush()
    session.refresh(new_reservation)
```

Ci-dessus, on voit donc qu'il ne suffit que de créer une nouvelle instance de l'objet réservation, la remplir et ensuite l'ajouter à la base de données. Le `flush` et `refresh` permettent simplement d'immédiatement effectuer la requête et de mettre à jour l'objet local new_reservation en mettant à jour l'ID nouvellement affecté par la base de données.

### Rasa

#### Rasa core

#### Rasa action server