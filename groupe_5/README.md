# Groupe 5 - Operateurs de Navigation

Implementation FastAPI de la partie commune du projet PlatonAAV et des operateurs de navigation du groupe 5.

## Structure

- `app/main.py` : application FastAPI, lifespan et gestion globale des erreurs
- `app/database.py` : connexion SQLite3, initialisation des tables communes et du groupe 5
- `app/models.py` : modeles Pydantic communs et reponses navigation
- `app/config.py` : configuration chargee depuis l'environnement
- `app/routers/votre_domaine.py` : endpoints navigation
- `tests/test_votre_domaine.py` : tests API avec base SQLite temporaire

## Endpoints principaux

- `GET /navigation/{id_apprenant}/accessible`
- `GET /navigation/{id_apprenant}/in-progress`
- `GET /navigation/{id_apprenant}/blocked`
- `GET /navigation/{id_apprenant}/reviewable`
- `GET /navigation/{id_apprenant}/dashboard`
- `GET /navigation/{id_apprenant}/by-discipline/{discipline}`
- `GET /navigation/{id_apprenant}/by-prerequisite/{id_aav}`
- `GET /navigation/{id_apprenant}/critical-path`

## Lancement

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload


# Lancement en mode développement (reload automatique)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Lancement en production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

```

## Tests

```bash
# Tous les tests
pytest

# Tests avec couverture
pytest --cov=app --cov-report=html

# Tests spécifiques
pytest tests/test_aavs.py -v
```
