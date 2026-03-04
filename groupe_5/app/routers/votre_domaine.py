"""Endpoints de navigation du groupe 5."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.config import settings
from app.database import from_json, get_db_connection, to_json
from app.models import (
    AAVNavigationInfo,
    BlockedAAVInfo,
    BlockingReason,
    DashboardResponse,
    ReviewableAAVInfo,
)

router = APIRouter(
    prefix="/navigation",
    tags=["navigation"],
    responses={404: {"description": "Apprenant non trouve"}},
)


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    if value.endswith("Z"):
        value = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _normalise_regles(raw_rules: Any) -> dict[str, Any]:
    rules = raw_rules if isinstance(raw_rules, dict) else from_json(raw_rules, {})
    if not isinstance(rules, dict):
        return {}
    return rules


def _fetch_apprenant(id_apprenant: int) -> dict[str, Any]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT *
            FROM apprenant
            WHERE id_apprenant = ? AND is_active = 1
            """,
            (id_apprenant,),
        )
        row = cursor.fetchone()
    if not row:
        raise HTTPException(
            status_code=404,
            detail=f"Apprenant avec l'ID {id_apprenant} non trouve",
        )
    return dict(row)


def _load_navigation_context(id_apprenant: int) -> dict[str, Any]:
    apprenant = _fetch_apprenant(id_apprenant)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM ontology_reference WHERE id_reference = ?",
            (apprenant["ontologie_reference_id"],),
        )
        ontology_row = cursor.fetchone()
        if not ontology_row:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Ontologie de reference non trouvee pour "
                    f"l'apprenant {id_apprenant}"
                ),
            )

        ontology = dict(ontology_row)
        ontology_ids = from_json(ontology["aavs_ids_actifs"], [])
        if not ontology_ids:
            return {
                "apprenant": apprenant,
                "ontology_ids": [],
                "aavs": {},
                "statuses": {},
                "attempts": defaultdict(list),
            }

        placeholders = ",".join("?" for _ in ontology_ids)
        cursor.execute(
            f"""
            SELECT *
            FROM aav
            WHERE is_active = 1 AND id_aav IN ({placeholders})
            """,
            ontology_ids,
        )
        aavs = {}
        for row in cursor.fetchall():
            item = dict(row)
            item["prerequis_ids"] = from_json(item["prerequis_ids"], [])
            item["regles_progression"] = _normalise_regles(item["regles_progression"])
            aavs[item["id_aav"]] = item

        cursor.execute(
            """
            SELECT *
            FROM statut_apprentissage
            WHERE id_apprenant = ?
            """,
            (id_apprenant,),
        )
        statuses = {row["id_aav_cible"]: dict(row) for row in cursor.fetchall()}

        cursor.execute(
            """
            SELECT *
            FROM tentative
            WHERE id_apprenant = ?
            ORDER BY date_tentative DESC
            """,
            (id_apprenant,),
        )
        attempts = defaultdict(list)
        for row in cursor.fetchall():
            attempts[row["id_aav_cible"]].append(dict(row))

    return {
        "apprenant": apprenant,
        "ontology_ids": ontology_ids,
        "aavs": aavs,
        "statuses": statuses,
        "attempts": attempts,
    }


def _success_threshold(aav: dict[str, Any]) -> float:
    rules = aav.get("regles_progression") or {}
    threshold = rules.get("seuil_succes")
    if isinstance(threshold, (int, float)):
        return float(threshold)
    return settings.default_success_threshold


def _mastery(aav_id: int, statuses: dict[int, dict[str, Any]]) -> float:
    status = statuses.get(aav_id)
    if not status:
        return 0.0
    return float(status.get("niveau_maitrise", 0.0) or 0.0)


def _last_activity(aav_id: int, statuses: dict[int, dict[str, Any]]) -> datetime | None:
    status = statuses.get(aav_id)
    if not status:
        return None
    return _parse_datetime(status.get("date_derniere_session"))


def _build_navigation_info(
    aav: dict[str, Any], statuses: dict[int, dict[str, Any]]
) -> AAVNavigationInfo:
    return AAVNavigationInfo(
        id_aav=aav["id_aav"],
        nom=aav["nom"],
        discipline=aav["discipline"],
        niveau_maitrise=_mastery(aav["id_aav"], statuses),
        prerequis_ids=aav.get("prerequis_ids", []),
        last_activity_at=_last_activity(aav["id_aav"], statuses),
        success_threshold=_success_threshold(aav),
    )


def _missing_prerequisites(
    aav: dict[str, Any],
    aavs: dict[int, dict[str, Any]],
    statuses: dict[int, dict[str, Any]],
) -> list[BlockingReason]:
    missing = []
    for prereq_id in aav.get("prerequis_ids", []):
        prereq = aavs.get(prereq_id)
        if not prereq:
            continue
        mastery = _mastery(prereq_id, statuses)
        required = _success_threshold(prereq)
        if mastery < required:
            missing.append(
                BlockingReason(
                    id_aav=prereq_id,
                    nom=prereq["nom"],
                    niveau_maitrise_actuel=mastery,
                    seuil_requis=required,
                )
            )
    return missing


