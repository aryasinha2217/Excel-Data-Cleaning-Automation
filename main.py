
import pandas as pd
from pathlib import Path
import argparse
import json

def main():

    
    # ==========================================
    # COMMAND LINE INTERFACE
    # ==========================================

    parser = argparse.ArgumentParser(
        description="CleanSheet - Customer Data Cleaning Automation"
    )

    parser.add_argument(
        "input_file",
        nargs="?",
        default="data/customers.csv",
        help="Path to the input CSV or XLSX file"
    )

    args = parser.parse_args()

    input_file = Path(args.input_file)


    # Check whether the file exists
    if not input_file.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_file}"
        )

    # Read the file based on its extension
    file_extension = input_file.suffix.lower()

    if file_extension == ".csv":
        df = pd.read_csv(input_file)

    elif file_extension == ".xlsx":
        df = pd.read_excel(input_file)

    else:
        raise ValueError(
            "Unsupported file format. Please use CSV or XLSX."
        )
    
    if file_extension == ".csv":
        df = pd.read_csv(input_file)

    elif file_extension == ".xlsx":
     df = pd.read_excel(input_file)

    else:
        raise ValueError(
        "Unsupported file format. Please use CSV or XLSX."
    )

    # ==========================================
    # STAGE 10: LOAD COLUMN MAPPING
    # ========================================== 
    mapping_file = Path("config/column_mapping.json")

    if mapping_file.exists():
        try:
            with open(mapping_file, "r", encoding="utf-8") as file:
                column_mapping = json.load(file)

            if not isinstance(column_mapping, dict):
                raise ValueError(
                    "Column mapping must be a JSON object."
                )

            df = df.rename(columns=column_mapping)

            print("\nColumn mapping loaded successfully!")

        except json.JSONDecodeError:
            raise ValueError(
                "Invalid JSON configuration. "
                "Please check config/column_mapping.json."
            )

    else:
        print("\nNo column mapping file found. Using original columns.")


    # ==========================================
    # STAGE 8: INPUT DATA VALIDATION
    # ==========================================

    # Remove accidental spaces around column names
    df.columns = df.columns.str.strip()

    # Columns required by CleanSheet
    required_columns = [
        "Customer_ID",
        "Name",
        "Email",
        "Phone",
        "City"
    ]

    # Identify missing columns
    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Invalid input file. Missing required columns: "
            f"{', '.join(missing_columns)}"
        )

    print("Input file structure validated successfully!")
    if df.empty:
        raise ValueError(
            "The input file contains no customer records."
        )
    original_records = len(df)

    print(f"\nInput file loaded: {input_file}")
    print(f"Original records: {original_records}")

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
    duplicate_count = len(duplicates)

    print("Duplicate records found:")
    print(duplicates)

    print("Total duplicates:", len(duplicates))

    # Step 7: Remove duplicate customers

    df["Email"] = df["Email"].str.strip().str.lower()

    df = df[
        df["Email"].isna() |
        ~df["Email"].duplicated(keep="first")
    ]

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
    # Convert phone numbers to strings first
    df["Phone"] = df["Phone"].astype("string")

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
    # Create output directory if it doesn't exist
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filenames based on the input filename
    file_name = input_file.stem

    output_file = output_dir / f"{file_name}_cleaned.xlsx"
    report_file = output_dir / f"{file_name}_report.txt"

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

    # ==========================================
    # STAGE 6: GENERATE CLEANING REPORT
    # ==========================================

    remaining_records = len(df)
    complete_count = len(complete_records)
    incomplete_count = len(incomplete_records)

    invalid_email_count = (~df["Email_Valid"]).sum()
    invalid_phone_count = (~df["Phone_Valid"]).sum()



    with open(report_file, "w") as report:
        report.write("========== CLEANSHEET REPORT ==========\n\n")

        report.write(f"Original records: {original_records}\n")
        report.write(f"Duplicate records removed: {duplicate_count}\n")
        report.write(f"Records after duplicate removal: {remaining_records}\n\n")

        report.write(f"Complete records: {complete_count}\n")
        report.write(f"Incomplete records: {incomplete_count}\n\n")

        report.write(f"Invalid email addresses: {invalid_email_count}\n")
        report.write(f"Invalid phone numbers: {invalid_phone_count}\n\n")

        report.write(f"Excel output: {output_file}\n\n")

        report.write("========== CLEANING COMPLETED ==========\n")

    print("\nCleaning report successfully created!")
    print("Saved at:", report_file)
if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError) as error:
        print(f"\nERROR: {error}")
        print("Please check your input file and try again.")