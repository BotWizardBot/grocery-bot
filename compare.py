from typing import Dict, List

def compare_prices(matched_data: Dict[str, List[Dict]]) -> List[Dict]:
    delivery_fees = {
        "tesco": 3.00,
        "sainsburys": 3.50,
        "asda": 2.95
    }

    store_totals = []
    for store, items in matched_data.items():
        subtotal = sum(item['price'] * item.get('quantity', 1) for item in items)
        total = subtotal + delivery_fees.get(store, 0)
        store_totals.append({
            "store": store,
            "subtotal": round(subtotal, 2),
            "delivery_fee": delivery_fees.get(store, 0),
            "total_price": round(total, 2),
            "items": items
        })

    store_totals.sort(key=lambda x: x['total_price'])
    return store_totals