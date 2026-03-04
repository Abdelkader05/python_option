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
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
pytest>=7.4.0
httpx>=0.25.0
networkx>=3.2.0  # Pour groupes 5 et 6
```

---

## 2. Module Database (database.py)

### 2.1 Objectif

Fournir une connexion unique et thread-safe à la base SQLite3 avec gestion automatique des transactions.

### 2.2 Implémentation Détaillée

```python
# app/database.py

import sqlite3
import json
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from pathlib import Path

# Configuration
DATABASE_PATH = Path("platonAAV.db")

class DatabaseError(Exception):
    """Exception personnalisée pour les erreurs de base de données."""
    pass

@contextmanager
def get_db_connection():
    """
    Context manager pour gérer les connexions SQLite3.

    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM aav")
            results = cursor.fetchall()

    Avantages:
    - Gestion automatique des transactions (commit/rollback)
    - Fermeture garantie de la connexion
    - Accessibilité des colonnes par nom (row_factory)
    """
    conn = sqlite3.connect(DATABASE_PATH)
    # Permet d'accéder aux colonnes par nom: row['nom_colonne']
    conn.row_factory = sqlite3.Row

    try:
        yield conn
        conn.commit()  # Validation automatique si tout s'est bien passé
    except Exception as e:
        conn.rollback()  # Annulation en cas d'erreur
        raise DatabaseError(f"Erreur base de données: {str(e)}") from e
    finally:
        conn.close()  # Fermeture garantie


