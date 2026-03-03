import os
from typing import List

from dotenv import load_dotenv

load_dotenv()


def _as_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _as_int(value: str, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class Settings:
    def __init__(self) -> None:
        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:test1234!@localhost:5432/football-bet",
        )
        self.secret_key = os.getenv(
            "JWT_SECRET_KEY",
            "change-me-in-production-please",
        )
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = _as_int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"),
            60,
        )
        self.refresh_token_expire_minutes = _as_int(
            os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"),
            600,
        )
        self.cors_origins = self._parse_origins(
            os.getenv(
                "CORS_ORIGINS",
                "http://localhost:3000,http://localhost:3001,http://localhost:5173,http://127.0.0.1:5173",
            )
        )
        self.auto_create_tables = _as_bool(os.getenv("DB_AUTO_CREATE_TABLES"), True)
        self.ldap_server_url = os.getenv("LDAP_SERVER_URL", "ldap://10.3.12.17")
        self.ldap_server_port = _as_int(os.getenv("LDAP_SERVER_PORT"), 389)
        self.ldap_email_domain = os.getenv("LDAP_EMAIL_DOMAIN", "mobifone.vn")

    @staticmethod
    def _parse_origins(raw: str) -> List[str]:
        if not raw:
            return []
        return [origin.strip() for origin in raw.split(",") if origin.strip()]


settings = Settings()
