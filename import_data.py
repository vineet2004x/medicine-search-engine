import pandas as pd
import sqlite3

# Read CSV
df = pd.read_csv("Medicine_Details.csv")

# Connect to SQLite
conn = sqlite3.connect("medicines.db")

# Select required columns
df = df[[
    "Medicine Name",
    "Composition",
    "Uses",
    "Side_effects",
    "Manufacturer"
]]

# Rename columns to match database
df.columns = [
    "MedicineName",
    "Composition",
    "Uses",
    "SideEffects",
    "Manufacturer"
]

# Insert into database
df.to_sql(
    "Medicines",
    conn,
    if_exists="append",
    index=False
)

conn.close()

print("Data imported successfully!")