def init_database():
    """
    Initialise la base de données avec les tables communes.
    Chaque groupe ajoute ses propres tables ici.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Activer les clés étrangères (désactivées par défaut en SQLite)
        cursor.execute("PRAGMA foreign_keys = ON")

        # ============================================
        # TABLE COMMUNE: AAV (Groupe 1)
        # ============================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS aav (
                id_aav INTEGER PRIMARY KEY,
                nom TEXT NOT NULL,
                libelle_integration TEXT,
                discipline TEXT NOT NULL,
                enseignement TEXT,
                type_aav TEXT CHECK(type_aav IN ('Atomique', 'Composite (Chapitre)')),
                description_markdown TEXT,
                prerequis_ids TEXT,  -- Stocké en JSON: [1, 2, 3]
                prerequis_externes_codes TEXT,  -- JSON: ["CODE1", "CODE2"]
                code_prerequis_interdisciplinaire TEXT,
                aav_enfant_ponderation TEXT,  -- JSON: [[1, 0.5], [2, 0.5]]
                type_evaluation TEXT CHECK(type_evaluation IN (
                    'Humaine', 'Calcul Automatisé', 'Compréhension par Chute',
                    'Validation par Invention', 'Exercice de Critique',
                    'Évaluation par les Pairs', 'Agrégation (Composite)'
                )),
                ids_exercices TEXT,  -- JSON: [101, 102, 103]
                prompts_fabrication_ids TEXT,  -- JSON: [201, 202]
                regles_progression TEXT,  -- JSON object
                is_active BOOLEAN DEFAULT 1,
                version INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Index pour accélérer les recherches fréquentes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_aav_discipline ON aav(discipline)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_aav_type ON aav(type_aav)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_aav_active ON aav(is_active)")

        # ============================================
        # TABLE COMMUNE: OntologyReference (Groupe 1)
        # ============================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ontology_reference (
                id_reference INTEGER PRIMARY KEY,
                discipline TEXT NOT NULL,
                aavs_ids_actifs TEXT NOT NULL,  -- JSON: [1, 2, 3, 4, 5]
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ============================================
        # TABLE COMMUNE: Apprenant (Groupe 2)
        # ============================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS apprenant (
                id_apprenant INTEGER PRIMARY KEY,
                nom_utilisateur TEXT NOT NULL UNIQUE,
                email TEXT,
                ontologie_reference_id INTEGER,
                statuts_actifs_ids TEXT,  -- JSON: [1, 2, 3]
                codes_prerequis_externes_valides TEXT,  -- JSON: ["CODE1"]
                date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                derniere_connexion TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (ontologie_reference_id) REFERENCES ontology_reference(id_reference)
                    ON DELETE SET NULL
                    ON UPDATE CASCADE
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_apprenant_username ON apprenant(nom_utilisateur)")

        # ============================================
        # TABLE COMMUNE: StatutApprentissage (Groupe 3)
        # ============================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS statut_apprentissage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_apprenant INTEGER NOT NULL,
                id_aav_cible INTEGER NOT NULL,
                niveau_maitrise REAL
                    CHECK (niveau_maitrise >= 0 AND niveau_maitrise <= 1)
                    DEFAULT 0.0,
                historique_tentatives_ids TEXT,  -- JSON: [1, 2, 3, 4, 5]
                date_debut_apprentissage TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_derniere_session TIMESTAMP,
                est_maitrise BOOLEAN GENERATED ALWAYS AS (niveau_maitrise >= 0.9) STORED,
                UNIQUE(id_apprenant, id_aav_cible),
                FOREIGN KEY (id_apprenant) REFERENCES apprenant(id_apprenant)
                    ON DELETE CASCADE,
                FOREIGN KEY (id_aav_cible) REFERENCES aav(id_aav)
                    ON DELETE CASCADE
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_statut_apprenant ON statut_apprentissage(id_apprenant)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_statut_aav ON statut_apprentissage(id_aav_cible)")

        # ============================================
        # TABLE COMMUNE: Tentative (Groupe 3)
        # ============================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tentative (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_exercice_ou_evenement INTEGER NOT NULL,
                id_apprenant INTEGER NOT NULL,
                id_aav_cible INTEGER NOT NULL,
                score_obtenu REAL
                    CHECK (score_obtenu >= 0 AND score_obtenu <= 1),
                date_tentative TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                est_valide BOOLEAN DEFAULT 0,
                temps_resolution_secondes INTEGER,
                metadata TEXT,  -- JSON: details supplémentaires
                FOREIGN KEY (id_apprenant) REFERENCES apprenant(id_apprenant)
                    ON DELETE CASCADE,
                FOREIGN KEY (id_aav_cible) REFERENCES aav(id_aav)
                    ON DELETE CASCADE
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tentative_apprenant ON tentative(id_apprenant)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tentative_aav ON tentative(id_aav_cible)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tentative_date ON tentative(date_tentative)")

        conn.commit()
        print("✅ Base de données initialisée avec succès")


# ============================================
# Fonctions utilitaires pour le JSON
# ============================================

def to_json(data: Any) -> str:
    """Convertit une donnée Python en chaîne JSON."""
    return json.dumps(data, ensure_ascii=False)

def from_json(json_str: str) -> Any:
    """Convertit une chaîne JSON en donnée Python."""
    if json_str is None:
        return None
    return json.loads(json_str)


# ============================================
# Pattern Repository de Base
# ============================================

class BaseRepository:
    """
    Classe de base pour tous les repositories.
    Fournit les opérations CRUD standardisées.
    """

    def __init__(self, table_name: str, primary_key: str = "id"):
        self.table_name = table_name
        self.primary_key = primary_key

    def get_by_id(self, id_value: int) -> Optional[Dict[str, Any]]:
        """Récupère un enregistrement par sa clé primaire."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM {self.table_name} WHERE {self.primary_key} = ?",
                (id_value,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Récupère tous les enregistrements avec pagination."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM {self.table_name} LIMIT ? OFFSET ?",
                (limit, offset)
            )
            return [dict(row) for row in cursor.fetchall()]

    def delete(self, id_value: int) -> bool:
        """Supprime un enregistrement. Retourne True si supprimé."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"DELETE FROM {self.table_name} WHERE {self.primary_key} = ?",
                (id_value,)
            )
            return cursor.rowcount > 0
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

```python
# app/models.py

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Literal
from enum import Enum
from datetime import datetime

# ============================================
# ÉNUMÉRATIONS
# ============================================

class TypeEvaluationAAV(str, Enum):
    """Types d'évaluation possibles pour un AAV."""
    HUMAINE = "Humaine"
    CALCUL = "Calcul Automatisé"
    CHUTE = "Compréhension par Chute"
    INVENTION = "Validation par Invention"
    CRITIQUE = "Exercice de Critique"
    EVALUATION_PAIRS = "Évaluation par les Pairs"
    EVALUATION_AGREGEE = "Agrégation (Composite)"

