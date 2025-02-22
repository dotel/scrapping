import numpy as np
import numpy_financial as npf  # Use numpy_financial for financial functions
import matplotlib.pyplot as plt

# ------------------------------
# PARAMETERS (adjust as needed)
# ------------------------------

# Upfront capital costs:
land_cost = 500_000                 # Land cost for 2 acres
chargers_cost = 1_000_000           # 10 DCFC chargers cost in $
construction_cost = 500_000          # Lounge & area construction cost in $
initial_investment = land_cost + chargers_cost + construction_cost

depreciable_capex = chargers_cost + construction_cost
subsidy_amount = 250_000
effective_initial_investment = initial_investment - subsidy_amount

# Depreciation (straight-line over analysis period, excluding land):
analysis_period = 9                 # Analysis period in years
annual_depreciation = depreciable_capex / analysis_period  # Only chargers and construction depreciate

# Operating assumptions:
sessions_per_day_per_charger = 18               # sessions per day per charger
revenue_per_session = 10            # $ per session (20 kWh at $0.50/kWh)
num_chargers = 10

# Charger revenue:
daily_revenue_per_charger = sessions_per_day_per_charger * revenue_per_session
annual_revenue_per_charger = daily_revenue_per_charger * 365
total_charger_revenue = annual_revenue_per_charger * num_chargers

# NEW: Lounge revenue based on visitors:
total_daily_people = sessions_per_day_per_charger * num_chargers  # Total sessions across all chargers
lounge_visit_percentage = 0.30      # 30% of people visit the lounge
lounge_spend_per_person = 10        # $10 average spend per lounge visitor
lounge_daily_visitors = total_daily_people * lounge_visit_percentage
lounge_daily_revenue = lounge_daily_visitors * lounge_spend_per_person
lounge_annual_revenue = lounge_daily_revenue * 365

# Total annual revenue:
annual_revenue = total_charger_revenue + lounge_annual_revenue

# --- PARAMETERS FOR OPERATIONAL COST CALCULATION ---
# Energy cost calculation (note: revenue_per_session is based on a charging price, not the cost to charge)
kWh_per_session = 20                   # kWh consumed per session
electricity_cost_per_kWh = 0.12        # cost in $ per kWh
energy_cost_per_session = kWh_per_session * electricity_cost_per_kWh

# Calculate annual energy cost:
daily_sessions = sessions_per_day_per_charger * num_chargers  # total sessions per day
daily_energy_cost = daily_sessions * energy_cost_per_session
annual_energy_cost = daily_energy_cost * 365

# Staffing/Administrative overhead (assumed value, adjust as needed)
staffing_cost = 100_000  

# Other miscellaneous operational expenses (this can be adjusted or further broken out)
# You might determine this as the residual needed to match an expected cost level or through direct estimation.
miscellaneous_cost = 22_070  

# Total operational cost (excluding maintenance, which is handled separately)
operational_costs = annual_energy_cost + staffing_cost + miscellaneous_cost

print(f"Calculated Annual Energy Cost: ${annual_energy_cost:,.2f}")
print(f"Calculated Operational Costs (excluding maintenance): ${operational_costs:,.2f}")


# Annual operating profit (before depreciation):
annual_operating_profit_pre_depr = annual_revenue - operational_costs

# Annual operating profit (after depreciation, for reporting):
annual_operating_profit = annual_operating_profit_pre_depr - annual_depreciation

# Discount rate:
discount_rate = 0.10                # Discount rate (10%)

# ---------------------------------
# CASH FLOW AND PROFITABILITY MODEL
# ---------------------------------

# Create an array for cash flows:
cash_flows = np.zeros(analysis_period + 1)
cash_flows[0] = -effective_initial_investment
cash_flows[1:] = annual_operating_profit_pre_depr  # Depreciation is added back as it’s non-cash

# Compute NPV:
years = np.arange(analysis_period + 1)
npv = np.sum(cash_flows / ((1 + discount_rate) ** years))

# Compute IRR (Internal Rate of Return) using numpy_financial
irr = npf.irr(cash_flows)

# Compute cumulative cash flow for each year (for payback period analysis):
cumulative_cash_flow = np.cumsum(cash_flows)

# Estimate the payback period:
payback_year = None
for i, cum_cash in enumerate(cumulative_cash_flow):
    if cum_cash >= 0:
        if i == 0:
            payback_year = 0
        else:
            prev_cum = cumulative_cash_flow[i - 1]
            # Linear interpolation between year (i-1) and i:
            fraction = (0 - prev_cum) / (cumulative_cash_flow[i] - prev_cum)
            payback_year = i - 1 + fraction
        break

# -----------------
# PRINT THE RESULTS
# -----------------

print(f"Initial Investment (before subsidy): ${initial_investment:,.2f}")
print(f"Government Subsidy: ${subsidy_amount:,.2f}")
print(f"Effective Initial Investment (after subsidy): ${effective_initial_investment:,.2f}")
print(f"Annual Depreciation Expense: ${annual_depreciation:,.2f}")
print(f"Total Daily People Visiting Station: {total_daily_people:.0f}")
print(f"Lounge Daily Visitors (at {lounge_visit_percentage*100:.0f}%): {lounge_daily_visitors:.2f}")
print(f"Lounge Annual Revenue: ${lounge_annual_revenue:,.2f}")
print(f"Annual Operating Profit (before depreciation): ${annual_operating_profit_pre_depr:,.2f}")
print(f"Annual Operating Profit (after depreciation): ${annual_operating_profit:,.2f}")
print(f"NPV over {analysis_period} years (at {discount_rate*100:.1f}% discount rate): ${npv:,.2f}")
print(f"IRR: {irr*100:.2f}%")
if payback_year is not None:
    print(f"Payback Period: {payback_year:.2f} years")
else:
    print("Payback period not reached within the analysis period.")

# -----------------
# VISUALIZATION
# -----------------

# Plot cumulative cash flow over time.
plt.figure(figsize=(10, 6))
plt.plot(years, cumulative_cash_flow, marker='o', linestyle='-', color='blue')
plt.axhline(0, color='black', linestyle='--', linewidth=1)
plt.xlabel('Year')
plt.ylabel('Cumulative Cash Flow ($)')
plt.title('Cumulative Cash Flow Over Time (with Subsidy and Depreciation)')
plt.grid(True)
plt.show()
