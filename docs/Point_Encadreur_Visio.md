# Point avec M. Touré — visio de 30 minutes

À garder ouvert à côté de la visio. Les phrases en italique sont à dire avec tes mots, pas à lire.

## La veille

- Enregistrer la démo en vidéo (3 à 4 min, enregistrement d'écran du Mac). Si Docker lâche pendant l'appel, tu la partages et tu continues.
- Faire le parcours de démo une fois en entier, avec les deux comptes.
- Préparer deux comptes avec des données propres : un patient (avec un RDV passé et un PHQ-9 rempli) et un psy validé.
- Ouvrir à l'avance le schéma d'architecture (slide « carte du système » de la présentation).

## Le jour J, 20 minutes avant

1. Fermer Laravel (`artisan serve`) et Expo : ils prennent les ports 8000 et 8081.
2. `cd ~/Desktop/MASTER-2/Memory/PsyConnect` puis `docker compose up -d`
3. Lancer `ollama serve` pour Xalaat.
4. Attendre que http://localhost:8761 affiche les 8 services, puis se connecter une fois avec chaque compte.
5. Couper les notifications du Mac, fermer les onglets inutiles avant de partager l'écran.

## Déroulé

**0–3 min · Où j'en suis**

*Merci d'avoir pris le temps. L'application est terminée et fonctionne de bout en bout. Depuis septembre je n'ajoute plus de fonctionnalités : je travaille la rédaction du mémoire et la préparation de la soutenance, visée pour décembre ou janvier.*

**3–15 min · Démo, un seul parcours**

1. Le patient se connecte, l'accueil lui propose des psychologues recommandés.
2. Il ouvre une fiche et réserve un créneau.
3. Il paie avec son solde (recharge Wave / Orange Money simulée).
4. Côté psy : il accepte le rendez-vous.
5. La séance en visio (un seul salon Jitsi pour les deux).
6. Le patient remplit un PHQ-9, le psy voit le score et l'évolution.
7. Pour finir, une minute sur Xalaat : *si le message parle de crise, il est intercepté avant même d'arriver au modèle, et la personne est orientée vers une aide humaine.*

Si une étape plante : ne pas déboguer en direct. *Je vous montre la vidéo de cette partie* et on avance.

**15–20 min · L'architecture en une image**

*Neuf services Java et un service Python. La passerelle est le point d'entrée, Eureka sert d'annuaire. Chaque service vérifie lui-même le jeton. Si un service secondaire tombe, l'essentiel continue : une notification perdue n'annule pas un rendez-vous.*

Trois raisons du choix microservices, si il demande pourquoi :
- deux langages dans le même système (la recommandation est en Python) ;
- une panne n'a pas le même effet partout (tomber en marche ou tomber fermé selon l'enjeu) ;
- j'ai pu sortir le paiement dans son propre service en cours de projet sans toucher au reste.

**20–27 min · Ce dont j'ai besoin de vous**

1. **Le professionnel.** *Je n'ai pas encore réussi à avoir un psychologue. Je compte contacter le service de psychologie de l'UCAD et le CHU de Fann. Est-ce que vous connaissez quelqu'un qui accepterait de tester l'application ou d'échanger 30 minutes avec moi ?*
2. **Le mémoire.** *Est-ce que je peux vous envoyer le plan, ou la version actuelle, pour avoir votre avis avant de finaliser ?*
3. **Le calendrier.** Date limite de dépôt, période de soutenance, ce qu'il attend d'ici là.

**27–30 min · Suite**

Redire en une phrase ce qui est décidé, et proposer la date du prochain point. Après l'appel, lui envoyer un court message récapitulatif le jour même.

## Ce qu'il risque de demander

**« Vous avez contacté un professionnel ? »**
Non, pas encore. Dire où tu comptes chercher et lui demander un contact. Ne pas inventer de démarche.

**« Pourquoi les microservices et pas une application classique ? »**
Les trois raisons ci-dessus. Ne pas dire « pour la sécurité » : plus de services, c'est plus de surface à protéger.

**« Le paiement est réel ? »**
Non, simulé. Wave et Orange Money demandent un contrat marchand. L'architecture est prête : le paiement est isolé dans son service, il suffirait de brancher l'API de l'opérateur.

**« Et les données de santé, la confidentialité ? »**
Mode anonyme avec pseudonyme côté backend, notes cliniques visibles par le seul psy qui les écrit, un psy ne peut suivre un patient qu'après un rendez-vous accepté. Tu as aussi audité ta propre sécurité et corrigé deux failles hautes en septembre (fil 04).

**« Qu'est-ce qui manque encore ? »**
Le dire toi-même : paiement simulé, pas de tests automatisés côté Flutter, jetons non révocables avant expiration, pas de déploiement en ligne. *Ce sont des limites assumées, notées dans les perspectives.*

**« La partie IA, c'est de l'apprentissage ? »**
La recommandation, non : c'est de la similarité de contenu (TF-IDF et cosinus). Xalaat utilise un modèle de langage local via Ollama, encadré par un garde-fou qui passe avant le modèle.

## Pour réviser vite

Fils rouges dans l'ordre : 03 Réservation, 10 Xalaat, 04 Paiement. Les réponses complètes sont dans `redact/Questions_Reponses_Jury.md`.
