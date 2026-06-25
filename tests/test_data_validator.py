import pandas as pd

from simtradedata.validators.data_validator import FundamentalDataValidator


def test_fundamental_validator_coerces_string_fields_for_range_checks():
    df = pd.DataFrame(
        {
            "roe": ["600", "not-a-number"],
            "current_ratio": ["1.2", "-0.1"],
            "debt_equity_ratio": ["0.5", "-2"],
        },
        index=pd.to_datetime(["2026-03-31", "2026-06-30"]),
    )

    assert FundamentalDataValidator.validate(df, "000001.SZ") is True
