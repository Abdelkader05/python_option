# Description du Jeu de Données de Test

Ce document explique comment utiliser le fichier `donnees_test.sql` pour tester chaque partie du projet de manière indépendante.

---

## Vue d'Ensemble des Données

Le jeu de données comprend **20 AAV** sur la syntaxe C, répartis en une ontologie complète avec **5 profils d'apprenants** variés pour couvrir tous les cas d'utilisation.

```
┌─────────────────────────────────────────────────────────────┐
│                    DONNÉES DE TEST                          │
├─────────────────────────────────────────────────────────────┤
│  20 AAV (types entiers → fichiers)                         │
│  ├── 18 AAV atomiques                                       │
│  └── 2 AAV composites (types de base, flux de contrôle)      │
├─────────────────────────────────────────────────────────────┤
│  5 Apprenants avec profils variés:                          │
│  ├── Alice: débutante complète (aucun AAV)                 │
│  ├── Bob: en progression (4 AAV en cours)                    │
│  ├── Charlie: avancé (14 AAV, dont maîtrisés)               │
│  ├── David: bloqué (échecs répétés)                         │
│  └── Eve: révision nécessaire (maîtrise ancienne)            │
└─────────────────────────────────────────────────────────────┘
```

---

## Comment Charger les Données

### Étape 1: Créer la Base de Données

```bash
# Depuis le répertoire contenant le fichier SQL
sqlite3 platonAAV_test.db < donnees_test.sql

# Vérifier le chargement
sqlite3 platonAAV_test.db "SELECT COUNT(*) FROM aav;"
# Doit afficher: 20
```

### Étape 2: Configuration dans Votre Projet

Dans votre `database.py`, modifiez temporairement le chemin:

```python
# Pour les tests avec les données fournies
DATABASE_PATH = "platonAAV_test.db"

# Pour votre propre développement
# DATABASE_PATH = "votre_base.db"
```

---

## Guide par Groupe

### 🔷 GROUPE 1: Gestion des AAV et Ontologies

#### Données Disponibles

| Table | Nombre d'Enregistrements | Cas de Test |
|-------|-------------------------|-------------|
| `aav` | 20 AAV | 18 atomiques, 2 composites |
| `ontology_reference` | 1 ontologie | Langage C |

#### Chaîne de Prérequis

```
AAV 1 (Types entiers) ──┬──→ AAV 2 (Char)
                        ├──→ AAV 3 (Flottants)
                        ├──→ AAV 4 (Variables)
                        │       └──→ AAV 5 (Opérateurs)
                        │               └──→ AAV 6 (Comparaison)
                        │                       └──→ AAV 7 (Logiques)
                        │                               └──→ AAV 8 (If-else)
                        │                                       └──→ AAV 9 (While)
                        │                                               └──→ AAV 10 (For)
                        └──→ AAV 19 (Composite: Types de base)

AAV 19 (Composite): poids [1→0.25, 2→0.25, 3→0.5]
AAV 20 (Composite): poids [8→0.4, 9→0.3, 10→0.3]
```

#### Tests Recommandés

**1. Validation du DAG (pas de cycles)**
```sql
-- Test: vérifier que les prérequis ne forment pas de cycle
-- Prérequis de AAV 1: [] (aucun)
-- Prérequis de AAV 2: [1]
-- Prérequis de AAV 4: [1, 2, 3]
-- etc.
```

**2. Validation des Pondérations**
```sql
-- AAV 19 (Composite): somme des pondérations = 0.25 + 0.25 + 0.5 = 1.0 ✓
-- AAV 20 (Composite): somme des pondérations = 0.4 + 0.3 + 0.3 = 1.0 ✓
```

**3. Test des Endpoints**
```bash
# GET /aavs - Liste avec pagination
curl http://localhost:8000/aavs?discipline=Programmation&limit=10

# GET /aavs/1 - Détails d'un AAV (prérequis vides)
curl http://localhost:8000/aavs/1

# GET /aavs/4 - AAV avec prérequis [1, 2, 3]
curl http://localhost:8000/aavs/4

# GET /aavs/19 - AAV Composite avec pondération
curl http://localhost:8000/aavs/19

# GET /aavs/1/prerequisites/chain - Chaîne complète
curl http://localhost:8000/aavs/8/prerequisites/chain
# Doit retourner: [1, 6, 7] (prérequis directs + indirects)

# POST /ontologies/1/validate - Validation DAG
curl -X POST http://localhost:8000/ontologies/1/validate
```

