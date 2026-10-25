# 15 — Zipkin : suivre une requête à travers tous les services

Ce fil explique, en partant de zéro, ce qu'est le traçage distribué, comment il est branché dans
PsyConnect, et surtout **pourquoi on en avait besoin**. Tout a été vérifié dans le code le 27/09/2026.

---

## En une phrase

Chaque requête reçoit un numéro unique (le *traceId*) qui la suit de service en service. Zipkin rassemble
tous les morceaux et affiche le trajet complet sous forme de frise : qui a appelé qui, dans quel ordre,
combien de temps chaque étape a pris, et où ça a échoué.

---

## 1. Pourquoi on l'a utilisé

### Le problème qu'on s'est créé en choisissant les microservices

Dans un monolithe, une action (« le psy confirme un rendez-vous ») s'exécute dans **un seul programme**,
avec **un seul journal**. Si quelque chose casse, on lit le journal et on trouve l'erreur.

Dans PsyConnect, la même action traverse plusieurs programmes :

```
Application Flutter
  └─ api-gateway
       └─ appointment-service   (vérifie le RDV, change son statut)
            ├─ user-service         (qui est ce psychologue ?)
            └─ notification-service (prévenir le patient)
```

Chaque service a **son propre journal**, dans **son propre conteneur Docker**. Quand l'utilisateur voit
« erreur » ou « c'est lent », la question devient : **dans lequel des quatre ?** Sans outil, il faut
ouvrir quatre journaux, deviner quelles lignes correspondent à la même requête en comparant les heures à la
milliseconde, et reconstituer le trajet à la main. Avec 8 services, ça devient impossible.

C'est **le prix de l'architecture microservices**, et c'est exactement ce qu'annonce la slide 8 : « Coût
assumé : plus de services à lancer et à déboguer, **compensé par le traçage distribué** ».

### Les quatre raisons concrètes

1. **Déboguer.** Voir en un coup d'œil quel service a échoué dans une chaîne d'appels, et avec quelle
   erreur, sans fouiller quatre journaux.
2. **Trouver ce qui est lent.** La frise montre la durée de chaque étape. Si une confirmation de RDV prend
   4 secondes, on voit tout de suite si c'est user-service, notification-service ou la base de données.
3. **Vérifier que l'architecture fait ce qu'on dit.** On voit réellement les appels entre services : la
   passerelle qui route, les vérifications d'identité vers user-service, les notifications. Les
   diagrammes de séquence du mémoire décrivent le trajet, Zipkin le **prouve** sur une vraie requête.
4. **Voir Resilience4j en action.** Quand notification-service est en panne, on voit dans la trace les
   **3 tentatives** successives, puis le repli (voir le fil 14). Et quand le disjoncteur est ouvert, on
   voit qu'aucun appel n'est plus envoyé.

### Pourquoi Zipkin, et pas autre chose ?

- **Intégration native avec Spring Boot 3** : deux dépendances et deux lignes de configuration par service,
  zéro ligne de code Java.
- **Léger** : un seul conteneur Docker, une interface web incluse, rien d'autre à installer.
- **Open source et standard** : c'est l'un des outils de référence du traçage distribué (avec Jaeger). Le
  format des données est reconnu par d'autres outils, donc on peut changer plus tard sans tout refaire.

Des alternatives existent (Jaeger, Grafana Tempo, ou OpenTelemetry avec un collecteur), mais elles
demandent plus d'infrastructure. Pour un projet local sous Docker Compose, Zipkin était le choix le plus
simple pour le même service rendu.

---

## 2. Le vocabulaire (à maîtriser devant le jury)

