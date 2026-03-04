# Projet Groupe 5 : Opérateurs de Navigation (Accessibles, EnCours, Bloques, Revisables)

## Description

Votre mission est d'implémenter les **opérateurs de limite** qui définissent la frontière d'apprentissage pour chaque apprenant. Ces opérateurs filtrent les AAV selon leur statut de disponibilité.

## Partie Commune (CRUD de Base)

Chaque groupe doit implémenter la partie d'accès direct à la base de données SQLite3 :

- Connexion à la base de données (`database.py`)
- Modèle de base avec gestion des transactions
- Gestion des erreurs HTTP standards (404, 422, 500)
- Validation des entrées avec Pydantic

## Votre Spécifique (Domaine Navigation)

### Opérateurs à Implémenter

Chaque opérateur est un endpoint qui retourne une liste d'AAV filtrée pour un apprenant donné :

#### Opérateur Accessibles
- `GET /navigation/{id_apprenant}/accessible` - AAV prêts à être appris
  - Prérequis SATISFAITS (niveau_maitrise >= seuil_succes)
  - Non Commencé (niveau_maitrise = 0)
  - Dans l'ontologie de référence de l'apprenant

#### Opérateur EnCours
- `GET /navigation/{id_apprenant}/in-progress` - AAV actuellement travaillés
  - Commencé (niveau_maitrise > 0)
  - Non Maîtrisé (niveau_maitrise < 0.9)
  - Avec historique de tentatives

#### Opérateur Bloques
- `GET /navigation/{id_apprenant}/blocked` - AAV bloqués par manque de prérequis
  - Au moins un prérequis NON SATISFAIT
  - Calcul récursif : remonter l'arbre des prérequis pour trouver les bloqueurs

#### Opérateur Revisables
- `GET /navigation/{id_apprenant}/reviewable` - AAV à réviser (entretien)
  - Maîtrisés (niveau_maitrise >= 0.8)
  - Critère de rappel atteint (spaced repetition)
  - Calcul basé sur la dernière tentative et la courbe d'oubli

### Endpoints Complémentaires

#### Vue d'Ensemble
- `GET /navigation/{id_apprenant}/dashboard` - Vue consolidée avec compteurs
  ```json
  {
    "accessible_count": 5,
    "in_progress_count": 3,
    "blocked_count": 2,
    "reviewable_count": 8,
    "recommended_next": [ /* AAV accessibles les plus pertinents */ ]
  }
  ```

#### Filtrage Avancé
- `GET /navigation/{id_apprenant}/by-discipline/{discipline}` - Navigation filtrée par discipline
- `GET /navigation/{id_apprenant}/by-prerequisite/{id_aav}` - AAV débloqués par maîtrise d'un AAV donné
- `GET /navigation/{id_apprenant}/critical-path` - Chemin critique (AAV bloquant le plus d'AAV descendants)

### Logique Métier à Implémenter

#### Algorithme "Accessibles"
```python
def get_accessible_aavs(apprenant: Apprenant) -> List[AAV]:
    ontologie = get_ontology(apprenant.ontologie_reference_id)
    accessibles = []

    for aav_id in ontologie.aavs_ids_actifs:
        aav = get_aav(aav_id)
        statut = get_statut(apprenant.id_apprenant, aav_id)

        # Non commencé
        if statut.niveau_maitrise > 0:
            continue

        # Vérifier prérequis
        prerequis_ok = True
        for prereq_id in aav.prerequis_ids:
            prereq_statut = get_statut(apprenant.id_apprenant, prereq_id)
            regles = get_regles(prereq_id)
            if prereq_statut.niveau_maitrise < regles.seuil_succes:
                prerequis_ok = False
                break

        if prerequis_ok:
            accessibles.append(aav)

    return accessibles
```

#### Algorithme "Bloques" avec Détection des Bloqueurs
```python
def get_blocked_with_reasons(apprenant: Apprenant) -> List[BlockedAAVInfo]:
    """
    Pour chaque AAV bloqué, retourne la liste des prérequis manquants
    et leur niveau de maîtrise actuel
    """
    pass
```

#### Algorithme "Revisables" (Spaced Repetition)
```python
def get_reviewable_aavs(apprenant: Apprenant) -> List[AAV]:
    """
    Basé sur la courbe d'oubli d'Ebbinghaus
    Intervalles suggérés : 1 jour, 3 jours, 7 jours, 14 jours, 30 jours
    """
    for statut in get_maitrised_aavs(apprenant):
        derniere_tentative = get_last_attempt(statut)
        jours_ecoules = (now() - derniere_tentative.date).days
        intervalle_attendu = calculer_intervalle_repetition(statut)

        if jours_ecoules >= intervalle_attendu:
            yield statut
```

### Tables SQL à Créer
```sql
-- Vue matérialisée ou table de cache optionnelle
navigation_cache (
    id_apprenant INTEGER,
    id_aav INTEGER,
    categorie TEXT, -- 'accessible', 'in_progress', 'blocked', 'reviewable'
    dernier_calcul TIMESTAMP,
    raison_blocage TEXT, -- JSON pour bloques
    PRIMARY KEY (id_apprenant, id_aav)
)

-- Historique de révisions pour spaced repetition
revision_history (
    id INTEGER PRIMARY KEY,
    id_apprenant INTEGER,
    id_aav INTEGER,
    date_revision TIMESTAMP,
    niveau_maitrise_apres REAL,
    prochaine_revision_prevue TIMESTAMP
)
```

### Intégration
- Vous dépendez du **Groupe 1** (AAV, Ontologies)
- Vous dépendez du **Groupe 2** (Apprenants)
- Vous dépendez du **Groupe 3** (Statuts, Tentatives)
- Vous fournissez des endpoints au **Groupe 4** (recommandations d'activités)
- Vous fournissez des endpoints au **Groupe 6** (détection des bloqueurs)

## Critères d'Évaluation
- Exactitude des algorithmes de catégorisation
- Performance acceptable (utilisation de cache si nécessaire)
- Découverte correcte des bloqueurs récursifs
- Tests unitaires avec graphes de prérequis complexes
- Documentation OpenAPI/Swagger
