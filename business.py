import numpy as np
import numpy_financial as npf  # Use numpy_financial for financial functions
import matplotlib.pyplot as plt

# ------------------------------
# PARAMETERS (adjust as needed)
# ------------------------------

# Upfront capital costs:
land_cost = 500_000                 # Land cost for 2 acres
chargers_cost = 1_000_000           # 10 DCFC chargers cost in $
construction_cost = 1_000_000         # Lounge & area construction cost in $
initial_investment = land_cost + chargers_cost + construction_cost

depreciable_capex = chargers_cost + construction_cost
subsidy_amount = 250_000
effective_initial_investment = initial_investment - subsidy_amount

# Depreciation (straight-line over analysis period, excluding land):
analysis_period = 10                 # Analysis period in years
annual_depreciation = depreciable_capex / analysis_period  # Only chargers and construction depreciate

# Operating assumptions:
# (The base sessions per day per charger is no longer used directly in sensitivity analysis.)
base_sessions = 10                  
revenue_per_session = 10            # $ per session (20 kWh at $0.50/kWh)
num_chargers = 10

# Charger revenue (base calculation):
daily_revenue_per_charger = base_sessions * revenue_per_session
annual_revenue_per_charger = daily_revenue_per_charger * 365
total_charger_revenue = annual_revenue_per_charger * num_chargers

# NEW: Lounge revenue based on visitors:
total_daily_people = base_sessions * num_chargers  # Total sessions across all chargers
lounge_visit_percentage = 0.4      # 40% of people visit the lounge
lounge_spend_per_person = 10     # $13 average spend per lounge visitor
local_visitors = 15                # 20 local visitors per day
lounge_daily_visitors = total_daily_people * lounge_visit_percentage + local_visitors
lounge_daily_revenue = lounge_daily_visitors * lounge_spend_per_person
lounge_annual_revenue = lounge_daily_revenue * 365

# Total annual revenue (base year):
annual_revenue = total_charger_revenue + lounge_annual_revenue

# Energy cost calculation (note: revenue_per_session is based on a charging price, not the cost to charge)
kWh_per_session = 20                   # kWh consumed per session
electricity_cost_per_kWh = 0.12        # cost in $ per kWh
energy_cost_per_session = kWh_per_session * electricity_cost_per_kWh

# Calculate annual energy cost:
daily_energy_cost = total_daily_people * energy_cost_per_session
annual_energy_cost = daily_energy_cost * 365

# Staffing/Administrative overhead (assumed value, adjust as needed)
staffing_cost = 100_000  

# Other miscellaneous operational expenses (this can be adjusted or further broken out)
# You might determine this as the residual needed to match an expected cost level or through direct estimation.
miscellaneous_cost = 22_070

# Total operational cost (excluding maintenance, which is handled separately)
operational_costs = annual_energy_cost + staffing_cost + miscellaneous_cost


maintenance_cost_per_charger = 3_000  # $3,000 per charger annually
total_annual_maintenance = maintenance_cost_per_charger * num_chargers  # $30,000 total maintenance

# Annual operating profit (before depreciation, base year):
annual_operating_profit_pre_depr = annual_revenue - operational_costs - total_annual_maintenance

# Annual operating profit (after depreciation, for reporting, base year):
annual_operating_profit = annual_operating_profit_pre_depr - annual_depreciation

# Discount rate:
discount_rate = 0.10                # Discount rate (10%)

# NEW: Growth and inflation rates:
revenue_growth_rate = 0.03          # 3% annual revenue growth
opex_inflation_rate = 0.02          # 2% annual operating cost inflation

# ---------------------------------
# CASH FLOW AND PROFITABILITY MODEL
# ---------------------------------

# Create an array for cash flows:
cash_flows = np.zeros(analysis_period + 1)
cash_flows[0] = -effective_initial_investment

# Dynamic cash flows with growth and inflation:
years = np.arange(analysis_period + 1)
for t in range(1, analysis_period + 1):
    revenue_t = annual_revenue * (1 + revenue_growth_rate) ** (t - 1)
    opex_t = operational_costs * (1 + opex_inflation_rate) ** (t - 1)
    maintenance_t = total_annual_maintenance * (1 + opex_inflation_rate) ** (t - 1)  # Maintenance escalates with inflation
    cash_flows[t] = revenue_t - opex_t - maintenance_t  # Depreciation added back as non-cash

# Compute NPV:
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
# SENSITIVITY ANALYSIS ON UTILIZATION PERCENTAGE
# -----------------
# Assuming 100% utilization means 48 charging sessions per day per charger.
# We'll vary utilization from 25% to 30% in 1% increments.
utilization_range = np.arange(15, 30 + 1, 1)  # in percent
npv_sensitivity_util = []      # to store NPV for each utilization level
sessions_list = []             # to store computed sessions per charger
profit_sensitivity_util = []   # to store Year 1 profit for each utilization level