---

### 🔷 GROUPE 2: Gestion des Apprenants

#### Données Disponibles

| Apprenant | Profil | Statuts Actifs | Usage |
|-----------|--------|----------------|-------|
| Alice | Débutante | `[]` | Test création de compte, progression 0% |
| Bob | Progressif | `[1, 2, 5, 6]` | Test progression partielle |
| Charlie | Expert | `[1-14]` | Test statistiques avancées |
| David | Bloqué | `[1, 2, 5, 6]` | Test apprenant en difficulté |
| Eve | Révision | `[1-5]` | Test anciens utilisateurs |

#### Tests Recommandés

**1. CRUD Apprenant**
```bash
# GET /learners - Liste paginée
curl http://localhost:8000/learners?limit=5

# GET /learners/1 - Alice (débutante)
curl http://localhost:8000/learners/1

# GET /learners/3 - Charlie (expert)
curl http://localhost:8000/learners/3
```

**2. Calcul de Progression**
```bash
# GET /learners/1/progress - Alice: 0%
curl http://localhost:8000/learners/1/progress
# Résultat attendu: {"total_aavs": 20, "maitrises": 0, "progression": 0.0}

# GET /learners/3/progress - Charlie: 70%
curl http://localhost:8000/learners/3/progress
# Résultat attendu: {"total_aavs": 20, "maitrises": 10, "progression": 0.70}

# GET /learners/4/progress - David: faible progression, AAV bloqués
curl http://localhost:8000/learners/4/progress
```

**3. Gestion des Prérequis Externes**
```bash
# POST /learners/1/external-prerequisites - Ajouter prérequis
curl -X POST http://localhost:8000/learners/1/external-prerequisites \
  -H "Content-Type: application/json" \
  -d '{"code": "MATH-101", "description": "Algèbre de base"}'

# GET /learners/1/external-prerequisites
curl http://localhost:8000/learners/1/external-prerequisites
```

---

### 🔷 GROUPE 3: Statuts et Tentatives

#### Données Disponibles

| Apprenant | AAV | Niveau | Historique | Cas de Test |
|-----------|-----|--------|------------|-------------|
| Bob | AAV 1 | 0.85 | 3 tentatives | Près de maîtrise |
| Bob | AAV 2 | 0.60 | 2 tentatives | En cours |
| Bob | AAV 6 | 0.30 | 1 tentative | Début difficile |
| Charlie | AAV 1-6 | 1.00 | 3 succès | Maîtrisés |
| Charlie | AAV 11-12 | 0.30-0.40 | 1 tentative | Démarrage |
| David | AAV 1 | 0.90 | 3 tentatives | Bon niveau |
| David | AAV 2, 5, 6 | 0.10-0.25 | 3-4 échecs | Bloqué |

#### Tests Recommandés

**1. Calcul de Maîtrise**
```bash
# GET /learning-status/1 - Bob sur AAV 1 (niveau 0.85)
curl http://localhost:8000/learning-status/1

# POST /attempts puis recalcul
# Envoyer une tentative réussie pour AAV 1
# Vérifier que le niveau passe à 1.0 après 3 succès consécutifs
```

**2. Historique des Tentatives**
```bash
# GET /learning-status/1/attempts - Historique Bob AAV 1
curl http://localhost:8000/learning-status/1/attempts
# Doit retourner 3 tentatives

# GET /learning-status/19/attempts - David AAV 2 (échecs)
curl http://localhost:8000/learning-status/19/attempts
# Historique: scores [0.20, 0.15, 0.30, 0.25] - tendance échec
```

**3. Traitement d'une Tentative**
```bash
# POST /attempts avec traitement
# Test: tentative réussie sur AAV 1 pour Bob
# Résultat: niveau passe de 0.85 à 1.0 (3ème succès consécutif)
```

