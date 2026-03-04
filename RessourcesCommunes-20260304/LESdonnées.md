 1. donnees_test.sql (Dump SQL complet)                                                             
                                                                                                     
  Contenu du dump :                                                                                  
  - 20 AAV (types entiers → fichiers)
  - 1 Ontologie (Langage C)
  - 5 Apprenants avec profils variés :
    - Alice : débutante (aucun AAV)
    - Bob : en progression (4 AAV en cours)
    - Charlie : expert (14 AAV)
    - David : bloqué (échecs répétés)
    - Eve : révision nécessaire (maîtrises anciennes)
  - 27 Statuts d'apprentissage
  - 46 Tentatives d'exercices
  - 4 Activités pédagogiques
  - 4 Sessions d'apprenants
  - 7 Prompts de fabrication
  - 7 Exercices générés
  - 3 Diagnostics de remédiation
  - 6 Métriques de qualité

  2. descriptiondonnees.md (Guide d'utilisation)

  Contenu pour chaque groupe :

  ┌────────┬──────────────────────┬────────────────────────────────────────────────────────┐
  │ Groupe │       Section        │                    Tests Expliqués                     │
  ├────────┼──────────────────────┼────────────────────────────────────────────────────────┤
  │ 1      │ AAV & Ontologies     │ Validation DAG, pondérations, chaîne de prérequis      │
  ├────────┼──────────────────────┼────────────────────────────────────────────────────────┤
  │ 2      │ Apprenants           │ Calcul de progression, profils variés                  │
  ├────────┼──────────────────────┼────────────────────────────────────────────────────────┤
  │ 3      │ Statuts & Tentatives │ Recalcul maîtrise, historique, règles                  │
  ├────────┼──────────────────────┼────────────────────────────────────────────────────────┤
  │ 4      │ Activités            │ Cycle session, bilan début/fin                         │
  ├────────┼──────────────────────┼────────────────────────────────────────────────────────┤
  │ 5      │ Navigation           │ 4 opérateurs (accessible, en cours, bloqué, révisable) │
  ├────────┼──────────────────────┼────────────────────────────────────────────────────────┤
  │ 6      │ Remédiation          │ Remontée causes racines, parcours                      │
  ├────────┼──────────────────────┼────────────────────────────────────────────────────────┤
  │ 7      │ Métriques            │ Alertes, détection problèmes, dashboard                │
  ├────────┼──────────────────────┼────────────────────────────────────────────────────────┤
  │ 8      │ Exercices            │ Sélection adaptative, enrichissement prompts           │
  └────────┴──────────────────────┴────────────────────────────────────────────────────────┘

  Scénarios End-to-End inclus :
  - Parcours complet "Alice" (débutante)
  - Remédiation "David" (bloqué)
  - Révision "Eve" (maîtrises anciennes)

  Commandes curl prêtes à l'emploi pour tester chaque endpoint avec les données fournies.

  ---
  Les groupes peuvent maintenant :
  1. Charger le dump SQL : sqlite3 platonAAV_test.db < donnees_test.sql
  2. Tester leur code avec des données réalistes
  3. Travailler indépendamment sans attendre les autres groupes