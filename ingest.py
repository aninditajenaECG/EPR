import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BASE_DIR = Path(r"D:\EPR_project\RAW_EPR_DATA")

files = list(BASE_DIR.rglob("*.xlsx")) + list(BASE_DIR.rglob("*.csv"))

print("TOTAL FILES FOUND:", len(files))


def process_file(file_path):

    try:
        if file_path.suffix == ".csv":
            df = pd.read_csv(file_path)
            sheets = [("sheet1", df)]
        else:
            xls = pd.ExcelFile(file_path)
            sheets = [(sheet, xls.parse(sheet)) for sheet in xls.sheet_names]

        for sheet_name, df in sheets:

            df = df.dropna(how="all")

            records = []

            for _, row in df.iterrows():

                row_dict = row.dropna().to_dict()

                if not row_dict:
                    continue

                records.append({
                    "file_name": str(file_path.name),
                    "sheet_name": sheet_name,
                    "row_data": row_dict
                })

            if records:
                supabase.table("raw_epr_data").insert(records).execute()

        print("DONE:", file_path.name)

    except Exception as e:
        print("FAILED:", file_path.name, "ERROR:", e)


for file in files:
    print("\nPROCESSING:", file)
    process_file(file)