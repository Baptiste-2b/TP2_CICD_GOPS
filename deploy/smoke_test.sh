#!/usr/bin/env bash
# Test de fumée après déploiement : échoue (code de sortie non nul) si le service ne répond pas.
#
# Usage : deploy/smoke_test.sh <port> <version attendue> <staging|production>
set -euo pipefail

PORT="$1"
EXPECTED_VERSION="$2"
ENV_NAME="$3"
BASE="http://localhost:$PORT"

fail() { echo "ÉCHEC du test de fumée : $1" >&2; exit 1; }

# 1. Le service répond sur /health (60 s maximum)
for i in $(seq 1 30); do
  HEALTH=$(curl -fsS "$BASE/health" 2>/dev/null) && break
  [ "$i" -eq 30 ] && fail "/health ne répond pas"
  sleep 2
done
echo "/health -> $HEALTH"

# 2. C'est bien la version attendue qui tourne (R4)
echo "$HEALTH" | grep -q "\"version\":\"$EXPECTED_VERSION\"" \
  || fail "version attendue $EXPECTED_VERSION"

# 3. La liste des produits répond
PRODUCTS=$(curl -fsS "$BASE/products?limit=1") || fail "GET /products"
PRODUCT_ID=$(echo "$PRODUCTS" | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)
[ -n "$PRODUCT_ID" ] || fail "GET /products ne renvoie aucun produit"
echo "GET /products -> OK (produit $PRODUCT_ID)"

# 4. En staging uniquement : une commande peut être passée (pas de fausse commande en production)
if [ "$ENV_NAME" = "staging" ]; then
  CODE=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE/orders" \
    -H 'Content-Type: application/json' \
    -d "{\"product_id\": $PRODUCT_ID, \"quantity\": 1}")
  # 201 = commande créée ; 409 = refus clair pour stock insuffisant (comportement attendu)
  [ "$CODE" = "201" ] || [ "$CODE" = "409" ] || fail "POST /orders a renvoyé $CODE"
  echo "POST /orders -> $CODE"
fi

echo "Test de fumée OK"