**4. Règles de Progression**
```sql
-- AAV 1 (Types entiers): règles
-- seuil_succes: 0.8, nombre_succes_consecutifs: 3
-- Tentatives Bob: [0.70, 0.80, 0.85] → 2 ≥ 0.8, manque 1 succès
-- Après tentative à 0.90: [0.80, 0.85, 0.90] → 3 ≥ 0.8 ✓ MAÎTRISE
```

---

### 🔷 GROUPE 4: Activités Pédagogiques

#### Données Disponibles

| Activité | Type | Exercices | AAV Ciblés |
|----------|------|-----------|------------|
| 1 | pilotee | [101, 102, 103, 104, 105] | AAV 1-3 (Types) |
| 2 | pilotee | [109, 110, 111, 112] | AAV 5-6 (Opérateurs) |
| 3 | prof_definie | [115-120] | AAV 8-10 (Contrôle) |
| 4 | revision | [121-124] | AAV 11-12 (Fonctions) |

#### Sessions Existantes

| Session | Apprenant | Activité | Statut | Progression |
|---------|-------------|----------|--------|-------------|
| 1 | Bob (2) | 1 | en_cours | 60% |
| 2 | Charlie (3) | 2 | terminee | 100% |
| 3 | David (4) | 1 | en_cours | 30% |

#### Tests Recommandés

**1. Démarrage d'Activité**
```bash
# POST /activities/1/start
# Body: {"id_apprenant": 1} (Alice)
# Résultat attendu:
# {
#   "message": "Dans cette activité, nous allons travailler les types entiers, le type char, les types flottants",
#   "exercices": [...],
#   "session_id": 5
# }
```

**2. Bilan de Fin**
```bash
# POST /activities/2/complete (Charlie termine activité 2)
curl -X POST http://localhost:8000/activities/2/complete \
  -H "Content-Type: application/json" \
  -d '{"id_apprenant": 3}'
# Résultat: bilan des AAV validés/partiels/non réussis
```

**3. Soumission de Tentative**
```bash
# POST /activities/1/submit-attempt (Bob continue son activité)
# Body: {"id_exercice": 102, "reponse": "...", "id_apprenant": 2}
# Résultat: mise à jour de la progression à 75%
```

---

### 🔷 GROUPE 5: Navigation et Filtres (NetworkX)

#### Scénarios de Test par Apprenant

```
ALICE (débutante) - aucun AAV commencé:
├─ Accessible: AAV 1 (prérequis: [], niveau 0)
├─ EnCours: []
├─ Bloqués: AAV 2-20 (prérequis non satisfaits)
└─ Révisables: []

BOB (en progression) - AAV 1 (0.85), 2 (0.60), 5 (0.45), 6 (0.30):
├─ Accessible: AAV 3 (prérequis [1] ✓), AAV 4 (prérequis [1,2,3] ✗)
├─ EnCours: AAV 1, 2, 5, 6
├─ Bloqués: AAV 7 (prérequis [6]=0.30 < 0.7)
└─ Révisables: []

CHARLIE (expert) - AAV 1-6 maîtrisés, AAV 11-12 commencés:
├─ Accessible: AAV 7 (prérequis [6]=1.0 ✓)
├─ EnCours: AAV 7 (0.90), 8 (0.75), 9 (0.60), 10 (0.50), 11 (0.40), 12 (0.30)
├─ Bloqués: AAV 13 (prérequis [1,4,10] - 10 insuffisant)
└─ Révisables: [] (dates trop récentes)

DAVID (bloqué) - échecs sur AAV 2, 5, 6:
├─ Accessible: AAV 3 (prérequis [1]=0.90 ✓)
├─ EnCours: AAV 2 (0.25), 5 (0.20), 6 (0.10)
├─ Bloqués: AAV 7 (prérequis [6]=0.10 < 0.3 ET < 0.7)
└─ Révisables: []

EVE (révision) - maîtrises anciennes:
├─ Accessible: []
├─ EnCours: []
├─ Bloqués: []
└─ Révisables: AAV 1-5 (niveau >= 0.8, dates anciennes)
```