| Terme | Définition | Exemple dans PsyConnect |
|---|---|---|
| **Trace** | le trajet complet d'une requête, de bout en bout | « le psy confirme le RDV n° 42 » |
| **Span** | une étape de ce trajet, dans un service, avec un début et une fin | « appointment-service traite PUT /appointments/42/status » |
| **traceId** | identifiant unique de la trace, **le même dans tous les services** | `6f1c2a…` |
| **spanId** | identifiant d'une étape | un par service traversé |
| **Parent span** | l'étape qui a déclenché celle-ci | le span d'appointment-service est parent de celui d'user-service |
| **Propagation** | le fait de transmettre le traceId d'un service au suivant, dans un en-tête HTTP | fait automatiquement |
| **Échantillonnage** | la proportion de requêtes tracées | 100 % dans PsyConnect |

Une trace, c'est donc un **arbre de spans** qui partagent le même traceId.

---

## 3. Comment ça marche, étape par étape

```
 1. La requête arrive à api-gateway sans identifiant.
    → la passerelle crée un traceId (ex. 6f1c…) et un premier span.

 2. La passerelle transmet la requête à appointment-service
    en ajoutant l'identifiant dans un en-tête HTTP.
    → appointment-service lit l'en-tête, garde le même traceId,
      et crée son propre span, enfant de celui de la passerelle.

 3. appointment-service appelle user-service puis notification-service
    avec RestTemplate, qui ajoute à son tour l'en-tête.
    → chacun crée son span, avec toujours le même traceId.

 4. À la fin de chaque span, chaque service envoie ses mesures
    (début, durée, service, URL, statut, erreur éventuelle) à Zipkin,
    en arrière-plan, sans ralentir la requête.

 5. Zipkin regroupe tous les spans qui ont le même traceId
    et dessine la frise.
```

Ce que ça donne dans l'interface (http://localhost:9411) :

```
api-gateway            ████████████████████████████████  180 ms
 appointment-service     ██████████████████████████████  165 ms
  user-service              ████████                      40 ms
  notification-service                    ██████████       55 ms
```

Chaque barre est un span. Sa position montre **quand** il commence, sa longueur **combien de temps** il
dure. Un span en rouge signale une erreur.

### L'en-tête qui transporte l'identifiant

Par défaut, Spring Boot 3 transmet l'identifiant dans l'en-tête standard W3C `traceparent`, qui ressemble à :

```
traceparent: 00-6f1c2a9b...-a3b4c5d6...-01
                  traceId      spanId  échantillonné
```

Les commentaires du code parlent de « B3 », l'ancien format de Zipkin. Les deux formats existent ; ce qui
compte, c'est que tous les services parlent le même, ce qui est le cas puisqu'ils ont tous la même
configuration.

---

## 4. Ce qui est branché dans PsyConnect

### Les dépendances (dans les 9 `build.gradle` Java)

```gradle
implementation 'org.springframework.boot:spring-boot-starter-actuator'
implementation 'io.micrometer:micrometer-tracing-bridge-brave'
implementation 'io.zipkin.reporter2:zipkin-reporter-brave'
```

| Dépendance | Rôle |
|---|---|
| `spring-boot-starter-actuator` | active l'observabilité de Spring Boot (santé, métriques, traçage) |
| `micrometer-tracing-bridge-brave` | **Micrometer Tracing** est l'interface standard de Spring ; **Brave** est la bibliothèque qui crée réellement les spans et propage l'identifiant |
| `zipkin-reporter-brave` | envoie les spans terminés au serveur Zipkin |

Micrometer, c'est un peu le « JDBC » du traçage : le code parle à une interface, et on branche derrière
l'implémentation de son choix.

### La configuration (dans les 9 `application.properties`)

```properties
management.tracing.sampling.probability=1.0
management.zipkin.tracing.endpoint=${ZIPKIN_ENDPOINT:http://localhost:9411/api/v2/spans}
```

- `sampling.probability=1.0` : **100 % des requêtes** sont tracées. Parfait en développement, où l'on veut
  tout voir. En production, on descendrait à 10 % ou moins pour limiter le volume.
