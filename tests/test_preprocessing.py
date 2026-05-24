from src.preprocessing.pipeline import CreditDataPreprocessor
from src.utils.sample_data import generate_credit_sample


def test_preprocessor_cleans_required_columns() -> None:
    data = generate_credit_sample(rows=25)
    data.loc[0, "annual_income"] = None

    cleaned = CreditDataPreprocessor(require_target=True).fit_transform(data)

    assert cleaned["annual_income"].isna().sum() == 0
    assert cleaned["home_ownership"].str.isupper().all()
