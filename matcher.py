from typing import List, Dict
from rapidfuzz import fuzz, process

def match_items(shopping_list: List[Dict], store_data: Dict[str, List[Dict]], allow_subs: bool = True) -> Dict[str, List[Dict]]:
    matched_results = {}
    for store, products in store_data.items():
        store_matches = []
        for item in shopping_list:
            choices = [product['name'] for product in products]
            if allow_subs:
                best_match = process.extractOne(
                    item.name,
                    choices,
                    scorer=fuzz.token_sort_ratio
                )
                if best_match and best_match[1] >= 70:
                    matched_name = best_match[0]
                else:
                    matched_name = None
            else:
                matched_name = item.name if item.name in choices else None
            if matched_name:
                matched_product = next(p for p in products if p['name'] == matched_name)
                store_matches.append({
                    "requested": item.name,
                    "matched": matched_name,
                    "price": matched_product['price'],
                    "quantity": item.quantity
                })
        matched_results[store] = store_matches
    return matched_results