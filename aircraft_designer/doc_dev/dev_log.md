# Journal de développement

- 2025-09-13 — Ajout : script de packaging PyInstaller
  - Création de `scripts/build_executable.py`.
  - Génère un exécutable (onefile par défaut) ou un dossier onedir.
  - Gestion optionnelle de l'icône et nettoyage build/dist.
  - Ajout automatique des ressources `assets/` et `ui/` si présents.
- 2025-09-12 — Ajout : créateur de raccourci Bureau cross-platform
  - Création de tools/shortcut_creator.py (Windows .lnk via PowerShell/COM; Linux .desktop; macOS .app via osacompile avec fallback .command).
  - Création de scripts/create_desktop_shortcut.py (CLI).
  - Détection de l’exécutable packagé dans dist/, sinon fallback python main.py.
  - Gestion d’icône optionnelle (défaut dans assets/).
  - Tests manuels effectués (voir section Tests dans ce prompt).

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
