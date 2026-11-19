# TP2 — Pipeline CI/CD

> **Contexte de l'équipe :** une équipe de **2 développeurs**.

Plateforme qui met en relation des producteurs avec des restaurants et des particuliers.
Ce dépôt contient l'API, son infrastructure conteneurisée et la chaîne de livraison CI/CD
reconstruite après l'incident d'août (14 h de commandes bloquées, version en production inconnue).

## Groupe de TP

- CERFAUX Baptiste
- PASQUALINI Pierre
- CHERBONNIER Aymeric
- ORTS Matéo

**Équipe incarnée :** une équipe de **2 développeurs**. Les règles et le processus du dépôt sont conçus pour ces 2 développeurs, même si les 4 membres du groupe contribuent au dépôt.

## Lancer le projet en local

Prérequis : Docker et Docker Compose.

```bash
# 1. Créer le fichier d'environnement local (jamais commité)
cp .env.example .env
#    puis renseigner les valeurs dans .env

# 2. Démarrer l'API et PostgreSQL
docker compose up --build -d

# 3. Charger les données initiales (1 200 produits)
docker compose exec api python scripts/seed.py

# 4. Vérifier que le service répond et quelle version tourne
curl http://localhost:8000/health
```

Arrêter : `docker compose down` (ajouter `-v` pour supprimer aussi les données).

## Endpoints

| Méthode | Route | Description |
|---|---|---|
| GET | `/health` | État du service + version et commit déployés |
| GET | `/products` | Liste des produits (avec leur stock) |
| PUT | `/products/{id}/stock` | Déclaration du stock d'un produit par le producteur |
| POST | `/orders` | Création d'une commande (refusée avec un message clair si elle dépasse le stock déclaré) |

## Environnements déployés

| Environnement | Adresse | Déploiement |
|---|---|---|
| Staging | `http://localhost:8001/health` | Automatique à chaque merge sur `main` |
| Production | `http://localhost:8000/health` | Tag `vX.Y.Z` + approbation (voir [docs/pipeline.md](docs/pipeline.md)) |

Le serveur est un poste de l'équipe équipé d'un runner GitHub Actions self-hosted (voir [docs/releases/initial.md](docs/releases/initial.md)).

## Documentation

| Document | Contenu |
|---|---|
| [docs/risques.md](docs/risques.md) | Analyse des risques (gravité × effort) |
| [docs/adr/0001-strategie-branches.md](docs/adr/0001-strategie-branches.md) | Stratégie de branches |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Règles de contribution, revue, DoD, secrets |
| [docs/config/](docs/config/) | Captures de la configuration GitHub |
| [docs/pipeline.md](docs/pipeline.md) | Conception du pipeline et procédure de retour arrière |
| [docs/releases/](docs/releases/) | Plan de la US-42 et fiches de mise en production |
| [docs/incidents.md](docs/incidents.md) | Journal des incidents |

## Règles essentielles

- Aucun push direct sur `main` : tout passe par une pull request relue (voir [CONTRIBUTING.md](CONTRIBUTING.md)).
- Aucun secret dans le dépôt : `.env` est ignoré, les secrets vivent dans GitHub Secrets.
- Chaque version déployée est taguée `vX.Y.Z` ; `GET /health` indique la version en cours.
