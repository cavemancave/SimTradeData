# PTrade Financial Field Coverage

This document tracks SimTradeData coverage against PTrade `get_fundamentals`
financial tables. PTrade field names and table membership come from
`docs/archive/requirements/Ptrade_Financial_API.md`.

Current implementation note: SimTradeData exports quarterly statement and
indicator fields into one `fundamentals/` wide table per symbol, plus a separate
daily `valuation/` table. It does not yet export separate PTrade-style logical
tables such as `balance_statement/`, `income_statement/`, or
`cashflow_statement/`.

Identifier and metadata fields such as `secu_code`, `secu_abbr`, `company_type`,
`end_date`, `publ_date`, and `trading_day` are excluded from the coverage counts.
`date` in the Parquet file represents PTrade `end_date` for quarterly financials.

## Summary

| PTrade table | Covered fields | PTrade data fields | Coverage | Current source |
| --- | ---: | ---: | ---: | --- |
| `valuation` | 9 | 19 | 47% | BaoStock valuation plus forward-filled fundamentals |
| `balance_statement` | 17 | 114 | 15% | TDX/mootdx FINVALUE batch |
| `income_statement` | 8 | 54 | 15% | TDX/mootdx FINVALUE batch |
| `cashflow_statement` | 5 | 81 | 6% | TDX/mootdx FINVALUE batch |
| `growth_ability` | 6 | 18 | 33% | BaoStock and TDX/mootdx FINVALUE batch |
| `profit_ability` | 12 | 40 | 30% | BaoStock, derived fields, and TDX/mootdx FINVALUE batch |
| `eps` | 5 | 21 | 24% | TDX/mootdx FINVALUE batch |
| `operating_ability` | 4 | 11 | 36% | BaoStock and TDX/mootdx FINVALUE batch |
| `debt_paying_ability` | 4 | 17 | 24% | BaoStock and TDX/mootdx FINVALUE batch |

## Covered Fields

| PTrade table | Covered PTrade fields |
| --- | --- |
| `valuation` | `naps`, `pcf`, `ps_ttm`, `pe_ttm`, `a_floats`, `total_shares`, `turnover_rate`, `pb`, `roe` |
| `balance_statement` | `total_assets`, `total_liability`, `cash_equivalents`, `account_receivable`, `inventories`, `total_current_assets`, `shortterm_loan`, `accounts_payable`, `total_current_liability`, `fixed_assets`, `intangible_assets`, `total_non_current_assets`, `longterm_loan`, `total_non_current_liability`, `paidin_capital`, `retained_profit`, `total_shareholder_equity` |
| `income_statement` | `basic_eps`, `net_profit`, `np_parent_company_owners`, `operating_cost`, `financial_expense`, `operating_profit`, `operating_revenue`, `total_profit` |
| `cashflow_statement` | `net_operate_cash_flow`, `net_invest_cash_flow`, `net_finance_cash_flow`, `net_profit`, `financial_expense` |
| `growth_ability` | `basic_eps_yoy`, `operating_revenue_grow_rate`, `np_parent_company_yoy`, `net_asset_grow_rate`, `total_asset_grow_rate`, `net_profit_grow_rate` |
| `profit_ability` | `roe_weighted`, `roe`, `roe_ttm`, `roa_ebit_ttm`, `roa`, `roa_ttm`, `roic`, `net_profit_ratio`, `net_profit_ratio_ttm`, `gross_income_ratio`, `gross_income_ratio_ttm`, `net_profit` |
| `eps` | `basic_eps`, `naps`, `capital_surplus_fund_ps`, `undivided_profit`, `net_operate_cash_flow_ps` |
| `operating_ability` | `inventory_turnover_rate`, `accounts_receivables_turnover_rate`, `current_assets_turnover_rate`, `total_asset_turnover_rate` |
| `debt_paying_ability` | `current_ratio`, `quick_ratio`, `debt_equity_ratio`, `interest_cover` |

## Missing Fields

### `valuation`

Missing: `total_value`, `float_value`, `ps`, `a_shares`, `pe_dynamic`,
`pe_static`, `b_floats`, `b_shares`, `h_shares`, `dividend_ratio`.

Notes: `total_value` and `float_value` are direct daily valuation requirements.
They should be sourced from a daily market-cap source rather than quarterly
FINVALUE.

### `balance_statement`

