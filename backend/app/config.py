"""
Configuración de la aplicación cargada desde variables de entorno.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Base de datos
    database_url: str = "postgresql://ce_user:contraseña@localhost:5432/consumo_estrategico"

    # JWT
    jwt_secret_key: str = "CAMBIA_ESTO"
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24

    # Archivos
    max_file_size_mb: int = 10
    upload_dir: str = "./uploads"

    # Base de datos - pool
    db_pool_size: int = 5
    db_max_overflow: int = 10

    # Entorno
    environment: str = "development"
    debug: bool = False

    # CORS
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


settings = Settings()
