# Journal de développement

- 2025-09-12 — Ajout du module Conceptual Sketches permettant de stocker des images et croquis par projet.
- 2025-09-12 — Module Stat v1
  - portée : création du module Stat pour analyses statistiques par projet.
  - fichiers créés :
    - modules/stat/__init__.py
    - modules/stat/stat_module.py
    - modules/stat/stat_view.py
    - modules/stat/stat_controller.py
    - modules/stat/stat_models.py
    - modules/stat/stat_io.py
    - modules/stat/stat_plots.py
    - core/paths.py
  - principales fonctionnalités :
    - gestion d’ensembles de sélection
    - statistiques descriptives, histogramme, boxplot et scatter
    - export Excel et graphes PNG
  - dépendances : PyQt5, pandas, numpy, matplotlib, openpyxl
- 2025-09-11 — Module "Technologies à utiliser"
  - Création du module indépendant lié aux projets.
  - Catégories et options **éditables** (CRUD).
  - Sélections par cases à cocher + justification texte.
  - Persistance JSON par projet avec écriture atomique.
  - Intégration UI (onglet/menu) + raccourcis (Ctrl+S, Ctrl+Z).
  - Stub d'export (CSV via DataFrame).
- 2025-09-08 : Mise en place du cœur du logiciel (gestion de projet, chargement de modules, interface PyQt5).
- 2025-09-09 : Module Cahier des charges / Nouveau concept — UI avec 2 onglets, bouton convertir, persistance JSON, intégration
navigation, test de sauvegarde/chargement.
- 2025-09-12 — Ajout du module **Database** (UI + logique complète).
  - Structure en 3 colonnes, repo SQLite global, import/export JSON.
  - Intégration au menu principal, logs, validations et dialogues.
## [2025-09-12] Module Constraint Analysis v1 (sans marges)
- Création du module `modules/constraint_analysis/` : UI PyQt5, calculs (TO, LDG, Climb, Cruise, Turn, Ceiling), enveloppe et point recommandé (sans marges).
- Tracé Matplotlib avec zone faisable, export PNG/SVG.
- Persistance par projet via `state_manager.py` (JSON).
- Export Excel avec feuilles Inputs/Curves/Envelope/Summary et insertion du graphique.
- Intégrations : stub import Database et Tech Packs, enregistrement dans le registre de modules.
