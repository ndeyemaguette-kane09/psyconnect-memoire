# 14 — Resilience4j : quand un service ne répond pas

Ce fil explique, en partant de zéro, comment PsyConnect se comporte quand un microservice en appelle un
autre et que celui-ci est lent, en panne ou surchargé. Tout ce qui suit a été vérifié dans le code le 27/09/2026.

---

## En une phrase

Chaque appel entre services passe par Resilience4j, qui **réessaie** quand l'échec semble passager et **coupe
le circuit** quand l'échec dure. Ensuite, une méthode de repli décide, **selon l'enjeu**, s'il faut laisser
l'opération continuer (*tomber en marche*) ou la refuser (*tomber fermé*).

---

## 1. Le problème de départ

Dans un monolithe, appeler une autre partie du code, c'est appeler une méthode : ça ne tombe pas en panne.
Dans une architecture microservices, c'est un **appel réseau** HTTP. Et un appel réseau peut :

- échouer une fois, pour rien : un redémarrage, un pic de charge, un paquet perdu ;
- échouer longtemps : le service est arrêté ;
- ne jamais répondre : le service est bloqué. C'est le pire cas, parce que l'appelant attend.

Sans protection, une panne se propage. Si notification-service est bloqué, appointment-service attend, ses
threads s'accumulent, il ralentit à son tour, et c'est toute l'application qui devient lente alors qu'un
seul service va mal. On appelle ça une **panne en cascade**.

**Resilience4j** est une bibliothèque Java qui entoure un appel de mécanismes de protection. PsyConnect en
utilise deux : **Retry** (nouvelle tentative) et **CircuitBreaker** (disjoncteur).

---

## 2. Où il est utilisé dans PsyConnect

Resilience4j est présent dans les 4 services qui appellent d'autres services :

| Service | Dépendance Gradle | Appelle |
|---|---|---|
| appointment-service | `resilience4j-spring-boot3:2.2.0` + AOP | user-service, notification-service, payment-service |
| payment-service | `resilience4j-spring-boot3:2.2.0` + AOP | user-service, appointment-service, notification-service |
| session-service | `spring-cloud-starter-circuitbreaker-resilience4j` + AOP | appointment-service, user-service, notification-service |
| user-service | `resilience4j-spring-boot3:2.2.0` + AOP | auth-service, appointment-service, notification-service |

auth-service, notification-service et ai-companion-service n'appellent aucun autre service Java : ils n'en
ont pas besoin. ml-service est en Python et n'utilise pas Resilience4j (voir les limites).

**Pourquoi AOP ?** Les annotations `@Retry` et `@CircuitBreaker` ne font rien toutes seules. Spring crée
autour de la classe un « proxy » qui intercepte l'appel de méthode et applique la protection. C'est de la
programmation orientée aspect (AOP).

---

## 3. Mécanisme 1 — Retry (réessayer)

### L'idée

Si l'échec est passager, un deuxième essai quelques instants plus tard a de bonnes chances de réussir.

### La configuration (la même partout, sauf auth-service)

```properties
retry.instances.userService.max-attempts=3
retry.instances.userService.wait-duration=300ms
retry.instances.userService.enable-randomized-wait=true
```

| Paramètre | Valeur | Ce que ça veut dire |
|---|---|---|
| `max-attempts` | 3 | 3 tentatives au total : 1 appel normal + 2 nouvelles tentatives |
| `wait-duration` | 300 ms | pause entre deux tentatives |
| `enable-randomized-wait` | true | la pause varie au hasard autour de 300 ms (en gros entre 150 et 450 ms) |

Seul user-service → auth-service (récupération du pseudo) fait `max-attempts=2` : c'est un appel
secondaire, pas la peine d'insister.

### Pourquoi une pause aléatoire ?

Imagine que notification-service redémarre et que 50 requêtes échouent au même moment. Avec une pause fixe,
les 50 réessaient **exactement ensemble** 300 ms plus tard et le resurchargent d'un coup. Avec une pause
aléatoire, les nouvelles tentatives s'étalent. C'est le principe du *jitter*.

### Les exceptions qu'on ne réessaie JAMAIS

```properties
retry.instances.userService.ignore-exceptions=\
  ...ResourceNotFoundException,...ForbiddenOperationException
```

Réessayer n'a de sens que pour une panne. Si user-service répond « ce profil n'existe pas » (404) ou « accès
interdit » (403), la réponse sera la même dans 300 ms. Ces erreurs **métier** sont donc exclues des
nouvelles tentatives, et aussi du calcul du disjoncteur : un 404 ne veut pas dire que le service est en panne.

