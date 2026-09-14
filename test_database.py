from database.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)

tables = inspector.get_table_names()

print("\n🏥 Smart Hospital Assistant Database")
print("-----------------------------------")

for table in tables:
    print("✅", table)

print("-----------------------------------")
print("Total tables:", len(tables))