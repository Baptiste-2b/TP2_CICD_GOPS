# Conception du pipeline CI/CD

Ce pipeline répond directement aux risques identifiés dans `docs/risques.md` (**R1** à **R6**) en automatisant la validation tout en conservant un processus léger adapté à une équipe de **2 développeurs**.

Les étapes 1 à 3 s'exécutent sur les runners hébergés par GitHub. Les déploiements (étapes 4 et 5, rollback) s'exécutent sur un runner self-hosted installé sur le poste qui sert de serveur, et ne se déclenchent jamais sur une pull request [R6].

---

## 1. Schéma du pipeline (de la PR jusqu'à la production)

```text
[Branche feat/*, fix/* ou hotfix/*]
        │
        ▼  (Ouverture ou mise à jour d'une Pull Request vers main)
┌─────────────────────────────────────────────────────────────┐
│  ÉTAPE 1 : Contrôles statiques & Sécurité (CI)              │
│  • Scan de secrets (.env, clés API) [R1]                    │
│  • Linter & formatage du code                               │
└───────┬─────────────────────────────────────────────────────┘
        │ (Succès)
        ▼
┌─────────────────────────────────────────────────────────────┐
│  ÉTAPE 2 : Tests automatisés & Intégration BDD (CI)         │
│  • Lancement conteneur PostgreSQL éphémère                  │
│  • Exécution des tests unitaires et d'intégration API [R5]  │
└───────┬─────────────────────────────────────────────────────┘
        │ (Succès)
        ▼
╔═════════════════════════════════════════════════════════════╗
║  POINT D'APPROBATION HUMAINE N°1 : Revue de code (PR)       ║
║  • 1 approbation requise (l'autre développeur)              ║
║  • Bloque le merge sur main si refusé ou incomplet [R2/R5]  ║
╚═══════╤═════════════════════════════════════════════════════╝
        │ (Merge sur main)
        ▼
┌─────────────────────────────────────────────────────────────┐
│  ÉTAPE 3 : Build & Publication de l'image immuable (CD)     │
│  • Build Docker de l'API                                    │
│  • Merge sur main → image taguée main-<sha> [R4]            │
│  • Tag Git vX.Y.Z → image construite et taguée vX.Y.Z [R4]  │
│  • Push vers GitHub Container Registry (GHCR)               │
└───────┬─────────────────────────────────────────────────────┘
        │ (Succès)
        ▼
┌─────────────────────────────────────────────────────────────┐
│  ÉTAPE 4 : Déploiement en Staging & Test de fumée (CD)      │
│  • Déploiement automatique de l'image sur "staging"         │
│  • Exécution des migrations sur la base de staging [R3]     │
│  • Test de fumée : /health, GET /products, POST /orders     │
│  • Échec si le test de fumée échoue [R2/R5]                 │
└───────┬─────────────────────────────────────────────────────┘
        │ (Succès)
        ▼
╔═════════════════════════════════════════════════════════════╗
║  POINT D'APPROBATION HUMAINE N°2 : Validation Prod (Gate)   ║
║  • Environment Protection Rule GitHub sur "production"      ║
║  • Approbation manuelle par un développeur                  ║
║  • Gel des mises en prod le vendredi après 16h00 [R2]       ║
╚═══════╤═════════════════════════════════════════════════════╝
        │ (Validation manuelle)
        ▼
┌─────────────────────────────────────────────────────────────┐
│  ÉTAPE 5 : Déploiement Production & Vérification (CD)       │
│  • Sauvegarde préventive de la BDD PostgreSQL [R3]          │
│  • Exécution automatique des migrations [R3]                │
│  • Mise à jour du conteneur API avec le tag vX.Y.Z [R4]     │
│  • Healthcheck automatique (/health) : échec si KO          │
└─────────────────────────────────────────────────────────────┘
```

## 2. Détail des étapes du pipeline

| Étape | Déclencheur | Durée estimée | Bloquante ? |
| :--- | :--- | :---: | :---: |
| **Étape 1 — Scan secrets & Linter** | Ouverture / Push sur une Pull Request vers `main` | ~ 30 s | **Oui** (empêche le merge) |
| **Étape 2 — Tests & Intégration PostgreSQL** | Succès de l'étape 1 sur la Pull Request | ~ 1 min 30 s | **Oui** (empêche le merge) |
| **Approbation n°1 — Revue de code** | Étapes 1 et 2 au vert sur la Pull Request | < 20 min *(cible)* | **Oui** (1 approbation requise) |
| **Étape 3 — Build & Push Docker** | Merge de la Pull Request dans `main` (image `main-<sha>`), puis création du tag Git `vX.Y.Z` (image `vX.Y.Z`) | ~ 1 min | **Oui** (arrête le CD si échec) |
| **Étape 4 — Déploiement Staging & Test de fumée** | Image publiée sur GHCR (fin étape 3) | ~ 1 min | **Oui** (bloque la mise en production si le test échoue) |
| **Approbation n°2 — Validation Prod** | Test de fumée staging au vert + tag `vX.Y.Z` (fin étape 4) | Variable (manuel) | **Oui** (gate humaine prod) |
| **Étape 5 — Backup BDD, migrations & Déploiement Prod** | Approbation manuelle sur l'environnement `production` | ~ 45 s | **Oui** (le job échoue si `/health` ne répond pas) |


## 3. Procédure de retour arrière (Rollback)

### Qui la déclenche ?
* **L'un des 2 développeurs** disponible en cas d'alerte ou de dysfonctionnement constaté en production (après notification sur le canal d'équipe).

### Comment la déclencher ?
1. Identifier le tag immuable de la dernière version stable sur GHCR (ex. : passer de `v1.1.0` défaillant à `v1.0.0` stable).
2. Lancer le workflow GitHub Actions **Rollback** (`workflow_dispatch`) avec l'environnement `production` et la version stable cible.
3. Un autre développeur approuve le déploiement (règle de l'environnement `production`).
4. Le workflow redéploie l'image et lance le test de fumée : il échoue si `/health` ne répond pas ou si la version n'est pas celle demandée.
5. *(Si la base a été altérée)* Restaurer manuellement le dump PostgreSQL généré lors de la sauvegarde préventive de l'Étape 5.

### En combien de temps ?
* **Moins de 3 minutes** pour le code applicatif (l'image Docker précédente est déjà sur GHCR, sans rebuild) : c'est ce délai qui répond à la contrainte de retour à la version précédente. Il suppose que l'approbateur soit disponible : il reste joignable pendant toute mise en production.
* **5 à 10 minutes supplémentaires** si une restauration de la sauvegarde PostgreSQL est nécessaire.

### Ce que cette procédure ne sait pas annuler
* **Les transactions enregistrées entre le déploiement et le rollback :** grâce à la sauvegarde préventive de l'Étape 5, on peut annuler un changement de schéma ou une corruption de données en restaurant l'état exact d'avant la mise en production. En revanche, cette restauration **écrase et perd toutes les nouvelles commandes passées par les restaurateurs/particuliers** durant le laps de temps où la version défaillante était en ligne.
* **Les migrations de base déjà appliquées :** redéployer l'ancienne image ne remet pas le schéma de la base dans son état précédent ; seule la restauration de la sauvegarde le permet, avec la perte de données décrite ci-dessus.
