
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
