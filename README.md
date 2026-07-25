# ETL Qualité de l'air

Pipeline ETL (extract → transform → load) qui collecte la qualité de l'air
(OpenWeatherMap Air Pollution API) pour 5 villes et alimente un entrepôt de
données en étoile sur Postgres (Neon).

## Structure

```
scripts/
  extract/     extraction "live" (extract.py) et historique (backfill.py)
  transform/   nettoyage, validation, écriture du CSV propre
  load/        chargement dans le data warehouse (dim_date, dim_location, fact_air_quality_hourly)
data/
  raw/         fichiers JSON bruts en attente de traitement
  processed/   fichiers JSON bruts déjà traités (archivés par transform.py)
  clean/       CSV nettoyé, prêt à charger
sql/
  create_dw.sql  schéma du data warehouse
.github/workflows/
  etl_hourly.yml   extract → transform → load, toutes les heures à la 7e minute
  backfill.yml     backfill manuel (workflow_dispatch), 3 mois d'historique par défaut
```

## Configuration

1. Copier `.env.example` en `.env` et renseigner `API_KEY` (OpenWeatherMap) et
   `NEON_DB_URL` (chaîne de connexion Postgres Neon).
2. `pip install -r requirements.txt`
3. Créer le schéma : exécuter `sql/create_dw.sql` sur la base Neon.

## Utilisation locale

Toutes les commandes se lancent **depuis la racine du dépôt** (import en
package Python) :

```bash
python -m scripts.extract.extract       # extraction live (5 villes, instant t)
python -m scripts.extract.backfill      # backfill des 3 derniers mois (historique)
python -m scripts.transform.transform   # nettoyage + validation + CSV
python -m scripts.load.load             # chargement dans le data warehouse
```

Le backfill interroge l'endpoint `air_pollution/history` par tranches de
15 jours (au lieu d'une requête par heure), ce qui limite le nombre d'appels
API. Chaque lecture horaire est éclatée en un fichier JSON individuel, au
même format que l'extraction live, pour que `transform.py` n'ait pas à
distinguer les deux sources.

`transform.py` archive les fichiers `data/raw/` traités avec succès vers
`data/processed/` : chaque exécution ne retraite donc que les nouveaux
fichiers, même après un gros backfill initial.

## GitHub Actions

Ajouter deux secrets dans **Settings > Secrets and variables > Actions** :
`API_KEY` et `NEON_DB_URL`.

- `etl_hourly.yml` tourne automatiquement chaque heure (cron `7 * * * *`).
- `backfill.yml` se lance manuellement depuis l'onglet Actions (bouton
  "Run workflow"), avec un paramètre optionnel `months` (3 par défaut).

Les deux workflows committent `data/raw/`, `data/processed/` et
`data/clean/aqi_clean.csv` dans le repo juste après l'étape `transform`
(avant `load`), avec le message `[skip ci]` pour ne pas redéclencher de
workflow. Comme `transform.py` écrase `aqi_clean.csv` avec uniquement les
nouvelles lignes de chaque run (voir plus haut), son contenu reflète
toujours le dernier lot traité — l'historique complet reste consultable via
`git log`. Ça implique un commit automatique par exécution (donc environ un
par heure), et un repo qui grossit avec le temps puisque chaque fichier JSON
brut (`data/raw/`, archivé ensuite dans `data/processed/`) est versionné
individuellement — à surveiller si le clone devient volumineux.

Note : les workflows planifiés (`schedule`) de GitHub Actions peuvent être
retardés en cas de forte charge sur la plateforme, et sont automatiquement
désactivés si le dépôt reste inactif (aucun commit) pendant 60 jours — il
faut alors les réactiver manuellement depuis l'onglet Actions.