class TypeAAV(str, Enum):
    """Types d'AAV possibles."""
    ATOMIQUE = "Atomique"
    COMPOSITE = "Composite (Chapitre)"

class NiveauDifficulte(str, Enum):
    """Niveaux de difficulté pour les exercices."""
    DEBUTANT = "debutant"
    INTERMEDIAIRE = "intermediaire"
    AVANCE = "avance"

# ============================================
# MODÈLES DE BASE (Communs à tous les groupes)
# ============================================

class RegleProgression(BaseModel):
    """
    Règles déterminant comment un apprenant progresse sur un AAV.

    Exemple:
        - seuil_succes: 0.7 (70% pour réussir)
        - nombre_succes_consecutifs: 3 (3 réussites d'affilée = maîtrise)
    """
    seuil_succes: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Score minimum pour considérer une tentative comme réussie"
    )
    maitrise_requise: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Niveau de maîtrise à atteindre pour valider l'AAV"
    )
    nombre_succes_consecutifs: int = Field(
        default=1,
        ge=1,
        description="Nombre de réussites consécutives requises"
    )
    nombre_jugements_pairs_requis: int = Field(
        default=3,
        ge=1,
        description="Pour évaluation par les pairs: jugements nécessaires"
    )
    tolerance_jugement: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Marge de tolérance pour les évaluations par pairs"
    )

class AAVBase(BaseModel):
    """Champs de base pour un AAV (création et mise à jour)."""
    nom: str = Field(..., min_length=3, max_length=200, description="Nom technique de l'AAV")
    libelle_integration: str = Field(
        ...,
        min_length=5,
        description="Forme grammaticale pour insertion dans une phrase"
    )
    discipline: str = Field(..., min_length=2, description="Discipline (ex: Mathématiques)")
    enseignement: str = Field(..., description="Enseignement spécifique (ex: Algèbre)")
    type_aav: TypeAAV
    description_markdown: str = Field(..., min_length=10, description="Description complète")
    prerequis_ids: List[int] = Field(default_factory=list, description="IDs des AAV prérequis")
    prerequis_externes_codes: List[str] = Field(default_factory=list)
    code_prerequis_interdisciplinaire: Optional[str] = None
    type_evaluation: TypeEvaluationAAV

    @field_validator('libelle_integration')
    @classmethod
    def validate_libelle(cls, v: str) -> str:
        """Vérifie que le libellé peut s'intégrer dans une phrase."""
        phrase_test = f"Nous allons travailler {v}"
        if len(phrase_test) > 250:
            raise ValueError("Libellé trop long pour une phrase fluide")
        return v

class AAVCreate(AAVBase):
    """Modèle pour la création d'un AAV (POST)."""
    id_aav: int = Field(..., gt=0, description="Identifiant unique de l'AAV")
    regles_progression: RegleProgression = Field(default_factory=RegleProgression)

class AAVUpdate(BaseModel):
    """Modèle pour la mise à jour partielle (PATCH). Tous les champs sont optionnels."""
    nom: Optional[str] = Field(None, min_length=3, max_length=200)
    libelle_integration: Optional[str] = None
    description_markdown: Optional[str] = None
    prerequis_ids: Optional[List[int]] = None
    is_active: Optional[bool] = None

class AAV(AAVBase):
    """Modèle complet d'un AAV (réponse API)."""
    id_aav: int
    is_active: bool = True
    version: int = 1
    created_at: datetime
    updated_at: datetime

    class Config:
        """Configuration Pydantic V2."""
        from_attributes = True  # Permet de créer depuis un objet SQLAlchemy/dict

# ============================================
# MODÈLES POUR LES RÉPONSES API
# ============================================