Dans payment-service, `InsufficientBalanceException` est aussi exclue : un solde insuffisant ne se règle
pas en réessayant.

---

## 4. Mécanisme 2 — CircuitBreaker (le disjoncteur)

### L'analogie

C'est exactement le disjoncteur électrique de la maison. Quand il y a trop de problèmes, il **coupe**, pour
protéger le reste de l'installation. Au bout d'un moment, on le réarme prudemment.

Transposé à PsyConnect : si user-service échoue sans arrêt, ça ne sert à rien de continuer à l'appeler et à
attendre 3 secondes à chaque fois. On arrête de l'appeler pendant un moment, et on répond tout de suite
« indisponible ».

### Les trois états

```
                   50 % d'échecs ou plus
                 (sur les 10 derniers appels)
     ┌────────┐  ──────────────────────────►  ┌────────┐
     │ FERMÉ  │                               │ OUVERT │   les appels sont refusés
     │(normal)│  ◄──────────┐                 │        │   immédiatement, sans réseau
     └────────┘             │                 └────────┘
                   les 3 appels test          │   au bout de 10 s
                   réussissent                ▼
                            │           ┌─────────────┐
                            └───────────│ SEMI-OUVERT │  on laisse passer
                                        │             │  3 appels test
          au moins un appel test ──────►└─────────────┘
          échoue : retour à OUVERT
```

- **FERMÉ (CLOSED)** : tout passe normalement. Resilience4j compte les succès et les échecs.
- **OUVERT (OPEN)** : trop d'échecs. Tous les appels sont refusés **sans même toucher au réseau**
  (exception `CallNotPermittedException`). Le service en panne n'est plus sollicité, il peut récupérer.
- **SEMI-OUVERT (HALF_OPEN)** : après 10 secondes, on teste avec quelques appels. S'ils réussissent, on
  referme. Sinon, on rouvre.

### La configuration

```properties
circuitbreaker.instances.userService.sliding-window-size=10
circuitbreaker.instances.userService.minimum-number-of-calls=5
circuitbreaker.instances.userService.failure-rate-threshold=50
circuitbreaker.instances.userService.wait-duration-in-open-state=10s
circuitbreaker.instances.userService.permitted-number-of-calls-in-half-open-state=3
circuitbreaker.instances.userService.automatic-transition-from-open-to-half-open-enabled=true
circuitbreaker.instances.userService.register-health-indicator=true
```

| Paramètre | Valeur | Ce que ça veut dire |
|---|---|---|
| `sliding-window-size` | 10 | on regarde les 10 derniers appels (fenêtre glissante) |
| `minimum-number-of-calls` | 5 | on ne juge pas avant 5 appels : 1 échec sur 1 ne doit pas tout couper |
| `failure-rate-threshold` | 50 | à partir de 50 % d'échecs, le circuit s'ouvre |
| `wait-duration-in-open-state` | 10 s | durée pendant laquelle le circuit reste ouvert |
| `permitted-number-of-calls-in-half-open-state` | 3 | nombre d'appels test en semi-ouvert |
| `automatic-transition-...` | true | le passage à semi-ouvert se fait tout seul après 10 s, sans attendre un nouvel appel |
| `register-health-indicator` | true | l'état du disjoncteur apparaît dans `/actuator/health` |

Dans appointment-, payment- et session-service, on peut consulter l'état des disjoncteurs en direct :
`management.endpoints.web.exposure.include=health,circuitbreakers`.

### Une instance par service appelé

Le nom dans l'annotation (`name = "userService"`) désigne **une instance** de disjoncteur. Dans
appointment-service, il y a trois instances indépendantes : `userService`, `notificationService` et
`paymentService`. Si notification-service tombe, seul le disjoncteur `notificationService` s'ouvre ; les
appels vers user-service continuent normalement. **Une panne reste locale**, et c'est exactement
l'argument de la slide 8.

---

## 5. Comment les deux s'emboîtent

Sur une même méthode, on trouve souvent les deux annotations :

```java
@CircuitBreaker(name = "notificationService")
@Retry(name = "notificationService", fallbackMethod = "fallbackSend")
public void send(Long userId, String title, String message, String type, String userRole) { ... }
```

Par défaut, Resilience4j les applique dans cet ordre : **Retry à l'extérieur, CircuitBreaker à
l'intérieur**.

```
appel de send()
  └─ Retry (jusqu'à 3 tentatives)
       └─ CircuitBreaker (compte chaque tentative, peut refuser)
            └─ RestTemplate → HTTP → notification-service
  └─ si tout a échoué : fallbackSend(...)
```

