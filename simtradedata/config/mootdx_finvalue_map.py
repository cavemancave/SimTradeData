"""
FINVALUE ID to PTrade field mapping for mootdx financial data.

This file maps mootdx FINVALUE array indices to PTrade field names.
Reference: docs/reference/mootdx_api/docs/api/fields.md
"""

# FINVALUE position -> (PTrade field name, description, unit)
# Note: FINVALUE data is 0-indexed array from mootdx finance() API
FINVALUE_TO_PTRADE = {
    # Report date (YYMMDD format, e.g., 150930 = 2015Q3)
    0: ("_report_date_raw", "Report period (YYMMDD)", None),

    # Per-share indicators
    1: ("basic_eps", "Basic EPS", "yuan"),
    2: ("_eps_deducted", "EPS after non-recurring", "yuan"),
    3: ("undivided_profit", "Undistributed profit per share", "yuan"),
    4: ("naps", "Net asset value per share", "yuan"),
    5: ("capital_surplus_fund_ps", "Capital reserve per share", "yuan"),
    6: ("roe", "Return on equity", "percent"),
    7: ("net_operate_cash_flow_ps", "Operating cash flow per share", "yuan"),

    # Balance sheet - key items
    8: ("cash_equivalents", "Cash and equivalents", "yuan"),
    11: ("account_receivable", "Accounts receivable", "yuan"),
    17: ("inventories", "Inventory", "yuan"),
    21: ("total_current_assets", "Total current assets", "yuan"),
    27: ("fixed_assets", "Fixed assets", "yuan"),
    33: ("intangible_assets", "Intangible assets", "yuan"),
    39: ("total_non_current_assets", "Total non-current assets", "yuan"),
    40: ("total_assets", "Total assets", "yuan"),
    41: ("shortterm_loan", "Short-term borrowings", "yuan"),
    44: ("accounts_payable", "Accounts payable", "yuan"),
    54: ("total_current_liability", "Total current liabilities", "yuan"),
    55: ("longterm_loan", "Long-term borrowings", "yuan"),
    62: ("total_non_current_liability", "Total non-current liabilities", "yuan"),
    63: ("total_liability", "Total liabilities", "yuan"),
    64: ("paidin_capital", "Paid-in capital (share capital)", "yuan"),
    68: ("retained_profit", "Undistributed profits", "yuan"),
    72: ("total_shareholder_equity", "Total shareholders' equity", "yuan"),

    # Income statement
    74: ("operating_revenue", "Operating revenue", "yuan"),
    75: ("operating_cost", "Operating cost", "yuan"),
    80: ("financial_expense", "Finance expenses", "yuan"),
    86: ("operating_profit", "Operating profit", "yuan"),
    92: ("total_profit", "Total profit", "yuan"),
    95: ("net_profit", "Net profit", "yuan"),
    96: ("np_parent_company_owners", "Net profit attributable to parent", "yuan"),

    # Cash flow statement
    107: ("net_operate_cash_flow", "Net cash from operations", "yuan"),
    119: ("net_invest_cash_flow", "Net cash from investing", "yuan"),
    128: ("net_finance_cash_flow", "Net cash from financing", "yuan"),

    # Solvency analysis
    159: ("current_ratio", "Current ratio", "ratio"),
    160: ("quick_ratio", "Quick ratio", "ratio"),
    162: ("interest_cover", "Interest coverage ratio", "ratio"),

    # Operating efficiency analysis
    172: ("accounts_receivables_turnover_rate", "A/R turnover rate", "times"),
    173: ("inventory_turnover_rate", "Inventory turnover rate", "times"),
    175: ("total_asset_turnover_rate", "Total asset turnover rate", "times"),
    179: ("current_assets_turnover_rate", "Current assets turnover rate", "times"),

    # Growth analysis
    183: ("operating_revenue_grow_rate", "Revenue YoY growth", "percent"),
    184: ("net_profit_grow_rate", "Net profit YoY growth", "percent"),
    185: ("net_asset_grow_rate", "Net asset YoY growth", "percent"),
    187: ("total_asset_grow_rate", "Total asset YoY growth", "percent"),

    # Profitability analysis
    197: ("roe_weighted", "Weighted ROE", "percent"),
    199: ("net_profit_ratio", "Net profit margin", "percent"),
    200: ("_total_asset_return_rate", "ROA", "percent"),
    202: ("gross_income_ratio", "Gross profit margin", "percent"),

    # Capital structure
    210: ("debt_equity_ratio", "Debt to asset ratio", "percent"),

    # Share capital
    238: ("total_shares", "Total shares", "shares"),
    239: ("a_floats", "Float A shares (listed circulating)", "shares"),
    242: ("_shareholder_count", "Number of shareholders", "count"),

    # TTM indicators
    276: ("_net_profit_ttm", "Net profit TTM", "yuan"),
    283: ("_operating_revenue_ttm", "Operating revenue TTM (10k yuan)", "wan_yuan"),

    # Announcement dates
    314: ("_publ_date_raw", "Financial report date (YYMMDD)", None),
}

# Reverse mapping: PTrade field name -> FINVALUE position
PTRADE_TO_FINVALUE = {v[0]: k for k, v in FINVALUE_TO_PTRADE.items()}

# Core fields commonly used in analysis
CORE_FUNDAMENTAL_FIELDS = [
    # Per-share
    "basic_eps",
    "naps",
    "roe",

    # Growth
    "operating_revenue_grow_rate",
    "net_profit_grow_rate",

    # Profitability
    "net_profit_ratio",
    "gross_income_ratio",

    # Solvency
    "current_ratio",
    "quick_ratio",
    "debt_equity_ratio",

    # Efficiency
    "accounts_receivables_turnover_rate",
    "total_asset_turnover_rate",
    "interest_cover",

    # Share data
    "total_shares",
    "a_floats",
]

# All mapped FINVALUE fields that can be exported as user-facing financial data.
# Internal date helper fields are intentionally excluded.
FULL_FUNDAMENTAL_FIELDS = [
    name
    for name, _desc, _unit in FINVALUE_TO_PTRADE.values()
    if not name.startswith("_")
]


def parse_finvalue_date(raw_date: int) -> str | None:
    """
    Parse FINVALUE date to ISO date string.

    Supports both formats:
    - YYMMDD (6-digit): e.g., 231231 -> '2023-12-31'
    - YYYYMMDD (8-digit): e.g., 20231231 -> '2023-12-31'

    Args:
        raw_date: Date in YYMMDD or YYYYMMDD format

    Returns:
        ISO date string (YYYY-MM-DD), or None if invalid
    """
    if not raw_date or raw_date == 0:
        return None

    raw_str = str(int(raw_date))

    if len(raw_str) == 8:
        # YYYYMMDD format
        return f"{raw_str[:4]}-{raw_str[4:6]}-{raw_str[6:8]}"

    # YYMMDD format (pad to 6 digits)
    raw_str = raw_str.zfill(6)
    year_prefix = "20" if int(raw_str[:2]) < 50 else "19"
    return f"{year_prefix}{raw_str[:2]}-{raw_str[2:4]}-{raw_str[4:6]}"
