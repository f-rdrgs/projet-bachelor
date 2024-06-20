COPY ressource(label,description)
FROM '/data/ressource_temp.csv'
WITH (FORMAT csv, HEADER);
COPY jour_horaire(jour,debut,fin,temps_reservation,label)
FROM '/data/horaire_temp.csv'
WITH (FORMAT csv, HEADER);
COPY options_resource(label_resource, label_option, description)
FROM '/data/options_temp.csv'
WITH (FORMAT csv, HEADER);
COPY options_resource_choix(label_option,choix)
FROM '/data/options_choix_temp.csv'
WITH (FORMAT csv, HEADER);