Missing: `total_liability_and_equity`, `settlement_provi`, `client_provi`,
`deposit_in_interbank`, `r_metal`, `lend_capital`, `derivative_assets`,
`bought_sellback_assets`, `loan_and_advance`, `insurance_receivables`,
`receivable_subrogation_fee`, `reinsurance_receivables`,
`receivable_unearned_r`, `receivable_claims_r`, `receivable_life_r`,
`receivable_lt_health_r`, `insurer_impawn_loan`, `fixed_deposit`,
`refundable_capital_deposit`, `refundable_deposit`,
`independence_account_assets`, `other_assets`, `borrowing_from_centralbank`,
`deposit_of_interbank`, `borrowing_capital`, `derivative_liability`,
`sold_buyback_secu_proceeds`, `deposit`, `proxy_secu_proceeds`,
`sub_issue_secu_proceeds`, `deposits_received`, `advance_insurance`,
`commission_payable`, `reinsurance_payables`, `compensation_payable`,
`policy_dividend_payable`, `insurer_deposit_investment`,
`unearned_premium_reserve`, `outstanding_claim_reserve`,
`life_insurance_reserve`, `lt_health_insurance_lr`,
`independence_liability`, `other_liability`, `client_deposit`,
`trading_assets`, `bill_receivable`, `dividend_receivable`,
`interest_receivable`, `other_receivable`, `advance_payment`,
`non_current_asset_in_one_year`, `other_current_assets`, `impawned_loan`,
`trading_liability`, `notes_payable`, `advance_receipts`,
`salaries_payable`, `dividend_payable`, `taxs_payable`, `interest_payable`,
`other_payable`, `non_current_liability_in_one_year`,
`other_current_liability`, `hold_for_sale_assets`,
`hold_to_maturity_investments`, `investment_property`,
`longterm_equity_invest`, `longterm_receivable_account`,
`construction_materials`, `constru_in_process`, `fixed_assets_liquidation`,
`biological_assets`, `oil_gas_assets`, `seat_costs`,
`development_expenditure`, `good_will`, `long_deferred_expense`,
`deferred_tax_assets`, `other_non_current_assets`, `bonds_payable`,
`longterm_account_payable`, `long_salaries_pay`,
`specific_account_payable`, `estimate_liability`,
`deferred_tax_liability`, `long_defer_income`,
`other_non_current_liability`, `other_equityinstruments`,
`capital_reserve_fund`, `surplus_reserve_fund`, `treasury_stock`,
`other_composite_income`, `ordinary_risk_reserve_fund`,
`foreign_currency_report_conv_diff`, `specific_reserves`, `se_without_mi`,
`minority_interests`.

Notes: Many non-financial-company balance sheet fields are present in TDX
FINVALUE but are not enabled yet. Bank, broker, and insurance-specific fields
need an external statement source because TDX FINVALUE coverage is incomplete.

### `income_statement`

Missing: `diluted_eps`, `minority_profit`, `total_operating_cost`,
`operating_payout`, `refunded_premiums`, `compensation_expense`,
`amortization_expense`, `premium_reserve`, `amortization_premium_reserve`,
`policy_dividend_payout`, `reinsurance_cost`,
`amortization_reinsurance_cost`, `insurance_commission_expense`,
`other_operating_cost`, `operating_tax_surcharges`, `operating_expense`,
`administration_expense`, `asset_impairment_loss`,
`non_operating_income`, `non_operating_expense`,
`non_current_assetss_deal_loss`, `total_operating_revenue`,
`net_interest_income`, `interest_income`, `interest_expense`,
`net_commission_income`, `commission_income`, `commission_expense`,
`net_proxy_secu_income`, `net_subissue_secu_income`, `net_trust_income`,
`premiums_earned`, `premiums_income`, `reinsurance_income`, `reinsurance`,
`unearned_premium_reserve`, `other_operating_revenue`, `other_net_revenue`,
`fair_value_change_income`, `invest_income`, `invest_income_associates`,
`exchange_income`, `income_tax_cost`, `total_composite_income`,
`ci_parent_company_owners`, `ci_minority_owners`.

Notes: TDX FINVALUE can cover several non-financial-company fields directly,
but full PTrade parity requires a statement source with financial-sector fields.

### `cashflow_statement`

Missing: `goods_sale_service_render_cash`, `tax_levy_refund`,
`net_deposit_increase`, `net_borrowing_from_central_bank`,
`net_borrowing_from_finance_co`, `interest_and_commission_cashin`,
`net_deal_trading_assets`, `net_buyback`, `net_original_insurance_cash`,
`net_reinsurance_cash`, `net_insurer_deposit_investment`,
`other_cashin_related_operate`, `subtotal_operate_cash_inflow`,
`goods_and_services_cash_paid`, `staff_behalf_paid`, `all_taxes_paid`,
`net_loan_and_advance_increase`, `net_deposit_in_cb_and_ib`,
`net_lend_capital`, `commission_cash_paid`, `original_compensation_paid`,
`net_cash_for_reinsurance`, `policy_dividend_cash_paid`,
`other_operate_cash_paid`, `subtotal_operate_cash_outflow`,
`invest_withdrawal_cash`, `invest_proceeds`,
`fix_intan_other_asset_dispo_cash`, `net_cash_deal_sub_company`,
`other_cash_from_invest_act`, `subtotal_invest_cash_inflow`,
`fix_intan_other_asset_acqui_cash`, `invest_cash_paid`,
`net_cash_from_sub_company`, `impawned_loan_net_increase`,
`other_cash_to_invest_act`, `subtotal_invest_cash_outflow`,
`cash_from_invest`, `cash_from_bonds_issue`, `cash_from_borrowing`,
`other_finance_act_cash`, `subtotal_finance_cash_inflow`,
`borrowing_repayment`, `dividend_interest_payment`,
`other_finance_act_payment`, `subtotal_finance_cash_outflow`,
`exchan_rate_change_effect`, `cash_equivalent_increase`,
`begin_period_cash`, `end_period_cash_equivalent`, `minority_profit`,
`assets_depreciation_reserves`, `fixed_asset_depreciation`,
`intangible_asset_amortization`, `deferred_expense_amort`,
`deferred_expense_decreased`, `accrued_expense_added`,
`fix_intanther_asset_dispo_loss`, `fixed_asset_scrap_loss`,
`loss_from_fair_value_changes`, `invest_loss`,
`defered_tax_asset_decrease`, `defered_tax_liability_increase`,
`inventory_decrease`, `operate_receivable_decrease`,
`operate_payable_increase`, `others`, `net_operate_cash_flow_notes`,
`debt_to_captical`, `cbs_expiring_within_one_year`,
`fixed_assets_finance_leases`, `cash_at_end_of_year`,
`cash_at_beginning_of_year`, `cash_equivalents_at_end_of_year`,
`cash_equivalents_at_beginning`, `net_incr_in_cash_and_equivalents`.