#### Tests Recommandés

**1. Opérateur Accessible**
```bash
# GET /learners/1/aavs/accessible - Alice
curl http://localhost:8000/learners/1/aavs/accessible
# Résultat: [AAV 1] (seul AAV sans prérequis)

# GET /learners/2/aavs/accessible - Bob
curl http://localhost:8000/learners/2/aavs/accessible
# Résultat: [AAV 3] (prérequis [1] satisfait)

# GET /learners/3/aavs/accessible - Charlie
curl http://localhost:8000/learners/3/aavs/accessible
# Résultat: [AAV 7, 16, 17, 18, 19, 20] (tous prérequis satisfaits)
```

**2. Opérateur EnCours**
```bash
# GET /learners/2/aavs/in-progress - Bob
curl http://localhost:8000/learners/2/aavs/in-progress
# Résultat: [AAV 1 (0.85), AAV 2 (0.60), AAV 5 (0.45), AAV 6 (0.30)]
```

**3. Opérateur Bloqués**
```bash
# GET /learners/4/aavs/blocked - David
curl http://localhost:8000/learners/4/aavs/blocked
# Résultat: [AAV 7, 8, 9, 10...] (niveau faible + prérequis insuffisants)
```

**4. Opérateur Révisables**
```bash
# GET /learners/5/aavs/revisable - Eve (critère: dernière session > 30 jours)
curl http://localhost:8000/learners/5/aavs/revisable
# Résultat: [AAV 1 (0.95), AAV 2 (0.90), ...] (maîtrisés depuis longtemps)
```

**5. Vue d'Ensemble (Frontière)**
```bash
# GET /learners/2/frontier
curl http://localhost:8000/learners/2/frontier
# Résultat:
# {
#   "accessible": [3],
#   "en_cours": [1, 2, 5, 6],
#   "bloques": [4, 7, 8, ...],
#   "revisables": []
# }
```

**6. Recommandations**
```bash
# GET /learners/2/next-recommendations
curl http://localhost:8000/learners/2/next-recommendations
# Résultat: [AAV 3] (accessible prioritaire)
```

**7. Graphe (NetworkX)**
```bash
# GET /learners/3/graph - Exporter graphe Charlie
curl http://localhost:8000/learners/3/graph
# Résultat: structure NetworkX avec nœuds et arêtes

# GET /ontologies/1/critical-path
curl http://localhost:8000/ontologies/1/critical-path
# Résultat: chemin le plus long dans le DAG
# Ex: [1, 4, 5, 6, 7, 8, 9, 10]
```

---

### 🔷 GROUPE 6: Remédiation et Diagnostic

#### Scénarios de Blocage à Analyser

| Apprenant | AAV Échoué | Score | Causes Racines Attendues |
|-----------|------------|-------|--------------------------|
| David (4) | AAV 5 (Opérateurs) | 0.20 | AAV 1 (Types entiers) |
| David (4) | AAV 6 (Comparaison) | 0.10 | AAV 1, puis AAV 2 (Char) |
| David (4) | AAV 2 (Char) | 0.25 | AAV 1 (Types entiers) |

#### Tests Recommandés

**1. Diagnostic de Remédiation**
```bash
# POST /diagnostics/remediation (David échoue sur AAV 5)
curl -X POST http://localhost:8000/diagnostics/remediation \
  -H "Content-Type: application/json" \
  -d '{
    "id_apprenant": 4,
    "id_aav_source": 5,
    "score_obtenu": 0.20,
    "type_echec": "calcul"
  }'
# Résultat attendu:
# {
#   "id_diagnostic": 4,
#   "aav_racines_defaillants": [1],
#   "message": "Problème de compréhension des types entiers"
# }
```

**2. Analyse de Causes**
```bash
# GET /aavs/6/root-causes?id_apprenant=4
curl "http://localhost:8000/aavs/6/root-causes?id_apprenant=4"
# Remonte: AAV 6 → prérequis [6] → AAV 6 niveau 0.10 ❌
#          → remonter sur prérequis de AAV 6: [1]
#          → AAV 1 niveau 0.90 ✓ (OK)
#          → AAV 2 niveau 0.25 ❌
# Résultat: causes_racines = [2]
```