Conséquences à bien comprendre :

1. **Chaque tentative compte** pour le disjoncteur. Un appel logique qui échoue 3 fois = 3 échecs dans
   la fenêtre de 10.
2. **Le repli n'est appelé qu'une fois**, quand toutes les tentatives ont échoué, ou quand le circuit est
   ouvert.
3. Quand le circuit est **ouvert**, les tentatives sont refusées instantanément : l'appelant passe au repli
   en quelques millisecondes au lieu d'attendre les délais réseau.

---

## 6. Le délai d'attente : l'oublié qui rend tout ça utile

Retry et CircuitBreaker ne réagissent qu'à une **erreur**. Un service bloqué qui ne répond jamais ne
produit pas d'erreur… sauf si on fixe un délai maximum. C'est le rôle du `RestTemplateConfig` de chaque
service :

| Service appelant | Connexion | Lecture de la réponse |
|---|---|---|
| appointment-, user-, session-, auth-service | 2 s | 3 s |
| payment-service | 5 s | 10 s |

Passé ce délai, RestTemplate lève une exception, et Resilience4j prend le relais.

**À savoir calculer devant un jury :** dans le pire cas (service bloqué, circuit encore fermé), un appel
d'appointment-service vers user-service peut prendre jusqu'à environ 3 × 3 s + 2 × 0,45 s ≈ **10 s** avant
le repli. Pour payment-service, dont les délais sont plus longs, c'est plus de 30 s. Ensuite, dès que le
circuit s'ouvre, la réponse devient immédiate.

---

## 7. Le cœur du sujet : tomber en marche ou tomber fermé

La méthode de repli (`fallbackMethod`) décide de ce qui arrive quand l'appel a définitivement échoué. Et
c'est là qu'il y a un **choix de conception**, pas juste de la technique.

- **Tomber en marche (fail open)** : on continue sans le service en panne. C'est acceptable quand ce qui
  est perdu n'est pas grave.
- **Tomber fermé (fail closed)** : on refuse l'opération. C'est obligatoire quand continuer créerait une
  faille de sécurité ou une incohérence.

### La carte complète des appels protégés

**appointment-service**

| Appel | Vers | Repli | Choix |
|---|---|---|---|
| `NotificationClient.send` | notification | journalise et continue : le RDV est créé quand même | en marche |
| `PaymentClient.refundCompletedPayments` | payment | journalise « remboursement manuel nécessaire », l'annulation aboutit | en marche, avec trace |
| `OwnershipResolver.resolveOwnPatientId` / `...PsychologistId` | user | erreur 503 | **fermé** |
| `OwnershipResolver.isPsychologistVerified` | user | erreur 503 | **fermé** |
| `getPsychologistProfile` / `getPatientProfile` | user | pas de repli : l'erreur remonte en 503 | fermé |

**payment-service**

| Appel | Vers | Repli | Choix |
|---|---|---|---|
| `OwnershipResolver.resolveOwn...` | user | 503 | **fermé** |
| `OwnershipResolver.getConsultationPrice` | user | 503 (pas de tarif = pas de paiement) | **fermé** |
| `WalletClient.debit` | user | « Solde insuffisant » si 402, sinon 503 | **fermé** |
| `WalletClient.credit` | user | 503 | **fermé** |
| `AppointmentClient.getAppointmentById` | appointment | garde les 404 / 403, sinon 503 | **fermé** |
| `NotificationClient.send` | notification | journalise et continue | en marche |

**session-service**

| Appel | Vers | Repli | Choix |
|---|---|---|---|
| `OwnershipResolver.resolveOwn...` | user | 503 | **fermé** |
| `AppointmentClient.getAppointment` | appointment | 503 : pas de salon sans RDV vérifié | **fermé** |
| `AppointmentClient.updateAppointmentStatus` | appointment | journalise : la séance est terminée quand même | en marche |
| `NotificationClient.send` | notification | journalise et continue | en marche |

**user-service**

| Appel | Vers | Repli | Choix |
|---|---|---|---|
| `AppointmentClient.hasAppointmentBetween` / `hasCompleted...` / `hasAccepted...` | appointment | renvoie `false` | **fermé** |
| `AuthServiceClient.getPseudo` | auth | renvoie `null`, le patient s'affiche « Patient anonyme » | **fermé** (côté vie privée) |
| `NotificationClient.send` | notification | journalise et continue | en marche |

### Comment lire ces choix

- **Les notifications tombent toujours en marche.** Perdre une notification est désagréable, mais bloquer
  une réservation ou un paiement pour ça serait pire.
