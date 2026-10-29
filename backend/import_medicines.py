import pandas as pd
import os

INPUT_FILE = "data/raw/medicines_raw.csv"
OUTPUT_FILE = "data/medicines.csv"

df = pd.read_csv(INPUT_FILE)

df = df.rename(columns={
    "name": "medicine_name",
    "composition": "generic_name",
    "uses": "uses",
    "side_effects": "side_effects"
})

df["category"] = ""
df["precautions"] = "Use only according to professional advice."
df["prescription_required"] = "Consult a healthcare professional."
df["doctor_verified"] = "No"

df = df[
    [
        "medicine_name",
        "generic_name",
        "category",
        "uses",
        "precautions",
        "side_effects",
        "prescription_required",
        "doctor_verified"
    ]
]

df = df.dropna(subset=["medicine_name"])
df = df.drop_duplicates(subset=["medicine_name"])

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)

print("Medicine dataset converted successfully.")
print("Total medicines:", len(df))
print("Saved to:", OUTPUT_FILE)