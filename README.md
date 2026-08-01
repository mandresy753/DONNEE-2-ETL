# Stockage — Qualité de l'air

## Villes couvertes

| Ville | Pays | Latitude | Longitude |
|---|---|---|---|
| Paris | FR | 48.8566 | 2.3522 |
| London | GB | 51.5074 | -0.1278 |
| Berlin | DE | 52.5200 | 13.4050 |
| Madrid | ES | 40.4168 | -3.7038 |
| Rome | IT | 41.9028 | 12.4964 |

(source : `data/cities.json`)

## `data/raw/` — data lake

Un fichier JSON par ville et par heure, réponse brute de l'API OpenWeatherMap
Air Pollution, jamais modifié ni supprimé. Organisé par dossier de date :
`data/raw/AAAA-MM-JJ/<ville>_HH-00-00.json`.

**Règle d'immutabilité** : aucun script ne modifie ni ne supprime jamais un
fichier de `data/raw/` après son écriture (`transform.py` ne fait que le
lire). `data/clean/aqi_clean.csv` est entièrement reconstructible depuis
`data/raw/` à tout moment :

```bash
rm data/clean/aqi_clean.csv
python -m scripts.transform.transform
```

## `data/clean/aqi_clean.csv` — fichier propre

Une ligne = une mesure horaire pour une ville. Régénéré en entier à chaque
run à partir de tout `data/raw/`.

| Colonne | Unité / format | Description |
|---|---|---|
| `city` | texte | Nom de la ville |
| `country` | code ISO 2 lettres | Pays |
| `latitude`, `longitude` | degrés décimaux | Coordonnées de la ville |
| `timestamp_utc` | ISO 8601, UTC | Horodatage de la mesure |
| `aqi` | entier, 1 à 5 | Indice de qualité de l'air OpenWeatherMap (1=Bon … 5=Très mauvais) |
| `co` | µg/m³ | Monoxyde de carbone |
| `no` | µg/m³ | Monoxyde d'azote |
| `no2` | µg/m³ | Dioxyde d'azote |
| `o3` | µg/m³ | Ozone |
| `so2` | µg/m³ | Dioxyde de soufre |
| `pm25` | µg/m³ | Particules fines PM2.5 |
| `pm10` | µg/m³ | Particules PM10 |
| `nh3` | µg/m³ | Ammoniac |

Validation (`scripts/transform/validator.py`) : `aqi` doit être entre 1 et 5,
tous les polluants doivent être ≥ 0 ; les lignes invalides sont filtrées
(pas de rejet du batch entier).

## Période couverte et trous connus

- **Période** : 2026-01-28 15:00 UTC → aujourd'hui (mise à jour horaire
  automatique), soit plus de 6 mois d'historique.
- **Trous connus** (heures manquantes, mêmes pour les 5 villes sauf mention
  contraire) — dus à des échecs ponctuels du run horaire (API indisponible,
  run GitHub Actions en échec/sauté) :

  | Période sans données | Durée | Villes concernées |
  |---|---|---|
  | 2026-02-15 01:00 → 2026-02-16 00:00 | 24h | Toutes |
  | 2026-02-21 01:00 → 2026-02-23 00:00 | 48h | Toutes |
  | 2026-03-01 01:00 → 2026-03-02 00:00 | 24h | Toutes sauf Madrid |
  | 2026-03-04 01:00 → 2026-03-05 00:00 | 24h | Toutes |
  | 2026-05-11 01:00 → 2026-05-12 00:00 | 24h | Toutes |
  | 2026-05-19 01:00 → 2026-05-20 00:00 | 24h | Toutes |
  | 2026-07-10 01:00 → 2026-07-11 00:00 | 24h | Toutes |
  | 2026-07-29 19:00 (1h) | 1h | Toutes |

  Total : 193 heures manquantes par ville (169 pour Madrid, qui a été
  extraite avec succès le 2026-03-01 contrairement aux 4 autres villes).

  Ces trous ont été vérifiés au niveau de `data/raw/` : les fichiers JSON
  correspondants sont absents (échec du run d'extraction horaire), il ne
  s'agit pas d'une perte de données lors de la transformation — le nombre
  de fichiers bruts (21 264) correspond exactement au nombre de lignes du
  CSV propre.

## Cohérence attendue

**Règle** : nombre de lignes de `fact_air_quality_hourly` ≈ nombre de villes
× nombre d'heures couvertes par la période.

- Période : 2026-01-28 15:00 UTC → 2026-08-01 15:00 UTC = **4 441 heures**
- Attendu : 4 441 × 5 villes = **22 205 lignes**
- Réel (au 2026-08-01) : **21 264 lignes**
  (Berlin/London/Paris/Rome : 4 248 chacune ; Madrid : 4 272)
- **Écart : 941 lignes**, entièrement expliqué par les trous ci-dessus
  (193 h × 4 villes + 169 h × 1 ville = 941), plus aucune autre perte —
  la validation (`validator.py`) n'a rejeté aucune ligne sur cette période
  (aucun `aqi` hors [1,5] ni polluant négatif rencontré à ce jour) et
  aucun doublon d'heure n'a été observé par ville.

## Schéma du data warehouse (Neon Postgres, schéma en étoile)

Voir `sql/create_dw.sql` pour le DDL complet.

- **`dim_date`** (`date_id` PK) : date calendaire, année, trimestre, mois, jour, jour de semaine, week-end.
- **`dim_time`** (`hour` PK) : heure 0-23 → période (Nuit / Matin / Après-midi / Soir).
- **`dim_location`** (`location_id` PK) : ville, pays, latitude, longitude.
- **`dim_aqi_category`** (`aqi` PK) : libellé et description de chaque niveau AQI (1 à 5).
- **`fact_air_quality_hourly`** (PK composite `location_id` + `measurement_timestamp`) : une ligne par mesure horaire, clés étrangères vers les 4 dimensions ci-dessus, colonnes de polluants (`co`, `no`, `no2`, `o3`, `so2`, `pm2_5`, `pm10`, `nh3`).

Chargement rejouable via `python -m scripts.load.load` (upsert sur les 3 tables).

## Connexion à la base

- Moteur : PostgreSQL (Neon, serverless)
- Variable d'environnement attendue : `NEON_DB_URL` (chaîne de connexion complète, ex. `postgresql://user:password@host/dbname?sslmode=require`)
- À définir dans `.env` en local (voir `.env.example`), ou dans les secrets GitHub Actions (`Settings > Secrets and variables > Actions`) pour l'exécution automatisée.
- Créer le schéma avant le premier chargement : exécuter `sql/create_dw.sql` sur la base cible.