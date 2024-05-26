COPY jour_horaire(jour,debut,fin)
FROM '/data/horaire_temp.csv'
WITH (FORMAT csv, HEADER);COPY ressource(label,description)
FROM '/data/ressource_temp.csv'
WITH (FORMAT csv, HEADER);