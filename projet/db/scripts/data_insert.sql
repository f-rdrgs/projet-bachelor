-- COPY ressource(label,description)
-- FROM '/data/ressource.csv'
-- WITH (FORMAT csv);


COPY jour_horaire(jour,debut,fin)
FROM '/data/horaire.csv'
WITH (FORMAT csv, HEADER);