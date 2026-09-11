# Freelance Profit & Tax Calculator with Smart Advice

print("====================================")
print("   FREELANCE NET PROFIT ESTIMATOR   ")
print("====================================")

# 1. Gather User Data
hourly_rate = float(input("Enter your hourly rate ($): "))
hours_per_week = float(input("Hours worked per week: "))
monthly_expenses = float(input("Monthly business expenses (software, internet, etc.) ($): "))

# 2. Math Calculations
weekly_gross = hourly_rate * hours_per_week
monthly_gross = weekly_gross * 4
yearly_gross = monthly_gross * 12

# 3. Decision Making: Calculate Tax Percentage based on income
if yearly_gross < 30000:
    tax_rate = 0.10   # 10% tax
elif yearly_gross < 80000:
    tax_rate = 0.20   # 20% tax
else:
    tax_rate = 0.30   # 30% tax

# 4. Deduct Taxes and Expenses
yearly_tax = yearly_gross * tax_rate
yearly_expenses = monthly_expenses * 12
yearly_net_profit = yearly_gross - yearly_tax - yearly_expenses
monthly_net_profit = yearly_net_profit / 12

# 5. Output Results using f-strings
print("\n" + "="*35)
print("           FINANCIAL SUMMARY         ")
print("="*35)
print(f"Gross Yearly Income:  ${yearly_gross:,.2f}")
print(f"Estimated Taxes:     -${yearly_tax:,.2f} ({int(tax_rate * 100)}%)")
print(f"Annual Expenses:     -${yearly_expenses:,.2f}")
print("-" * 35)
print(f"NET Take-Home (Year): ${yearly_net_profit:,.2f}")
print(f"NET Take-Home (Month):${monthly_net_profit:,.2f}")
print("="*35)

# 6. Smart Advice based on results
if yearly_net_profit >= 50000:
    print(" Advice: Excellent! Your business model is highly profitable.")
elif yearly_net_profit >= 25000:
    print(" Advice: Good, but consider raising your hourly rate by 15-20%.")
else:
    print(" Advice: Warning! Your expenses or hours are cutting too deep into profits.")