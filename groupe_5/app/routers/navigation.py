from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime

from app.database import get_db_connection, from_json, to_json
from app.models import AAV

router = APIRouter(
    prefix="/navigation",
    tags=["Navigation"]
)

# ============================================================
# CACHE NAVIGATION
# ============================================================

def load_cache(cursor, id_apprenant, categorie):

    cursor.execute("""
        SELECT a.*
        FROM navigation_cache c
        JOIN aav a ON a.id_aav = c.id_aav
        WHERE c.id_apprenant = ?
        AND c.categorie = ?
        AND a.is_active = 1
    """, (id_apprenant, categorie))

    rows = cursor.fetchall()

    result = []

    for row in rows:
        data = dict(row)
        data["prerequis_ids"] = from_json(data["prerequis_ids"]) or []
        data["prerequis_externes_codes"] = from_json(data.get("prerequis_externes_codes")) or []
        result.append(AAV(**data))

    return result


def save_cache(cursor, id_apprenant, aav_id, categorie, raison=None):

    cursor.execute("""
        INSERT OR REPLACE INTO navigation_cache
        (id_apprenant, id_aav, categorie, dernier_calcul, raison_blocage)
        VALUES (?, ?, ?, ?, ?)
    """, (
        id_apprenant,
        aav_id,
        categorie,
        datetime.now(),
        to_json(raison) if raison else None
    ))

# ============================================================
# ACCESSIBLE
# ============================================================
@router.get("/{id_apprenant}/accessible", response_model=List[AAV])
def get_accessible_aavs(id_apprenant: int):

    with get_db_connection() as conn:
        cursor = conn.cursor()

        cached = load_cache(cursor, id_apprenant, "accessible")
        if cached:
            return cached

        accessibles = []

        cursor.execute("""
            SELECT o.aavs_ids_actifs
            FROM apprenant a
            JOIN ontology_reference o
            ON a.ontologie_reference_id = o.id_reference
            WHERE a.id_apprenant = ?
        """, (id_apprenant,))

        row = cursor.fetchone()

        if not row:
            return []

        aavs_ids = from_json(row["aavs_ids_actifs"]) or []

        for aav_id in aavs_ids:

            cursor.execute("""
                SELECT *
                FROM aav
                WHERE id_aav = ?
                AND is_active = 1
            """, (aav_id,))

            aav = cursor.fetchone()

            if not aav:
                continue

            data = dict(aav)

            data["prerequis_ids"] = from_json(data.get("prerequis_ids")) or []
            data["prerequis_externes_codes"] = from_json(data.get("prerequis_externes_codes")) or []

            cursor.execute("""
                SELECT niveau_maitrise
                FROM statut_apprentissage
                WHERE id_apprenant = ?
                AND id_aav_cible = ?
            """, (id_apprenant, aav_id))

            statut = cursor.fetchone()

            # déjà commencé → pas accessible
            if statut and statut["niveau_maitrise"] > 0:
                continue

            prerequis_ok = True

            for prereq in data["prerequis_ids"]:

                cursor.execute("""
                    SELECT niveau_maitrise
                    FROM statut_apprentissage
                    WHERE id_apprenant = ?
                    AND id_aav_cible = ?
                """, (id_apprenant, prereq))

                prereq_statut = cursor.fetchone()

                if not prereq_statut or prereq_statut["niveau_maitrise"] < 0.8:
                    prerequis_ok = False
                    break

            if prerequis_ok:

                accessibles.append(AAV(**data))

                save_cache(cursor, id_apprenant, aav_id, "accessible")

        return accessibles

# ============================================================
# IN PROGRESS
# ============================================================

@router.get("/{id_apprenant}/in-progress")
def get_in_progress_aavs(id_apprenant: int):

    with get_db_connection() as conn:
        cursor = conn.cursor()

        cached = load_cache(cursor, id_apprenant, "in_progress")
        if cached:
            return cached

        result = []

        cursor.execute("""
            SELECT a.*, s.historique_tentatives_ids
            FROM aav a
            JOIN statut_apprentissage s
            ON a.id_aav = s.id_aav_cible
            WHERE s.id_apprenant = ?
            AND s.niveau_maitrise > 0
            AND s.niveau_maitrise < 0.9
            AND a.is_active = 1
        """, (id_apprenant,))

        rows = cursor.fetchall()

        for row in rows:

            data = dict(row)

            data["prerequis_ids"] = from_json(data["prerequis_ids"]) or []
            data["historique_tentatives_ids"] = from_json(data["historique_tentatives_ids"]) or []

            result.append(data)

            save_cache(cursor, id_apprenant, data["id_aav"], "in_progress")

        return result


