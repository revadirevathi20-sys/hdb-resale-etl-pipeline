import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))
from clean import validate_fields, additional_cleaning, flag_anomalous_prices

def sample_row():
    return {
        "month": pd.Timestamp("2014-06-01"),
        "town": "TAMPINES",
        "flat_type": "4 ROOM",
        "flat_model": "IMPROVED",
        "storey_range": "07 TO 09",
        "resale_price": 450000.0,
        "floor_area_sqm": 90.0,
        "lease_commence_date": 1985,
        "block": "123A",
        "street_name": "TAMPINES ST 11"
    }

def test_valid_row_passes_validation():
    df = pd.DataFrame([sample_row()])
    passed, failed = validate_fields(df)
    assert len(passed) == 1
    assert len(failed) == 0

def test_invalid_town_fails_validation():
    row = sample_row()
    row["town"] = "ATLANTIS"
    df = pd.DataFrame([row])
    passed, failed = validate_fields(df)
    assert len(failed) == 1
    assert "invalid_town" in failed["fail_reason"].values[0]

def test_invalid_date_fails_validation():
    row = sample_row()
    row["month"] = pd.Timestamp("2020-01-01")  # outside Jan 2012 - Dec 2016
    df = pd.DataFrame([row])
    passed, failed = validate_fields(df)
    assert len(failed) == 1
    assert "invalid_date" in failed["fail_reason"].values[0]

def test_additional_cleaning_removes_bad_price():
    row = sample_row()
    row["resale_price"] = -500
    df = pd.DataFrame([row])
    passed, failed = additional_cleaning(df)
    assert len(failed) == 1

def test_additional_cleaning_removes_bad_floor_area():
    row = sample_row()
    row["floor_area_sqm"] = 5  
    df = pd.DataFrame([row])
    passed, failed = additional_cleaning(df)
    assert len(failed) == 1

def test_anomalous_price_flagged():
    rows = [sample_row() for _ in range(10)]
    rows[-1]["resale_price"] = 5000 
    df = pd.DataFrame(rows)
    passed, failed = flag_anomalous_prices(df)
    assert any(failed["resale_price"] <= 10000)