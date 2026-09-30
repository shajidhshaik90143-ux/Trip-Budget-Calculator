def build_budget(costs, travelers, contingency_percent):
    travelers = max(int(travelers), 1)
    rows = []

    for category, amount in costs.items():
        amount = float(amount)

        rows.append({
            "Category": category,
            "Amount": round(amount, 2),
            "PerPerson": round(amount / travelers, 2)
        })

    base_total = sum(row["Amount"] for row in rows)
    contingency = base_total * float(contingency_percent) / 100

    rows.append({
        "Category": "Contingency",
        "Amount": round(contingency, 2),
        "PerPerson": round(contingency / travelers, 2)
    })

    return rows


def budget_summary(rows):
    base_total = sum(
        row["Amount"]
        for row in rows
        if row["Category"] != "Contingency"
    )

    contingency = sum(
        row["Amount"]
        for row in rows
        if row["Category"] == "Contingency"
    )

    grand_total = base_total + contingency

    per_person = sum(
        row["PerPerson"]
        for row in rows
    )

    return {
        "base_total": round(base_total, 2),
        "contingency": round(contingency, 2),
        "grand_total": round(grand_total, 2),
        "per_person": round(per_person, 2)
    }


def daily_breakdown(costs, days, contingency_percent):
    days = max(int(days), 1)
    rows = []

    for day_number in range(1, days + 1):

        for category, amount in costs.items():
            daily_amount = float(amount) / days

            rows.append({
                "Day": f"Day {day_number}",
                "Category": category,
                "Total": round(daily_amount, 2)
            })

        base_total = sum(float(value) for value in costs.values())
        contingency = base_total * float(contingency_percent) / 100
        daily_contingency = contingency / days

        rows.append({
            "Day": f"Day {day_number}",
            "Category": "Contingency",
            "Total": round(daily_contingency, 2)
        })

    return rows
