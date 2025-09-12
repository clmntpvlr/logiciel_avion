# Liste des tâches

## En cours
- [ ] Créer le module technologies (catégories éditables, persistance JSON, export stub)
- [ ] Intégrer le module Database avec le futur module d’analyses statistiques (sélections par projet).
- [ ] Valider l’ergonomie avec des jeux de données réels.
- [ ] Améliorer la recherche (filtre multi-champs, RegEx).
- [ ] Ajouter un export CSV des valeurs avion x caractéristiques.
- [ ] Créer le module `Statistics` pour effectuer des analyses personnalisées sur la base de données commune, avec sauvegarde des sélections propres à chaque projet.
- [ ] Intégrer pleinement l’import depuis la Database (mapping champs + validations)
- [ ] Intégrer les Tech Packs (deltas sur CLmax, e, Cd0) avec UI dédiée
- [ ] Ajouter tests unitaires légers sur constraint_core (plages W/S, cohérence enveloppe)
- [ ] Brancher “Verrouiller comme cible de projet” sur le cœur projet (si API)

## À faire
- [ ] Export XLSX natif (ou via module global d’export)
- [ ] Internationalisation des libellés UI
- [ ] Tests unitaires étendus du technologies_model
- [ ] Liaison aval avec modules d’optimisation/dimensionnement

## Terminée
- [2025-09-09] Créer le module `cahier_des_charges` avec ses deux sous-parties
- [2025-09-12] Créer le module `database` (UI + logique)
- [2025-09-12] Créer le module `stat`
- [2025-09-12] Créer le module `Conceptual Sketches`
- [x] Créer le module constraint_analysis v1 (UI, calculs, export, persistance) — sans marges

## Idées / Backlog
- Corrélations multi-variables et régressions simples
- Graphes comparatifs multi-ensembles
- Templates d’analyses réutilisables
