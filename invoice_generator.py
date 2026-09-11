# Itemized Freelance Invoice Generator

print("========================================")
print("       FREELANCE INVOICE BUILDER        ")
print("========================================")

# 1. Basic Client Information
client_name = input("Client / Company Name: ")
invoice_number = input("Invoice #: ")

# 2. Collect Line Items Using a List and a While Loop
items = []  # Empty list to store all services

print("\n--- Enter line items (type 'done' when finished) ---")

while True:
    description = input("\nService description (or 'done' to finish): ")
    
    # Check if the user wants to stop adding items
    if description.lower() == "done":
        break
    
    price = float(input(f"Price for '{description}' ($): "))
    
    # Store this item as a dictionary and add it to our list
    item_entry = {"name": description, "price": price}
    items.append(item_entry)
    print(f" Added: {description} - ${price:,.2f}")

# 3. Calculate Totals with a For Loop
subtotal = 0
for item in items:
    subtotal += item["price"]

tax_rate = 0.08  # 8% sales tax or transaction fee
tax_amount = subtotal * tax_rate
total_due = subtotal + tax_amount

# 4. Print the Clean Itemized Invoice
print("\n\n" + "=" * 50)
print(f"                   INVOICE #{invoice_number}")
print("=" * 50)
print(f"Billed To: {client_name}")
print("-" * 50)
print(f"{'DESCRIPTION':<35} {'AMOUNT':>12}")
print("-" * 50)

# Loop through each item to print line-by-line
for item in items:
    print(f"{item['name']:<35} ${item['price']:>11,.2f}")

print("-" * 50)
print(f"{'Subtotal:':<35} ${subtotal:>11,.2f}")
print(f"{'Tax / Processing Fee (8%):':<35} ${tax_amount:>11,.2f}")
print("=" * 50)
print(f"{'TOTAL DUE:':<35} ${total_due:>11,.2f}")
print("=" * 50)
print(" Payment due within 14 days. Thank you for your business!\n")