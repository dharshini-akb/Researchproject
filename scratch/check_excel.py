import pandas as pd
import openpyxl

excel_path = r"d:\finalresearchproject\project_hpo_feature_audit.xlsx"
try:
    xl = pd.ExcelFile(excel_path)
    print("Sheets in project_hpo_feature_audit.xlsx:", xl.sheet_names)
    for sheet in xl.sheet_names:
        df = xl.parse(sheet)
        print(f"\nSheet: {sheet}, Shape: {df.shape}")
        print("Columns:", df.columns.tolist())
        print(df.head(2))
except Exception as e:
    print("Error:", e)
