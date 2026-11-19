#!/usr/bin/env bash
# Déploie une image de l'API sur un environnement du serveur, puis lance le test de fumée.
# Le script échoue (code de sortie non nul) si une étape échoue ou si le service ne répond pas.
#
# Usage : deploy/deploy.sh <staging|production> <image complète> <version attendue>
# Variable d'environnement requise : POSTGRES_PASSWORD
set -euo pipefail

ENV_NAME="$1"
export API_IMAGE="$2"
EXPECTED_VERSION="$3"

case "$ENV_NAME" in
  staging)    export API_PORT=8001 ;;
  production) export API_PORT=8000 ;;
  *) echo "Environnement inconnu : $ENV_NAME" >&2; exit 1 ;;
esac
: "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD manquant}"

COMPOSE=(docker compose -p "tp2-$ENV_NAME" -f deploy/docker-compose.yml)

echo "== Déploiement de $API_IMAGE en $ENV_NAME (port $API_PORT)"
echo "Version actuellement en $ENV_NAME :"
curl -fsS "http://localhost:$API_PORT/health" || echo "(aucune)"
echo

# 1. Sauvegarde préventive de la base avant un déploiement en production (R3)
if [ "$ENV_NAME" = "production" ] && [ -n "$("${COMPOSE[@]}" ps -q db)" ]; then
  mkdir -p "$HOME/tp2-backups"
  BACKUP="$HOME/tp2-backups/production-$(date +%Y%m%d-%H%M%S).sql"
  "${COMPOSE[@]}" exec -T db pg_dump -U producteurs producteurs > "$BACKUP"
  echo "Sauvegarde de la base : $BACKUP"
fi

# 2. Récupération de l'image versionnée depuis GHCR
"${COMPOSE[@]}" pull api

# 3. Base de données démarrée et prête
"${COMPOSE[@]}" up -d --wait db

# 4. Migrations versionnées appliquées par le pipeline (R3), puis données initiales (idempotent)
"${COMPOSE[@]}" run --rm api python scripts/migrate.py
"${COMPOSE[@]}" run --rm api python scripts/seed.py

# 5. (Re)démarrage de l'API avec la nouvelle image
"${COMPOSE[@]}" up -d api

# 6. Test de fumée : échoue si le service ne répond pas
bash deploy/smoke_test.sh "$API_PORT" "$EXPECTED_VERSION" "$ENV_NAME"

echo "== $ENV_NAME est en version $EXPECTED_VERSION"
