# Décisions de design — octobre 2026

Validé avec les maquettes du canevas « PsyConnect — pistes d'identité ». Ne pas revenir dessus sans raison forte.

## Ce qu'on garde
- Palette : ivoire très clair `#FAF7F2` (fond), blanc `#FFFFFF` (surfaces), encre `#22201C`, gris texte `#6B645A`.
- Une couleur, une fonction : vert profond `#1E4D43` = agir, confirmer ; terre cuite `#B5532F` = urgence, annulé, réponse à risque ; ocre `#D2A04A` = en attente, à faire.
- Police unique : Nunito Sans. La hiérarchie vient du gras et de la taille.
- Navigation basse avec icônes + libellés, bouton central de recherche en arche.

## Règles de composition
- Pas de traits fins pour séparer : de l'espace.
- Au maximum un bloc vert par écran, pour ce qui compte maintenant.
- Surfaces blanches seulement pour regrouper des lignes cliquables.
- Les informations simples vont directement sur l'ivoire.
- Pas de pastilles « badge » : une phrase courte, colorée si besoin.
- Statuts (confirmée, en attente, annulée, à faire) : étiquette pleine, texte blanc, coins à 6 px, jamais de fond pastel. Vert `#1E4D43`, ocre foncé `#9A6B12`, terre cuite foncée `#A2461F` (contraste suffisant pour le blanc).
- Pas d'étiquettes en majuscules espacées.
- Pas de « Dr. » devant les noms des psychologues.

## Éléments propres à PsyConnect
- L'arche : avatars, date sélectionnée, bouton central de navigation. Les boutons d'envoi restent ronds, comme partout.
- Avatars : silhouette dans une arche, couleur calculée depuis l'identifiant du psy (toujours la même). Gardés pour le MVP, pas prioritaires.
- Xalaat : icône de discussion, pas de message d'accueil (la mention « Rien n'est enregistré » suffit). Ses messages s'écrivent sur la page, ceux du patient dans une bulle. Le garde-fou de crise s'affiche dans un bloc sombre signé « Message de l'équipe PsyConnect, pas de l'IA », avec des boutons d'appel.
- Humeurs en formes (du losange au cercle), réservées au journal.

## Écrans
- Portefeuille : solde en grand sur l'ivoire, rangée de 4 actions, seul « Recharger » en vert.
- Accueil : Xalaat accessible en permanence, plus de jauges d'humeur.
- Urgence : bloc terre cuite doux en bas de l'accueil, toujours visible.

## Questionnaire dans la conversation
- Affiché dans le fil de messages par fusion côté Flutter : l'entité `Questionnaire` porte déjà `psychologistId`, `patientId` et `sentAt`. Aucun changement backend, aucun changement des diagrammes UML.

## À faire hors code
- Remplacer les captures d'écran du mémoire après la refonte (voir `redact/Captures_A_Remplacer_Memoire.md`).
- Ajouter aux perspectives du mémoire : extension aux psychiatres (ordonnances, prescriptions), les psychologues ne prescrivant pas.