**3. Génération de Parcours**
```bash
# POST /remediation/generate-path
curl -X POST http://localhost:8000/remediation/generate-path \
  -H "Content-Type: application/json" \
  -d '{
    "id_apprenant": 4,
    "id_aav_cible": 5,
    "profondeur_max": 3
  }'
# Résultat: [AAV 1] (reprendre les bases)
```

**4. Points Faibles Identifiés**
```bash
# GET /learners/4/weaknesses
curl http://localhost:8000/learners/4/weaknesses
# Résultat: [AAV 2, AAV 5, AAV 6] (niveaux < 0.3)
```

---

### 🔷 GROUPE 7: Métriques et Qualité

#### Données de Métriques Existantes

| AAV | Couverture | Taux Succès | Utilisable | Problème |
|-----|------------|-------------|------------|----------|
| 1 | 0.90 | 0.75 | ✓ | OK |
| 2 | 0.80 | 0.45 | ✗ | Trop difficile |
| 5 | 0.85 | 0.55 | ✓ | OK |
| 6 | 0.70 | 0.40 | ✗ | Taux faible |
| 15 | 0.75 | 0.40 | ✗ | Difficile |
| 16 | 0.80 | 0.75 | ✓ | OK |

#### Tests Recommandés

**1. Calcul des Métriques**
```bash
# POST /metrics/aav/2/calculate - Recalculer métriques AAV 2
curl -X POST http://localhost:8000/metrics/aav/2/calculate
# Résultat: score bas (0.45), marqué comme non utilisable
```

**2. Alertes de Qualité**
```bash
# GET /alerts/difficult-aavs
curl http://localhost:8000/alerts/difficult-aavs
# Résultat: [AAV 2 (0.45), AAV 6 (0.40)] - taux < 0.5

# GET /alerts/students-at-risk
curl http://localhost:8000/alerts/students-at-risk
# Résultat: [David] - progression faible, nombreux échecs
```

**3. Dashboard Enseignant**
```bash
# GET /dashboard/disciplines/Programmation/stats
curl http://localhost:8000/dashboard/disciplines/Programmation/stats
# Résultat: statistiques globales sur tous les apprenants
```

**4. Comparaison**
```bash
# GET /metrics/compare/aavs?ids=1,2,5,6
curl "http://localhost:8000/metrics/compare/aavs?ids=1,2,5,6"
# Comparaison visuelle des 4 AAV
```

---

### 🔷 GROUPE 8: Génération d'Exercices

#### Données Disponibles

| Prompt | AAV Cible | Type | Exercices Générés |
|--------|-----------|------|-------------------|
| 1 | AAV 1 (Types entiers) | Calcul | 101, 102 |
| 3 | AAV 5 (Opérateurs) | Calcul | 109, 110 |
| 8 | AAV 8 (If-else) | Invention | 115, 116 |
| 15 | AAV 15 (Pointeurs) | Chute | 129, 130 |

#### Tests Recommandés

**1. Sélection Adaptative**
```bash
# POST /exercises/select (pour Bob, niveau intermédiaire)
curl -X POST http://localhost:8000/exercises/select \
  -H "Content-Type: application/json" \
  -d '{
    "id_apprenant": 2,
    "id_aavs_cibles": [1, 2, 5],
    "nombre_exercices": 3,
    "strategie": "adaptive"
  }'
# Résultat: exercices de difficulté intermédiaire (niveau Bob: 0.6-0.8)
```

**2. Enrichissement de Prompt**
```bash
# POST /prompts/1/preview (pour Bob)
curl -X POST http://localhost:8000/prompts/1/preview \
  -H "Content-Type: application/json" \
  -d '{"id_apprenant": 2, "include_context": true}'
# Résultat: prompt enrichi avec le contexte de Bob
# "Contexte: AAV maîtrisés: [Types entiers], AAV en cours: [Char]..."
```

**3. Validation des Règles**
```bash
# POST /exercises/evaluate
# Tester validation automatique d'une réponse
```

