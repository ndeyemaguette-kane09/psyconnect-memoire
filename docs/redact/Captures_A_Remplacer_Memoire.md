# Mémoire PsyConnect — captures à faire ou remplacer

> Mise à jour du 19/10/2026 : toutes les captures d'écran de l'app ont été remplacées par celles de la nouvelle interface (dossiers admin, patient, psy), les doublons ont disparu (chaque figure a sa propre image) et les légendes 3.5, 3.6, 3.18, 3.21, 3.24, 4.1, 4.2, 4.4, 4.5 et 4.6 ont été renommées. Les figures 3.9 et 4.8 montrent le garde-fou actuel (« Tu comptes. », numéro vert du ministère). Version d'avant : Memoire_PsyConnect_avant_captures_20261019.docx.
> Restent à faire : Fig. 3.7 (psy non validé), 3.33 (logo Docker), 4.7 (Postman), 4.9 (Zipkin), et la slide 11 du PowerPoint (ancienne capture du garde-fou).

Toutes les corrections de texte sont faites dans Memoire_PsyConnect.docx (26/09/2026). La version d'avant est gardée dans Memoire_PsyConnect_avant_corrections_20260926.docx.
Il ne reste que les images ci-dessous et deux points à compléter à la main.

## 1. Captures à faire (emplacements encore vides)

| Figure | Section | Quoi capturer |
|---|---|---|
| 3.7 | §3.2.3.2 | Accueil d'un psy pas encore validé, avec le bandeau « pas visible des patients » |
| 3.33 | §3.6 | Logo Docker (logo_docker.png, même format que les autres logos) |
| 4.7 | §4.5.2 | Postman : requête POST /appointments avec la réponse 201 |
| 4.9 | §4.5.4 | Zipkin (localhost:9411) : trace d'une confirmation de RDV avec les spans des différents services |

## 2. Capture obsolète à refaire (prioritaire)

| Figure | Problème | Quoi capturer |
|---|---|---|
| 3.9 | L'ancien message du garde-fou parle d'un « numéro vert santé mentale », ce qui contredit le §5.4.4 et le code actuel | Refaire la même scène avec l'app actuelle. Le message doit finir par « Tu comptes. » et citer le « numéro vert du ministère de la Santé » |
| 4.8 | Même image que 3.9 | Pour éviter le doublon : le résultat vert du test RiskDetectionServiceTest (IntelliJ ou `./gradlew test`), puisque la section parle de validation |

## 3. Images en double (même capture sous deux numéros)

| Figure | Image actuelle | Proposition |
|---|---|---|
| 3.5 « Confirmation d'un rendez-vous par le psychologue » | agenda vue semaine (même image que 3.21 et 4.4) | La demande en attente avec les boutons Accepter / Refuser |
| 4.4 « Agenda hebdomadaire du psychologue » | doublon de 3.21 | L'écran des disponibilités récurrentes, puis renommer la légende en conséquence |
| 3.24 « Validation des comptes psychologues » | doublon de 3.6 | La liste des psys en attente (3.6 montre déjà le détail d'un dossier) |
| 4.1 « Écran d'accueil du patient » | doublon de 3.18 | Le journal d'humeur ou l'accueil de Xalaat, puis renommer la légende |
| 4.2 « Liste des psychologues avec recommandations » | doublon de 3.19 | La fiche d'un praticien avec ses avis |
| 4.6 « Interface administrateur » | doublon de 3.23 | Les signalements ou les messages de support |

La Fig. 4.5 a été renommée « Suivi des questionnaires d'un patient (vue psychologue) » pour correspondre à l'image actuelle.

## 4. Captures facultatives (nouvelles sections du texte)

Le §4.3.2 présente maintenant les avis patients, les recommandations post-séance et le contact du support. Une capture de chacun peut être ajoutée si tu veux, mais le texte tient sans.

## 5. À compléter à la main

- **Jury :** remplacer les trois « A completer » en page de garde.
- **Sommaire et table des matières :** Word va proposer de mettre à jour les champs à l'ouverture. Répondre Oui, puis refaire F9 après avoir ajouté les images, pour que les numéros de page soient à jour.
- **Sources des chiffres de contexte :** ajouter une référence pour la prévalence de plus de 20 % (résumé), pour « moins d'une quarantaine de psychiatres », pour les 17 millions d'habitants et pour les 19 millions de SIM (ARTP).
- **Conseil :** si possible, faire toutes les captures dans la même session de l'app, pour que le design soit homogène d'une figure à l'autre.

## 6. PowerPoint (PsyConnect_Soutenance_15min.pptx)

| Slide | Quoi faire |
|---|---|
| 11 — Xalaat | L'image de droite (« Garde-fou déclenché ») est l'ancienne capture du garde-fou. Il faut la remplacer par la même nouvelle capture que la Fig. 3.9 du mémoire, sinon elle contredit le texte de la slide (« numéro vert du ministère »). |
| 10 — Démonstration | Insérer la vidéo de 3 minutes dans le cadre prévu (Insertion › Vidéo). |
