# TP2 — Pipeline CI/CD

> **Carte(s) contexte tirée(s)**
>
> | Carte | Contenu |
> |---|---|
> | Carte contexte | _À compléter : recopier le texte exact de la carte_ |
> | Carte incident 1 | _À compléter si reçue (voir [docs/incidents.md](docs/incidents.md))_ |
> | Carte incident 2 | _À compléter si reçue_ |

Plateforme qui met en relation des producteurs avec des restaurants et des particuliers.
Ce dépôt contient l'API, son infrastructure conteneurisée et la chaîne de livraison CI/CD
reconstruite après l'incident d'août (14 h de commandes bloquées, version en production inconnue).

## Équipe

| Membre | Rôle |
|---|---|
| Baptiste | Lead dev — administrateur du dépôt |
| _Membre 2_ | Développeur |
| _Membre 3_ | Développeur |
| _Membre 4_ | Développeur |

## Lancer le projet en local

Prérequis : Docker et Docker Compose.

```bash
# 1. Créer le fichier d'environnement local (jamais commité)
cp .env.example .env
#    puis renseigner les valeurs dans .env

# 2. Démarrer l'API et PostgreSQL
docker compose up --build -d

# 3. Charger les données initiales (1 200 produits)
docker compose exec api <commande-de-seed>

# 4. Vérifier que le service répond et quelle version tourne
curl http://localhost:8000/health
```

Arrêter : `docker compose down` (ajouter `-v` pour supprimer aussi les données).

## Endpoints

| Méthode | Route | Description |
|---|---|---|
| GET | `/health` | État du service + version et commit déployés |
| GET | `/products` | Liste des produits |
| POST | `/orders` | Création d'une commande |

## Documentation

| Document | Contenu |
|---|---|
| [docs/risques.md](docs/risques.md) | Analyse des risques (gravité × effort) |
| [docs/adr/0001-strategie-branches.md](docs/adr/0001-strategie-branches.md) | Stratégie de branches |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Règles de contribution, revue, DoD, secrets |
| [docs/config/](docs/config/) | Captures de la configuration GitHub |
| [docs/pipeline.md](docs/pipeline.md) | Conception du pipeline et procédure de retour arrière |
| [docs/releases/](docs/releases/) | Plan de la US-42 et fiches de mise en production |
| [docs/incidents.md](docs/incidents.md) | Journal des cartes incident |

## Règles essentielles

- Aucun push direct sur `main` : tout passe par une pull request relue (voir [CONTRIBUTING.md](CONTRIBUTING.md)).
- Aucun secret dans le dépôt : `.env` est ignoré, les secrets vivent dans GitHub Secrets.
- Chaque version déployée est taguée `vX.Y.Z` ; `GET /health` indique la version en cours.
