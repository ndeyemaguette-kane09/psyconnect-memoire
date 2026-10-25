# Questions UML — à relire avant la soutenance

Réponses aux questions qu'on s'est posées en refaisant les diagrammes (octobre 2026).
Les diagrammes sont dans `docs/redact/diagrammes_v2/`.

---

## 1. Cas d'utilisation

**Pourquoi un seul diagramme complet par acteur, sur deux colonnes ?**
Chaque diagramme montre toutes les fonctionnalités de l'acteur (34 pour le patient, 26 pour le psy, 16 pour l'admin),
regroupées par domaine (paquetages). Pour que tout tienne lisiblement sur une page, les paquetages sont sur deux colonnes.

**Pourquoi le bonhomme est dessiné deux fois ?** Avec deux colonnes, un seul acteur à gauche obligerait ses traits
à traverser les ellipses de gauche pour atteindre celles de droite. UML autorise à représenter le même acteur plusieurs
fois sur un diagramme pour la lisibilité ; une note le précise sous chaque diagramme.

**Pourquoi certains cas ne sont pas reliés à l'acteur ?** Ce sont des extensions (Reporter, Annuler, Réinitialiser son
mot de passe…). On y accède depuis le cas de base, qui est, lui, relié à l'acteur. Les diagrammes sont faits sous draw.io
(`docs/redact/diagrammes_v2/use_cases_admin_user_psy.drawio`).

**Pourquoi un diagramme par acteur ?** C'est ce que demande le canevas : « dessiner le diagramme des cas
d'utilisation par chaque acteur ».

**Include ou extend ?**
- `<<include>>` : toujours exécuté. Valider un psychologue inclut consulter son justificatif (obligatoire).
- `<<extend>>` : optionnel, sous condition. Consulter la preuve jointe étend traiter un signalement, car la preuve est facultative.

**Pourquoi Jitsi n'est plus un acteur ?** C'est un outil technique, pas un utilisateur du système. Il apparaît dans la séquence vidéo.

---

## 2. Diagrammes de classes

**Pourquoi 5 vues + une vue d'ensemble ?** 25 classes sur 6 microservices : impossible à lire sur une page.
La vue d'ensemble montre les paquets (un par microservice) et qui référence qui. Les 5 vues détaillent.
Les classes en gris « attributs omis » sont les points de raccord entre les vues.

**Trait plein / pointillé ?**
- Trait plein : vraie association JPA, dans la même base de données.
- Pointillé avec flèche : référence par identifiant (ex. `patientId`). Chaque microservice a sa propre base,
  donc pas de clé étrangère SQL entre services : on stocke l'identifiant et on interroge l'autre service.

**Pourquoi SupportMessage n'est relié à rien ?**
L'expéditeur peut être un patient OU un psychologue. On stocke `senderProfileId` + `senderRole`.
Le numéro seul ne dit pas dans quelle table chercher : c'est une référence polymorphe.
Un trait fixe vers PatientProfile serait faux la moitié du temps.

**Pourquoi Broadcast n'est relié à rien ?**
Une annonce s'adresse à un groupe (ALL, PATIENTS, PSYCHOLOGISTS), pas à une personne.
On ne stocke que l'audience et le nombre de destinataires. À l'envoi, le code crée une Notification
par destinataire dans notification-service : c'est elle qui porte le lien vers chaque personne.

**Pourquoi Payment → Appointment en 0..* et pas 0..1 ?** Un rendez-vous peut avoir un paiement échoué puis
un paiement réussi. Le code interdit seulement un 2e paiement réussi.

**Pourquoi Conversation et Message sont dans appointment-service ?** La messagerie est liée à la relation
de soin patient–psy ; on l'a regroupée là plutôt que de créer un 9e service.

---

## 3. Séquence : inscription

Quatre appels, parce que l'information est répartie entre deux services :
1. **Créer le compte** (auth-service) : email et pseudo libres ? mot de passe haché (BCrypt), User rôle PATIENT.
2. **Se connecter tout de suite** : les appels suivants vers user-service sont protégés, il faut un jeton JWT.
3. **Créer le profil commun** (UserProfile) : nom, prénom, téléphone, ville — commun à tout utilisateur.
4. **Créer le profil patient** (PatientProfile) : langue, mode anonyme, solde à 0.

À dire : « Le compte, qui sert à l'authentification, est dans auth-service. Le profil, qui sert au métier,
est dans user-service. Chaque service garde ses données. »

Piège : « Et si l'étape 3 échoue ? » → Le compte existe déjà : le patient se reconnecte et complète son profil.
Limite des microservices : pas de transaction unique entre deux bases.

