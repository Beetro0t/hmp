import argparse
from pathlib import Path

import pandas as pd

from app.config import settings
from app.ml import save_artifacts, train_models
from app.metrics_store import save_metrics


def load_sales_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


def run_training(data_path: str) -> tuple[dict[str, float], int]:
    df = load_sales_data(data_path)
    artifacts, metrics, rows = train_models(df, settings.data_region)
    Path(settings.model_dir).mkdir(parents=True, exist_ok=True)
    save_artifacts(artifacts, f"{settings.model_dir}/model.joblib")
    save_metrics(settings.metrics_path, metrics)
    return metrics, rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Train valuation models")
    parser.add_argument("--data", required=True, help="Path to CSV data")
    args = parser.parse_args()

    metrics, rows = run_training(args.data)
    print("Training complete")
    print(f"Rows: {rows}")
    for key, value in metrics.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
