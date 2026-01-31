from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Central Coast Housing Market Wizard"
    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/hmp"
    model_dir: str = "./models"
    metrics_path: str = "./models/metrics.json"
    schema_path: str = "./data/schema.yaml"
    data_region: str = "Central Coast, NSW"
    domain_api_key: str | None = None
    domain_enabled: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
