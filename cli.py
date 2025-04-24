# grocery_bot_mvp/cli.py

import requests

API_URL = "http://localhost:8000/compare"

def get_user_input():
    print("Enter your shopping list items one by one. Format: '<quantity> <item>'. Type 'done' to finish:")
    items = []
    while True:
        entry = input("Item: ").strip()
        if entry.lower() == 'done':
            break
        if entry:
            try:
                quantity, name = entry.split(" ", 1)
                items.append({"name": name, "quantity": float(quantity)})
            except ValueError:
                print("Invalid format. Use '<quantity> <item>', e.g., '2 milk'")

    allow_subs = input("Allow substitutions? (yes/no): ").strip().lower() in ["yes", "y"]
    include_tags = input("Include tags (e.g., 'vegan gluten-free', leave blank if none): ").strip().split()
    exclude_brands = input("Exclude brands (e.g., 'Nestlé Heinz', leave blank if none): ").strip().split()

    return {
        "items": items,
        "allow_substitutions": allow_subs,
        "include_tags": include_tags,
        "exclude_brands": exclude_brands
    }

def main():
    shopping_list = get_user_input()
    print("\nComparing prices...\n")
    response = requests.post(API_URL, json=shopping_list)
    if response.status_code == 200:
        results = response.json()
        for store in results:
            print(f"Store: {store['store']}")
            print(f"  Subtotal: £{store['subtotal']:.2f}")
            print(f"  Delivery: £{store['delivery_fee']:.2f}")
            print(f"  Total:    £{store['total_price']:.2f}")
            for item in store['items']:
                print(f"    - {item['quantity']} × {item['requested']} → {item['matched']} @ £{item['price']:.2f} each")
            print()
    else:
        print("Error fetching comparison results.")

if __name__ == "__main__":
    main()