def _get_accessible_items(context: dict[str, Any]) -> list[AAVNavigationInfo]:
    items = []
    for aav_id in context["ontology_ids"]:
        aav = context["aavs"].get(aav_id)
        if not aav:
            continue
        if _mastery(aav_id, context["statuses"]) > 0:
            continue
        if _missing_prerequisites(aav, context["aavs"], context["statuses"]):
            continue
        items.append(_build_navigation_info(aav, context["statuses"]))
    return items


def _get_in_progress_items(context: dict[str, Any]) -> list[AAVNavigationInfo]:
    items = []
    for aav_id in context["ontology_ids"]:
        level = _mastery(aav_id, context["statuses"])
        if level <= 0 or level >= settings.mastery_threshold:
            continue
        if not context["attempts"].get(aav_id):
            continue
        aav = context["aavs"].get(aav_id)
        if aav:
            items.append(_build_navigation_info(aav, context["statuses"]))
    return items


def _get_blocked_items(context: dict[str, Any]) -> list[BlockedAAVInfo]:
    items = []
    for aav_id in context["ontology_ids"]:
        aav = context["aavs"].get(aav_id)
        if not aav:
            continue
        level = _mastery(aav_id, context["statuses"])
        if level >= settings.mastery_threshold:
            continue
        missing = _missing_prerequisites(aav, context["aavs"], context["statuses"])
        if missing:
            items.append(
                BlockedAAVInfo(
                    **_build_navigation_info(aav, context["statuses"]).model_dump(),
                    blocking_prerequisites=missing,
                )
            )
    return items


def _review_interval_for_level(level: float) -> int:
    intervals = settings.review_intervals_days
    if level >= 0.98:
        return intervals[min(4, len(intervals) - 1)]
    if level >= 0.95:
        return intervals[min(3, len(intervals) - 1)]
    if level >= 0.9:
        return intervals[min(2, len(intervals) - 1)]
    return intervals[min(1, len(intervals) - 1)]


def _get_reviewable_items(context: dict[str, Any]) -> list[ReviewableAAVInfo]:
    now = datetime.now(timezone.utc)
    items = []
    for aav_id in context["ontology_ids"]:
        level = _mastery(aav_id, context["statuses"])
        if level < settings.review_threshold:
            continue
        attempts = context["attempts"].get(aav_id, [])
        if not attempts:
            continue
        last_attempt = _parse_datetime(attempts[0]["date_tentative"])
        if not last_attempt:
            continue
        days_since = (now - last_attempt).days
        expected_interval = _review_interval_for_level(level)
        if days_since < expected_interval:
            continue
        aav = context["aavs"].get(aav_id)
        if aav:
            items.append(
                ReviewableAAVInfo(
                    **_build_navigation_info(aav, context["statuses"]).model_dump(),
                    days_since_last_attempt=days_since,
                    expected_interval_days=expected_interval,
                )
            )
    return items


def _write_cache(
    id_apprenant: int, category: str, items: list[AAVNavigationInfo | BlockedAAVInfo | ReviewableAAVInfo]
) -> None:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM navigation_cache WHERE id_apprenant = ? AND categorie = ?",
            (id_apprenant, category),
        )
        for item in items:
            reason = None
            if isinstance(item, BlockedAAVInfo):
                reason = to_json(
                    [reason.model_dump() for reason in item.blocking_prerequisites]
                )
            cursor.execute(
                """
                INSERT INTO navigation_cache (id_apprenant, id_aav, categorie, raison_blocage)
                VALUES (?, ?, ?, ?)
                """,
                (id_apprenant, item.id_aav, category, reason),
            )


def _descendants_count(aav_id: int, graph: dict[int, list[int]]) -> int:
    seen: set[int] = set()
    stack = list(graph.get(aav_id, []))
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        stack.extend(graph.get(current, []))
    return len(seen)


@router.get(
    "/{id_apprenant}/accessible",
    response_model=list[AAVNavigationInfo],
    summary="Liste les AAV accessibles",
)
def get_accessible_aavs(id_apprenant: int) -> list[AAVNavigationInfo]:
    context = _load_navigation_context(id_apprenant)
    items = _get_accessible_items(context)
    _write_cache(id_apprenant, "accessible", items)
    return items


@router.get(
    "/{id_apprenant}/in-progress",
    response_model=list[AAVNavigationInfo],
    summary="Liste les AAV en cours",
)
def get_in_progress_aavs(id_apprenant: int) -> list[AAVNavigationInfo]:
    context = _load_navigation_context(id_apprenant)
    items = _get_in_progress_items(context)
    _write_cache(id_apprenant, "in_progress", items)
    return items


@router.get(
    "/{id_apprenant}/blocked",
    response_model=list[BlockedAAVInfo],
    summary="Liste les AAV bloques",
)
def get_blocked_aavs(id_apprenant: int) -> list[BlockedAAVInfo]:
    context = _load_navigation_context(id_apprenant)
    items = _get_blocked_items(context)
    _write_cache(id_apprenant, "blocked", items)
    return items