---

## Scénarios de Test End-to-End

### Scénario 1: Parcours Complet "Alice"

```python
# Alice (débutante) veut apprendre
# 1. Démarrer une activité
POST /activities/1/start {id_apprenant: 1}
# → Reçoit exercice sur types entiers

# 2. Réussir exercices
POST /exercises/evaluate {id_exercice: 101, reponse: "4"}
# → Score: 0.80

# 3. Tentative enregistrée → Mise à jour statut
POST /attempts {id_apprenant: 1, id_aav: 1, score: 0.80}
# → Niveau AAV 1: 0.80

# 4. Vérifier progression
GET /learners/1/progress
# → Progression: 5%

# 5. Vérifier AAV accessibles
GET /learners/1/aavs/accessible
# → AAV 1 toujours accessible, autres bloqués
```

### Scénario 2: Remédiation "David"

```python
# David (bloqué) échoue sur les opérateurs
# 1. Soumettre tentative échouée
POST /attempts {id_apprenant: 4, id_aav: 5, score: 0.20}

# 2. Diagnostic automatique
POST /diagnostics/remediation {id_apprenant: 4, id_aav_source: 5}
# → Causes racines: [AAV 1] (types entiers)

# 3. Générer parcours de remédiation
POST /remediation/generate-path {id_apprenant: 4, id_aav_cible: 5}
# → Parcours: [AAV 1] → [AAV 5]

# 4. Proposer activité de révision sur AAV 1
GET /remediation/activities/4
# → Activité de révision des types entiers
```

### Scénario 3: Révision "Eve"

```python
# Eve (maîtrises anciennes) se reconnecte après 4 mois
# 1. Vérifier AAV à réviser
GET /learners/5/aavs/revisable
# → [AAV 1, 2, 3, 4, 5] (trop vieux)

# 2. Proposer activité de révision
POST /activities/4/start {id_apprenant: 5}
# → Activité "Fonctions avancées" (mais suggère révision d'abord)

# 3. Sélection exercices révision
POST /exercises/select {
#   id_apprenant: 5,
#   id_aavs_cibles: [1, 2, 3, 4, 5],
#   strategie: "revision"
# }
```

---

## Requêtes SQL Utiles pour le Débogage

```sql
-- Vérifier la structure du graphe de prérequis
SELECT id_aav, nom, prerequis_ids
FROM aav
ORDER BY id_aav;

-- Voir les statuts d'un apprenant
SELECT a.nom, sa.niveau_maitrise, aav.nom as aav_nom
FROM statut_apprentissage sa
JOIN apprenant a ON sa.id_apprenant = a.id_apprenant
JOIN aav ON sa.id_aav_cible = aav.id_aav
WHERE a.id_apprenant = 4;

-- Calculer taux de succès par AAV
SELECT id_aav_cible, AVG(score_obtenu) as taux_succes, COUNT(*) as nb_tentatives
FROM tentative
GROUP BY id_aav_cible;

-- Vérifier les cycles potentiels (à ne pas avoir!)
-- Si AAV A a prérequis B, et B a prérequis A: CYCLE!
```

---

## Résumé par Groupe

| Groupe | Données Clés | Test Principal |
|--------|---------------|----------------|
| 1 | 20 AAV, 1 ontologie | Validation DAG, chaîne prérequis |
| 2 | 5 apprenants variés | Calcul progression, statistiques |
| 3 | 27 statuts, 46 tentatives | Recalcul maîtrise, historique |
| 4 | 4 activités, 4 sessions | Cycle activité, bilan fin |
| 5 | Graphe 20 nœuds | 4 opérateurs, recommandations |
| 6 | 3 diagnostics | Remontée causes, parcours remédiation |
| 7 | 6 métriques | Alertes, rapports, détection problèmes |
| 8 | 7 prompts, 7 exercices | Sélection adaptative, enrichment |

---

**Note**: Ce jeu de données permet à chaque groupe de travailler **indépendamment** sans attendre les autres. Les mocks ne sont nécessaires que pour les dépendances fonctionnelles complexes (ex: calcul de navigation dépendant des statuts).
