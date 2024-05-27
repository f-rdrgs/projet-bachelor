COPY ressource(label,description)
FROM '/data/ressource_temp.csv'
WITH (FORMAT csv, HEADER);COPY jour_horaire(jour,debut,fin,label)
FROM '/data/horaire_temp.csv'
WITH (FORMAT csv, HEADER);