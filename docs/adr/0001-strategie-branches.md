# ADR 0001 — Stratégie de branches

## Contexte

- Équipe de 2 développeurs
- Ancienne pratique : tout le monde poussait directement sur la branche principale.
- Le Product Owner veut pouvoir livrer vite.

## Décision

**GitHub Flow** : une seule branche permanente (`main`) et des branches courtes fusionnées par pull request.

### Quelles branches ?

| Branche | Rôle |
|---|---|
| `main` | Branche principale, toujours déployable, protégée |
| `feat/<desc>` | Nouvelle fonctionnalité |
| `fix/<desc>` | Correction de bug |
| `hotfix/<desc>` | Correctif urgent en production |

Les branches de travail partent de `main` et vivent quelques jours au maximum.

### Qui ?

- Chaque développeur crée ses branches et ouvre une pull request vers `main`.
- Personne ne pousse directement sur `main`.
- L'autre développeur relit la pull request avant fusion.

### Comment ?

1. Créer une branche depuis `main`.
2. Ouvrir une pull request vers `main`.
3. Relecture par l'autre développeur.
4. Fusion dans `main`, puis suppression de la branche.

## Correctif urgent

**Arrivée en production :**
1. Branche `hotfix/<desc>` depuis `main`.
2. Pull request vers `main`, relue en priorité.
3. Fusion dans `main`, qui est ensuite déployée en production.

**Retour dans le travail en cours :** le correctif est dans `main` ; chaque branche en cours se met à jour depuis `main` (`git rebase main`). Comme il n'existe pas d'autre branche permanente, il n'y a rien d'autre à synchroniser.

## Alternatives écartées

- **GitFlow** : branches `develop`, `release`, `hotfix` en plus de `main` ; trop lourd pour 2 développeurs et ralentit la livraison voulue par le PO.
- **Trunk-based development** : commits quasi directs sur la branche principale, trop proche de l'ancienne pratique.

## Signaux que ce choix ne fonctionne plus

- Les pull requests restent ouvertes plusieurs jours sans être fusionnées.
- Les conflits de fusion deviennent fréquents.
- `main` n'est plus déployable (cassée régulièrement).
- On doit maintenir plusieurs versions en production en même temps.
