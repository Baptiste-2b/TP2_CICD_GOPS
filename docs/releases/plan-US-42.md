# Plan — US-42 Gestion du stock

## User story

> En tant que producteur, je déclare un stock pour chacun de mes produits, afin qu'une commande qui dépasse ce stock soit refusée avec un message clair.

Contrainte de mise en production : revenir à la version précédente en moins de 5 minutes.

## Décision : stock non déclaré = aucune limite

| Valeur de `stock` | Signification | Commande |
|---|---|---|
| `NULL` | Stock non déclaré par le producteur | Acceptée (comportement actuel) |
| `0` | Stock déclaré, épuisé | Refusée (409, message clair) |
| `n > 0` | Stock déclaré | Acceptée si quantité ≤ n, puis stock décrémenté |

**Justification :**
- **Ne pas reproduire l'incident d'août** : un stock par défaut à `0` bloquerait toutes les commandes des produits existants dès la mise en production, jusqu'à ce que chaque producteur déclare son stock.
- **La user story est respectée** : une commande est refusée quand elle dépasse le stock *déclaré*.
- **Rollback simple (R3)** : la migration ajoute seulement une colonne vide ; l'ancienne version de l'API fonctionne avec la nouvelle base, le retour arrière ne nécessite pas de restauration.

## Découpage en tâches

| Tâche | Responsable | Branche | Contenu | Dépend de |
|---|---|---|---|---|
| **T1** — Stock en base | Mateo | `feat/stock-en-base` | Migration `002_stock.sql`, stock dans le seed, `GET /products` renvoie le stock | — |
| **T2** — Déclarer le stock | Pierre | `feat/declaration-stock` | `PUT /products/{id}/stock` (404 produit inconnu, 422 stock négatif) + tests | T1 |
| **T3** — Refuser une commande hors stock | Aymeric | `feat/refus-commande-hors-stock` | `POST /orders` vérifie et décrémente le stock, 409 avec message clair + tests | T2 |
| **T4** — Pipeline de déploiement | Baptiste | `feat/pipeline-deploiement` | Push GHCR, staging + test de fumée, production avec approbation, rollback | — |

**Ordre :** T1 et T4 en parallèle → T2 → T3. T2 et T3 modifient les mêmes fichiers (`app/main.py`, `tests/test_api.py`), elles sont donc faites l'une après l'autre pour éviter les conflits.

## Suivi

- Une issue GitHub par tâche, assignée à son responsable.
- Une branche et une pull request par tâche, qui ferme l'issue (`Closes #n`).
- Chaque pull request respecte [CONTRIBUTING.md](../../CONTRIBUTING.md) : CI verte, 1 approbation, Definition of Done.
