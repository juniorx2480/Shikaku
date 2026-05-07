import os


class Settings:
    def __init__(self) -> None:
        # Valor local por defecto sin Docker
        self.database_url: str = os.getenv("DATABASE_URL", "sqlite:///shikaku.db")


settings = Settings()