Notes: TDX FINVALUE has many of the non-financial-company cash-flow fields.
Full PTrade parity still needs an external statement source for specialized
financial-sector cash-flow rows.

### `growth_ability`

Missing: `diluted_eps_yoy`, `net_operate_cash_flow_yoy`,
`oper_profit_grow_rate`, `total_profit_grow_rate`, `eps_grow_rate_ytd`,
`se_without_mi_grow_rate_ytd`, `ta_grow_rate_ytd`,
`np_parent_company_cut_yoy`, `avg_np_yoy_past_five_year`,
`oper_cash_ps_grow_rate`, `naor_yoy`, `sustainable_grow_rate`.

### `profit_ability`

Missing: `roe_avg`, `roe_cut`, `roe_cut_weighted`, `roa_ebit`,
`sales_cost_ratio`, `period_costs_rate`, `period_costs_rate_ttm`,
`np_to_tor`, `np_to_tor_ttm`, `operating_profit_to_tor`,
`operating_profit_to_tor_ttm`, `ebit_to_tor`, `ebit_to_tor_ttm`,
`t_operating_cost_to_tor`, `t_operating_cost_to_tor_ttm`,
`operating_expense_rate`, `operating_expense_rate_ttm`,
`admini_expense_rate`, `admini_expense_rate_ttm`,
`financial_expense_rate`, `financial_expense_rate_ttm`,
`asset_impa_loss_to_tor`, `asset_impa_loss_to_tor_ttm`,
`net_profit_cut`, `ebit`, `ebitda`, `operating_profit_ratio`,
`total_profit_cost_ratio`.

### `eps`

Missing: `diluted_eps`, `eps`, `eps_ttm`,
`total_operating_revenue_ps`, `main_income_ps`,
`operating_revenue_ps_ttm`, `oper_profit_ps`, `ebitps`,
`surplus_reserve_fund_ps`, `accumulation_fund_ps`,
`retained_earnings_ps`, `net_operate_cash_flow_ps_ttm`,
`cash_flow_ps`, `cash_flow_ps_ttm`, `enterprise_fcf_ps`,
`shareholder_fcf_ps`.

### `operating_ability`

Missing: `oper_cycle`, `inventory_turnover_days`,
`accounts_receivables_turnover_days`, `accounts_payables_turnover_rate`,
`accounts_payables_turnover_days`, `fixed_asset_turnover_rate`,
`equity_turnover_rate`.

### `debt_paying_ability`

Missing: `super_quick_ratio`, `sewmi_to_total_liability`,
`sewmi_to_interest_bear_debt`, `debt_tangible_equity_ratio`,
`tangible_a_to_interest_bear_debt`, `tangible_a_to_net_debt`,
`ebitda_to_t_liability`, `nocf_to_t_liability`,
`nocf_to_interest_bear_debt`, `nocf_to_current_liability`,
`nocf_to_net_debt`, `long_debt_to_working_capital`,
`opercashinto_current_debt`.

## Recommended Source Plan

1. Keep TDX/mootdx FINVALUE as the fast batch baseline for fields it can map
   exactly to PTrade names and semantics.
2. Add remaining exact FINVALUE mappings first, because they preserve the fast
   all-symbol quarterly refresh path and do not add a new dependency.
3. Add a separate statement-source adapter for missing PTrade fields that TDX
   cannot supply. AKShare documents EastMoney report-period interfaces for
   balance sheet, income statement, cash-flow statement, and major financial
   indicators:
   `stock_balance_sheet_by_report_em`,
   `stock_profit_sheet_by_report_em`,
   `stock_cash_flow_sheet_by_report_em`, and
   `stock_financial_analysis_indicator_em`.
4. Do not export upstream-specific fields unless they map to a documented
   PTrade field name and meaning.
5. Decide before implementation whether strict PTrade compatibility requires
   separate Parquet directories per logical financial table, or whether the
   current single `fundamentals/` wide table remains the project contract.
