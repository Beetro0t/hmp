from pathlib import Path

import pandas as pd
import yaml
from sqlalchemy.orm import Session

from app.models import Sale


def load_schema(schema_path: str) -> dict[str, str]:
    with open(schema_path, "r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    return raw["columns"]


def import_sales_csv(
    file_path: str,
    db: Session,
    schema_path: str,
) -> int:
    column_map = load_schema(schema_path)
    df = pd.read_csv(file_path)
    df = df.rename(columns=column_map)
    df["sale_date"] = pd.to_datetime(df["sale_date"]).dt.date
    records = df.to_dict(orient="records")

    created = 0
    for record in records:
        sale = Sale(**record)
        db.add(sale)
        created += 1
    db.commit()
    return created


def list_files(path: str) -> list[str]:
    target = Path(path)
    if target.is_dir():
        return [str(p) for p in target.glob("*.csv")]
    return [str(target)]
