# Automated Invoice Generator & File Saver

def create_invoice():
    print("========================================")
    print("      AUTOMATED INVOICE GENERATOR       ")
    print("========================================")

    # 1. Gather Client Info
    client_name = input("Client Name: ")
    invoice_num = input("Invoice # (e.g. 101): ")

    items = []

    # 2. Collect Items
    print("\n--- Enter items (type 'done' when finished) ---")
    while True:
        desc = input("\nService description: ")
        if desc.lower() == "done":
            break
        
        try:
            price = float(input(f"Price for '{desc}' ($): "))
            items.append({"name": desc, "price": price})
        except ValueError:
            print("❌ Invalid price! Please enter a number.")

    if not items:
        print("⚠️ No items added. Invoice creation cancelled.")
        return

    # 3. Calculations
    subtotal = sum(item["price"] for item in items)
    tax = subtotal * 0.08
    total = subtotal + tax

    # 4. Build the invoice text layout
    lines = []
    lines.append("=" * 50)
    lines.append(f"                   INVOICE #{invoice_num}")
    lines.append("=" * 50)
    lines.append(f"Billed To: {client_name}")
    lines.append("-" * 50)
    lines.append(f"{'DESCRIPTION':<35} {'AMOUNT':>12}")
    lines.append("-" * 50)

    for item in items:
        lines.append(f"{item['name']:<35} ${item['price']:>11,.2f}")

    lines.append("-" * 50)
    lines.append(f"{'Subtotal:':<35} ${subtotal:>11,.2f}")
    lines.append(f"{'Tax (8%):':<35} ${tax:>11,.2f}")
    lines.append("=" * 50)
    lines.append(f"{'TOTAL DUE:':<35} ${total:>11,.2f}")
    lines.append("=" * 50)
    lines.append("Payment due within 14 days. Thank you!")

    invoice_text = "\n".join(lines)

    # 5. Display on Screen
    print("\n" + invoice_text)

    # 6. Save to a real text file on your computer
    filename = f"invoice_{invoice_num}.txt"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(invoice_text)

    print(f"\n✅ SUCCESS! Saved as: {filename}")


# Run the function
create_invoice()