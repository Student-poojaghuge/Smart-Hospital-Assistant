import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)
import pandas as pd

from database.database import SessionLocal
from database.models import Medicine


CSV_FILE = "data/medicines.csv"


def load_medicines():

    db = SessionLocal()

    try:
        df = pd.read_csv(CSV_FILE)

        df = df.fillna("")

        added = 0
        skipped = 0

        for _, row in df.iterrows():

            medicine_name = str(
                row["medicine_name"]
            ).strip()

            if not medicine_name:
                continue

            existing = db.query(Medicine).filter(
                Medicine.medicine_name.ilike(
                    medicine_name
                )
            ).first()

            if existing:
                skipped += 1
                continue

            medicine = Medicine(
                medicine_name=medicine_name,
                generic_name=str(
                    row["generic_name"]
                ).strip(),
                category=str(
                    row["category"]
                ).strip(),
                uses=str(
                    row["uses"]
                ).strip(),
                precautions=str(
                    row["precautions"]
                ).strip(),
                side_effects=str(
                    row["side_effects"]
                ).strip(),
                prescription_required=str(
                    row["prescription_required"]
                ).strip(),
                doctor_verified=str(
                    row["doctor_verified"]
                ).strip()
            )

            db.add(medicine)
            added += 1

        db.commit()

        print("Medicine database import completed.")
        print("Medicines added:", added)
        print("Medicines skipped:", skipped)

        total = db.query(Medicine).count()

        print("Total medicines in database:", total)

    except Exception as e:

        db.rollback()
        print("Import failed:", e)

    finally:
        db.close()


if __name__ == "__main__":
    load_medicines()