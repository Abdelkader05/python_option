from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import settings
from app.database import get_db_connection, init_database, to_json
from app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database(tmp_path: Path) -> None:
    settings.database_path = tmp_path / "test_groupe5.db"
    init_database()

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO ontology_reference (
                id_reference, discipline, aavs_ids_actifs, description
            ) VALUES (?, ?, ?, ?)
            """,
            (1, "Programmation C", to_json([1, 2, 3, 4, 5]), "Ontologie de test"),
        )

        aavs = [
            (
                1,
                "Bases C",
                "les bases du C",
                "Programmation",
                "Langage C",
                "Atomique",
                "Introduction au langage C",
                to_json([]),
                to_json({"seuil_succes": 0.7}),
            ),
            (
                2,
                "Variables",
                "les variables en C",
                "Programmation",
                "Langage C",
                "Atomique",
                "Manipuler des variables",
                to_json([1]),
                to_json({"seuil_succes": 0.7}),
            ),
            (
                3,
                "Conditions",
                "les conditions en C",
                "Programmation",
                "Langage C",
                "Atomique",
                "Utiliser if et else",
                to_json([2]),
                to_json({"seuil_succes": 0.7}),
            ),
            (
                4,
                "Boucles",
                "les boucles en C",
                "Programmation",
                "Langage C",
                "Atomique",
                "Utiliser while et for",
                to_json([3]),
                to_json({"seuil_succes": 0.7}),
            ),
            (
                5,
                "Fichiers",
                "les fichiers en C",
                "Systeme",
                "Langage C",
                "Atomique",
                "Lire et ecrire des fichiers",
                to_json([2]),
                to_json({"seuil_succes": 0.7}),
            ),
        ]
        cursor.executemany(
            """
            INSERT INTO aav (
                id_aav, nom, libelle_integration, discipline, enseignement,
                type_aav, description_markdown, prerequis_ids, regles_progression
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            aavs,
        )

        cursor.execute(
            """
            INSERT INTO apprenant (
                id_apprenant, nom_utilisateur, email, ontologie_reference_id
            ) VALUES (?, ?, ?, ?)
            """,
            (1, "alice", "alice@example.com", 1),
        )

        statuses = [
            (1, 1, 1, 1.0, to_json([1, 2, 3]), "2026-02-20T10:00:00+00:00"),
            (2, 1, 2, 0.5, to_json([4]), "2026-03-02T09:00:00+00:00"),
            (3, 1, 5, 0.92, to_json([5]), "2026-02-20T09:00:00+00:00"),
        ]
        cursor.executemany(
            """
            INSERT INTO statut_apprentissage (
                id, id_apprenant, id_aav_cible, niveau_maitrise,
                historique_tentatives_ids, date_derniere_session
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            statuses,
        )

        attempts = [
            (101, 1, 1, 1.0, "2026-02-20T10:00:00+00:00", 1),
            (102, 1, 2, 0.5, "2026-03-02T09:00:00+00:00", 0),
            (103, 1, 5, 0.95, "2026-02-20T09:00:00+00:00", 1),
        ]
        cursor.executemany(
            """
            INSERT INTO tentative (
                id_exercice_ou_evenement, id_apprenant, id_aav_cible,
                score_obtenu, date_tentative, est_valide
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            attempts,
        )

    yield


def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "database": "connected"}


def test_accessible_aavs() -> None:
    response = client.get("/navigation/1/accessible")
    assert response.status_code == 200
    assert [item["id_aav"] for item in response.json()] == [3]


def test_in_progress_aavs() -> None:
    response = client.get("/navigation/1/in-progress")
    assert response.status_code == 200
    assert [item["id_aav"] for item in response.json()] == [2]


def test_blocked_aavs() -> None:
    response = client.get("/navigation/1/blocked")
    assert response.status_code == 200
    data = response.json()
    assert [item["id_aav"] for item in data] == [4]
    assert data[0]["blocking_prerequisites"][0]["id_aav"] == 3


def test_reviewable_aavs() -> None:
    response = client.get("/navigation/1/reviewable")
    assert response.status_code == 200
    data = response.json()
    assert [item["id_aav"] for item in data] == [1, 5]


def test_dashboard() -> None:
    response = client.get("/navigation/1/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["accessible_count"] == 1
    assert data["in_progress_count"] == 1
    assert data["blocked_count"] == 1
    assert data["reviewable_count"] == 2
    assert data["recommended_next"][0]["id_aav"] == 3


def test_by_prerequisite() -> None:
    response = client.get("/navigation/1/by-prerequisite/3")
    assert response.status_code == 200
    assert [item["id_aav"] for item in response.json()] == [4]


def test_critical_path() -> None:
    response = client.get("/navigation/1/critical-path")
    assert response.status_code == 200
    data = response.json()
    assert data["critical_aav"]["id_aav"] == 3
    assert data["blocked_descendants_count"] == 1


def test_apprenant_not_found() -> None:
    response = client.get("/navigation/999/accessible")
    assert response.status_code == 404
    assert response.json()["error"] == "http_error"
