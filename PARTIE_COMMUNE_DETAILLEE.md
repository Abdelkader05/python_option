# Partie Commune Détaillée - Guide d'Implémentation

## Introduction

Ce document décrit en détail la **partie commune** que chacun des 8 groupes doit implémenter. Il s'agit de la fondation sur laquelle chaque groupe construit sa spécificité.
Ce sont des recommandations qui permettront de fuisionner les programmes.


---

## 1. Architecture Globale

### 1.1 Structure de Fichiers Recommandée

```
votre_groupe_X/
├── app/
│   ├── __init__.py
│   ├── main.py              # Point d'entrée FastAPI
│   ├── database.py          # Gestion SQLite3
│   ├── models.py            # Modèles Pydantic
│   ├── config.py           # Configuration
│   └── routers/
│       ├── __init__.py
│       └── votre_domaine.py  # Vos endpoints ICI VOTRE CODE
├── tests/
│   ├── __init__.py
│   └── test_votre_domaine.py #  ICI VOTRE CODE
├── requirements.txt
└── README.md  #  ICI VOS INFORMATION
```

### 1.2 Technologies Obligatoires

| Technologie | Version | Usage |
|-------------|---------|-------|
| **FastAPI** | ≥ 0.100.0 | Framework web REST |
| **Uvicorn** | ≥ 0.23.0 | Serveur ASGI |
| **Pydantic** | ≥ 2.0.0 | Validation des données |
| **SQLite3** | (built-in) | Base de données |
| **Python** | ≥ 3.9 | Langage |

### 1.3 Fichier requirements.txt

```txt

```

---

## 2. Module Database (database.py)

### 2.1 Objectif

Fournir une connexion unique et thread-safe à la base SQLite3 avec gestion automatique des transactions.

### 2.2 Implémentation Détaillée

```python

```

### 2.3 Explications Clés

#### Le Context Manager (`@contextmanager`)

Un **context manager** est un pattern Python qui garantit que certaines opérations sont exécutées avant et après un bloc de code, même en cas d'erreur.

**Avantages pour la base de données:**
1. **Transaction atomique** : `commit()` ne s'exécute que si tout le bloc réussit
2. **Rollback automatique** : En cas d'exception, les changements sont annulés
3. **Fermeture garantie** : `conn.close()` s'exécute toujours (même si erreur)

#### Le Row Factory

```python
conn.row_factory = sqlite3.Row
```

Sans cela, `cursor.fetchone()` retourne un tuple: `(1, "Nom", "Desc")`

Avec cela, on peut accéder par nom: `row['nom']` → `"Nom"`

C'est essentiel pour un code lisible et maintenable.

#### Stockage JSON dans SQLite

SQLite n'a pas de type "array" ou "object". On utilise le type `TEXT` pour stocker du JSON:

```python
# Stockage
prerequis_ids = to_json([1, 2, 3, 4])  # "[1, 2, 3, 4]"

# Récupération
prerequis = from_json(row['prerequis_ids'])  # [1, 2, 3, 4]
```

---

## 3. Modèles Pydantic (models.py)

### 3.1 Objectif

Définir la structure des données avec validation automatique. Pydantic garantit que les données reçues/envoyées respectent le format attendu.

### 3.2 Implémentation Détaillée


### 3.3 Concepts Pydantic Clés

#### Validation avec Field()

```python
nom: str = Field(
    ...,           # ... = champ obligatoire (required)
    min_length=3,  # Validation: minimum 3 caractères
    max_length=200 # Validation: maximum 200 caractères
)
```

#### Validation Personnalisée (@field_validator)

```python
@field_validator('libelle_integration')
@classmethod
def validate_libelle(cls, v: str) -> str:
    # Cette méthode est appelée automatiquement lors de la validation
    if len(v) < 5:
        raise ValueError("Le libellé doit faire au moins 5 caractères")
    return v
```

#### Héritage de Modèles

```
AAVBase (champs communs)
    ├── AAVCreate (champs pour création + id)
    ├── AAVUpdate (tous optionnels pour PATCH)
    └── AAV (modèle complet avec métadonnées)
```

Cette hiérarchie permet de:
- **AAVCreate**: Forcer certains champs obligatoires à la création
- **AAVUpdate**: Permettre des mises à jour partielles (tout optionnel)
- **AAV**: Retourner la représentation complète avec métadonnées

---

## 4. Gestion des Erreurs HTTP

### 4.1 Objectif

Retourner des codes HTTP standardisés avec des messages compréhensibles.

### 4.2 Table des Codes HTTP à Utiliser

| Code | Nom | Usage |
|------|-----|-------|
| **200** | OK | Requête réussie (GET, PUT) |
| **201** | Created | Création réussie (POST) |
| **204** | No Content | Suppression réussie (DELETE) |
| **400** | Bad Request | Requête mal formée |
| **404** | Not Found | Ressource inexistante |
| **422** | Unprocessable Entity | Données invalides (validation Pydantic) |
| **500** | Internal Server Error | Erreur serveur inattendue |

### 4.3 Implémentation des Exceptions HTTP

```python
# app/main.py ou app/exceptions.py

```

### 4.4 Utilisation dans les Routers