- **Tout ce qui touche à l'identité, aux droits ou à l'argent tombe fermé.** Si on ne peut pas vérifier qui
  fait la demande, ou si le patient a le droit, on refuse. Laisser passer « par défaut » serait une faille.
- **Les vérifications de user-service renvoient `false`.** Par exemple, si appointment-service est en
  panne, user-service ne peut pas vérifier qu'un patient a bien eu une séance : il répond « non », donc
  pas d'avis possible et pas de suivi possible. On refuse plutôt que de risquer un faux « oui ».
- **Le pseudo manquant donne « Patient anonyme »**, jamais le vrai nom. En cas de doute, on protège la vie
  privée.

---

## 8. Un scénario complet, seconde par seconde

**Situation :** notification-service vient de planter. Un psychologue confirme un rendez-vous.

1. appointment-service passe le RDV en `CONFIRMED` et l'enregistre.
2. Il appelle `NotificationClient.send` pour prévenir le patient.
   - Tentative 1 : échec (connexion refusée). Le disjoncteur note 1 échec.
   - Pause d'environ 300 ms, tentative 2 : échec. Pause, tentative 3 : échec.
   - Retry abandonne et appelle `fallbackSend`, qui écrit un avertissement dans les journaux.
3. La réponse part au psychologue : **le RDV est confirmé**. Il ne voit aucune erreur.
4. D'autres actions suivent et échouent aussi sur les notifications. Dès 5 appels dans la fenêtre avec au
   moins 50 % d'échecs, le disjoncteur `notificationService` **s'ouvre**.
5. Pendant 10 s, chaque envoi de notification est refusé instantanément, sans attendre le réseau.
6. Au bout de 10 s, le circuit passe en semi-ouvert. notification-service a redémarré, les 3 appels test
   réussissent, et le circuit **se referme**.

**Même scénario avec user-service en panne :** le psychologue essaie de confirmer, mais appointment-service
ne peut pas vérifier son identité. Il reçoit une erreur 503, « Le service utilisateur est temporairement
indisponible, merci de réessayer dans quelques instants », et **rien n'est modifié**.

---

## 9. Les tests automatisés

Deux classes de test dans appointment-service, `@SpringBootTest` avec un `RestTemplate` simulé
(`@MockBean`) qui lève toujours une erreur :

**`NotificationClientResilienceTest`**
- `send_transientFailure_retriesThenFallsBackSilently` : un appel logique déclenche **exactement 3**
  appels HTTP (`verify(restTemplate, times(3))`), puis le repli, **sans exception** pour l'appelant.
- `send_repeatedFailures_opensCircuitAndStopsCallingNotificationService` : après plusieurs échecs, le
  disjoncteur est `OPEN`, et l'appel suivant **ne touche plus au réseau** (`never()`).

**`OwnershipResolverResilienceTest`**
- `resolveOwnPatientId_transientFailure_retriesThenThrowsServiceUnavailable` : 3 tentatives, puis une
  `ServiceUnavailableException`. C'est le « tomber fermé » prouvé par un test.
- `resolveOwnPatientId_repeatedFailures_opensCircuitAndStopsCallingUserService` : le circuit s'ouvre et
  l'appel suivant échoue immédiatement.

Les tests utilisent une configuration légèrement réduite (`minimum-number-of-calls=4`) pour faire basculer
le circuit plus vite.

Ce qui **n'est pas** testé : le repli du remboursement, et les clients des autres services.

---

## 10. Limites et pièges à connaître (et à reconnaître si on te les pose)

1. **Disjoncteur retiré sur deux clients de notification.** Dans payment-service et user-service,
   `NotificationClient` n'a plus que `@Retry`. Le commentaire du code l'explique : l'état OPEN bloquait
   toutes les notifications. La configuration `circuitbreaker.instances.notificationService` y est
   restée, mais ne sert plus. En réalité, avec la transition automatique vers semi-ouvert, le circuit
   devrait se refermer tout seul : la vraie cause mériterait d'être réanalysée.
2. **Un `try/catch` qui rend Retry inutile.** Dans session-service, `updateAppointmentStatus` attrape
   lui-même l'erreur réseau. Resilience4j ne voit donc jamais d'échec : il n'y a ni nouvelle tentative, ni
   comptage dans le disjoncteur. C'est volontaire (« best-effort »), mais les annotations sur cette méthode
   ne servent à rien.
