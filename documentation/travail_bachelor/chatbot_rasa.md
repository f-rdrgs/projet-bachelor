# Chatbot Rasa

[toc]

## Intents

1. Ressource (Dans le cas d'une salle de sport : Tennis, Badminton, Pétanque, Squash, Ping-pong, etc.)
2. Date réservation
3. Heure réservation
4. Nom
5. Prénom
6. Email
7. Numéro téléphone
8. Confirmer
9. Annuler
10. Salutation
11. Au revoir

## Stories

### Déroulement général

1. Utilisateur dit bonjour ou effectue une requête comme "Je veux réserver"
2. Le chatbot énonce les horaires disponibles généraux disponibles pour cette ressource
   *Optionnellement proposer 3 horaires très proches de disponible ?*
3. L'utilisateur choisit 1 date et 1 heure (Selon la tranche d'heure définie)
4. **Si l'heure et date convient**
   1. Le bot répète la réservation en demandant une confirmation
   2. L'utilisateur confirme
5. **Si l'heure et date ne conviennent pas (déjà réservé)**
   1. Le bot annonce que la date n'est pas disponible
   2. Le bot propose ensuite 3 dates les plus proches qui le sont ou de choisir une autre date
   3. Si tout est correct, continue
6. Le bot demande des informations telles que Nom, Prénom
7. Le bot demande ensuite le numéro de téléphone ou email
8. Le bot confirme la réservation avec un résumé de cette dernière et potentiellement un mail ou message est envoyé (voir si possible à faire)
9. Fin de l'interaction