```python
from fastapi import APIRouter, HTTPException
from app.models import AAV, AAVCreate, ErrorResponse

router = APIRouter()

@router.get("/{id_aav}", response_model=AAV)
def get_aav(id_aav: int):
    """
    Récupère un AAV par son ID.
    Retourne 404 si l'AAV n'existe pas.
    """
    aav_data = repository.get_by_id(id_aav)

    if not aav_data:
        # Lève une exception HTTP 404
        raise HTTPException(
            status_code=404,
            detail=f"AAV avec l'ID {id_aav} non trouvé"
        )

    return AAV(**aav_data)

@router.post("/", response_model=AAV, status_code=201)
def create_aav(aav: AAVCreate):
    """
    Crée un nouvel AAV.
    Retourne 201 en cas de succès.
    Retourne 422 si les données sont invalides (validation automatique par Pydantic).
    """
    try:
        # Conversion en dict pour SQLite
        data = aav.model_dump()
        created_id = repository.create(data)

        # Récupère l'objet créé
        created = repository.get_by_id(created_id)
        return AAV(**created)

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=400,
            detail=f"Un AAV avec l'ID {aav.id_aav} existe déjà"
        )
```

---

## 5. Structure Complète d'un Router

### 5.1 Exemple Complet (AAV)

```python
# app/routers/aavs.py

```

---

## 6. Tests Unitaires avec Pytest

### 6.1 Structure des Tests

```python
# tests/test_aavs.py

```

### 6.2 Exécution des Tests

```bash
# Tous les tests
pytest

# Tests avec couverture
pytest --cov=app --cov-report=html

# Tests spécifiques
pytest tests/test_aavs.py -v

# Tests avec détail
pytest -v --tb=short
```

---

## 7. Documentation OpenAPI (Swagger)

### 7.1 Génération Automatique

FastAPI génère automatiquement la documentation OpenAPI à partir des modèles Pydantic et des type hints.

Accessible via:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **JSON OpenAPI**: `http://localhost:8000/openapi.json`

### 7.2 Amélioration de la Documentation

```python
from fastapi import APIRouter, Query
from typing import Annotated

router = APIRouter()

@router.get(
    "/{id_aav}",
    response_model=AAV,
    summary="Récupère un AAV",
    description="""
    Retourne les détails complets d'un AAV par son identifiant.

    **Cas d'erreur:**
    - `404`: L'AAV n'existe pas ou a été désactivé
    """,
    responses={
        200: {
            "description": "AAV trouvé",
            "content": {
                "application/json": {
                    "example": {
                        "id_aav": 1,
                        "nom": "Théorème de Pythagore",
                        "type_aav": "Atomique"
                    }
                }
            }
        },
        404: {"description": "AAV non trouvé"}
    }
)
def get_aav(
    id_aav: Annotated[int, Query(description="Identifiant unique de l'AAV")]
):
    ...
```

---

## 8. Lancer l'Application

### 8.1 Fichier main.py Complet

```python
# app/main.py

```

### 8.2 Commande de Lancement

```bash
# Installation des dépendances
pip install -r requirements.txt

# Lancement en mode développement (reload automatique)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Lancement en production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 9. Checklist de Validation

Avant de soumettre votre projet, vérifiez:

### Fonctionnalité
- [ ] Tous les endpoints CRUD fonctionnent (POST, GET, PUT, PATCH, DELETE)
- [ ] La validation Pydantic rejette les données invalides
- [ ] Les codes HTTP sont corrects (201 pour création, 404 si inexistant, etc.)
- [ ] La pagination fonctionne pour les listes
- [ ] Les filtres de recherche fonctionnent

### Code
- [ ] Le code suit les conventions PEP 8
- [ ] Les fonctions ont des docstrings
- [ ] Les types sont annotés (type hints)
- [ ] Pas de code dupliqué (utilisation du BaseRepository)

### Tests
- [ ] Tous les tests passent (`pytest`)
- [ ] Couverture de tests > 80%
- [ ] Tests pour les cas d'erreur (404, 422, 500)

### Documentation
- [ ] README.md explique comment lancer le projet
- [ ] La documentation Swagger est complète (`/docs`)
- [ ] Les modèles Pydantic ont des descriptions

---

## 10. Anti-Patterns à Éviter

### ❌ Ne PAS faire:

```python
# Mauvais: connexion non fermée
def get_data():
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM table")
    return cursor.fetchall()  # Connexion jamais fermée!

# Mauvais: pas de gestion d'erreur
@app.get("/item/{id}")
def get_item(id: int):
    return repository.get_by_id(id)  # Retourne None si inexistant

# Mauvais: pas de validation
@app.post("/item")
def create_item(data: dict):  # dict trop générique
    ...
```

### ✅ FAIRE:

```python
# Bon: context manager
with get_db_connection() as conn:
    ...

# Bon: gestion explicite des erreurs
@app.get("/item/{id}")
def get_item(id: int):
    item = repository.get_by_id(id)
    if not item:
        raise HTTPException(404, "Item non trouvé")
    return item

# Bon: validation Pydantic
@app.post("/item")
def create_item(data: ItemCreate):  # Modèle Pydantic spécifique
    ...
```

---

*Fin du document de la Partie Commune*
