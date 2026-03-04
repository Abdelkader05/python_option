
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