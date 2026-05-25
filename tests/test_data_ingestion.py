import pandas as pd

from src.data_ingestion.loader import available_mappings, load_credit_dataset, map_to_canonical_schema
from src.data_ingestion.mappings import GIVE_ME_SOME_CREDIT_MAPPING, LENDING_CLUB_MAPPING
from src.preprocessing.schema import TRAINING_COLUMNS
from src.utils.sample_data import generate_credit_sample


def test_available_mappings_include_supported_profiles() -> None:
    mappings = available_mappings()

    assert "canonical" in mappings
    assert "lending_club" in mappings
    assert "give_me_some_credit" in mappings


def test_load_canonical_dataset(tmp_path) -> None:
    path = tmp_path / "canonical.csv"
    generate_credit_sample(rows=5).to_csv(path, index=False)

    mapped = load_credit_dataset(path)

    assert list(mapped.columns) == TRAINING_COLUMNS
    assert len(mapped) == 5


def test_map_lending_club_style_dataset() -> None:
    source = pd.DataFrame(
        {
            "annual_inc": [90000],
            "dti": [18.5],
            "loan_amnt": [16000],
            "int_rate": ["12.4%"],
            "emp_length": ["10+ years"],
            "delinq_2yrs": [1],
            "revol_util": ["62.5%"],
            "open_acc": [9],
            "home_ownership": ["MORTGAGE"],
            "purpose": ["debt_consolidation"],
            "loan_status": ["Charged Off"],
        }
    )

    mapped = map_to_canonical_schema(source, LENDING_CLUB_MAPPING)

    assert mapped.loc[0, "default_flag"] == 1
    assert mapped.loc[0, "employment_length_years"] == 10
    assert mapped.loc[0, "interest_rate"] == 0.124
    assert mapped.loc[0, "revolving_utilization"] == 0.625
    assert mapped.loc[0, "credit_history_years"] == 8


def test_map_give_me_some_credit_style_dataset() -> None:
    source = pd.DataFrame(
        {
            "MonthlyIncome": [5000],
            "DebtRatio": [0.34],
            "NumberOfTime30-59DaysPastDueNotWorse": [2],
            "RevolvingUtilizationOfUnsecuredLines": [0.72],
            "NumberOfOpenCreditLinesAndLoans": [6],
            "SeriousDlqin2yrs": [1],
        }
    )

    mapped = map_to_canonical_schema(source, GIVE_ME_SOME_CREDIT_MAPPING)

    assert mapped.loc[0, "annual_income"] == 60000
    assert mapped.loc[0, "default_flag"] == 1
    assert mapped.loc[0, "home_ownership"] == "UNKNOWN"
    assert mapped.loc[0, "loan_purpose"] == "UNKNOWN"
