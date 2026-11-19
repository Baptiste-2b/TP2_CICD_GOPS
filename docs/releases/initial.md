# Mise en production initiale — v1.0.0

| | |
|---|---|
| **Version** | `v1.0.0` (première version en production) |
| **Date** | 19/11/2026 |
| **Contenu** | Socle : API (`/health`, `GET /products`, `POST /orders`), Docker + PostgreSQL, migrations versionnées, 1 200 produits de démonstration, pipeline CI/CD |
| **Approbateur** | Aymeric (`AyScorp`) |
| **Release GitHub** | `v1.0.0 — Socle initial` |

## 1. Pourquoi une version initiale

La user story US-42 impose de pouvoir revenir à la version précédente en moins de 5 minutes. Il faut donc qu'une version stable soit déjà en production, publiée sur GHCR et taguée, avant de livrer la gestion du stock : c'est `v1.0.0`.

## 2. La « production » simulée

Pas de VPS : le serveur est le poste d'un membre de l'équipe, sur lequel tourne un runner GitHub Actions self-hosted (label `tp2-deploy`).

| Environnement | Adresse | Base de données | Déploiement |
|---|---|---|---|
| `staging` | `http://localhost:8001` | propre (projet Docker `tp2-staging`) | automatique à chaque merge sur `main` et à chaque tag |
| `production` | `http://localhost:8000` | propre (projet Docker `tp2-production`) | sur tag `vX.Y.Z`, après approbation |

Les mots de passe des bases sont des secrets d'environnement GitHub (R1). Les déploiements ne se déclenchent jamais sur une pull request (R6).

## 3. Déroulement

1. Merge de la PR #2 (pipeline de déploiement) → déploiement automatique en staging, test de fumée OK.
2. Tag `v1.0.0` → secrets, lint, tests, build et publication de l'image `v1.0.0` sur GHCR.
3. Déploiement en staging + test de fumée OK (`/health` → `v1.0.0`).
4. Déploiement en production + test de fumée OK (`/health` → `v1.0.0`).
5. Publication de la Release GitHub `v1.0.0`.

## 4. Écart au processus

Lors de la première tentative, le déploiement en production est parti **sans approbation** : la règle *Required reviewers* de l'environnement `production` n'avait pas été enregistrée.

- **Qui / quand** : constaté par l'équipe le 19/11/2026, juste après le déploiement.
- **Correction** : règle enregistrée (relecteurs + *Prevent self-review*), puis le job `deploy-production` a été relancé : il a attendu l'approbation, donnée par Aymeric, avant de redéployer `v1.0.0`. Une sauvegarde de la base a été faite automatiquement avant ce redéploiement.
- Détail dans [../incidents.md](../incidents.md).

## 5. Résultat

`v1.0.0` est en production, approuvée, avec une image versionnée et immuable sur GHCR : c'est la version de retour arrière pour `v1.1.0`.
