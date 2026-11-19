# Journal des incidents

Chaque entrée indique ce qui a été décidé, la règle appliquée ou enfreinte, et ce qui change dans nos règles.

## INC-1 — Mise en production `v1.0.0` sans approbation (19/11/2026)

| | |
|---|---|
| **Constat** | Le job `deploy-production` du tag `v1.0.0` s'est exécuté sans attendre de validation humaine : personne n'a vu de demande d'approbation. |
| **Cause** | La règle *Required reviewers* de l'environnement `production` n'avait pas été enregistrée lors de la configuration de GitHub. |
| **Règle enfreinte** | Approbation humaine obligatoire avant la production ([pipeline.md](pipeline.md), approbation n°2 ; [CONTRIBUTING.md](../CONTRIBUTING.md), section 6). Risques concernés : R2, R5. |
| **Décision** | Enregistrer la règle (relecteurs + *Prevent self-review*), puis relancer le déploiement de `v1.0.0` pour qu'il passe par l'approbation. Redéploiement approuvé par Aymeric. |
| **Impact** | Aucun : la version déployée était celle validée en staging, et elle a été redéployée avec approbation. |
| **Ce qu'on change** | Après toute modification de la configuration GitHub (environnements, rulesets), vérifier qu'elle est bien active avant de s'appuyer dessus : contrôle de la page de l'environnement et capture dans `docs/config/`. |