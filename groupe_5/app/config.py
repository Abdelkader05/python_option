"""Configuration de l'application."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Parametres de configuration chargeables depuis l'environnement."""

    app_name: str = "PlatonAAV Groupe 5 API"
    app_version: str = "1.0.0"
    debug: bool = False
    database_path: Path = Field(
        default=Path(__file__).resolve().parent.parent / "groupe5.db"
    )
    review_intervals_days: tuple[int, ...] = (1, 3, 7, 14, 30)
    mastery_threshold: float = 0.9
    review_threshold: float = 0.8
    default_success_threshold: float = 0.7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="GROUPE5_",
        case_sensitive=False,
    )


settings = Settings()