class ErrorResponse(BaseModel):
    """Format standard pour les réponses d'erreur."""
    error: str = Field(..., description="Type d'erreur")
    message: str = Field(..., description="Message lisible par l'utilisateur")
    details: Optional[dict] = Field(None, description="Détails techniques supplémentaires")
    timestamp: datetime = Field(default_factory=datetime.now)

class PaginatedResponse(BaseModel):
    """Format standard pour les réponses paginées."""
    items: List[dict]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_previous: bool

class SuccessResponse(BaseModel):
    """Format standard pour les confirmations de succès."""
    success: bool = True
    message: str
    id: Optional[int] = None
    data: Optional[dict] = None
```

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

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()

# ============================================
# GESTIONNAIRES D'EXCEPTIONS GLOBAUX
# ============================================

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Gère les erreurs HTTP 404, 400, etc."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Gère les erreurs de validation Pydantic (422)."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "Les données fournies sont invalides",
            "details": errors,
            "path": str(request.url)
        }
    )

@app.exception_handler(DatabaseError)
async def database_exception_handler(request: Request, exc: DatabaseError):
    """Gère les erreurs de base de données."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "database_error",
            "message": "Une erreur est survenue lors de l'accès aux données",
            "details": {"error": str(exc)},
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Attrape toutes les exceptions non gérées."""
    # En production, ne pas exposer les détails de l'erreur
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "Une erreur interne est survenue",
            "path": str(request.url)
        }
    )
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

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from app.models import AAV, AAVCreate, AAVUpdate, PaginatedResponse
from app.database import get_db_connection, BaseRepository, to_json
import sqlite3

router = APIRouter(
    prefix="/aavs",
    tags=["AAVs"],
    responses={
        404: {"description": "AAV non trouvé"},
        422: {"description": "Données invalides"}
    }
)

# Repository spécifique
class AAVRepository(BaseRepository):
    def __init__(self):
        super().__init__("aav", "id_aav")

    def create(self, data: dict) -> int:
        """Crée un AAV et retourne son ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Conversion des listes en JSON
            prerequis_json = to_json(data.get('prerequis_ids', []))

            cursor.execute("""
                INSERT INTO aav (
                    id_aav, nom, libelle_integration, discipline, enseignement,
                    type_aav, description_markdown, prerequis_ids, type_evaluation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['id_aav'],
                data['nom'],
                data['libelle_integration'],
                data['discipline'],
                data['enseignement'],
                data['type_aav'],
                data['description_markdown'],
                prerequis_json,
                data['type_evaluation']
            ))

            return data['id_aav']

    def update(self, id_aav: int, data: dict) -> bool:
        """Met à jour un AAV (partiellement ou complètement)."""
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Construction dynamique de la requête UPDATE
            # Seuls les champs non-null sont mis à jour
            fields = []
            values = []

            for key, value in data.items():
                if value is not None:
                    fields.append(f"{key} = ?")
                    # Conversion JSON si nécessaire
                    if isinstance(value, list):
                        value = to_json(value)
                    values.append(value)

            if not fields:
                return False

            values.append(id_aav)
            query = f"UPDATE aav SET {', '.join(fields)} WHERE id_aav = ?"

            cursor.execute(query, values)
            return cursor.rowcount > 0

# Instance du repository
repo = AAVRepository()

# ============================================
# ENDPOINTS CRUD
# ============================================

@router.get("/", response_model=List[AAV])
def list_aavs(
    discipline: Optional[str] = Query(None, description="Filtrer par discipline"),
    type_aav: Optional[str] = Query(None, description="Filtrer par type"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre maximum de résultats"),
    offset: int = Query(0, ge=0, description="Offset pour la pagination")
):
    """
    Liste tous les AAV avec possibilité de filtrer par discipline ou type.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        query = "SELECT * FROM aav WHERE is_active = 1"
        params = []

        if discipline:
            query += " AND discipline = ?"
            params.append(discipline)

        if type_aav:
            query += " AND type_aav = ?"
            params.append(type_aav)

        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [AAV(**dict(row)) for row in rows]

@router.get("/{id_aav}", response_model=AAV)
def get_aav(id_aav: int):
    """
    Récupère un AAV spécifique par son identifiant.
    """
    data = repo.get_by_id(id_aav)
    if not data:
        raise HTTPException(status_code=404, detail="AAV non trouvé")
    return AAV(**data)

@router.post("/", response_model=AAV, status_code=201)
def create_aav(aav: AAVCreate):
    """
    Crée un nouvel AAV. L'ID doit être unique.
    """
    # Vérifier si l'ID existe déjà
    existing = repo.get_by_id(aav.id_aav)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Un AAV avec l'ID {aav.id_aav} existe déjà"
        )

    try:
        repo.create(aav.model_dump())
        created = repo.get_by_id(aav.id_aav)
        return AAV(**created)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id_aav}", response_model=AAV)
def update_aav_full(id_aav: int, aav: AAVCreate):
    """
    Remplace complètement un AAV (tous les champs).
    """
    existing = repo.get_by_id(id_aav)
    if not existing:
        raise HTTPException(status_code=404, detail="AAV non trouvé")

    # Force l'ID de l'URL
    data = aav.model_dump()
    data['id_aav'] = id_aav

    # Supprimer l'ancien et recréer (ou faire un vrai UPDATE)
    repo.delete(id_aav)
    repo.create(data)

    updated = repo.get_by_id(id_aav)
    return AAV(**updated)

@router.patch("/{id_aav}", response_model=AAV)
def update_aav_partial(id_aav: int, aav: AAVUpdate):
    """
    Met à jour partiellement un AAV (seuls les champs fournis sont modifiés).
    """
    existing = repo.get_by_id(id_aav)
    if not existing:
        raise HTTPException(status_code=404, detail="AAV non trouvé")

    # Ne met à jour que les champs non-null
    update_data = {k: v for k, v in aav.model_dump().items() if v is not None}

    if update_data:
        repo.update(id_aav, update_data)

    updated = repo.get_by_id(id_aav)
    return AAV(**updated)

@router.delete("/{id_aav}", status_code=204)
def delete_aav(id_aav: int):
    """
    Supprime (ou désactive) un AAV.
    Retourne 204 No Content en cas de succès.
    """
    existing = repo.get_by_id(id_aav)
    if not existing:
        raise HTTPException(status_code=404, detail="AAV non trouvé")

    # Soft delete: marquer comme inactif plutôt que supprimer
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE aav SET is_active = 0 WHERE id_aav = ?",
            (id_aav,)
        )

    return None  # 204 No Content
```

