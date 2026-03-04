"""Gestion SQLite3 et acces aux donnees pour le groupe 5."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from app.config import settings


class DatabaseError(Exception):
    """Exception levee lors d'une erreur SQLite."""


def get_database_path() -> Path:
    """Retourne le chemin de la base active."""

    return Path(settings.database_path)


@contextmanager
def get_db_connection() -> sqlite3.Connection:
    """Ouvre une connexion SQLite avec commit/rollback automatiques."""

    db_path = get_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
        conn.commit()
    except Exception as exc:  # pragma: no cover - gestion globale
        conn.rollback()
        raise DatabaseError(f"Erreur base de donnees: {exc}") from exc
    finally:
        conn.close()


def to_json(data: Any) -> str:
    """Serialise une valeur Python en JSON."""

    return json.dumps(data, ensure_ascii=False)


def from_json(json_str: str | None, default: Any = None) -> Any:
    """Deserialise une valeur JSON."""

    if json_str in (None, ""):
        return default
    return json.loads(json_str)


def init_database() -> None:
    """Cree les tables communes et celles du groupe 5 si necessaire."""

    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS aav (
                id_aav INTEGER PRIMARY KEY,
                nom TEXT NOT NULL,
                libelle_integration TEXT,
                discipline TEXT NOT NULL,
                enseignement TEXT,
                type_aav TEXT,
                description_markdown TEXT,
                prerequis_ids TEXT DEFAULT '[]',
                prerequis_externes_codes TEXT DEFAULT '[]',
                code_prerequis_interdisciplinaire TEXT,
                aav_enfant_ponderation TEXT,
                type_evaluation TEXT,
                ids_exercices TEXT DEFAULT '[]',
                prompts_fabrication_ids TEXT DEFAULT '[]',
                regles_progression TEXT DEFAULT '{}',
                is_active BOOLEAN DEFAULT 1,
                version INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ontology_reference (
                id_reference INTEGER PRIMARY KEY,
                discipline TEXT NOT NULL,
                aavs_ids_actifs TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS apprenant (
                id_apprenant INTEGER PRIMARY KEY,
                nom_utilisateur TEXT NOT NULL UNIQUE,
                email TEXT,
                ontologie_reference_id INTEGER,
                statuts_actifs_ids TEXT DEFAULT '[]',
                codes_prerequis_externes_valides TEXT DEFAULT '[]',
                date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                derniere_connexion TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (ontologie_reference_id) REFERENCES ontology_reference(id_reference)
                    ON DELETE SET NULL ON UPDATE CASCADE
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS statut_apprentissage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_apprenant INTEGER NOT NULL,
                id_aav_cible INTEGER NOT NULL,
                niveau_maitrise REAL DEFAULT 0.0
                    CHECK (niveau_maitrise >= 0 AND niveau_maitrise <= 1),
                historique_tentatives_ids TEXT DEFAULT '[]',
                date_debut_apprentissage TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_derniere_session TIMESTAMP,
                UNIQUE (id_apprenant, id_aav_cible),
                FOREIGN KEY (id_apprenant) REFERENCES apprenant(id_apprenant) ON DELETE CASCADE,
                FOREIGN KEY (id_aav_cible) REFERENCES aav(id_aav) ON DELETE CASCADE
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tentative (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_exercice_ou_evenement INTEGER NOT NULL,
                id_apprenant INTEGER NOT NULL,
                id_aav_cible INTEGER NOT NULL,
                score_obtenu REAL CHECK (score_obtenu >= 0 AND score_obtenu <= 1),
                date_tentative TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                est_valide BOOLEAN DEFAULT 0,
                temps_resolution_secondes INTEGER,
                metadata TEXT,
                FOREIGN KEY (id_apprenant) REFERENCES apprenant(id_apprenant) ON DELETE CASCADE,
                FOREIGN KEY (id_aav_cible) REFERENCES aav(id_aav) ON DELETE CASCADE
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS navigation_cache (
                id_apprenant INTEGER NOT NULL,
                id_aav INTEGER NOT NULL,
                categorie TEXT NOT NULL,
                dernier_calcul TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                raison_blocage TEXT,
                PRIMARY KEY (id_apprenant, id_aav, categorie),
                FOREIGN KEY (id_apprenant) REFERENCES apprenant(id_apprenant) ON DELETE CASCADE,
                FOREIGN KEY (id_aav) REFERENCES aav(id_aav) ON DELETE CASCADE
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS revision_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_apprenant INTEGER NOT NULL,
                id_aav INTEGER NOT NULL,
                date_revision TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                niveau_maitrise_apres REAL NOT NULL,
                prochaine_revision_prevue TIMESTAMP,
                FOREIGN KEY (id_apprenant) REFERENCES apprenant(id_apprenant) ON DELETE CASCADE,
                FOREIGN KEY (id_aav) REFERENCES aav(id_aav) ON DELETE CASCADE
            )
            """
        )

        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_aav_active ON aav(is_active)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_statut_apprenant_aav ON statut_apprentissage(id_apprenant, id_aav_cible)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_tentative_apprenant_aav_date ON tentative(id_apprenant, id_aav_cible, date_tentative DESC)"
        )


class BaseRepository:
    """Repository minimal pour les operations generiques."""

    def __init__(self, table_name: str, primary_key: str = "id") -> None:
        self.table_name = table_name
        self.primary_key = primary_key

    def get_by_id(self, id_value: int) -> dict[str, Any] | None:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM {self.table_name} WHERE {self.primary_key} = ?",
                (id_value,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all(self, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM {self.table_name} LIMIT ? OFFSET ?",
                (limit, offset),
            )
            return [dict(row) for row in cursor.fetchall()]

    def delete(self, id_value: int) -> bool:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"DELETE FROM {self.table_name} WHERE {self.primary_key} = ?",
                (id_value,),
            )
            return cursor.rowcount > 0
