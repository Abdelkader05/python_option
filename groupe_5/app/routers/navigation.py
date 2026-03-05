from fastapi import APIRouter, HTTPException
from typing import List
from app.database import get_db_connection, from_json
from app.models import AAV

router = APIRouter(
    prefix="/navigation",
    tags=["Navigation"],
    responses={
        404: {"description": "Apprenant non trouvé"}
    }
)



@router.get("/{id_apprenant}/accessible", response_model=List[AAV])
def get_accessible_aavs(id_apprenant: int):

    accessibles = []

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # récupérer tous les AAV actifs
        cursor.execute("SELECT * FROM aav WHERE is_active = 1")
        rows = cursor.fetchall()

        for row in rows:
            data = dict(row)

            data["prerequis_ids"] = from_json(data["prerequis_ids"]) or []
            data["prerequis_externes_codes"] = from_json(data.get("prerequis_externes_codes")) or []

            cursor.execute(
                "SELECT niveau_maitrise FROM statut_apprentissage WHERE id_apprenant = ? AND id_aav_cible = ?",
                (id_apprenant, data["id_aav"])
            )
            statut = cursor.fetchone()

            if statut and data["niveau_maitrise"] > 0:
                continue


            prerequis_ok = True
            for prereq in data["prerequis_ids"]:

                cursor.execute(
                    "SELECT est_maitrise FROM statut_apprentissage WHERE id_apprenant = ? AND id_aav_cible = ?",
                    (id_apprenant, prereq)
                )

                prereq_statut = cursor.fetchone()

                if not prereq_statut or not prereq_statut["est_maitrise"] :
                    prerequis_ok = False
                    break

            if prerequis_ok:
                accessibles.append(AAV(**data))

    return accessibles



@router.get("/{id_apprenant}/in-progress", response_model=List[AAV, ])
def get_in_progress_aavs(id_apprenant: int):

    result = []

    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT a.* , s.historique_tentatives_ids
            FROM aav a
            JOIN statut_apprentissage s
            ON a.id_aav = s.id_aav_cible
            WHERE s.id_apprenant = ?
            AND NOT s.est_maitrise
            AND a.is_active = 1
        """, (id_apprenant,))

        rows = cursor.fetchall()

        for row in rows:
            data = dict(row)

            data["prerequis_ids"] = from_json(data["prerequis_ids"]) or []
            data["prerequis_externes_codes"] = from_json(data.get("prerequis_externes_codes")) or []

            result.append(AAV(**data))

    return result



@router.get("/{id_apprenant}/blocked")
def get_blocked_aavs(id_apprenant: int):

    blocked = []

    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM aav WHERE is_active = 1")
        rows = cursor.fetchall()

        for row in rows:
            data = dict(row)

            prerequis = from_json(data["prerequis_ids"]) or []

            missing = []

            for prereq in prerequis:

                cursor.execute(
                    "SELECT niveau_maitrise FROM statut_apprentissage WHERE id_apprenant = ? AND id_aav = ?",
                    (id_apprenant, prereq)
                )

                statut = cursor.fetchone()

                if not statut or statut["niveau_maitrise"] < 0.7:
                    missing.append(prereq)

            if missing:
                blocked.append({
                    "id_aav": data["id_aav"],
                    "nom": data["nom"],
                    "missing_prerequisites": missing
                })

    return blocked


# ============================================
# AAV À RÉVISER
# ============================================

@router.get("/{id_apprenant}/reviewable", response_model=List[AAV])
def get_reviewable_aavs(id_apprenant: int):

    result = []

    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT a.*, s.niveau_maitrise
            FROM aav a
            JOIN statut_apprentissage s
            ON a.id_aav = s.id_aav
            WHERE s.id_apprenant = ?
            AND s.niveau_maitrise >= 0.8
            AND a.is_active = 1
        """, (id_apprenant,))

        rows = cursor.fetchall()

        for row in rows:
            data = dict(row)

            data["prerequis_ids"] = from_json(data["prerequis_ids"]) or []
            data["prerequis_externes_codes"] = from_json(data.get("prerequis_externes_codes")) or []

            result.append(AAV(**data))

    return result


# ============================================
# DASHBOARD NAVIGATION
# ============================================

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