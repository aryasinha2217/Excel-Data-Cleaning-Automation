import pytest
from main import split_complete_incomplete
import pandas as pd
from main import remove_duplicate_emails
from main import is_valid_phone
from main import is_valid_email
from main import apply_column_mapping


def test_valid_email():
    assert is_valid_email("rahul@gmail.com") == True


def test_invalid_email():
    assert is_valid_email("rahulgmail.com") == False


def test_empty_email():
    assert is_valid_email(None) == False

def test_valid_phone():
    assert is_valid_phone("9876543210") == True


def test_invalid_phone():
    assert is_valid_phone("98765432") == False


def test_empty_phone():
    assert is_valid_phone(None) == False

def test_email_with_uppercase():
    assert is_valid_email("RAHUL@GMAIL.COM") == True


def test_email_with_spaces():
    assert is_valid_email(" rahul@gmail.com ") == False


def test_email_without_domain_extension():
    assert is_valid_email("rahul@gmail") == False

def test_phone_with_letters():
    assert is_valid_phone("98765abc10") == False


def test_phone_with_special_characters():
    assert is_valid_phone("98765-43210") == False


def test_phone_with_eleven_digits():
    assert is_valid_phone("98765432101") == False

def test_remove_duplicate_emails():
    df = pd.DataFrame({
        "Name": ["Rahul", "Priya", "Rahul Sharma"],
        "Email": [
            "rahul@gmail.com",
            "priya@gmail.com",
            "RAHUL@gmail.com"
        ]
    })

    result = remove_duplicate_emails(df)

    assert len(result) == 2
    assert list(result["Name"]) == ["Rahul", "Priya"]


def test_preserve_missing_emails():
    df = pd.DataFrame({
        "Name": ["Rahul", "Priya"],
        "Email": [None, None]
    })

    result = remove_duplicate_emails(df)

    assert len(result) == 2


def test_duplicate_removal_does_not_modify_original():
    df = pd.DataFrame({
        "Email": ["RAHUL@gmail.com", "rahul@gmail.com"]
    })

    original_length = len(df)

    remove_duplicate_emails(df)

    assert len(df) == original_length
def test_split_complete_and_incomplete_records():
    df = pd.DataFrame({
        "Name": ["Rahul", "Priya", "Amit"],
        "Email": ["rahul@gmail.com", None, "amit@gmail.com"],
        "Phone": ["9876543210", "9876543211", "9876543212"],
        "City": ["Delhi", "Mumbai", "Pune"]
    })

    cleaned, complete, incomplete = split_complete_incomplete(df)

    assert len(complete) == 2
    assert len(incomplete) == 1


def test_whitespace_is_treated_as_missing():
    df = pd.DataFrame({
        "Name": ["Rahul", "Priya"],
        "Email": ["rahul@gmail.com", "   "],
        "Phone": ["9876543210", "9876543211"],
        "City": ["Delhi", "Mumbai"]
    })

    cleaned, complete, incomplete = split_complete_incomplete(df)

    assert len(complete) == 1
    assert len(incomplete) == 1
    assert pd.isna(cleaned.loc[1, "Email"])


def test_missing_value_handling_does_not_modify_original():
    df = pd.DataFrame({
        "Name": ["Rahul", "Priya"],
        "Email": ["rahul@gmail.com", "   "],
        "Phone": ["9876543210", "9876543211"],
        "City": ["Delhi", "Mumbai"]
    })

    original = df.copy()

    split_complete_incomplete(df)

    pd.testing.assert_frame_equal(df, original)

def test_apply_column_mapping():
    df = pd.DataFrame({
        "ID": [101],
        "Full_Name": ["Rahul Sharma"],
        "Email_Address": ["rahul@gmail.com"],
        "Mobile": ["9876543210"],
        "Location": ["Delhi"]
    })

    mapping = {
        "ID": "Customer_ID",
        "Full_Name": "Name",
        "Email_Address": "Email",
        "Mobile": "Phone",
        "Location": "City"
    }

    result = apply_column_mapping(df, "config/column_mapping.json")

    assert "Customer_ID" in result.columns
    assert "Name" in result.columns
    assert "Email" in result.columns
    assert "Phone" in result.columns
    assert "City" in result.columns

def test_apply_column_mapping_when_file_missing(tmp_path):
    df = pd.DataFrame({
        "Name": ["Rahul"],
        "Email": ["rahul@gmail.com"]
    })

    missing_file = tmp_path / "missing.json"

    result = apply_column_mapping(df, missing_file)

    assert list(result.columns) == ["Name", "Email"]
    assert len(result) == 1

def test_apply_column_mapping_with_invalid_json(tmp_path):
    df = pd.DataFrame({
        "ID": [101],
        "Full_Name": ["Rahul Sharma"]
    })

    invalid_file = tmp_path / "invalid.json"
    invalid_file.write_text('{"ID": "Customer_ID" "Full_Name": "Name"}')

    with pytest.raises(ValueError, match="Invalid JSON configuration"):
        apply_column_mapping(df, invalid_file)

def test_apply_column_mapping_with_wrong_json_type(tmp_path):
    df = pd.DataFrame({
        "ID": [101]
    })

    invalid_file = tmp_path / "wrong_type.json"
    invalid_file.write_text('["ID", "Name", "Email"]')

    with pytest.raises(ValueError, match="Column mapping must be a JSON object"):
        apply_column_mapping(df, invalid_file)

def test_column_mapping_does_not_modify_original(tmp_path):
    df = pd.DataFrame({
        "ID": [101],
        "Full_Name": ["Rahul"]
    })

    original = df.copy()

    mapping_file = tmp_path / "mapping.json"
    mapping_file.write_text(
        '{"ID": "Customer_ID", "Full_Name": "Name"}'
    )

    result = apply_column_mapping(df, mapping_file)

    pd.testing.assert_frame_equal(df, original)

    assert "Customer_ID" in result.columns
    assert "Name" in result.columns