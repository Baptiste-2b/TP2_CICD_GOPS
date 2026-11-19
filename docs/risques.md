# Analyse des risques — Nouveau socle applicatif et CI/CD


## 1. Identification et traitement des risques

| ID | Risque & Catégorie | Scénario concret de défaillance | Gravité | Mesure dans le futur socle |
| :--- | :--- | :--- | :---: | :--- |
| **R1** | **Fuite de données**<br>*(Sécurité)* | Les accès PostgreSQL et les clés API sont dans le `.env` versionné : n'importe qui ayant accès au dépôt Git peut les récupérer facilement. | **Critique (4/4)** | `.env` ignoré par le `.gitignore`, seul un `.env.example` (valeurs factices) est versionné, secrets stockés dans GitHub Secrets. |
| **R2** | **Déploiement direct sur la branche principale (`main`)**<br>*(Fiabilité/Organisation)* | Toute l'équipe travaille sur la même branche `main` et un vendredi à 19 h, le tunnel de commande casse et bloque l'activité pendant 14 h. | **Critique (4/4)** | Protection de `main` (aucun push direct), une branche pour chaque fonctionnalité ou ajout, fusion dans `main` uniquement après validation, suivre une stratégie de branches reconnue (GitHub Flow) pour garder une bonne organisation et fiabilité. |
| **R3** | **Migrations faites à la main et quand on y pense**<br>*(Fiabilité)* | Une migration oubliée ou lancée irrégulièrement : la base ne correspond plus au code déployé, les retours en arrière deviennent compliqués et la maintenance complexe. | **Majeure (3/4)** | Migrations versionnées dans le dépôt et exécutées automatiquement par le pipeline à chaque déploiement, complétées par une sauvegarde journalière de la base. |
| **R4** | **Perte de traçabilité due au push avec le tag `latest`**<br>*(Fiabilité)* | Personne ne savait quelle version était en production, ce qui entraîne un problème de traçabilité et, en cas de panne, aucun retour en arrière possible. | **Majeure (3/4)** | Bannissement du tag `latest` dans le workflow, convention stricte de nommage des versions (`vX.Y.Z`), `/health` indique la version en production. |
| **R5** | **Peu de ressources humaines donc mauvaise revue de code**<br>*(Organisation)* | Avec seulement 2 développeurs, la relecture prend trop de temps ou est bâclée, et les tests ne sont jamais lancés : du code non vérifié part en production et les délais de livraison augmentent. | **Majeure (3/4)** | Une seule approbation (l'autre développeur), petites pull requests, tests automatiques lancés par la CI et bloquants avant fusion. |
| **R6** | **Serveur de déploiement exposé via le dépôt public**<br>*(Sécurité)* | Sans serveur dédié, le déploiement passe par un runner GitHub installé sur un poste de l'équipe. Le dépôt étant public, une pull request venue d'un fork pourrait faire exécuter du code inconnu sur ce poste. | **Critique (4/4)** | Les jobs de déploiement ne se déclenchent jamais sur une pull request (seulement sur `main`, un tag `v*` ou un lancement manuel) ; approbation obligatoire des workflows venant de contributeurs extérieurs ; tests et build sur les runners GitHub. |

---

## 2. Matrice Gravité × Effort (Échelle 1 à 4)

* **Gravité :** `1` Mineure · `2` Modérée · `3` Majeure · `4` Critique
* **Effort :** `1` Immédiat (< 1 h) · `2` Court (quelques heures) · `3` Modéré (changement d'habitudes) · `4` Élevé

| Priorité | Risque | Gravité | Effort | Justification du positionnement |
| :--- | :--- | :---: | :---: | :--- |
| **P1** *(Quick Win)* | **R1** — Fuite de données (`.env` versionné) | **4** | **1** | Mettre en place un `.gitignore` et un `.env.example` prend quelques minutes à l'initialisation du dépôt pour neutraliser un risque de sécurité critique. |
| **P1** *(Quick Win)* | **R4** — Perte de traçabilité (tag `latest`) | **3** | **1** | Remplacer le tag `latest` par une convention de nommage stricte dans le workflow CI/CD demande une modification minime pour garantir les retours arrière. |
| **P1** *(Socle)* | **R2** — Déploiement direct sur la branche `main` | **4** | **2** | Verrouiller `main` et imposer des branches par fonctionnalité avec validation demande un peu de configuration GitHub, mais empêche directement la répétition de la panne de 14 h. |
| **P2** *(Structure)* | **R3** — Migrations manuelles et irrégulières | **3** | **2** | Intégrer les migrations au pipeline et paramétrer une sauvegarde journalière demande un effort technique modéré, une seule fois, pour sécuriser la maintenabilité. |
| **P2** *(Organisation)* | **R5** — Peu de ressources humaines / revue de code | **3** | **3** | L'automatisation des tests et l'adoption d'une revue légère mais systématique demandent un effort d'adaptation des 2 développeurs (changement d'habitudes) pour fluidifier les livraisons sans saturer le relecteur. |
| **P1** *(Quick Win)* | **R6** — Serveur de déploiement exposé via le dépôt public | **4** | **1** | Une condition dans le workflow et un réglage GitHub suffisent à empêcher toute exécution de code non relu sur le poste qui sert de serveur. |