---

## 4. Séquence : authentification

**Le bloc alt** : 3 issues possibles du login.
- Compte désactivé par l'admin → 403.
- Mot de passe incorrect → 400.
- Identifiants valides → jeton JWT signé (email, rôle, id), valable 24 h.

**La passerelle ne vérifie pas le jeton : est-ce une faille ? Non.**
Le jeton EST vérifié, mais par chaque microservice, à chaque requête (son propre filtre JWT).
C'est même plus sûr : si quelqu'un contourne la passerelle et appelle un service directement, il est quand même refusé.
À dire : « La passerelle ne fait que router. Chaque service revérifie le jeton : on ne fait confiance à aucun intermédiaire. »

**Pourquoi deux GET après la connexion ?**
Le jeton ne contient qu'une seule information d'identité : l'id du **compte** (authUserId, dans auth-service).
Mais pour utiliser l'appli, il faut les identifiants des **profils**, qui sont dans user-service :
- `GET /users/by-auth-user/{authUserId}` → l'id du **UserProfile** (partie commune : nom, téléphone…).
- `GET /patients/by-auth-user/{authUserId}` → l'id du **PatientProfile** (ou PsychologistProfile pour un psy),
  qui sert à réserver, payer, écrire dans le journal…

Comparaison simple : le jeton, c'est ta carte d'étudiante (numéro d'inscription). Pour aller à la bibliothèque,
il te faut aussi ta carte de lecteur, qui a un autre numéro. Les deux GET vont chercher ces numéros, une seule fois, à la connexion.

Si un prof dit qu'on pourrait faire un seul appel : il a raison, c'est une optimisation possible.
À dire : « On pourrait regrouper ces deux appels en un endpoint qui renvoie tous les identifiants.
Je ne l'ai pas fait car ça n'arrive qu'une fois par connexion, mais c'est simple à ajouter. »

---

## 5. Séquence : consultation vidéo

**Le alt « aucune session / session déjà en cours »** : celui qui clique en premier (patient OU psy) crée la session
et le salon unique. Le second récupère la session déjà ouverte, donc le même salon.

**Le verrou** : sert au cas où les deux cliquent exactement au même moment. Sans lui, chacun créait son propre salon
(c'était un vrai bug, corrigé).

**« Toutes les 5 min : créneau dépassé ? clôt la session »**
C'est une tâche automatique de session-service (`SessionExpiryScheduler`), lancée toutes les 5 minutes.
Quitter l'appel ne ferme pas la séance (pour qu'une coupure réseau ne la casse pas). Il fallait donc un autre
mécanisme pour la terminer. Pour chaque session encore ouverte, si la fin du rendez-vous est dépassée de plus de
30 minutes : session → COMPLETED, rendez-vous → COMPLETED, notification au patient.
C'est ce qui fait apparaître le rendez-vous dans les séances terminées et qui permet ensuite de laisser un avis.

---

## 6. Limites connues (à assumer)

- **Appel d'urgence (SOS)** : le salon est créé mais le psychologue n'est ni notifié ni doté d'un écran pour le rejoindre.
  Démonstrateur côté patient, documenté au §4.3.5 et §5.4.1. Ne pas le lancer en démo.
- **Paiement non vérifié avant l'appel vidéo** : session-service vérifie que le rendez-vous est CONFIRMED,
  mais pas qu'il est payé. Évolution prévue : session-service interroge payment-service avant d'ouvrir le salon.
- **Paiement** : si l'enregistrement échoue après le débit, le solde est recrédité (compensation). Point fort à défendre.

---

## 7. Le BPMN (figure 3.1)

**BPMN = Business Process Model and Notation.** Une notation pour dessiner un processus métier tel qu'il se
passe dans la réalité (le travail des gens), avec ou sans logiciel. Ici : la prise en charge d'un patient
AUJOURD'HUI, sans PsyConnect.

Les symboles :
- **Couloir** : un acteur (Patient, Psychologue). Chaque tâche est dans le couloir de celui qui la fait.
- **Cercle fin** : événement de début (« besoin d'aide ressenti »).
- **Rectangle arrondi** : une tâche (« appeler le cabinet »).
- **Losange avec un X** : passerelle exclusive = une décision, un seul chemin possible (« créneau libre ? »).
- **Cercle épais** : événement de fin. Il y en a deux : démarche abandonnée, ou séance terminée sans suivi.
- **Flèche pleine** : l'ordre des étapes.

Différence avec le diagramme d'activités UML : très proches visuellement. Le BPMN décrit le métier (comment
les gens travaillent), le diagramme d'activités décrit le comportement du système. C'est pour ça que le BPMN
est dans l'analyse de l'existant (3.1) et les activités dans la conception (3.3).

À dire : « Ce schéma BPMN montre le parcours actuel d'un patient : il peut abandonner dès la recherche, il dépend
du téléphone pour obtenir un créneau, il paie en espèces sans reçu, et rien n'assure le suivi entre les séances.
Chacun de ces points correspond à une fonctionnalité de PsyConnect. »

## 8. Pourquoi seulement 11 diagrammes dans le mémoire ?

Le canevas ne fixe pas de nombre. On a gardé ceux qu'on sait défendre : 3 cas d'utilisation (un par acteur),
3 classes (vue d'ensemble + identité + rendez-vous), 3 séquences (authentification, paiement, vidéo),
2 activités, + le BPMN. Les 18 diagrammes complets sont dans `docs/redact/Diagrammes_UML_complets.pdf`.

---

## 9. Les éléments de temps et les échéances automatiques

**« Est-ce que vos diagrammes représentent le temps ? »**
Oui, là où le temps déclenche quelque chose. En UML, on utilise l'**événement temporel** (le sablier). Dans le diagramme d'activités « Échéances automatiques » (Fig. 3.19), le sablier « Toutes les 5 minutes » montre qu'aucun acteur ne lance l'action : c'est l'écoulement du temps qui la déclenche. En BPMN, l'équivalent est l'**événement minuterie** (une horloge dans un cercle).

**Pourquoi je n'en mets pas partout ?** Une durée n'a sa place dans un diagramme que si elle change le comportement. « Le patient remplit le formulaire en 2 minutes » n'apporte rien. En revanche, « si le psychologue n'a pas confirmé 2 h avant, le rendez-vous est annulé » est une règle métier, donc je la représente.

**Les règles de temps de PsyConnect :**
- Une réservation se fait **au moins 2 h à l'avance**.
- Le psychologue peut accepter ou refuser **jusqu'à 2 h avant** la séance. Passé ce délai, la demande est annulée automatiquement, et le patient et le psychologue sont notifiés.
- Un rendez-vous confirmé mais non payé reçoit **un rappel de paiement** (une seule fois), puis il est annulé **1 h avant le début** et le créneau est libéré.
- Le patient qui annule **plus de 48 h avant** la séance est remboursé sur son portefeuille. En dessous de 48 h, il n'est pas remboursé. Dans les deux cas, le psychologue est notifié.
- On ne peut rejoindre la vidéo que si le rendez-vous est **confirmé et payé**, de 10 min avant à 30 min après le début. La session est fermée 30 min après la fin du créneau.

**« Pourquoi toutes les 5 minutes et pas en temps réel ? »** C'est un compromis : la vérification est légère, et 5 minutes de décalage sur une échéance de 1 h ou 2 h n'ont aucun impact pour l'utilisateur. Un déclenchement exact à la seconde demanderait de programmer une tâche par rendez-vous, ce qui est plus fragile.

**« Ces règles corrigent quoi ? »** Avant, une demande sans réponse du psychologue ou un rendez-vous jamais payé restait bloqué indéfiniment et occupait le créneau. Maintenant, chaque rendez-vous a toujours une issue.

**« Pourquoi “le psy ne répond pas” n'est pas une troisième branche du losange ? »** Un nœud de décision choisit entre des réponses données : accepter ou refuser. Ne rien faire n'est pas une réponse, c'est une absence d'action. En UML, on la représente par un événement temporel, le sablier, qui se déclenche à l'échéance (2 h avant la séance pour une demande en attente, 1 h avant pour un rendez-vous non payé). Le sablier n'a pas de flèche entrante parce qu'il est actif dès que le processus commence : il « surveille » en parallèle. Cela couvre aussi le patient dont le solde est insuffisant et qui ne recharge jamais.

---

## 10. Les relations entre cas d'utilisation

**« Quelle différence entre include et extend ? »**
- **«include»** : une étape qui fait **toujours** partie du cas de base. La flèche part du cas de base vers l'étape incluse. Exemples : *S'inscrire* (psy) inclut *Joindre son justificatif de licence* ; *Accéder à l'aide immédiate* inclut *Voir les numéros d'urgence*.
- **«extend»** : un prolongement **optionnel ou conditionnel**. La flèche part de l'extension vers le cas de base. Exemples : *Être remboursé sur son solde* étend *Annuler un rendez-vous* (seulement à plus de 48 h) ; *Recharger son solde* étend *Payer un rendez-vous* (si le solde est insuffisant) ; *Appeler un psychologue disponible* étend *Accéder à l'aide immédiate* (seulement si un psy est disponible) ; *Rédiger des notes cliniques* et *Envoyer un questionnaire* étendent *Consulter le dossier d'un patient*.

**« Pourquoi Réserver n'inclut pas Payer ? »** Parce qu'un include veut dire « toujours, dans la même interaction ». Or le paiement vient plus tard, après la confirmation du psy, et il peut ne jamais avoir lieu (refus, absence de réponse, patient qui renonce). Ce sont deux cas d'utilisation distincts.

**« Et “rejoindre la vidéo nécessite un RDV confirmé et payé” ? “laisser un avis après une séance terminée” ? »** Ce sont des **préconditions**, pas des relations. Un diagramme de cas d'utilisation ne montre pas l'ordre ni les conditions préalables : je les indique entre parenthèses sous le nom du cas, et elles sont détaillées dans les fiches descriptives (tableaux 3.1 à 3.3) et dans les diagrammes d'activités.

**« Pourquoi l'aide immédiate est à part ? »** Une urgence en santé mentale n'est pas une consultation comme les autres. Le paquetage *Aide immédiate (hors rendez-vous)* montre que le premier réflexe proposé est d'appeler les secours (SAMU, police, pompiers), et que l'appel gratuit à un psychologue disponible n'est qu'un prolongement possible. Limite assumée : le psychologue n'est pas encore alerté de l'appel entrant (perspective d'évolution).

**« Le mode anonyme, concrètement ? »** Le psychologue voit le pseudonyme du patient à la place de son nom, et le contact d'urgence lui est masqué. L'administrateur garde la vue complète pour la modération.

## 11. Questions probables issues de la relecture

**« Comment ml-service sait qui appelle, alors qu'il est en Python ? »** Il ne valide pas le JWT lui-même, et la passerelle non plus (elle ne fait que router). ml-service relaie le jeton du patient tel quel quand il demande les profils des psychologues à user-service, en repassant par la passerelle : c'est user-service qui vérifie le jeton et applique ses contrôles d'accès. ml-service ne détient aucun droit particulier.

**« Pourquoi le psychologue ne peut pas annuler un rendez-vous ? »** Choix délibéré : il peut **refuser** une demande en attente, mais une fois le rendez-vous confirmé et payé, seul le patient annule (avec remboursement selon le délai). Ça protège le patient d'une annulation de dernière minute. Perspective : une annulation psy avec remboursement intégral automatique.

**« D'où viennent les poids 0,6 / 0,25 / 0,15 de la recommandation ? »** Fixés empiriquement, pas appris : 0,6 pour la ressemblance entre le besoin du patient et le profil du psy (TF-IDF + cosinus), 0,25 pour la note moyenne (sur 5), 0,15 si le psy est dans la même ville. La pertinence passe avant tout. Seuls les psys validés et disponibles sont classés. Je l'assume : sans utilisateurs réels, il n'y a pas de données pour les apprendre. Perspective : ajuster les poids à partir des réservations effectives.

**« Et la protection des données personnelles ? »** Au Sénégal, c'est la loi n° 2008-12 du 25 janvier 2008, contrôlée par la CDP (Commission de Protection des Données Personnelles). Des données de santé mentale sont des données sensibles : une mise en production supposerait une déclaration / autorisation auprès de la CDP, un hébergement maîtrisé et le consentement explicite. Le prototype pose les bases (JWT, rôles, mode anonyme, contact d'urgence masqué), mais la conformité n'est pas faite, et c'est écrit dans les limites.

**« Avez-vous testé avec de vrais patients ? »** Non, et c'est dit dans le mémoire. Les tests sont techniques : unitaires, parcours Postman (31 requêtes, 47 tests réussis), traces Zipkin, et tests manuels de l'application. Une étude avec de vrais utilisateurs demande un cadre éthique et l'accord d'une structure de soins : c'est une perspective.

**« Sur quels appareils l'application tourne ? »** Testée sur deux iPhone (XR et 13 Pro Max). Flutter permet de compiler pour Android, mais je ne l'ai pas validé sur un appareil Android : limite assumée.

**« Le bouton d'urgence, il alerte vraiment quelqu'un ? »** C'est un démonstrateur : il affiche les numéros (1515 SAMU, 17 Police, 18 Pompiers) et propose l'appel à un psychologue disponible, mais le psychologue n'est pas encore notifié en temps réel. Le mémoire le présente comme tel.
