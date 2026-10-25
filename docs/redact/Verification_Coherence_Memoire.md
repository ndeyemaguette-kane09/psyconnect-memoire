# Vérification de cohérence — Memoire_PsyConnect.docx vs code

> **Statut 26/09 :** les corrections de texte (points 3 à 8 et « fonctionnalités absentes ») sont faites dans le .docx. Ce qui reste (captures, jury, sources) est dans Captures_A_Remplacer_Memoire.md.

Vérifié le 26/09/2026 sur la version du mémoire du 24/09 et le code actuel (y compris les modifications non commitées).

## À corriger avant impression

1. **Figures 3.9 et 4.8 — capture du garde-fou obsolète.** Elle montre l'ancien message (« numéro vert santé mentale du ministère », texte sans accents, renvoi vers la réservation). Le code actuel dit « numéro vert du ministère de la Santé », ce que confirme le §5.4.4 (pas de ligne dédiée santé mentale au Sénégal). En l'état, la figure contredit le texte. → Refaire la capture.
2. **Emplacements vides :** Fig. 3.7 (bandeau d'attente psy), Fig. 3.33 (logo Docker), Fig. 4.7 (Postman), Fig. 4.9 (Zipkin) ; jury « A completer » ×3 ; consignes « Ctrl+A → F9 » laissées dans le Sommaire et la Table des matières.
3. **§4.3.3 « Marquer comme suivi » :** le lien n'est plus créé librement. user-service exige maintenant un rendez-vous accepté (CONFIRMED ou COMPLETED) entre le psy et le patient. → Ajouter cette condition.
4. **§4.3.1 structure Flutter :**
   - « chaque feature expose ses propres providers spécialisés » est faux : il n'y a qu'un seul Provider (AuthProvider, déclaré dans app.dart, pas dans main.dart) ;
   - le wallet est dans `features/payment/`, pas dans `patient/` ;
   - toutes les features n'ont pas models/services/screens/widgets (ex. `home/` n'a que `screens/`).
5. **§4.3.2 flux de réservation :** « sélection → créneau → confirmation et paiement » laisse penser que le patient paie en réservant. En réalité (et au §3.2.3.1), il paie **après** la confirmation du psy : payment-service refuse tout paiement si le RDV n'est pas CONFIRMED. → Reformuler.
6. **§4.4 extrait docker-compose :** le mémoire affiche `JWT_SECRET: ${JWT_SECRET}`, mais le vrai fichier met le secret en clair. → Soit sortir le secret dans un `.env`, soit le signaler dans les limites (§5.3).
7. **§1.5 Plan :** il annonce des « schémas de bases de données » au chapitre 3, mais ils n'y figurent pas. → Retirer la mention ou ajouter les schémas.
8. **Figures en double / légendes décalées :**
   - agenda psy vue semaine : utilisé 3 fois (3.5, 3.21, 4.4), et en 3.5 sous la légende « Confirmation d'un rendez-vous » ;
   - mêmes images en 3.6/3.24, 3.18/4.1, 3.19/4.2, 3.23/4.6 ;
   - la Fig. 4.5 est légendée « Fiche de suivi d'un patient », mais l'image montre les questionnaires vus par le psy.

## Fonctionnalités présentes dans le code mais absentes du mémoire

- **Avis patients sur les psychologues** (ReviewController) : le §4.2.6 parle de « note moyenne » dans le score ML sans jamais expliquer d'où elle vient.
- **Recommandations post-séance** du psy au patient (`/session-recommendations`, appointment-service).
- **Messages au support admin** (« Contacter l'administration », SupportMessage, et le type de notification SUPPORT_REPLY, qui fait partie des 9 types annoncés).
- **Sécurité du paiement :** le montant est maintenant lu côté serveur depuis le tarif du psy (le client ne l'impose plus), et le remboursement est revérifié dans payment-service (propriétaire, statut CANCELLED, 48 h). C'est un bon argument à ajouter au §3.3.3 ou au §5.2.

## Point de rigueur

- Plusieurs chiffres de contexte n'ont pas de référence : > 20 % de prévalence (résumé), moins de 40 psychiatres, 17 M d'habitants, 19 M de SIM (ARTP). → Ajouter des références dans la bibliographie.
- 15 fichiers backend + docker-compose.yml sont modifiés mais **pas commités** (garde-fou, paiement, suivi patient, route ML). Le mémoire décrit ces corrections comme faites. → Committer avant la soutenance.

## Vérifié conforme

8 microservices (7 Spring Boot 3.5 / Java 17 + ml-service FastAPI) et leurs ports ; 13 conteneurs dans Compose ; 6 bases PostgreSQL 16 ; images eclipse-temurin:17-jre ; JWT de 24 h validé dans chaque service (la gateway ne fait que router) ; Resilience4j retry + circuit breaker (NotificationClient conforme à l'extrait) ; Zipkin sur 7 services + gateway + Eureka ; qwen2.5:3b via Spring AI, timeout de 90 s contre 15 s ; garde-fou (SAMU 1515, 800 00 50 50, 17, 18) avec un test auto d'environ 19 phrases, et les 3 défauts cités sont bien corrigés ; ML avec score 0,6/0,25/0,15, NumPy sans scikit-learn, psys vérifiés et disponibles uniquement ; rappel 10 min avant ; bouton Rejoindre de −10 à +30 min ; remboursement ≥ 48 h, annulation par le patient seul ; verrou synchronized dans session-service ; 9 types de notif ; notif de fin de session envoyée au patient seulement ; code de reset à 6 chiffres haché ; justificatif de 20 Mo max ; psy non approuvé connecté avec un bandeau ; nav patient Accueil/RDV/Messages/Profil + bouton de recherche central ; Dart ^3.6.1 ; statuts et snippets Appointment/Controller conformes.
