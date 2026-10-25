# Tests automatisés du frontend Flutter

Ajoutés le 27/09/2026. Ce document décrit ce que testent les fichiers du dossier `frontend/psyconnect/test/models/`, pourquoi ces choix, et comment les lancer.

## Lancer les tests

Depuis `frontend/psyconnect/` :

```bash
flutter test test/models
```

Pour tout lancer, y compris le test de démarrage déjà présent :

```bash
flutter test
```

Résultat attendu : `All tests passed!`, avec 42 tests pour `test/models` (44 avec `widget_test.dart`).

## Ce qui est testé, et pourquoi

Ce sont des **tests unitaires** : ils vérifient la logique des modèles Dart sans afficher d'écran et sans appeler le backend. Ils tournent donc en quelques secondes, sans Docker.

Les modèles ont été choisis parce que c'est la **frontière entre Flutter et les microservices** : chaque `fromJson` lit une réponse du backend, et chaque `toJson` fabrique une requête. Si un nom de champ ou une valeur d'enum change d'un côté sans l'autre, l'app plante ou affiche un écran vide sans message clair. Ces tests servent à détecter ce décalage tout de suite.

### `payment_models_test.dart` : paiement et portefeuille (15 tests)

| Ce qui est vérifié | Pourquoi c'est important |
|---|---|
| `formatAmount` : `15000` → `15 000`, décimales avec virgule, signe moins, `5000.0` affiché comme un entier | C'est ce que voit le patient sur chaque montant en FCFA. Une erreur ici se voit sur tous les écrans de paiement. |
| `PaymentStatusX.fromApiValue` reconnaît les 4 statuts, ignore la casse, rejette un statut inconnu | Un statut mal lu afficherait « Payé » pour un paiement remboursé. |
| `CreatePaymentRequest.toJson` envoie `WALLET` ; Wave / Orange Money / carte sont envoyés en `SIMULATED_*` | Ça documente dans le code que les moyens mobile money sont simulés, et que le paiement d'un RDV passe par le solde. |
| `Payment.fromJson` lit un paiement complet, et ne plante pas si la méthode est absente ou inconnue | Les anciens paiements en base n'ont pas tous une méthode. |
| `PsychologistWallet.fromJson({})` donne des zéros et une liste de retraits vide | Un psy qui vient d'être validé n'a encore rien gagné : l'écran doit s'afficher quand même. |
| `PaymentTransaction.fromJson` : brut − commission = net | Ça vérifie la cohérence du revenu net affiché au psy. |

### `appointment_models_test.dart` : rendez-vous (12 tests)

| Ce qui est vérifié | Pourquoi c'est important |
|---|---|
| `isoLocalDateTime` produit `2026-03-05T09:07:00` (sans `Z` ni fuseau) | appointment-service attend un `LocalDateTime` Java. Une date envoyée en UTC décalerait le créneau réservé. |
| Aller-retour `apiValue` ↔ `fromApiValue` pour **tous** les statuts et types de consultation | Si on ajoute un statut côté Java sans le gérer côté Flutter, le test le signale. |
| `CreateAppointmentRequest` et `RescheduleAppointmentRequest` produisent exactement le JSON attendu | C'est le contrat de `POST /appointments` et du report d'un RDV. |
| `Appointment.fromJson` : si `createdAt` manque, on prend la date de la séance | C'est une règle de compatibilité avec les RDV créés avant l'ajout du champ. |

### `questionnaire_models_test.dart` : PHQ-9 / GAD-7 (11 tests)

C'est le fichier le plus important, parce qu'il vérifie le **filet de sécurité clinique**.

| Ce qui est vérifié | Pourquoi c'est important |
|---|---|
| `signalsImmediateRisk` est vrai quand l'item 9 du PHQ-9 (idées suicidaires) vaut 2 ou plus | C'est ce qui déclenche la proposition d'aide immédiate côté patient et l'alerte côté psy. |
| L'alerte se déclenche **même avec un score total de 3/27** | Un score global « minimal » ne doit pas masquer une réponse positive à cet item. C'est la règle clinique du PHQ-9. |
| Pas d'alerte si l'item 9 vaut 1, même avec un score total élevé | L'alerte porte sur l'item, pas sur le total. |
| Jamais d'alerte sur un GAD-7, sur un questionnaire non rempli, ni sur une liste de réponses incomplète | Ça évite les fausses alertes et les plantages. |
| PHQ-9 = 9 questions / max 27, GAD-7 = 7 questions / max 21, et l'item surveillé est bien celui qui parle de mort | Si quelqu'un réordonne les questions, le test casse au lieu de surveiller la mauvaise question. |
| `fromJson` lit un PHQ-9 rempli et un GAD-7 envoyé mais pas encore rempli | Ce sont les deux états qu'affiche l'historique. |

### `user_role_test.dart` : rôles (4 tests)

Aller-retour `PATIENT` / `PSYCHOLOGIST` / `ADMIN` avec auth-service, casse ignorée, rôle inconnu rejeté. Le rôle décide quelle interface s'ouvre après la connexion : une erreur ici enverrait un patient sur l'interface psy.

## Ce qui n'est pas couvert

| Niveau | État | Suite logique |
|---|---|---|
| Tests unitaires des modèles | 42 tests (ce document) | Étendre aux autres modèles (`wallet_models`, `notification_models`, `availability_models`). |
| Tests de widgets | 1 seul test de démarrage (`widget_test.dart`) | Écran de connexion (validation du formulaire), écran de réservation, avec des services simulés (`mocktail`). |
| Tests d'intégration | Aucun | Un parcours complet avec `integration_test` : connexion → recherche → réservation → paiement. |

La logique sensible (droits d'accès, paiement, pseudonymisation) est exécutée côté backend, et c'est là que se concentrent les tests d'intégration Spring Boot. Côté Flutter, les tests visent le contrat avec l'API et la règle d'alerte du PHQ-9.

## Point relevé en écrivant les tests

`Questionnaire.fromJson` transforme tout type autre que `PHQ9` en `GAD7`, et tout statut autre que `COMPLETED` en `SENT`, sans signaler d'erreur. Aujourd'hui ce n'est pas gênant, le backend ne renvoie que ces valeurs. Mais si un 3e questionnaire (par exemple l'EPDS, cf. `Perspective_EPDS.md`) était ajouté côté backend, il serait affiché à tort comme un GAD-7. Les autres modèles (`AppointmentStatusX`, `UserRoleX`…) lèvent au contraire une erreur explicite. Aucun test ne verrouille ce comportement, pour ne pas figer ce qui ressemble plutôt à une faiblesse.

## Pour la soutenance

Formulation possible pour la section Limites :

> « Côté Flutter, les tests automatisés se limitent à des tests unitaires des modèles (contrat avec l'API, règle d'alerte de l'item 9 du PHQ-9) et à un test de démarrage : les écrans ne sont couverts ni par des tests de widgets ni par des tests d'intégration. »

Si le jury demande pourquoi l'item 9 est testé à part : sur le PHQ-9, une réponse positive à cet item impose une évaluation du risque, quel que soit le score total. Un patient peut avoir 3/27 (dépression « minimale ») et avoir coché des idées suicidaires. Le test garantit que l'application ne se fie pas au score seul.
