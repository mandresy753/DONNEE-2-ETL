# Architecture

## Stack choisie

| Composant | Choix | Justification |
|---|---|---|
| **Orchestrateur** | GitHub Actions (`workflow_dispatch`), déclenché toutes les heures par un cron externe ([cron-job.org](https://cron-job.org)) qui appelle l'API GitHub | Gratuit, versionné avec le code, et le déclenchement externe évite les retards/sauts du scheduler `schedule` natif de GitHub Actions sous forte charge. |
| **Orchestrateur (backfill)** | Workflow GitHub Actions séparé (`backfill.yml`), déclenché manuellement avec un paramètre `months` | Sépare le run récurrent (léger, 1h) du run ponctuel et lourd (plusieurs mois d'historique), sans risquer un timeout sur le workflow horaire. |
| **Stockage brut (data lake)** | Fichiers JSON individuels par ville/heure dans `data/raw/`, versionnés dans le dépôt Git | Aucune infra externe à gérer ni payer ; chaque réponse API est conservée telle quelle, ce qui permet de rejouer `transform.py` à volonté sans jamais perdre la donnée source. |
| **Stockage nettoyé** | CSV unique `data/clean/aqi_clean.csv`, régénéré en entier à chaque run à partir de tout `data/raw/` | Un seul fichier facile à valider, à charger, et à ouvrir dans un tableur, sans dérive possible entre plusieurs fichiers partiels. |
| **Base / Data Warehouse** | PostgreSQL managé (Neon, serverless), schéma en étoile (`dim_date`, `dim_time`, `dim_location`, `dim_aqi_category`, `fact_air_quality_hourly`) | Neon offre un tier gratuit sans serveur à gérer ; le schéma en étoile facilite les agrégations (par ville, par heure, par catégorie AQI) pour la dataviz en aval. |
| **Chargement** | `load.py`, upsert (`ON CONFLICT ... DO UPDATE`) rejouable à chaque run | Recharger tout l'historique à chaque exécution est sans risque de doublon et permet de corriger a posteriori une ligne déjà chargée. |

## Flux du pipeline

```
OpenWeatherMap Air Pollution API
        │  extract.py / backfill.py
        ▼
data/raw/  (JSON brut, 1 fichier par ville × heure, jamais modifié)
        │  transform.py (nettoyage + validation)
        ▼
data/clean/aqi_clean.csv  (historique complet, régénéré à chaque run)
        │  load.py (upsert)
        ▼
Neon Postgres — data warehouse en étoile
```

## Villes couvertes

Paris (FR), London (GB), Berlin (DE), Madrid (ES), Rome (IT) — coordonnées dans `data/cities.json`.
