# Références de Lecture et Ressources

Ce document compile les ressources essentielles pour réaliser le projet PlatonAAV, organisées par technologie et niveau de difficulté.

---

## 1. FastAPI

### Documentation Officielle (Obligatoire)

| Ressource | Description | Priorité |
|-----------|-------------|----------|
| [FastAPI Official Docs](https://fastapi.tiangolo.com/) | Documentation complète et tutoriels | ⭐⭐⭐ ESSENTIEL |
| [FastAPI Tutorial - User Guide](https://fastapi.tiangolo.com/tutorial/) | Guide pas à pas pour débuter | ⭐⭐⭐ ESSENTIEL |
| [FastAPI SQL Databases](https://fastapi.tiangolo.com/tutorial/sql-databases/) | Intégration SQLite/SQLAlchemy | ⭐⭐⭐ ESSENTIEL |

### Tutoriels Vidéo Recommandés

| Ressource | Auteur | Durée | Contenu |
|-----------|--------|-------|---------|
| [FastAPI Course for Beginners](https://www.youtube.com/watch?v=0sOvCWFmrtA) | freeCodeCamp | 5h | Cours complet FastAPI + SQLAlchemy |
| [FastAPI in 3 Hours](https://www.youtube.com/watch?v=7t2alSnE2-I) | Tech With Tim | 3h | API REST complète avec authentification |
| [Python API Development](https://www.youtube.com/playlist?list=PLK8U0UV9HlWskBF8HbXBGj1aV2Z4D9s5M) | Sanjeev Thiyagarajan | Playlist | Série complète sur FastAPI |

### Articles et Guides Spécifiques

```
Sujets à rechercher:
1. "FastAPI CRUD operations with SQLite"
2. "FastAPI dependency injection explained"
3. "FastAPI error handling best practices"
4. "FastAPI testing with pytest and TestClient"
```

#### Ressources Clés en Ligne
- [FastAPI Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/) - Structure avec routers
- [FastAPI Error Handling](https://fastapi.tiangolo.com/tutorial/handling-errors/) - Gestion des exceptions
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/) - Tests avec TestClient
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/) - Tâches asynchrones

---

## 2. Pydantic V2

### Documentation Essentielle

| Ressource | Lien | Description |
|-----------|------|-------------|
| [Pydantic Docs](https://docs.pydantic.dev/latest/) | docs.pydantic.dev | Documentation officielle |
| [Pydantic Models](https://docs.pydantic.dev/latest/concepts/models/) | Concepts/Models | Création de modèles |
| [Field Validation](https://docs.pydantic.dev/latest/concepts/fields/) | Concepts/Fields | Validation des champs |
| [Validators](https://docs.pydantic.dev/latest/concepts/validators/) | Concepts/Validators | Validateurs personnalisés |

### Exemples Pratiques pour le Projet

```python
# À étudier dans la documentation:

# 1. Validation de champs
from pydantic import Field
name: str = Field(min_length=3, max_length=200)

# 2. Validateurs personnalisés
from pydantic import field_validator
@field_validator('email')
def validate_email(cls, v):
    if '@' not in v:
        raise ValueError('Email invalide')
    return v

# 3. Modèles imbriqués
class AAV(BaseModel):
    regles: RegleProgression  # Modèle imbriqué

# 4. Enumération
from enum import Enum
class TypeAAV(str, Enum):
    ATOMIQUE = "Atomique"
```

### Migration Pydantic V1 → V2

Si vous trouvez des tutoriels en V1:
- [Migration Guide](https://docs.pydantic.dev/latest/migration/) - Guide officiel
- `from pydantic import BaseModel` reste identique
- `@validator` devient `@field_validator`
- `dict()` devient `model_dump()`
- `json()` devient `model_dump_json()`

---

## 3. SQLite3 avec Python

### Documentation Officielle

| Ressource | Lien | Description |
|-----------|------|-------------|
| [Python sqlite3](https://docs.python.org/3/library/sqlite3.html) | docs.python.org | Module intégré Python |
| [SQLite Tutorial](https://sqlitetutorial.net/) | sqlitetutorial.net | Tutoriels SQL complets |

### Concepts Clés à Maîtriser

#### 1. Context Managers (ESSENTIEL)
```python
# Ressource: https://docs.python.org/3/library/contextlib.html
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    conn = sqlite3.connect("db.db")
    try:
        yield conn
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()
```

#### 2. Row Factory
```python
# Documentation: https://docs.python.org/3/library/sqlite3.html#row-objects
conn.row_factory = sqlite3.Row  # Accès par nom de colonne
```

#### 3. Transactions
```python
# Ressource: https://docs.python.org/3/library/sqlite3.html#transaction-control
conn.commit()   # Valider
conn.rollback() # Annuler
```

### Tutoriels SQLite3 Python

- [Real Python - SQLite3](https://realpython.com/python-sqlite-sqlalchemy/) - Comparaison sqlite3/SQLAlchemy
- [GeeksforGeeks SQLite3](https://www.geeksforgeeks.org/python-sqlite/) - Exemples pratiques
- [TutorialsPoint SQLite](https://www.tutorialspoint.com/sqlite/index.htm) - Référence SQL

---

## 4. NetworkX (Groupes 5 et 6)

### Documentation Officielle

| Ressource | Lien | Description |
|-----------|------|-------------|
| [NetworkX Docs](https://networkx.org/documentation/stable/) | networkx.org | Documentation complète |
| [Tutorial](https://networkx.org/documentation/stable/tutorial.html) | Tutorial | Introduction rapide |

### Concepts Essentiels pour le Projet

```python
# 1. Création d'un graphe orienté
import networkx as nx
G = nx.DiGraph()  # Graphe orienté

# 2. Ajout de nœuds et arêtes
G.add_node(1, nom="AAV 1")
G.add_edge(1, 2)  # 1 -> 2 (prérequis)

# 3. Vérification DAG (Graphe Orienté Acyclique)
nx.is_directed_acyclic_graph(G)  # True/False

# 4. Chemin le plus long
nx.dag_longest_path(G)

# 5. Parcours des prédécesseurs
list(G.predecessors(2))  # [1]

# 6. Parcours des successeurs
list(G.successors(1))    # [2]
```

### Tutoriels Vidéo NetworkX

- [NetworkX Graph Analysis](https://www.youtube.com/watch?v=flqfP4L1UvA) - Graphes en Python
- [Graph Algorithms](https://www.youtube.com/playlist?list=PL9xmBV_5YoZOx9TTz1Nbiy3jcw3aA1zDX) - Algorithmes de graphes

---

## 5. Pytest et Tests Unitaires

### Documentation Essentielle

| Ressource | Lien | Description |
|-----------|------|-------------|
| [Pytest Docs](https://docs.pytest.org/) | docs.pytest.org | Framework de test |
| [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/) | FastAPI Docs | TestClient |

### Concepts à Maîtriser

#### 1. Fixtures
```python
# Documentation: https://docs.pytest.org/how-to/fixtures.html
@pytest.fixture
def client():
    return TestClient(app)
```

#### 2. Paramétrisation
```python
# Documentation: https://docs.pytest.org/how-to/parametrize.html
@pytest.mark.parametrize("id,expected", [(1, 200), (999, 404)])
def test_get_item(id, expected):
    ...
```

#### 3. Couverture de Code
```bash
# Documentation: https://pytest-cov.readthedocs.io/
pytest --cov=app --cov-report=html
```

### Tutoriels Testing

- [Pytest Tutorial](https://www.youtube.com/watch?v=cHYq1MRoyI0) - Tutoriel vidéo
- [Real Python Testing](https://realpython.com/pytest-python-testing/) - Guide complet

---

## 6. REST API et Conception d'API

### Principes REST

| Ressource | Lien | Description |
|-----------|------|-------------|
| [REST API Tutorial](https://restfulapi.net/) | restfulapi.net | Concepts REST complets |
| [RESTful API Design](https://docs.microsoft.com/en-us/azure/architecture/best-practices/api-design) | Microsoft | Bonnes pratiques |

### Codes HTTP et Méthodes

```
Méthodes HTTP:
- GET: Lecture
- POST: Création
- PUT: Remplacement complet
- PATCH: Modification partielle
- DELETE: Suppression

Codes à connaître:
- 200 OK
- 201 Created
- 204 No Content
- 400 Bad Request
- 404 Not Found
- 422 Unprocessable Entity
- 500 Internal Server Error
```

### Conception d'Endpoints

Ressources:
- [API Naming Conventions](https://restfulapi.net/resource-naming/)
- [REST API Best Practices](https://stackoverflow.blog/2020/03/02/best-practices-for-rest-api-design/)

---

## 7. Python Avancé (Utile pour le Projet)

### Concepts Recommandés

#### 1. Type Hints
```python
# Documentation: https://docs.python.org/3/library/typing.html
from typing import Optional, List, Dict, Any

def get_item(id: int) -> Optional[dict]:
    ...
```

#### 2. Dataclasses
```python
# Documentation: https://docs.python.org/3/library/dataclasses.html
from dataclasses import dataclass

@dataclass
class Config:
    database_url: str
    debug: bool = False
```

#### 3. Enumérations
```python
# Documentation: https://docs.python.org/3/library/enum.html
from enum import Enum

class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
```

### Ressources Python

- [Real Python](https://realpython.com/) - Articles de qualité
- [Python Docs](https://docs.python.org/3/) - Documentation officielle
- [Fluent Python](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/) - Livre avancé (disponible via O'Reilly)

---

## 8. Git et GitHub

### Documentation Essentielle

| Ressource | Lien | Description |
|-----------|------|-------------|
| [Git Docs](https://git-scm.com/doc) | git-scm.com | Documentation officielle |
| [GitHub Guides](https://guides.github.com/) | guides.github.com | Guides GitHub |
| [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf) | PDF | Aide-mémoire |

### Commandes Essentielles

```bash
# Configuration initiale
git init
git remote add origin https://github.com/user/repo.git

# Workflow quotidien
git add .
git commit -m "feat: description"
git push origin main

# Branches
git checkout -b feature/ma-fonctionnalite
git merge feature/ma-fonctionnalite

# Résolution de conflits
git pull origin main
# Éditer les fichiers en conflit
git add .
git commit -m "resolve: conflits de fusion"
```

### Tutoriels Git

- [Git Tutorial - Atlassian](https://www.atlassian.com/git/tutorials) - Tutoriels complets
- [Oh Shit, Git!?!](https://ohshitgit.com/) - Résolution de problèmes
- [GitHub Learning Lab](https://lab.github.com/) - Apprentissage interactif

---

## 9. Outils de Développement

### IDE Recommandés

| IDE | Lien | Extensions Recommandées |
|-----|------|------------------------|
| VS Code | [code.visualstudio.com](https://code.visualstudio.com/) | Python, Pylance, autoDocstring |
| PyCharm | [jetbrains.com/pycharm](https://www.jetbrains.com/pycharm/) | Community Edition gratuite |

### Outils de Qualité de Code

```bash
# Installation recommandée
pip install flake8 black isort mypy

# Utilisation
flake8 app/              # Vérification PEP 8
black app/               # Formatage automatique
isort app/               # Tri des imports
mypy app/                # Vérification des types
```

### Extensions VS Code pour le Projet

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "njpwerner.autodocstring",
    "eamodio.gitlens",
    "davidanson.vscode-markdownlint",
    "redhat.vscode-yaml"
  ]
}
```

---

## 10. Ressources Complémentaires

### Livres Recommandés (Disponibles en Ligne)

| Livre | Auteur | Description | Accès |
|-------|--------|-------------|-------|
| Architecture Patterns with Python | Harry Percival | Architecture logicielle Python | O'Reilly Safari |
| Python Testing with pytest | Brian Okken | Tests avec pytest | O'Reilly Safari |
| Fluent Python (2nd Ed) | Luciano Ramalho | Python avancé | O'Reilly Safari |

### Blogs et Newsletters

- [TestDriven.io](https://testdriven.io/) - Tutoriels FastAPI/Testing
- [Full Stack Python](https://www.fullstackpython.com/) - Ressources Python web
- [Real Python](https://realpython.com/) - Articles approfondis
- [FastAPI on GitHub](https://github.com/tiangolo/fastapi) - Exemples officiels

### Communautés

- [FastAPI Discord](https://discord.gg/fastapi) - Communauté officielle
- [Reddit r/Python](https://www.reddit.com/r/Python/) - Questions générales
- [Stack Overflow](https://stackoverflow.com/questions/tagged/fastapi) - FastAPI tag

---

## 11. Chemin d'Apprentissage Recommandé

### semaine 1: Pour tous

Créer le projet sous github avec la structure recommandée. 
Intégrer toutes les données fournies. 

### Semaine 2: Spécifique au Groupe

```
Jour 1-2: Comprendre votre domaine
  └─ Relire: Votre fiche de projet
  └─ Étudier: Les algorithmes requis

Jour 3-5: Implémentation spécifique
  └─ Développer: Vos endpoints spéciaux
  └─ Tester: Avec des mocks

Jour 6-7: Intégration
  └─ Tester: Avec d'autres groupes
  └─ Corriger: Problèmes d'intégration
```

### Semaine 3: Finalisation

```
Finalisation
  └─ Rédiger: README complet
  └─ Générer: Screenshots Swagger (optionel)
  └─ Vérifier: Couverture de tests > 70% >50% >10% 
  └─ Tester: Scénarios end-to-end
  └─ Soumettre: Repository GitHub final
```

---

## 12. Aide Mémoire Rapide

### Commandes Essentielles

```bash
# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Installation
pip install fastapi uvicorn pydantic pytest pytest-cov httpx

# Lancer le serveur
uvicorn app.main:app --reload

# Tests
pytest
pytest --cov=app --cov-report=html

# Qualité du code
flake8 app/
black app/
```

### Structure de Fichier Rapide

```
app/
├── __init__.py
├── main.py              # FastAPI app, routers
├── database.py          # get_db_connection()
├── models.py            # Pydantic models
└── routers/
    ├── __init__.py
    └── items.py         # @router.get("/")

tests/
├── __init__.py
└── test_items.py        # def test_get_items()
```

---

**Note**: Ces ressources sont régulièrement mises à jour. Si un lien est cassé, recherchez le titre sur Google pour trouver la nouvelle URL.

**Dernière mise à jour**: Février 2025
