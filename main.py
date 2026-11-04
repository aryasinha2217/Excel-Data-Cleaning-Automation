
import pandas as pd

# Step 1: Define the input file
input_file = "data/customers.csv"

# Step 2: Read the CSV file
df = pd.read_csv(input_file)

# Step 3: Display the original data
print("\n========== CUSTOMER DATA ==========")
print(df)

# Step 4: Display dataset information
print("\n========== DATASET INFORMATION ==========")
print("Total records:", len(df))
print("Total columns:", len(df.columns))

# Step 5: Check missing values
print("\n========== MISSING VALUES ==========")
print(df.isnull().sum())

# Step 6: Identify duplicate customers

print("\n========== DUPLICATE RECORDS ==========")

# Find duplicate email addresses
duplicates = df[
    df["Email"].notna() &
    df["Email"].str.strip().str.lower().duplicated()
]

print("Duplicate records found:")
print(duplicates)

print("Total duplicates:", len(duplicates))

# Step 7: Remove duplicate customers

df["Email"] = df["Email"].str.strip().str.lower()

df = df.drop_duplicates(
    subset=["Email"],
    keep="first"
)

print("\n========== AFTER DUPLICATE REMOVAL ==========")
print("Remaining records:", len(df))
print(df)

# Step 8: Data Standardisation

print("\n========== DATA STANDARDISATION ==========")

# Clean customer names
df["Name"] = df["Name"].str.strip().str.title()

# Clean email addresses
df["Email"] = df["Email"].str.strip().str.lower()

# Clean phone numbers
df["Phone"] = (
    df["Phone"]
    .str.replace(r"[\s()-]", "", regex=True)
)

# Standardise city names
df["City"] = df["City"].str.strip().str.title()

print("\nCleaned customer data:")
print(df)

# Step 9: Handle missing values

print("\n========== MISSING VALUE HANDLING ==========")

# Convert empty strings and whitespace-only values to missing values
df = df.replace(r"^\s*$", pd.NA, regex=True)

# Define required columns
required_columns = ["Name", "Email", "Phone", "City"]

# Identify incomplete records
incomplete_records = df[
    df[required_columns].isna().any(axis=1)
]

# Identify complete records
complete_records = df[
    df[required_columns].notna().all(axis=1)
]

# Display results
print("Complete records:", len(complete_records))
print("Incomplete records:", len(incomplete_records))

print("\nINCOMPLETE CUSTOMER RECORDS:")
print(incomplete_records)

print("\nCOMPLETE CUSTOMER RECORDS:")
print(complete_records)

# Step 10: Validate email and phone numbers

import re

def is_valid_email(email):
    if pd.isna(email):
        return False

    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    return bool(re.match(pattern, str(email)))


def is_valid_phone(phone):
    if pd.isna(phone):
        return False

    # Our sample project uses 10-digit Indian phone numbers
    return bool(re.fullmatch(r"\d{10}", str(phone)))


# Check email validity
df["Email_Valid"] = df["Email"].apply(is_valid_email)

# Check phone validity
df["Phone_Valid"] = df["Phone"].apply(is_valid_phone)

print("\n========== VALIDATION RESULTS ==========")

print("Invalid emails:", (~df["Email_Valid"]).sum())
print("Invalid phone numbers:", (~df["Phone_Valid"]).sum())

# ==========================================
# STAGE 5: EXPORT CLEANED DATA TO EXCEL
# ==========================================

output_file = "output/cleaned_customers.xlsx"

with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="All Records", index=False)
    complete_records.to_excel(
        writer,
        sheet_name="Complete Records",
        index=False
    )
    incomplete_records.to_excel(
        writer,
        sheet_name="Incomplete Records",
        index=False
    )

print("\n========== EXCEL EXPORT ==========")
print("Excel file successfully created!")
print("Saved at:", output_file)
