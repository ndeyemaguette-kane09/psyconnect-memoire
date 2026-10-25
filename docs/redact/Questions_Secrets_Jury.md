# Questions du jury sur les secrets, et réponses

Fiche préparée le 27/09/2026, après la correction des secrets en clair.
Même principe que les autres fiches : une phrase d'abord, puis tu développes seulement si le jury relance.

---

## Ce qui a été fait, en 30 secondes

Avant : la clé qui signe les jetons de connexion et le mot de passe de la base étaient écrits en dur dans `docker-compose.yml` et dans chaque fichier de configuration, et le tout était publié sur GitHub.

Maintenant :

1. Les secrets sont dans un fichier `.env`, exclu de Git. Le dépôt contient seulement un `.env.example` avec des valeurs à remplacer.
2. Aucune valeur par défaut : si un secret manque, la stack refuse de démarrer, au lieu de tourner avec une clé faible sans prévenir.
3. De nouvelles valeurs aléatoires ont été générées. Les anciennes restent visibles dans l'historique GitHub, mais elles ne servent plus à rien.

---

## Les questions

**« C'est quoi, un secret, dans votre application ? »**
Tout ce qui donne un accès. Dans PsyConnect, il y en a trois : la clé qui signe les jetons de connexion, le mot de passe de la base de données, et le mot de passe du compte administrateur créé au premier démarrage.

**« Où sont-ils stockés ? »**
Dans un fichier `.env` à la racine du projet. Il est exclu de Git, donc il ne part jamais sur le dépôt. Docker Compose le lit au démarrage et transmet les valeurs aux services sous forme de variables d'environnement.

**« Que se passerait-il si la clé des jetons fuitait ? »**
C'est le secret le plus sensible. Avec cette clé, quelqu'un peut fabriquer lui-même un jeton qui dit « je suis administrateur », et tous les services l'accepteraient, sans mot de passe. C'est pour ça qu'il fallait la sortir du code.

**« Votre code est sur GitHub. L'ancienne clé est encore dans l'historique ? »**
Oui, et c'est pour ça que je ne me suis pas contentée de la retirer : j'en ai généré une nouvelle. L'ancienne est visible, mais elle ne signe plus rien. En sécurité, quand un secret a fuité, on ne le cache pas, on le change. On appelle ça une rotation.

**« Comment avez-vous généré la nouvelle clé ? »**
Avec un générateur aléatoire cryptographique (`openssl rand`) : 64 octets, soit 512 bits. Elle est impossible à deviner, contrairement à l'ancienne, qui était une phrase lisible.

**« Et si le fichier `.env` n'est pas là ? »**
La stack refuse de démarrer, avec un message qui dit quel secret manque. C'est voulu : avant, chaque service avait une valeur de secours écrite dans le code. S'il manquait la variable, il démarrait quand même avec la clé publique de GitHub, et personne ne s'en rendait compte.

**« Pourquoi un fichier `.env` et pas un vrai coffre-fort à secrets ? »**
Parce que le projet tourne en local, sur Docker Compose. Le `.env` est la pratique standard à ce niveau. En production, on passerait à un gestionnaire de secrets dédié, comme HashiCorp Vault ou Docker Secrets. L'avantage : les services lisent déjà leurs secrets depuis l'environnement, donc ce changement ne toucherait pas au code.

**« Le `.env` est-il chiffré ? »**
Non, il est en clair sur la machine qui fait tourner l'application. C'est la limite qui reste, et elle est écrite dans le mémoire. Un gestionnaire de secrets la règle : les secrets y sont chiffrés, les accès sont tracés, et on peut changer une clé sans redéployer.

**« Pourquoi une seule clé pour tous les services ? »**
Parce que les jetons sont signés en HS256, une signature symétrique : la même clé sert à signer et à vérifier. Chaque service doit donc la connaître, et si un seul est compromis, la clé l'est aussi. L'amélioration classique, c'est RS256 : auth-service signe avec une clé privée qu'il est seul à posséder, et les autres services vérifient avec une clé publique. Un service compromis ne pourrait alors plus fabriquer de jetons.

**« Les mots de passe des utilisateurs, ce sont aussi des secrets de ce type ? »**
Non, c'est différent. Ils ne sont pas dans la configuration, ils sont en base, et ils y sont hachés avec BCrypt. Même avec un accès à la base, on ne peut pas les relire.

**« Et le compte administrateur par défaut ? »**
Il est créé au premier démarrage, avec le mot de passe lu dans le `.env`. En production, il faudrait le changer juste après l'installation. Je ne l'ai pas rendu obligatoire dans l'application.

**« Pourquoi ne pas avoir fait ça dès le début ? »**
Réponse honnête : au début, j'ai privilégié le fonctionnement de l'application, et j'ai laissé les secrets dans la configuration. Je l'ai corrigé après un audit de sécurité de mon propre code. C'est d'ailleurs la première chose que je ferais différemment : sortir les secrets dès le premier jour.

**Piège : « Donc votre application est prête pour la production ? »**
Non, et je ne le prétends pas. Les secrets sont maintenant hors du code, mais il reste le chiffrement des échanges (HTTPS), un gestionnaire de secrets, et la révocation des jetons de connexion. Je sais exactement ce qui sépare le prototype d'une mise en production.

---

## Mots à placer si l'occasion se présente

- **Rotation** : changer un secret, surtout après une fuite.
- **Fail fast** : refuser de démarrer plutôt que de tourner dans un état dangereux.
- **HS256 / RS256** : signature symétrique (une clé partagée) ou asymétrique (une clé privée pour signer, une clé publique pour vérifier).
- **Gestionnaire de secrets** : Vault, Docker Secrets, AWS Secrets Manager.