for util in utilization_range:
    sessions = (util / 100) * 48  # convert utilization percentage to sessions per charger
    sessions_list.append(sessions)
    
    # Recalculate revenue with the new sessions per charger
    daily_revenue_per_charger_sens = sessions * revenue_per_session
    annual_revenue_per_charger_sens = daily_revenue_per_charger_sens * 365
    total_charger_revenue_sens = annual_revenue_per_charger_sens * num_chargers
    
    total_daily_people_sens = sessions * num_chargers

    lounge_daily_visitors_sens = total_daily_people_sens * lounge_visit_percentage  + local_visitors

    lounge_daily_revenue_sens = lounge_daily_visitors_sens * lounge_spend_per_person
    lounge_annual_revenue_sens = lounge_daily_revenue_sens * 365
    
    annual_revenue_sens = total_charger_revenue_sens + lounge_annual_revenue_sens
    
    # Calculate Year 1 profit (after depreciation)
    profit_year1 = annual_revenue_sens - operational_costs - total_annual_maintenance - annual_depreciation
    profit_sensitivity_util.append(profit_year1)
    
    # Recalculate cash flows for this scenario
    cash_flows_sens = np.zeros(analysis_period + 1)
    cash_flows_sens[0] = -effective_initial_investment
    for t in range(1, analysis_period + 1):
        revenue_t_sens = annual_revenue_sens * (1 + revenue_growth_rate) ** (t - 1)
        opex_t_sens = operational_costs * (1 + opex_inflation_rate) ** (t - 1)
        maintenance_t_sens = total_annual_maintenance * (1 + opex_inflation_rate) ** (t - 1)
        cash_flows_sens[t] = revenue_t_sens - opex_t_sens - maintenance_t_sens
    
    # Calculate NPV for this scenario
    npv_util = np.sum(cash_flows_sens / ((1 + discount_rate) ** years))
    npv_sensitivity_util.append(npv_util)

# -----------------
# PRINT THE RESULTS
# -----------------

print(f"Initial Investment (before subsidy): ${initial_investment:,.2f}")
print(f"Government Subsidy: ${subsidy_amount:,.2f}")
print(f"Effective Initial Investment (after subsidy): ${effective_initial_investment:,.2f}")
print(f"Annual Depreciation Expense: ${annual_depreciation:,.2f}")
print(f"Total Daily People Visiting Station: {total_daily_people:.0f}")
print(f"Lounge Daily Visitors (at {lounge_visit_percentage*100:.0f}%): {lounge_daily_visitors:.2f}")
print(f"Lounge Annual Revenue (Year 1): ${lounge_annual_revenue:,.2f}")
print(f"Annual Operating Profit (before depreciation, Year 1): ${annual_operating_profit_pre_depr:,.2f}")
print(f"Annual Operating Profit (after depreciation, Year 1): ${annual_operating_profit:,.2f}")
print(f"NPV over {analysis_period} years (at {discount_rate*100:.1f}% discount rate): ${npv:,.2f}")
print(f"IRR: {irr*100:.2f}%")
if payback_year is not None:
    print(f"Payback Period: {payback_year:.2f} years")
else:
    print("Payback period not reached within the analysis period.")
print(" Operating costs including maintenance:", operational_costs + total_annual_maintenance)
print("operating cost ")
# -----------------
# VISUALIZATION
# -----------------

plt.figure(figsize=(12, 6))

# Plot 1: Cumulative cash flow over time
plt.subplot(1, 2, 1)
plt.plot(years, cumulative_cash_flow, marker='o', linestyle='-', color='blue')
plt.axhline(0, color='black', linestyle='--', linewidth=1)
plt.xlabel('Year')
plt.ylabel('Cumulative Cash Flow ($)')
plt.title('Cumulative Cash Flow Over Time')
plt.grid(True)

# Plot 2: Sensitivity analysis table for NPV and Profit vs. Utilization Percentage
plt.subplot(1, 2, 2)
plt.axis('tight')
plt.axis('off')

# Prepare table data: columns are Utilization (%), Sessions/Charger, NPV, and Profit (Year 1).
table_data = []
for i, util in enumerate(utilization_range):
    table_data.append([f"{util:.0f}%", f"{sessions_list[i]:.2f}", f"${npv_sensitivity_util[i]:,.2f}", f"${profit_sensitivity_util[i]:,.2f}"])

table = plt.table(cellText=table_data,
                  colLabels=["Utilization", "Sessions/Charger", "NPV in year 10", "Profit (Year 1)"],
                  cellLoc='center',
                  loc='center')
table.auto_set_font_size(False)
table.set_fontsize(10)
plt.title('Sensitivity Analysis (Utilization vs. NPV & Profit)', pad=20)

plt.tight_layout()
plt.show()