---

## 6. Tests Unitaires avec Pytest

### 6.1 Structure des Tests

```python
# tests/test_aavs.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_database, get_db_connection
import os

# Client de test
client = TestClient(app)

# Fixture: exécutée avant chaque test
@pytest.fixture(autouse=True)
def setup_database():
    """Initialise une base de données de test propre."""
    # Utiliser une base de test séparée
    os.environ['DATABASE_PATH'] = 'test_platonAAV.db'

    # Supprimer l'ancienne base de test
    if os.path.exists('test_platonAAV.db'):
        os.remove('test_platonAAV.db')

    # Initialiser la base
    init_database()

    yield  # Le test s'exécute ici

    # Nettoyage après le test
    if os.path.exists('test_platonAAV.db'):
        os.remove('test_platonAAV.db')

# ============================================
# TESTS CRUD
# ============================================

def test_create_aav():
    """Test la création d'un AAV."""
    response = client.post("/aavs/", json={
        "id_aav": 1,
        "nom": "Test AAV",
        "libelle_integration": "le test d'AAV",
        "discipline": "Test",
        "enseignement": "Unit Testing",
        "type_aav": "Atomique",
        "description_markdown": "Description de test",
        "prerequis_ids": [],
        "type_evaluation": "Calcul Automatisé"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["nom"] == "Test AAV"
    assert data["id_aav"] == 1

def test_get_aav():
    """Test la récupération d'un AAV existant."""
    # Créer un AAV d'abord
    client.post("/aavs/", json={
        "id_aav": 2,
        "nom": "AAV à récupérer",
        "libelle_integration": "la récupération",
        "discipline": "Test",
        "enseignement": "Test",
        "type_aav": "Atomique",
        "description_markdown": "Test",
        "prerequis_ids": [],
        "type_evaluation": "Humaine"
    })

    # Récupérer
    response = client.get("/aavs/2")
    assert response.status_code == 200
    assert response.json()["nom"] == "AAV à récupérer"

def test_get_aav_not_found():
    """Test la récupération d'un AAV inexistant (404)."""
    response = client.get("/aavs/99999")
    assert response.status_code == 404
    assert "non trouvé" in response.json()["message"]

def test_update_aav_partial():
    """Test la mise à jour partielle (PATCH)."""
    # Créer
    client.post("/aavs/", json={
        "id_aav": 3,
        "nom": "Nom original",
        "libelle_integration": "l'original",
        "discipline": "Test",
        "enseignement": "Test",
        "type_aav": "Atomique",
        "description_markdown": "Description originale",
        "prerequis_ids": [],
        "type_evaluation": "Humaine"
    })

    # Modifier uniquement le nom
    response = client.patch("/aavs/3", json={"nom": "Nom modifié"})
    assert response.status_code == 200
    assert response.json()["nom"] == "Nom modifié"
    assert response.json()["description_markdown"] == "Description originale"

def test_list_aavs_with_filter():
    """Test le filtrage de la liste."""
    # Créer plusieurs AAV
    for i in range(4, 7):
        client.post("/aavs/", json={
            "id_aav": i,
            "nom": f"AAV {i}",
            "libelle_integration": f"l'AAV {i}",
            "discipline": "Math" if i % 2 == 0 else "Physique",
            "enseignement": "Test",
            "type_aav": "Atomique",
            "description_markdown": "Test",
            "prerequis_ids": [],
            "type_evaluation": "Humaine"
        })

    # Filtrer par discipline
    response = client.get("/aavs/?discipline=Math")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # AAV 4 et 6

def test_delete_aav():
    """Test la suppression (soft delete)."""
    # Créer
    client.post("/aavs/", json={
        "id_aav": 10,
        "nom": "AAV à supprimer",
        "libelle_integration": "la suppression",
        "discipline": "Test",
        "enseignement": "Test",
        "type_aav": "Atomique",
        "description_markdown": "Test",
        "prerequis_ids": [],
        "type_evaluation": "Humaine"
    })

    # Supprimer
    response = client.delete("/aavs/10")
    assert response.status_code == 204

    # Vérifier qu'il n'est plus accessible
    response = client.get("/aavs/10")
    assert response.status_code == 404

# ============================================
# TESTS DE VALIDATION
# ============================================

def test_create_aav_invalid_data():
    """Test la création avec données invalides (422)."""
    response = client.post("/aavs/", json={
        "id_aav": 20,
        "nom": "AB",  # Trop court (< 3 caractères)
        "libelle_integration": "test",
        "discipline": "Test",
        "enseignement": "Test",
        "type_aav": "TypeInvalide",  # Type non valide
        "description_markdown": "Test",
        "prerequis_ids": [],
        "type_evaluation": "Humaine"
    })

    assert response.status_code == 422
    assert "validation_error" in response.json()["error"]
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

from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database import init_database
from app.routers import aavs  # Chaque groupe importe ses routers

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application."""
    # Startup: initialisation
    print("🚀 Initialisation de la base de données...")
    init_database()
    yield
    # Shutdown: nettoyage
    print("🛑 Arrêt du serveur")

app = FastAPI(
    title="PlatonAAV API",
    description="""
    API REST pour la gestion des Acquis d'Apprentissage Visés (AAV).

    ## Groupes

    * **AAVs** - Gestion des acquis (Groupe 1)
    * **Learners** - Gestion des apprenants (Groupe 2)
    * etc.
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Inclusion des routers
app.include_router(aavs.router)
# app.include_router(learners.router)  # Décommenter selon le groupe

@app.get("/")
def root():
    return {
        "message": "Bienvenue sur l'API PlatonAAV",
        "documentation": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    """Endpoint pour vérifier que le serveur fonctionne."""
    return {"status": "healthy", "database": "connected"}
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