# ============================================================
# BLOCKED
# ============================================================

@router.get("/{id_apprenant}/blocked")
def get_blocked_aavs(id_apprenant: int):

    with get_db_connection() as conn:
        cursor = conn.cursor()

        blocked = []

        cursor.execute("SELECT * FROM aav WHERE is_active = 1")

        rows = cursor.fetchall()

        for row in rows:

            data = dict(row)

            prerequis = from_json(data["prerequis_ids"]) or []

            missing = []

            for prereq in prerequis:

                cursor.execute("""
                    SELECT niveau_maitrise
                    FROM statut_apprentissage
                    WHERE id_apprenant = ?
                    AND id_aav_cible = ?
                """, (id_apprenant, prereq))

                statut = cursor.fetchone()

                if not statut or statut["niveau_maitrise"] < 0.8:
                    missing.append(prereq)

            if missing:

                data["blocked_prerequisites"] = missing

                blocked.append(data)

                save_cache(cursor, id_apprenant, data["id_aav"], "blocked", missing)

        return blocked


# ============================================================
# REVIEWABLE
# ============================================================

@router.get("/{id_apprenant}/reviewable", response_model=List[AAV])
def get_reviewable_aavs(id_apprenant: int):

    with get_db_connection() as conn:
        cursor = conn.cursor()

        reviewable = []

        # récupérer les AAV maîtrisés
        cursor.execute("""
            SELECT a.*, s.niveau_maitrise
            FROM aav a
            JOIN statut_apprentissage s
            ON a.id_aav = s.id_aav_cible
            WHERE s.id_apprenant = ?
            AND s.niveau_maitrise >= 0.8
            AND a.is_active = 1
        """, (id_apprenant,))

        rows = cursor.fetchall()

        now = datetime.now()

        for row in rows:

            data = dict(row)

            # chercher l'historique de révision
            cursor.execute("""
                SELECT prochaine_revision_prevue
                FROM revision_history
                WHERE id_apprenant = ?
                AND id_aav = ?
            """, (id_apprenant, data["id_aav"]))

            revision = cursor.fetchone()

            # cas 1 : jamais révisé
            if not revision:
                data["prerequis_ids"] = from_json(data["prerequis_ids"]) or []
                data["prerequis_externes_codes"] = from_json(data.get("prerequis_externes_codes")) or []
                reviewable.append(AAV(**data))
                continue

            prochaine_revision = revision["prochaine_revision_prevue"]

            if prochaine_revision:
                prochaine_revision = datetime.fromisoformat(prochaine_revision)

                # cas 2 : révision due
                if prochaine_revision <= now:

                    data["prerequis_ids"] = from_json(data["prerequis_ids"]) or []
                    data["prerequis_externes_codes"] = from_json(data.get("prerequis_externes_codes")) or []

                    reviewable.append(AAV(**data))

                    save_cache(cursor, id_apprenant, data["id_aav"], "reviewable")

        return reviewable


# ============================================================
# DASHBOARD
# ============================================================

@router.get("/{id_apprenant}/dashboard")
def navigation_dashboard(id_apprenant: int):

    accessible = get_accessible_aavs(id_apprenant)
    in_progress = get_in_progress_aavs(id_apprenant)
    blocked = get_blocked_aavs(id_apprenant)
    reviewable = get_reviewable_aavs(id_apprenant)

    return {
        "accessible_count": len(accessible),
        "in_progress_count": len(in_progress),
        "blocked_count": len(blocked),
        "reviewable_count": len(reviewable),
        "recommended_next": accessible[:3]
    }

@router.get("/{id_apprenant}")
def get_all_navigation_aavs(id_apprenant: int):

    result = []

    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT a.*, s.niveau_maitrise, s.date_derniere_session
            FROM aav a
            JOIN statut_apprentissage s
            ON a.id_aav = s.id_aav_cible
            AND s.id_apprenant = ?
            WHERE a.is_active = 1
        """, (id_apprenant,))

        rows = cursor.fetchall()

        for row in rows:
            data = dict(row)

            data["prerequis_ids"] = from_json(data["prerequis_ids"]) or []
            data["prerequis_externes_codes"] = from_json(data.get("prerequis_externes_codes")) or []
            result.append(data)

    return result