- `zipkin.tracing.endpoint` : l'adresse où envoyer les spans. Dans Docker, elle vaut
  `http://zipkin:9411/api/v2/spans` grâce à la variable `ZIPKIN_ENDPOINT` du `docker-compose.yml`
  (présente sur les 9 services Java). En local, hors Docker, c'est `localhost:9411` par défaut.

### Les services tracés

Les 7 microservices Java, **plus api-gateway et eureka-server** : 9 composants au total.

| Tracé | Non tracé |
|---|---|
| api-gateway, eureka-server, auth, user, appointment, payment, notification, session, ai-companion | ml-service (Python), PostgreSQL, Ollama, Jitsi |

### Le détail qui fait tout marcher : `RestTemplateBuilder`

Le traçage ne se propage que si l'appel HTTP sortant est **instrumenté**, c'est-à-dire que Spring y
ajoute l'en-tête. C'est pour ça que chaque `RestTemplateConfig` crée le `RestTemplate` à partir du
`RestTemplateBuilder` fourni par Spring, et pas avec `new RestTemplate()` :

```java
@Bean
@LoadBalanced
public RestTemplate restTemplate(RestTemplateBuilder builder) {
    return builder
            .connectTimeout(CONNECT_TIMEOUT)
            .readTimeout(READ_TIMEOUT)
            .build();
}
```

Un `new RestTemplate()` fonctionnerait pour les appels, mais **casserait silencieusement la trace** : le
service appelé créerait un nouveau traceId, et Zipkin afficherait deux traces séparées au lieu d'une. Le
commentaire dans payment-service et notification-service le rappelle.

### Le serveur Zipkin (dans `docker-compose.yml`)

```yaml
zipkin:
  image: openzipkin/zipkin:latest
  container_name: psyconnect-zipkin
  ports:
    - "9411:9411"
```

Un seul conteneur qui reçoit les spans, les stocke et fournit l'interface web sur http://localhost:9411.

### Bonus : le traceId dans les journaux

Depuis Spring Boot 3.2, quand le traçage est actif, chaque ligne de journal inclut le traceId et le spanId.
Concrètement, si Zipkin montre une erreur dans la trace `6f1c…`, on peut chercher `6f1c` dans les
journaux Docker du service concerné et retrouver **exactement** les lignes de cette requête.

---

## 5. Comment s'en servir (démo en 2 minutes)

1. Lancer le projet : `docker compose up -d`.
2. Faire une action dans l'app, par exemple confirmer un rendez-vous côté psy.
3. Ouvrir **http://localhost:9411**.
4. Cliquer sur **« Run Query »** (on peut filtrer par service, par exemple `appointment-service`).
5. Ouvrir la trace la plus récente : la frise apparaît, avec un span par service traversé.
6. Cliquer sur un span pour voir le détail : URL appelée, méthode HTTP, code de statut, erreur éventuelle.
7. Onglet **« Dependencies »** : Zipkin dessine automatiquement la **carte des services** et de leurs
   appels, à partir des traces reçues. C'est un bon visuel à montrer au jury, parce qu'il reconstruit
   l'architecture tout seul à partir du trafic réel.

**Pour montrer Resilience4j :** arrêter notification-service (`docker stop psyconnect-notification`), refaire
une confirmation, puis ouvrir la trace : on voit les 3 tentatives en échec, et pourtant la requête
principale se termine avec succès.

C'est aussi ce qu'il faut capturer pour la **figure 4.9 du mémoire** (voir
`Captures_A_Remplacer_Memoire.md`).

---

## 6. Limites (à connaître et à reconnaître)

1. **ml-service n'est pas tracé.** Il est en Python et n'a pas d'instrumentation. Et comme il ne retransmet
   pas l'en-tête `traceparent` quand il rappelle la passerelle pour obtenir les profils, la trace se
   **coupe en deux** : la demande de recommandation d'un côté, la récupération des profils de l'autre.
   Correction : ajouter OpenTelemetry à ml-service et relayer l'en-tête, comme il relaie déjà le jeton JWT.
