"""Modeles Pydantic pour la partie commune et la navigation."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class TypeEvaluationAAV(str, Enum):
    HUMAINE = "Humaine"
    CALCUL = "Calcul Automatisé"
    CHUTE = "Compréhension par Chute"
    INVENTION = "Validation par Invention"
    CRITIQUE = "Exercice de Critique"
    EVALUATION_PAIRS = "Évaluation par les Pairs"
    EVALUATION_AGREGEE = "Agrégation (Composite)"


class TypeAAV(str, Enum):
    ATOMIQUE = "Atomique"
    COMPOSITE = "Composite (Chapitre)"


class RegleProgression(BaseModel):
    seuil_succes: float = Field(default=0.7, ge=0.0, le=1.0)
    maitrise_requise: float = Field(default=1.0, ge=0.0, le=1.0)
    nombre_succes_consecutifs: int = Field(default=1, ge=1)
    nombre_jugements_pairs_requis: int = Field(default=3, ge=1)
    tolerance_jugement: float = Field(default=0.2, ge=0.0, le=1.0)


class AAVBase(BaseModel):
    nom: str = Field(..., min_length=3, max_length=200)
    libelle_integration: str = Field(..., min_length=5)
    discipline: str = Field(..., min_length=2)
    enseignement: str = Field(..., min_length=2)
    type_aav: TypeAAV
    description_markdown: str = Field(..., min_length=10)
    prerequis_ids: list[int] = Field(default_factory=list)
    prerequis_externes_codes: list[str] = Field(default_factory=list)
    code_prerequis_interdisciplinaire: str | None = None
    type_evaluation: TypeEvaluationAAV

    @field_validator("libelle_integration")
    @classmethod
    def validate_libelle(cls, value: str) -> str:
        if len(f"Nous allons travailler {value}") > 250:
            raise ValueError("Libelle trop long pour une phrase fluide")
        return value


class AAVCreate(AAVBase):
    id_aav: int = Field(..., gt=0)
    regles_progression: RegleProgression = Field(default_factory=RegleProgression)


class AAVUpdate(BaseModel):
    nom: str | None = Field(default=None, min_length=3, max_length=200)
    libelle_integration: str | None = None
    description_markdown: str | None = None
    prerequis_ids: list[int] | None = None
    is_active: bool | None = None


class AAV(AAVBase):
    id_aav: int
    regles_progression: RegleProgression = Field(default_factory=RegleProgression)
    is_active: bool = True
    version: int = 1
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: dict[str, Any] | list[dict[str, Any]] | None = None
    path: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    id: int | None = None
    data: dict[str, Any] | None = None


class AAVNavigationInfo(BaseModel):
    id_aav: int
    nom: str
    discipline: str
    niveau_maitrise: float = Field(ge=0.0, le=1.0)
    prerequis_ids: list[int] = Field(default_factory=list)
    last_activity_at: datetime | None = None
    success_threshold: float = Field(ge=0.0, le=1.0)


class BlockingReason(BaseModel):
    id_aav: int
    nom: str
    niveau_maitrise_actuel: float = Field(ge=0.0, le=1.0)
    seuil_requis: float = Field(ge=0.0, le=1.0)


class BlockedAAVInfo(AAVNavigationInfo):
    blocking_prerequisites: list[BlockingReason] = Field(default_factory=list)


class ReviewableAAVInfo(AAVNavigationInfo):
    days_since_last_attempt: int
    expected_interval_days: int


class DashboardResponse(BaseModel):
    accessible_count: int
    in_progress_count: int
    blocked_count: int
    reviewable_count: int
    recommended_next: list[AAVNavigationInfo]
