# Vocabulaire du mémoire : à savoir expliquer simplement

Un mot, ce qu'il veut dire, et une phrase toute prête si le jury le demande.

---

## Architecture et back-end

**Microservice** : un petit programme indépendant qui gère un seul domaine (paiement, rendez-vous…). Chacun a sa base de données.
→ « Si le paiement tombe en panne, les rendez-vous continuent de fonctionner. »

**API Gateway (passerelle)** : la porte d'entrée unique. L'application ne parle qu'à elle, et elle transmet au bon service.
→ « Elle ne fait que router, elle ne vérifie pas le jeton. »

**Eureka** : l'annuaire des services. Chaque service s'y inscrit, et la passerelle y cherche où envoyer la requête.

**JWT** : un jeton signé que reçoit l'utilisateur à la connexion (identifiant, rôle, expiration 24 h). Il l'envoie à chaque requête.

**Stateless (sans état)** : le serveur ne garde pas de session en mémoire. Tout ce qu'il faut savoir est dans le jeton.

**Retry / circuit breaker (disjoncteur)** : retry = on réessaie un appel qui a échoué (3 fois). Disjoncteur = après trop d'échecs, on arrête d'appeler un service en panne pendant un moment, pour ne pas tout bloquer.

**Zipkin / trace** : chaque action reçoit un identifiant qui suit tous les appels entre services. On voit le chemin complet d'une requête.

**Polling** : l'application redemande régulièrement au serveur s'il y a du nouveau (messages). Ce n'est pas du vrai temps réel.
→ Évolution possible : WebSocket, où le serveur pousse les messages.

**ORM / JPA / Hibernate** : on manipule des objets Java, et l'outil écrit les requêtes SQL à notre place.

**ddl-auto=update** : Hibernate crée ou met à jour les tables au démarrage. Pratique en développement, déconseillé en production (on utiliserait Flyway ou Liquibase).

**ACID** : les garanties d'une base de données. Une opération se fait entièrement ou pas du tout, et les données restent cohérentes.

**Saga / compensation** : quand une opération touche plusieurs services, on ne peut pas faire une seule transaction. Si une étape échoue, on annule les précédentes. Dans PsyConnect : si le paiement n'est pas enregistré après le débit, le solde est recrédité. C'est une compensation simple, pas une saga complète.

**Conteneur / Docker Compose / health check** : un conteneur emballe un service avec tout ce dont il a besoin. Compose les lance tous ensemble. Le health check vérifie qu'un service est prêt avant de démarrer ceux qui en dépendent.

**HTTP / HTTPS / TLS** : HTTPS = HTTP chiffré grâce à TLS. Le prototype tourne en HTTP en local, HTTPS est prévu pour la production.

## IA et recommandation

**LLM** : grand modèle de langage, une IA qui génère du texte. Xalaat utilise Qwen2.5 (3 milliards de paramètres) qui tourne sur le serveur, via Ollama.

**Garde-fou pré-LLM** : un filtre qui lit le message AVANT l'IA. S'il contient une expression de détresse, il répond directement avec les numéros d'urgence, sans appeler le modèle.

**TF-IDF** : une façon de transformer un texte en liste de nombres. Les mots fréquents dans un texte mais rares ailleurs pèsent plus lourd.

**Similarité cosinus** : mesure à quel point deux de ces listes de nombres « pointent dans la même direction », donc à quel point deux textes se ressemblent (de 0 à 1).

**Score de recommandation** : 0,6 × ressemblance + 0,25 × note/5 + 0,15 × même ville. Poids fixés empiriquement.

**Filtrage vectoriel / par contenu** : recommander à partir du contenu (le besoin du patient, le profil du psy), pas à partir de ce qu'ont fait d'autres utilisateurs.

**Polyglotte** : un système qui mélange plusieurs langages (ici Java et Python).

## Vidéo

**WebRTC** : la technologie standard de vidéo en temps réel dans les navigateurs et les applications. Je ne l'ai pas codée : Jitsi Meet l'utilise en interne.

**NAT / TURN / coturn** : derrière une box ou un réseau mobile, deux téléphones n'arrivent pas toujours à se connecter directement. Un serveur TURN (coturn) sert alors de relais. C'est une perspective si l'infrastructure publique de Jitsi ne suffit pas.

## Modélisation

**BPMN** : une notation pour dessiner un processus métier réel (ici, le parcours actuel sans PsyConnect).

**Include / extend** : include = étape toujours faite. Extend = prolongement optionnel ou sous condition.

**Précondition / postcondition** : ce qui doit être vrai avant le cas d'utilisation / ce qui est vrai après.

## Mots de français soutenu dans le mémoire

**Suivi longitudinal** : suivre un patient dans la durée, séance après séance.
**De facto** : dans les faits.
**Jalonner** : marquer les étapes d'un parcours.
**Somatique** : qui concerne le corps (par opposition au psychique).
**Pseudonymat** : utiliser un faux nom (pseudonyme) à la place du vrai.

## Petits détails qu'on peut te demander

**Apostrophes du clavier iOS** : l'iPhone tape ’ (apostrophe courbe) au lieu de ' (droite). Le filtre de Xalaat reconnaît les deux, sinon « j’en peux plus » passerait à travers.

**Numéro vert 800 00 50 50** : le numéro vert des autorités sanitaires, connu depuis le Covid-19. Il n'existe pas de ligne dédiée à la santé mentale : le plan stratégique 2024–2028 le relève [13].

**Loi n° 2008-12 / CDP** : la loi sénégalaise sur les données personnelles, et la Commission qui la fait appliquer. Les données de santé sont des données sensibles.

**PWA** : un site web qui s'utilise comme une application, sans passer par l'App Store.
