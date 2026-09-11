# Freelance Income & Profit Calculator

print("=== FREELANCE EARNINGS CALCULATOR ===")

# 1. Ask user for information
hourly_rate = float(input("Enter your hourly rate ($): "))
hours_per_day = float(input("How many hours do you work per day? "))
days_per_week = int(input("How many days do you work per week? "))

# 2. Perform calculations
daily_income = hourly_rate * hours_per_day
weekly_income = daily_income * days_per_week
monthly_income = weekly_income * 4
yearly_income = monthly_income * 12

# 3. Display the results
print("\n--- YOUR POTENTIAL EARNINGS ---")
print("Daily Earnings:   $" + str(daily_income))
print("Weekly Earnings:  $" + str(weekly_income))
print("Monthly Earnings: $" + str(monthly_income))
print("Yearly Earnings:  $" + str(yearly_income))
print("------------------------------")