2. **Les traces sont perdues au redémarrage.** Zipkin stocke tout en mémoire par défaut : aucune base n'est
   configurée. Suffisant en développement ; en production, il faudrait un stockage (Elasticsearch,
   Cassandra ou MySQL).
3. **100 % d'échantillonnage** : très bien en développement, mais trop coûteux à grande échelle.
4. **Image `latest`** : la version de Zipkin n'est pas figée, donc un redémarrage peut récupérer une
   nouvelle version. Mieux vaut fixer une version précise.
5. **Aucune protection sur l'interface Zipkin.** Elle est ouverte sur le port 9411. En local, ce n'est pas
   grave ; en production, les traces contiennent des URL (donc des identifiants de patients et de
   rendez-vous) : il faudrait la protéger et ne pas l'exposer publiquement.
6. **Le traçage ne remplace pas les journaux ni les métriques.** Il dit **où** et **combien de temps** ;
   les journaux disent **pourquoi**. Les trois ensemble forment ce qu'on appelle l'**observabilité**
   (traces, logs, métriques).

---

## 7. Questions probables du jury

**« Pourquoi avoir mis du traçage distribué ? »**
Parce qu'en microservices, une action traverse plusieurs services qui ont chacun leur journal. Sans
traçage, retrouver où une requête a échoué ou ralenti demande de recouper les journaux à la main. Zipkin
montre le trajet complet d'une requête sur une seule frise. C'est ce qui compense le coût de débogage de
l'architecture microservices.

**« Comment Zipkin sait que deux lignes appartiennent à la même requête ? »**
Grâce au traceId, créé à l'entrée (la passerelle) et transmis de service en service dans un en-tête HTTP.
Chaque service crée son span avec ce même traceId, et Zipkin les regroupe.

**« Est-ce que ça ralentit l'application ? »**
Très peu : l'ajout d'un en-tête et la mesure d'un temps, c'est négligeable, et l'envoi des spans à Zipkin
se fait en arrière-plan, par lots. Si Zipkin est arrêté, l'application continue de fonctionner
normalement : on perd seulement les traces.

**« Quelle différence entre Zipkin et Eureka ? »**
Eureka est un **annuaire** : il dit où se trouve chaque service pour pouvoir l'appeler. Zipkin est un
**enregistreur** : il montre après coup le trajet qu'a suivi une requête. L'un sert à faire fonctionner les
appels, l'autre à les observer.

**« Et Micrometer, Brave, Zipkin : qui fait quoi ? »**
Micrometer Tracing est l'interface standard de Spring. Brave est la bibliothèque qui crée réellement les
spans et propage l'identifiant. Zipkin est le serveur qui reçoit, stocke et affiche les traces.

**« En production, vous garderiez Zipkin ? »**
Oui, ou un équivalent compatible comme Grafana Tempo, avec trois changements : un stockage persistant, un
échantillonnage réduit (par exemple 10 %), et une interface protégée. J'ajouterais aussi ml-service dans
les traces avec OpenTelemetry.

---

## Ce que ce fil démontre

| Notion | Où |
|---|---|
| Observabilité d'un système distribué | Zipkin, traces et spans |
| Propagation de contexte entre services | en-tête `traceparent`, `RestTemplateBuilder` |
| Abstraction et implémentation | Micrometer (interface) + Brave (implémentation) |
| Configuration externalisée | `ZIPKIN_ENDPOINT` dans `docker-compose.yml` |
| Compromis dev / production | échantillonnage à 100 %, stockage en mémoire |

## À retenir en trois phrases

1. En microservices, une action traverse plusieurs services qui ont chacun leur journal : sans traçage, on
   ne sait pas où une requête a échoué ou ralenti.
2. Un traceId unique suit la requête de service en service ; Zipkin rassemble les étapes et affiche le
   trajet complet, avec la durée de chaque étape.
3. C'est ce qui compense le coût de débogage des microservices, avec deux limites assumées : ml-service
   n'est pas tracé, et les traces ne sont pas conservées.