@router.get(
    "/{id_apprenant}/reviewable",
    response_model=list[ReviewableAAVInfo],
    summary="Liste les AAV a reviser",
)
def get_reviewable_aavs(id_apprenant: int) -> list[ReviewableAAVInfo]:
    context = _load_navigation_context(id_apprenant)
    items = _get_reviewable_items(context)
    _write_cache(id_apprenant, "reviewable", items)
    return items


@router.get(
    "/{id_apprenant}/dashboard",
    response_model=DashboardResponse,
    summary="Vue consolidee de navigation",
)
def get_dashboard(id_apprenant: int) -> DashboardResponse:
    context = _load_navigation_context(id_apprenant)
    accessible = _get_accessible_items(context)
    in_progress = _get_in_progress_items(context)
    blocked = _get_blocked_items(context)
    reviewable = _get_reviewable_items(context)
    recommended_next = sorted(
        accessible,
        key=lambda item: (len(item.prerequis_ids), item.id_aav),
    )[:3]
    return DashboardResponse(
        accessible_count=len(accessible),
        in_progress_count=len(in_progress),
        blocked_count=len(blocked),
        reviewable_count=len(reviewable),
        recommended_next=recommended_next,
    )


@router.get(
    "/{id_apprenant}/by-discipline/{discipline}",
    response_model=dict[str, list[AAVNavigationInfo | ReviewableAAVInfo]],
    summary="Navigation filtree par discipline",
)
def get_navigation_by_discipline(
    id_apprenant: int, discipline: str
) -> dict[str, list[AAVNavigationInfo | ReviewableAAVInfo]]:
    context = _load_navigation_context(id_apprenant)
    accessible = [
        item
        for item in _get_accessible_items(context)
        if item.discipline.lower() == discipline.lower()
    ]
    in_progress = [
        item
        for item in _get_in_progress_items(context)
        if item.discipline.lower() == discipline.lower()
    ]
    reviewable = [
        item
        for item in _get_reviewable_items(context)
        if item.discipline.lower() == discipline.lower()
    ]
    return {
        "accessible": accessible,
        "in_progress": in_progress,
        "reviewable": reviewable,
    }


@router.get(
    "/{id_apprenant}/by-prerequisite/{id_aav}",
    response_model=list[AAVNavigationInfo],
    summary="Liste les AAV debloques par la maitrise d'un prerequis",
)
def get_unlocked_by_prerequisite(
    id_apprenant: int,
    id_aav: int,
    include_already_accessible: bool = Query(default=True),
) -> list[AAVNavigationInfo]:
    context = _load_navigation_context(id_apprenant)
    accessible_ids = {item.id_aav for item in _get_accessible_items(context)}
    result = []
    for ontology_aav_id in context["ontology_ids"]:
        aav = context["aavs"].get(ontology_aav_id)
        if not aav or id_aav not in aav.get("prerequis_ids", []):
            continue
        if _mastery(ontology_aav_id, context["statuses"]) >= settings.mastery_threshold:
            continue

        remaining_prereqs = [
            prereq_id
            for prereq_id in aav.get("prerequis_ids", [])
            if prereq_id != id_aav
        ]
        still_blocked = False
        for prereq_id in remaining_prereqs:
            prereq = context["aavs"].get(prereq_id)
            if not prereq:
                continue
            if _mastery(prereq_id, context["statuses"]) < _success_threshold(prereq):
                still_blocked = True
                break
        if still_blocked:
            continue
        if not include_already_accessible and ontology_aav_id in accessible_ids:
            continue
        result.append(_build_navigation_info(aav, context["statuses"]))
    return result


@router.get(
    "/{id_apprenant}/critical-path",
    response_model=dict[str, Any],
    summary="Retourne l'AAV bloquant le plus d'AAV descendants",
)
def get_critical_path(id_apprenant: int) -> dict[str, Any]:
    context = _load_navigation_context(id_apprenant)
    graph: dict[int, list[int]] = defaultdict(list)
    for aav in context["aavs"].values():
        for prereq_id in aav.get("prerequis_ids", []):
            graph[prereq_id].append(aav["id_aav"])

    blocked_prereqs = {}
    for blocked in _get_blocked_items(context):
        for reason in blocked.blocking_prerequisites:
            if reason.id_aav not in blocked_prereqs:
                blocked_prereqs[reason.id_aav] = _descendants_count(reason.id_aav, graph)

    if not blocked_prereqs:
        return {"critical_aav": None, "blocked_descendants_count": 0}

    critical_id = max(blocked_prereqs, key=blocked_prereqs.get)
    critical_aav = context["aavs"][critical_id]
    return {
        "critical_aav": {
            "id_aav": critical_aav["id_aav"],
            "nom": critical_aav["nom"],
            "discipline": critical_aav["discipline"],
        },
        "blocked_descendants_count": blocked_prereqs[critical_id],
    }
