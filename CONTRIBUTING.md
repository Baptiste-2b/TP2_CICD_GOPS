# Contribuer

Règles de l'équipe (2 développeurs). Chaque règle cite le risque qu'elle traite (voir [docs/risques.md](docs/risques.md)).

## 1. Revue de code

| Règle | Risque traité |
|---|---|
| Toute modification passe par une pull request vers `main`. Personne ne pousse directement sur `main`. | **R2** — Déploiement direct sur la branche `main` |
| **1 approbation** obligatoire : celle de l'autre développeur. L'auteur ne peut pas approuver sa propre PR. | **R5** — Peu de ressources humaines, mauvaise revue de code : 1 seul relecteur car l'équipe n'a que 2 développeurs |
| Un nouveau commit après approbation annule l'approbation. | **R5** — Code ajouté après la relecture, donc non relu |
| Les tests automatiques doivent passer avant toute fusion. | **R5** — La revue humaine est complétée par des tests automatiques |

**Si le relecteur est absent :**
- Hors urgence, la PR attend son retour.
- En cas de correctif urgent, le développeur présent peut fusionner sans approbation (bypass GitHub, uniquement via PR). Il indique dans la PR **qui, quand, pourquoi**, et l'autre développeur relit la modification à son retour.

Risque traité : **R5** — à 2 développeurs, l'absence d'une personne ne doit pas bloquer une livraison urgente.

**Rôles et bypass : cible entreprise vs configuration du TP**

| | En entreprise (organisation GitHub) | Dans ce TP (dépôt personnel) |
|---|---|---|
| Dev 1 | Admin + bypass | Propriétaire du dépôt = Admin + bypass |
| Dev 2 | Maintain + bypass (ne peut pas modifier les règles ni les secrets) | Write + bypass : un dépôt personnel ne propose pas le rôle Maintain, le bypass est donc donné au rôle Write |
| Relecteurs externes | Write, sans bypass | Write + bypass (autres membres du groupe) |

Pourquoi les deux développeurs ont le bypass : à 2, l'absence d'une personne bloquerait toute livraison urgente. Le bypass reste limité : uniquement via PR, tests toujours obligatoires, tracé par GitHub, justifié dans la PR.

Limite assumée : dans ce TP, le bypass est accordé aux rôles **Repository admin** et **Write** (mode « pull requests only »). Comme le rôle Write est aussi celui des autres membres du groupe, ils disposent eux aussi du bypass : c'est une contrainte de l'outil sur un dépôt personnel, validée avec l'enseignant. Le respect de la règle « bypass réservé à l'urgence » repose donc sur la discipline de l'équipe (voir section 6) et sur la trace laissée par GitHub à chaque bypass.

## 2. Nommage

### Branches

| Préfixe | Usage | Exemple |
|---|---|---|
| `feat/` | Nouvelle fonctionnalité | `feat/gestion-stock` |
| `fix/` | Correction de bug | `fix/total-commande` |
| `hotfix/` | Correctif urgent en production | `hotfix/commandes-bloquees` |

Risque traité : **R2** — une branche par fonctionnalité, identifiable, au lieu de tout faire sur `main`.

### Messages de commit

Format [Conventional Commits](https://www.conventionalcommits.org/fr/) : `type: description`

```
feat: ajoute le stock par produit
fix: refuse une commande sans produit
docs: ajoute l'analyse des risques
```

Types : `feat`, `fix`, `docs`, `ci`, `test`, `refactor`, `chore`.

Risque traité : **R4** — perte de traçabilité, impossible de savoir ce qui a changé entre deux versions.

## 3. Definition of Done

Une tâche est **terminée** quand :

- [ ] le code est fusionné dans `main` via une PR approuvée (**R2**, **R5**) ;
- [ ] les tests existent pour la modification et passent dans la CI (**R5**) ;
- [ ] aucun secret n'a été ajouté au dépôt (**R1**) ;
- [ ] la documentation est à jour si le comportement change (**R4**) ;
- [ ] la modification est déployée et `/health` répond (**R4**).

## 4. Versionnage

- Versionnage sémantique **`vX.Y.Z`** :
  - `X` : changement incompatible ;
  - `Y` : nouvelle fonctionnalité ;
  - `Z` : correctif.
- Chaque mise en production correspond à un **tag Git `vX.Y.Z`** et à une **image Docker du même tag**. Le tag `latest` n'est jamais déployé.
- **Savoir en 10 secondes ce qui tourne en production** : `GET /health` renvoie la version et le commit.

```json
{ "status": "ok", "version": "v1.0.0", "commit": "a1b2c3d" }
```

Risque traité : **R4** — perte de traçabilité due au tag `latest`, personne ne savait quelle version tournait en production.

## 5. Secrets

| Question | Règle |
|---|---|
| Où vivent-ils ? | Dans **GitHub Secrets** (secrets d'environnement `staging` / `production`). En local, dans un fichier `.env` **jamais versionné** (ignoré par `.gitignore`). Seul `.env.example` (valeurs factices) est versionné. |
| Qui y a accès ? | Seul l'**administrateur du dépôt** peut créer ou modifier les secrets. Les workflows les lisent, aucun développeur ne les voit en clair. |
| Que fait-on si un secret fuit ? | 1. **Révoquer et régénérer** le secret immédiatement. 2. Mettre à jour GitHub Secrets et redéployer. 3. Supprimer le secret de l'historique Git. 4. Consigner l'incident dans `docs/incidents.md`. |

Le secret est révoqué **avant** le nettoyage de l'historique : une fois publié, il doit être considéré comme compromis.

Risque traité : **R1** — fuite de données, mots de passe et clés d'API dans un fichier `.env` versionné.

## 6. Ce que GitHub impose / ce qui repose sur l'équipe

| Règle | Risque | Imposée par GitHub | Discipline d'équipe |
|---|:---:|---|---|
| Pas de push direct sur `main` | R2 | ✅ Ruleset | |
| Pas de force push ni de suppression de `main` | R2 | ✅ Ruleset | |
| 1 approbation obligatoire | R5 | ✅ Ruleset | |
| Approbation annulée après un nouveau commit | R5 | ✅ Ruleset | |
| Tests verts avant fusion | R5 | ✅ Status check obligatoire | |
| Secrets stockés dans GitHub Secrets | R1 | ✅ Secrets d'environnement | |
| Tags de version non modifiables | R4 | ✅ Ruleset sur les tags `v*` | |
| Bypass réservé à l'urgence et justifié dans la PR | R5 | | ⚠️ GitHub trace le bypass mais ne vérifie pas la justification |
| Relecture a posteriori après un bypass | R5 | | ⚠️ |
| Validation en staging avant la production | R2, R5 | ✅ Workflow : le job production dépend du job staging | |
| Pas de mise en production le vendredi après 16 h (sauf correctif urgent) | R2 | | ⚠️ GitHub ne bloque pas un jour ou une heure |
| Nommage des branches | R2 | | ⚠️ |
| Nommage des commits | R4 | | ⚠️ |
| Definition of Done | R1, R2, R4, R5 | | ⚠️ |
| Ne jamais commiter de secret | R1 | | ⚠️ `.gitignore` aide, mais n'empêche pas tout |
| Procédure en cas de fuite de secret | R1 | | ⚠️ |

Captures de la configuration : [docs/config/](docs/config/).
