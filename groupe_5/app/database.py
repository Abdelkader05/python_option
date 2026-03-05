
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

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS navigation_cache (
                id_apprenant INTEGER,
                id_aav INTEGER,
                categorie TEXT,
                dernier_calcul TIMESTAMP,
                raison_blocage TEXT,

                PRIMARY KEY (id_apprenant, id_aav),

                FOREIGN KEY (id_apprenant)
                    REFERENCES apprenant(id_apprenant)
                    ON DELETE CASCADE,

                FOREIGN KEY (id_aav)
                    REFERENCES aav(id_aav)
                    ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS revision_history (
                id INTEGER PRIMARY KEY,

                id_apprenant INTEGER,
                id_aav INTEGER,

                date_revision TIMESTAMP,
                niveau_maitrise_apres REAL,
                prochaine_revision_prevue TIMESTAMP,

                FOREIGN KEY (id_apprenant)
                    REFERENCES apprenant(id_apprenant)
                    ON DELETE CASCADE,

                FOREIGN KEY (id_aav)
                    REFERENCES aav(id_aav)
                    ON DELETE CASCADE
            )
        """)
        
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