3. **Le message de remboursement peut mentir.** Dans appointment-service, si payment-service est en panne,
   le repli journalise « remboursement manuel nécessaire »… mais le patient reçoit quand même « le
   paiement a été crédité sur votre solde », car l'information que le repli a été utilisé ne remonte pas.
   Correction simple : faire renvoyer un booléen au client de paiement.
4. **« Signalé », c'est seulement un journal.** Aucun administrateur n'est alerté automatiquement d'un
   remboursement manuel à faire. En production, il faudrait une alerte (monitoring, tâche en base).
5. **Latence cumulée** (voir la section 6) : jusqu'à environ 10 s, voire plus de 30 s dans payment-service,
   avant que le circuit s'ouvre.
6. **Deux mécanismes seulement.** Resilience4j propose aussi `TimeLimiter`, `Bulkhead` (limiter le nombre
   d'appels simultanés) et `RateLimiter`. Ils ne sont pas utilisés : les délais sont gérés par
   RestTemplate.
7. **ml-service (Python) n'est pas couvert.** Il utilise un délai `httpx` de 5 s et renvoie une erreur 502
   si user-service ne répond pas, sans nouvelle tentative ni disjoncteur.
8. **Nouvelle tentative et opérations non idempotentes.** Réessayer un `debit` du portefeuille pourrait,
   en théorie, débiter deux fois si la première requête a réussi mais que la réponse s'est perdue. C'est
   un cas rare (délai dépassé après exécution), mais c'est la vraie question qu'un jury expert peut poser.
   La parade classique est une clé d'idempotence par paiement.

---

## 11. Questions probables du jury

**« Quelle différence entre Retry et CircuitBreaker ? »**
Retry gère l'échec **passager** : on réessaie. CircuitBreaker gère l'échec **durable** : on arrête
d'appeler pour ne pas attendre inutilement, et pour laisser le service récupérer. Les deux sont
complémentaires : Retry seul peut aggraver une panne en multipliant les appels.

**« Pourquoi ne pas réessayer sur un 404 ? »**
Parce que c'est une réponse métier, pas une panne. Elle sera identique au prochain essai. Ces exceptions
sont dans `ignore-exceptions`, et elles ne comptent pas non plus comme des échecs du disjoncteur.

**« Pourquoi 50 %, 10 appels, 10 secondes ? »**
Ce sont des valeurs raisonnables pour un MVP à faible trafic : assez d'appels pour ne pas couper sur un
incident isolé (minimum 5), assez court pour que le service récupère vite. En production, on les ajusterait
avec des mesures réelles (Zipkin, métriques Actuator).

**« Qu'est-ce qui se passe si user-service tombe pendant un paiement ? »**
Le paiement est **refusé** (503) : impossible de vérifier le tarif, l'identité ou le solde. Et si l'erreur
survient après le débit, payment-service recrédite le patient (compensation).

**« Pourquoi ne pas tout faire tomber en marche, pour que l'app reste utilisable ? »**
Parce que certaines opérations en marche seraient des failles : laisser réserver sans vérifier l'identité,
ou afficher le vrai nom d'un patient anonyme faute de pseudo. Le choix se fait **appel par appel, selon
l'enjeu**, c'est tout l'intérêt de la méthode de repli.

**« Comment savez-vous que ça marche ? »**
Par quatre tests automatisés, qui simulent une panne et vérifient le nombre exact de tentatives, l'ouverture
du circuit et le comportement du repli. Et on peut observer l'état des disjoncteurs en direct via
`/actuator/health`.

---

## Ce que ce fil démontre

| Notion | Où |
|---|---|
| Panne en cascade et isolation des pannes | une instance de disjoncteur par service appelé |
| Nouvelle tentative avec *jitter* | `enable-randomized-wait=true` |
| Machine à états (fermé, ouvert, semi-ouvert) | `circuitbreaker.instances.*` |
| Erreur métier vs erreur technique | `ignore-exceptions` |
| Choix de conception : fail open vs fail closed | les méthodes `fallback...` |
| Programmation orientée aspect | les annotations et le proxy Spring |
| Délais d'attente | `RestTemplateConfig` |
| Tests de résilience | `NotificationClientResilienceTest`, `OwnershipResolverResilienceTest` |

## À retenir en trois phrases

1. Un appel entre services peut échouer : Resilience4j réessaie quand c'est passager et coupe le circuit
   quand ça dure.
2. La méthode de repli fait le vrai choix : les notifications tombent en marche, l'identité, les droits
   et l'argent tombent fermés.
3. C'est prouvé par des tests automatisés, et les limites (latence cumulée, repli du remboursement,
   ml-service non couvert) sont connues.
