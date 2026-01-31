import argparse

from sqlalchemy.orm import Session

from app.config import settings
from app.db import Base, SessionLocal, engine
from app.ingest import import_sales_csv, list_files


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest NSW sales data files")
    parser.add_argument("--path", required=True, help="CSV file or directory")
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        files = list_files(args.path)
        total = 0
        for file_path in files:
            total += import_sales_csv(file_path, db, settings.schema_path)
        print(f"Imported {total} rows")
    finally:
        db.close()


if __name__ == "__main__":
    main()
