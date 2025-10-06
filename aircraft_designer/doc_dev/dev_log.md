# Journal de dǸveloppement

## 2025-10-05 — Database: Filtre avancé
- Ajout du filtre avancé (caractéristique + opérateur + valeur/plage) limité à la liste d’avions.
- Comparaison numérique/texte robuste et indépendante de la recherche simple.
- UI: groupe "Filtre avancé" au-dessus de la liste d’avions (opérateurs =, ≠, >, ≥, <, ≤, in [a,b]).

## 2025-10-06 �?" UI: SǸcurisation des QComboBox (molette)
- Ajout de `NoWheelComboBox` pour empǦcher la molette de changer la sǸlection quand la liste n'est pas ouverte.
- IntǸgration dans la colonne �� CaractǸristique �� du tableau des caractǸristiques (via setCellWidget ou dǸlǸguǸ selon le module).
- CrǸation de `NoWheelComboDelegate` quand `QTableView` est utilisǸ.
- Aucun changement de logique de sauvegarde ; comportement inchangǸ lorsque la liste est dǸroulǸe.

- 2025-09-12 ??" Ajout : crǸateur de raccourci Bureau cross-platform
  - CrǸation de tools/shortcut_creator.py (Windows .lnk via PowerShell/COM; Linux .desktop; macOS .app via osacompile avec fallback .command).
  - CrǸation de scripts/create_desktop_shortcut.py (CLI).
  - DǸtection de l�?TexǸcutable packagǸ dans dist/, sinon fallback python main.py.
  - Gestion d�?Tic��ne optionnelle (dǸfaut dans assets/).
  - Tests manuels effectuǸs (voir section Tests dans ce prompt).

- 2025-09-12 ??" Ajout du module Conceptual Sketches permettant de stocker des images et croquis par projet.
- 2025-09-12 ??" Module Stat v1
  - portǸe : crǸation du module Stat pour analyses statistiques par projet.
  - fichiers crǸǸs :
    - modules/stat/__init__.py
    - modules/stat/stat_module.py
    - modules/stat/stat_view.py
    - modules/stat/stat_controller.py
    - modules/stat/stat_models.py
    - modules/stat/stat_io.py
    - modules/stat/stat_plots.py
    - core/paths.py
  - principales fonctionnalitǸs :
    - gestion d�?Tensembles de sǸlection
    - statistiques descriptives, histogramme, boxplot et scatter
    - export Excel et graphes PNG
  - dǸpendances : PyQt5, pandas, numpy, matplotlib, openpyxl
- 2025-09-11 ??" Module "Technologies �� utiliser"
  - CrǸation du module indǸpendant liǸ aux projets.
  - CatǸgories et options Ǹditables (CRUD).
  - SǸlections par cases �� cocher + justification texte.
  - Persistance JSON par projet avec Ǹcriture atomique.
  - IntǸgration UI (onglet/menu) + raccourcis (Ctrl+S, Ctrl+Z).
  - Stub d'export (CSV via DataFrame).
- 2025-09-08 : Mise en place du c�"ur du logiciel (gestion de projet, chargement de modules, interface PyQt5).
- 2025-09-09 : Module Cahier des charges / Nouveau concept �?" UI avec 2 onglets, bouton convertir, persistance JSON, intǸgration
navigation, test de sauvegarde/chargement.
- 2025-09-12 ??" Ajout du module **Database** (UI + logique compl��te).
  - Structure en 3 colonnes, repo SQLite global, import/export JSON.
  - IntǸgration au menu principal, logs, validations et dialogues.
## [2025-09-12] Module Constraint Analysis v1 (sans marges)
- CrǸation du module `modules/constraint_analysis/` : UI PyQt5, calculs (TO, LDG, Climb, Cruise, Turn, Ceiling), enveloppe et point recommandǸ (sans marges).
- TracǸ Matplotlib avec zone faisable, export PNG/SVG.
- Persistance par projet via `state_manager.py` (JSON).
- Export Excel avec feuilles Inputs/Curves/Envelope/Summary et insertion du graphique.
- IntǸgrations : stub import Database et Tech Packs, enregistrement dans le registre de modules.
## [2025-10-05] Database - Import JSON natif
- Remplacement de la boǩte d'import personnalisǸe par `QFileDialog.getOpenFileName` (boǩte native Windows).
- Ajout de `QSettings` pour mǸmoriser le dernier dossier d'import.
- Gestion d'erreurs : `JSONDecodeError` et exceptions gǸnǸriques avec `QMessageBox`.
- Connexion de l'action "Importer" �� `DatabaseWidget.import_json`.
- Nettoyage : suppression des anciennes boǩtes de dialogue d'import non utilisǸes.
- Tests manuels OK : filtre .json, dossier mǸmorisǸ, messages d'erreur/succ��s.


