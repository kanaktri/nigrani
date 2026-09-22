"""
Centralised settings. Every configurable value lives here and is read from
the environment (see .env.example) - nothing is hardcoded in business logic.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- App ---
    APP_NAME: str = "DoSJE Nigrani API"
    ENV: str = "development"
    DEBUG: bool = True

    # --- Database ---
    DATABASE_URL: str = "sqlite:///./dosje_nigrani.db"

    # --- Auth ---
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12  # 12 hours - inspectors work a shift

    # --- CORS ---
    # Comma-separated allowed frontend origins, e.g.
    # "https://your-dashboard.onrender.com,http://localhost:5173".
    # "*" (the default) allows any origin - fine for local dev; set this
    # explicitly once a real frontend URL exists, via an env var, not a
    # DEBUG-linked switch (that combination used to silently block every
    # origin once DEBUG was turned off for production - the opposite of
    # what you'd want).
    CORS_ORIGINS: str = "*"

    # --- Rate limiting ---
    LOGIN_RATE_LIMIT: str = "5/minute"  # per source IP, via slowapi

    # --- Object storage (evidence files) ---
    STORAGE_BACKEND: str = "local"  # "local" | "s3"
    STORAGE_LOCAL_PATH: str = "./evidence_store"
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "evidence-bucket"

    # --- Assignment engine ---
    FAIRNESS_WINDOW: int = 5  # cycles an inspector can't be repaired with same institute
    GEOFENCE_RADIUS_METERS: float = 500.0

    # --- VC calls ---
    VC_PICKUP_WINDOW_SECONDS: int = 120


settings = Settings()
